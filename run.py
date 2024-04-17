#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import server_conf_generator
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
   
def read_tunnel_from_db(config_name):
   tunnel = Tunnel.query.get(config_name)
   if tunnel:
       return tunnel.id
   else:
       return None

def read_all_tunnels():
  tunnels = Tunnel.query.all()

  if not tunnels:
    print("No tunnels found in the database.")
    return

  print("{:<20} {:<20} {:<20} {:<40} {:<40}".format(
      'Name', 'Remote Port', 'Bind Port', 'Token', 'Config Name'))
  print("-" * 140)

  for tunnel in tunnels:
    print("{:<20} {:<20} {:<20} {:<40} {:<40}".format(
        tunnel.id, tunnel.remote_port, tunnel.bind_port, tunnel.token, tunnel.config_name))
    
def delete_all_tunnels():
    db.session.query(Tunnel).delete()
    print("All tunnel data deleted successfully.")

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
    
    # tunnel_id = db.session.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    return jsonify({"status": "OK", "serverIP": server_ip, "remotePort": remote_port, "bindPort": bind_port, "token": token, "tunnelID": tunnel_id, "message": "Tunnel created OK"}), 201



@app.route('/gettunnel', methods=['GET'])
@token_required
def get_tunnel():
    read_all_tunnels()
    # delete_all_tunnels()
    # name = request.args.get('name')
    # if not name or name not in users:
    #     return "Tunnel not found", 404
    return "hoang", 200

users = {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=44444)
