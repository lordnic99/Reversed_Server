#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import server_conf_generator
import instance_deploy
import sys
from requests import get
    

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proxy_endpoint.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


SECRET_KEY = os.getenv('SECRET_KEY', '')

class Tunnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tunnel_name = db.Column(db.String(255))
    remote_port = db.Column(db.String(255))
    bind_port = db.Column(db.String(255))
    token = db.Column(db.String(255))
    config_name = db.Column(db.String(255))

with app.app_context():
    db.create_all()

def insert_tunnel_to_db(tunnel_name, remote_port, bind_port, token, config_name):
    new_data = Tunnel(tunnel_name=tunnel_name, remote_port=remote_port, bind_port=bind_port, token=token, config_name=config_name)
    db.session.add(new_data)
    db.session.commit()
    return new_data.id
   
def read_tunnel_from_db(id):
   tunnel = Tunnel.query.get(id)
   if tunnel:
       return tunnel
   else:
       return None

# def read_all_tunnels():
#   tunnels = Tunnel.query.all()

#   if not tunnels:
#     print("No tunnels found in the database.")
#     return

#   print("{:<20} {:<20} {:<20} {:<40} {:<40}".format(
#       'Name', 'Remote Port', 'Bind Port', 'Token', 'Config Name'))
#   print("-" * 140)

#   for tunnel in tunnels:
#     print("{:<20} {:<20} {:<20} {:<40} {:<40}".format(
#         tunnel.id, tunnel.remote_port, tunnel.bind_port, tunnel.token, tunnel.config_name))

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != SECRET_KEY:
            return jsonify({"status": "NOK", "message": "Wrong secret key"}), 401
        return f(*args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator


@app.route('/createtunnel', methods=['POST'])
@token_required
def create_tunnel():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"status": "NOK", "message": "Tunnel name required"}), 400
    tunnel_name = data['name']
    
    print(f"-> Recive tunnel post request with name: {tunnel_name}")
    
    server_ip, remote_port, bind_port, token, config_name = server_conf_generator.main(tunnel_name)
    
    tunnel_id = insert_tunnel_to_db(tunnel_name, str(remote_port), str(bind_port), token, config_name)
    
    instance_deploy.main(config_name)
    
    return jsonify({"status": "OK", "serverIP": server_ip, "remotePort": remote_port, "bindPort": bind_port, "token": token, "tunnelID": tunnel_id, "message": "Tunnel created OK"}), 201



@app.route('/gettunnel', methods=['GET'])
@token_required
def get_tunnel():
    id = request.args.get('id')
    tunnel = read_tunnel_from_db(id)
    
    if tunnel == None:
        return jsonify({"status": "NOK", "message": "Wrong tunnel ID"}), 401
    
    server_ip = get('https://api.ipify.org').content.decode('utf8')
    return jsonify({"status": "OK", "serverIP": server_ip, "remotePort": tunnel.remote_port, "bindPort": tunnel.bind_port, "token": tunnel.token, "tunnelID": tunnel.id, "message": "Tunnel get request OK"})

users = {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=44444)
