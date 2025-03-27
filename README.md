# SOCKS5-Connection-Monitoring
A Python script for monitoring SOCKS5 proxy connections and sending email notifications when they fail.

## Installation

### Debian/Ubuntu-based:
```sh
bash <(curl -L https://raw.githubusercontent.com/Log-NLoad/SOCKS5-Connection-Monitoring/main/install.sh)
```
### RHEL-based:
```sh
bash <(curl -L https://raw.githubusercontent.com/Log-NLoad/SOCKS5-Connection-Monitoring/main/install_rhel.sh)
```

## Configuration
The installation script will ask for necessary information, and store it in a config.json file.
You can manually check it and make changes:
```sh
/socks_monitor/config.json
```

## Usage
The script uses cronjob to run at a 5-minute interval.
To manually run the script:
```sh
cd /socks_monitor
venv/bin/python3 monitor.py
```

## Uninstall
```sh
sudo rm -rf /socks_monitor
crontab -l | grep -v 'monitor.py' | crontab -
```
