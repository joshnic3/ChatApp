# Note that the Flask server is designed for development only.
# It is not a production-ready server.
# Don't rely on it to run your site on the wider web.
# Use a proper WSGI server (like gunicorn or uWSGI) instead.

import os

from flask import Flask, render_template, request, make_response
from flask_socketio import SocketIO, join_room, leave_room

from lib.chat import User, ChatManager, new_chat_manager
from lib.database import DAO
from lib.utils import HashManager

DB_PATH = '/Users/joshnicholls/Desktop/tempchat.db'


template_dir = os.path.abspath('../web/templates')
static_dir = os.path.abspath('../web/static')


app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socket_io = SocketIO(app)

dao = DAO(DB_PATH)
hm = HashManager(dao)

chat_managers = {}


def _message_as_dict(message, chat):
    message_dict = message.as_dict()
    sent_by_user = chat.users.get(message.sent_by)
    if sent_by_user is not None:
        message_dict['sent_by'] = sent_by_user.as_dict()
    return message_dict


# *** Sockets *** ---------------------------------------
# TODO Implement
# use to= param in emit?
@socket_io.on('join_room')
def on_join(data):
    # join_room(data.get('chat_id'))
    print('join_room: ' + data.get('chat_id'))


@socket_io.on('leave_room')
def on_leave(data):
    # leave_room(data.get('chat_id'))
    print('leave_room: ' + data.get('chat_id'))


@socket_io.on('message_send')
def receive_message(data):
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(int(data.get('userId')))
    if isinstance(user, User):
        broadcast_message(chat, user, data.get('content'))


def broadcast_message(chat, user, content):
    from_id = user.id if isinstance(user, User) else None
    cm = chat_managers.get(hm.encode(chat.id))
    message = cm.new_message(from_id, content)
    socket_io.emit('broadcast_message', _message_as_dict(message, chat))


# *** API *** ---------------------------------------
@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    cm = new_chat_manager(dao, data.get('chat_name'), int(data.get('max_users')))
    hashed_id = hm.encode(cm.chat_id)
    chat_managers[hashed_id] = cm
    return make_response({'accepted': {'chat_id': hashed_id}})


@app.route('/api/new_user', methods=['POST'])
def new_user():
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    user = cm.new_user(data.get('display_name'))
    chat = cm.chat
    broadcast_message(chat, None, f'{user.display_name} has joined the chat')
    response = make_response({'accepted': {'chat_id': data.get('chat_id'), 'user_id': user.id, 'display_name': user.display_name}})
    return response


@app.route('/api/get_messages', methods=['POST'])
def get_messages():
    # Client knows user_id, so use cookie.
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(int(request.cookies.get('userId')))
    if user is None:
        return make_response({'error': user})
    else:
        messages = [ _message_as_dict(m, chat) for m in chat.messages]
        return make_response({'messages': messages})


@app.route('/api/leave', methods=['POST'])
def leave():
    # Client knows user_id, so use cookie.
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(int(request.cookies.get('userId')))
    if isinstance(user, str):
        return make_response({'error': user})
    else:
        cm.delete_user(user.id)
        broadcast_message(chat, None, f'{user.display_name} left the chat')
        return make_response({'removed': True})


# *** HTML *** ---------------------------------------
@app.route('/')
def landing():
    return render_template('index.html')


@app.route('/<chat_id_hash>')
def chat_page(chat_id_hash):
    # Load chat and redirect if it doesn't exist.
    chat_id = hm.decode(chat_id_hash)
    if chat_id is None:
        # Chat id hash is not in map.
        return render_template('index.html')

    if chat_id_hash not in chat_managers:
        # Chat manager is not in cache so create one.
        chat_managers[chat_id_hash] = ChatManager(dao, chat_id)

    chat = chat_managers.get(chat_id_hash).chat

    # Handle returning user.
    user_id = request.args.get('u') if request.args.get('u') else request.cookies.get('userId')
    user = chat.users.get(int(user_id)) if user_id else None

    # TODO Implement
    # Handle Invites.
    invite_key = request.args.get('i')
    if invite_key:
        print('Invite key: ' + invite_key)

    if isinstance(user, User):
        return render_template('chat.html', title=chat.display_name, chat=chat.as_dict(), user=user.as_dict())
    else:
        # TODO Only do if invite is valid
        return render_template('join.html', title=chat.display_name)


if __name__ == '__main__':
    socket_io.run(app, port=9000, host="0.0.0.0", debug=True)
