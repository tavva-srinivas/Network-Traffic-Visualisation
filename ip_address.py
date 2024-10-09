import socket
private_ip = socket.gethostbyname(socket.gethostname())
print(f"Private IP: {private_ip}")


import requests
public_ip = requests.get('https://api.ipify.org').text
print(f"Public IP: {public_ip}")
