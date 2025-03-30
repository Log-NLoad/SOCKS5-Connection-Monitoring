import json
import socks_module
import email_module
import sys
import logging
import time

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Error: Configuration file '{config_file}' not found.")
        logging.info(f"❌ Error: Configuration file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in '{config_file}'.")
        logging.info(f"❌ Error: Invalid JSON format in '{config_file}'.")
        sys.exit(1)


def main(config):
    failure_count = {}
    proxies = config["proxies"]
    smtp_host = config["smtp_host"]
    smtp_port = config["smtp_port"]
    sender_email = config["sender_email"]
    sender_password = config["sender_password"]
    recipient_email = config["recipient_email"]
    email_subject = config["email_subject"]
    email_body = config["email_body"]

    for proxy in proxies:
        proxy_address = proxy['server'] + ':' + str(proxy['port'])
        if proxy_address not in failure_count:
            failure_count[proxy_address] = 0
        print(f"🔄 Checking connection through the SOCKS server: {proxy['server']}:{proxy['port']}...")
        logging.info(f"🔄 Checking connection through the SOCKS server: {proxy['server']}:{proxy['port']}...")
        resolve_status = socks_module.test_connection(proxy)
        while not resolve_status:
            failure_count[proxy_address] += 1
            if failure_count[proxy_address] >= 3:
                print(f"❌ Failed to resolve public IP through the SOCKS server: {proxy['server']}:{proxy['port']}.")
                print("📨 Sending email notification...")
                logging.info(f"❌ Failed to resolve public IP through the SOCKS server: {proxy['server']}:{proxy['port']}.")
                logging.info(f"📨 Sending email notification...")
                email_module.send_email(smtp_host, smtp_port, sender_email, sender_password, recipient_email, email_subject, email_body, proxy)
                failure_count[proxy_address] = 0
                break
            print("The proxy failed. Waiting 10 seconds before retrying...")
            logging.info("The proxy failed. Waiting 10 seconds before retrying...")
            time.sleep(10)
            resolve_status = socks_module.test_connection(proxy)
            if resolve_status:
                print(f"✅ SOCKS connection has recovered and is working through: {proxy['server']}:{proxy['port']}.")
                logging.info(f"✅ SOCKS connection has recovered and is working through: {proxy['server']}:{proxy['port']}.")
                failure_count[proxy_address] = 0
                break
        if resolve_status:
            print(f"✅ SOCKS connection is working through: {proxy['server']}:{proxy['port']}.")
            logging.info(f"✅ SOCKS connection is working through: {proxy['server']}:{proxy['port']}.")
            failure_count[proxy_address] = 0

if __name__ == "__main__":
    config = load_config("config.json")
    main(config)