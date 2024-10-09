# ip_location.py
import requests

def get_ip_location(ip):
    url = f'http://ip-api.com/json/{ip}'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data['status'] == 'success':
        return data['lat'], data['lon']
    else:
        print(f"Location data not found for IP: {ip}")
        return None, None
