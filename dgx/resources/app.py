# manejo de cola (NO ORDENAR)
import eventlet
eventlet.monkey_patch()

# dependencias
from flask import Flask, jsonify
from flask_socketio import SocketIO
from const import ENV, MONGO_CONN
from utils.helpers import CustomJSONEncoder
import json


# instancia de aplicacion con socket
app = Flask(__name__)
app.secret_key = "@3!f3719em$893&"
app.json_encoder = CustomJSONEncoder
json.JSONEncoder = CustomJSONEncoder
socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://', async_mode='eventlet')


# saludo
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to <<API_NAME>> API", "ENV": ENV, "db": MONGO_CONN['database']})
