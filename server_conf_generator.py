#!/usr/bin/env python3

import socket
import sys
import string
import random
from requests import get
import os
from pathlib import Path
import csv

def check_available_ports(start_port, end_port):
    available_ports = []
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.bind(("localhost", port))
                available_ports.append(port)
        except OSError:
            pass

    return available_ports

def generate_token(length=32):
  characters = string.ascii_letters
  return ''.join(random.choice(characters) for _ in range(length))

def generate_server_config(token, listen_port, bind_port, tunnel_name, config_name):
    SERVER_CONF_TEMPLATE = f'''[server]
bind_addr = "0.0.0.0:{listen_port}"
default_token = "{token}"

[server.services.{tunnel_name}]
type = "udp"
bind_addr = "0.0.0.0:{bind_port}"
'''
    
    with open(f"{config_name}.toml", "w") as f:
        f.write(SERVER_CONF_TEMPLATE)
        
# def generate_client_config(token, remote_addr, tunnel_name, config_name):
#     CLIENT_CONF_TEMPLATE = f'''[client]
# remote_addr = "{remote_addr}"
# default_token = "{token}"

# [client.services.{tunnel_name}]
# type = "udp"
# local_addr = "127.0.0.1:55555"
# '''
#     with open(f"{config_name}.toml", "w") as f:
#         f.write(CLIENT_CONF_TEMPLATE)

def save_used_ports_to_csv(port_list, config_dir=".config/reversed_server", filename="port_used.csv"):
  full_path = os.path.join(str(Path.home()), config_dir, filename)
  
  os.makedirs(os.path.dirname(full_path), exist_ok=True)

  with open(full_path, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(port_list)
    
def read_used_ports_from_csv(config_dir=".config/reversed_server", filename="port_used.csv"):
  full_path = os.path.join(str(Path.home()), config_dir, filename)
  used_ports = []
  if not os.path.exists(full_path):
    return used_ports

  with open(full_path, "r", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      used_ports.extend([int(port) for port in row])

  return used_ports
    
    
def main(tunnel_name):
    start_port = 49152
    end_port = 65535
    
    print("-> Getting available port for setup")
    
    used_ports = read_used_ports_from_csv()
    
    available_ports = check_available_ports(start_port, end_port)
    
    available_ports[:] = list(set(available_ports) - set(used_ports))
    
    if len(available_ports) >= 2:
        pass
    else:
        print("not enough port ready for setup")
        os._exit(1)
        
    remote_port = available_ports[0]
    bind_port = available_ports[1]
    token = generate_token()
    server_ip = get('https://api.ipify.org').content.decode('utf8')
    config_name = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
    
    print(f"-> Public IP found: {server_ip}")
    generate_server_config(token, remote_port, bind_port, tunnel_name, f"server_{config_name}")
    print(f"-> Config generate ok!")
    
    save_used_ports_to_csv([remote_port, bind_port])
    return server_ip, remote_port, bind_port, token, f"server_{config_name}.toml"

