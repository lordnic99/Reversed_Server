from flask import Flask, request, jsonify, abort



app = Flask(__name__)



# Dummy data store and token for simplicity

# In a real application, you should use a database and a secure method for tokens

users = {}

TOKEN = "hoang20cm"



def token_required(f):

    def decorator(*args, **kwargs):

        token = request.headers.get('Authorization')

        if token != TOKEN:

            abort(401, description="Invalid or missing token")

        return f(*args, **kwargs)

    decorator.__name__ = f.__name__

    return decorator



@app.route('/createtunnel', methods=['POST'])

@token_required

def create_tunnel():

    data = request.json

    if not data or 'name' not in data:

        return jsonify({"error": "Name is required"}), 400

    name = data['name']

    # For simplicity, we're just storing the name in a dictionary

    users[name] = f"Tunnel for {name} created"

    return jsonify({"message": f"Tunnel for {name} created successfully"}), 201



@app.route('/gettunnel', methods=['GET'])

@token_required

def get_tunnel():

    name = request.args.get('name')

    if not name or name not in users:

        return "Tunnel not found", 404

    return users[name], 200



if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True, port=45642)
