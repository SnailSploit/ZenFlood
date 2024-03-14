# ZenFlood
ZenFlood is a low-bandwidth stress testing tool designed to simulate a DDoS attack by holding open a large number of HTTP connections to the target server. This tool is inspired by the Slowloris attack and is designed to test the resilience of web servers to such attacks.

# ZenFlood

ZenFlood is a low-bandwidth stress testing tool designed to simulate a DDoS attack by holding open a large number of HTTP connections to the target server. This tool is inspired by the Slowloris attack and is designed to test the resilience of web servers to such attacks.

## Features

- Customizable number of sockets to open
- Randomized user-agent headers to mimic different browsers
- Optional SOCKS5 proxy support for anonymized testing
- Supports HTTP and HTTPS protocols
- Configurable request intervals

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine
- Access to a terminal or command-line interface

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/ZenFlood.git
cd ZenFlood


## Usage
To use ZenFlood, you can run the script with the required options from the command line:

bash
Copy code
python3 zenflood.py [host] [options]
Options
-p, --port: Port of the webserver, default is 80
-s, --sockets: Number of sockets to use in the test
-v, --verbose: Increase logging to see the details of the attack
-ua, --randuseragents: Randomize user-agents with each request
-x, --useproxy: Use a SOCKS5 proxy for connecting
--proxy-host: SOCKS5 proxy host
--proxy-port: SOCKS5 proxy port
--https: Use HTTPS for the requests
--sleeptime: Time to sleep between each header sent
Contributing
Contributions to ZenFlood are welcome. To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-branch).
Create a new Pull Request.





