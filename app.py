from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from db import get_user

app = Flask(__name__)
app.secret_key = 'my-secret-key'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# TODO - move routes, socketio, login into seperate files
@app.route("/")
def base():
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('index.html')


@app.route('/chat')
@login_required
def chat():
    username = request.args.get('username')
    room_id = request.args.get('room_id')
    if username and room_id:
        return render_template('chat.html', username=username, room_id=room_id)
    else:
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login'
    return render_template('login.html', message=message)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


### SOCKET-IO ###
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


### AUTHENTICATION ###
@login_manager.user_loader
def load_user(username):
    return get_user(username)


if __name__ == '__main__':
    socketio.run(app, debug=True)
