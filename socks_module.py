import requests

def test_connection(proxy):
    proxy_server = proxy["server"]
    proxy_port = proxy["port"]
    proxy_username = proxy["username"]
    proxy_password = proxy["password"]
    proxies = {
        "http": f"socks5://{proxy_username}:{proxy_password}@{proxy_server}:{proxy_port}",
        "https": f"socks5://{proxy_username}:{proxy_password}@{proxy_server}:{proxy_port}",
    }

    try:
        response = requests.get("http://ifconfig.me", proxies=proxies, timeout=5)
        return True
    except requests.RequestException as e:
        print(f"❌ Failed to resolve public IP through the SOCKS server: {proxy['server']}:{proxy['port']} - {e}")
        return False