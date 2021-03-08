from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)

socketio = SocketIO(app)


@app.route("/")
def base():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room_id = request.args.get('room_id')
    if username and room_id:
        return render_template('chat.html', username=username, room_id=room_id)
    else:
        return redirect(url_for('home'))


@socketio.on('join_room')
def handle_join_room(data):
    app.logger.info(f'{data["username"]} joined {data["room_id"]} room')
    join_room(data['room_id'])
    socketio.emit('join_room_announcement', data)


@socketio.on('leave_room')
def handle_leave_room(data):
    app.logger.info(f'{data["username"]} left {data["room_id"]} room')
    leave_room(data['room_id'])
    socketio.emit('leave_room_announcement', data)


@socketio.on('send_message')
def handle_send_message(data):
    app.logger.info(f'{data["username"]} messaged:\n {data["message"]}')
    socketio.emit('message_announcement', data)


if __name__ == '__main__':
    socketio.run(app, debug=True)
