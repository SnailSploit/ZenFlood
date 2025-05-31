```
 ________                      ________  __                            __
/        |                    /        |/  |                          /  |
$$$$$$$$/   ______   _______  $$$$$$$$/ $$ |  ______    ______    ____$$ |
    /$$/   /      \ /       \ $$ |__    $$ | /      \  /      \  /    $$ |
   /$$/   /$$$$$$  |$$$$$$$  |$$    |   $$ |/$$$$$$  |/$$$$$$  |/$$$$$$$ |
  /$$/    $$    $$ |$$ |  $$ |$$$$$/    $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |
 /$$/____ $$$$$$$$/ $$ |  $$ |$$ |      $$ |$$ \__$$ |$$ \__$$ |$$ \__$$ |
/$$      |$$       |$$ |  $$ |$$ |      $$ |$$    $$/ $$    $$/ $$    $$ |
$$$$$$$$/  $$$$$$$/ $$/   $$/ $$/       $$/  $$$$$$/   $$$$$$/   $$$$$$$/
```


**ZenFlood** is an advanced, multi-protocol slow HTTP research tool for red team, adversarial AI, and defensive simulation.

- **HTTP/1.1 (classic Slowloris)** and **HTTP/2 (multiplexed slow attacks)**
- Randomized, obfuscated, jittered headers and payloads
- Supports both **slow GET** and **slow POST (chunked)**
- Captures server responses for behavioral and ML analysis
- Designed for research, not crime — **authorized use only**

---

## Features

- **HTTP/1.1 & HTTP/2 support:** Modern coverage, cloud/CDN-ready
- **Header & Payload Randomization:** Mimics advanced bots, defeats naive heuristics
- **Timing Jitter:** Simulates organic slow clients, evades static rules
- **Response Logging:** Enables ML, detection, and adversarial signal analysis
- **Easy to Extend:** Modular code for rapid experimentation

---

## Installation

```bash
pip install h2 pysocks
````

---

## Usage

### Classic Slowloris (HTTP/1.1, HTTPS):

```bash
python3 zenflood.py example.com --https
```

### Slowloris with HTTP/2 (modern, multiplexed):

```bash
python3 zenflood.py example.com --https --http2
```

### Slow POST / Chunked transfer:

```bash
python3 zenflood.py example.com --https --mode post
```

### Advanced Jitter (adversarial/realistic traffic):

```bash
python3 zenflood.py example.com --https --header-jitter-min 0.5 --header-jitter-max 2 --payload-jitter-min 4 --payload-jitter-max 10
```

### Full options:

```bash
python3 zenflood.py -h
```

---

## Example Output

```
[+] Active sockets: 100 | Recent log: [b'HTTP/1.1 503 Service Unavailable\r\n...']
```

---

## Research and Defensive Use

ZenFlood is built for:

* Adversarial red team and XDR/SIEM/AI dataset generation
* Real-world simulation of slow HTTP/1.1 and HTTP/2 DoS for blue teams
* Testing rate-limiting, WAF, and CDN protections in hybrid/cloud environments

---

## Ethical Notice

**Only use ZenFlood with explicit, written authorization on systems you own or are approved to test.
This tool is for research and defense — not for unauthorized activity, crime, or vandalism.**

---

## Attribution

Original by ZenRat-47
Modernized and maintained by Kai Aizen
2025 — For the security community and responsible adversarial research

---

## License

MIT License

---

## Roadmap

* HTTP/3/QUIC support (planned)
* ML integration for automated label generation
* AsyncIO-based high-scale mode

---

*Open to contributions, feedback, and professional collaboration.*

```

---

**You can copy-paste this directly for your repo.**  
Let me know if you want additional badges, FAQ, or ML integration examples!
```
