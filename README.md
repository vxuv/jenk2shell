# jenk2shell
Jenkins has the ability to execute commands through the script console using `"".execute().text`. This tool provides a small reverse shell through Jenkins Script Manager, allowing users to execute commands on a remote server from within Jenkins. Provides an easy way to manage shell access without having to setup a ncat instance. For bugbounties or devops.


## Setup
```bash
# python3 required
cd jenk2shell
# linux
pip3 install -r requirements.txt
# windows
pip install -r requirements.txt
```

## Usage
```bash
# cookies are optional, only if the jenkins instance requires auth
# proxy is also optional, supports http, https, socks5 format: type://ipv4:port
python3 --url target.com --cookies "JSESSIONID=1234; " --proxy "socks5://127.0.0.1:9050"
```


## Notes
Each command is executed without respect to any prior commands so if you want to chain two commands use the `&` operator like `cd folder & ls -a`
