from flask import Flask, request, Response
from flask_cors import CORS
import requests
from flask_socketio import SocketIO, emit
import websocket

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes with the policy set to "*"
socketio = SocketIO(app, cors_allowed_origins="*")

TARGET_URL = 'http://192.168.18.16:8080'
WEBSOCKET_URL = 'ws://172.24.6.108:8080/feed'

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    target_url = f'{TARGET_URL}/{path}'
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    try:
        resp = requests.request(method, target_url, headers=headers, data=data, params=request.args)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    except requests.exceptions.RequestException as e:
        response = Response(str(e), status=500)
    
    return response

@socketio.on('connect')
def handle_connect():
    ws = websocket.create_connection(WEBSOCKET_URL)
    print(f"ws = {ws}")
    
    @socketio.on('message')
    def handle_message(message):
        ws.send(message)
        response = ws.recv()
        emit('message', response)

    @socketio.on('disconnect')
    def handle_disconnect():
        ws.close()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3001)
