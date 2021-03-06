# Note that the Flask server is designed for development only.
# It is not a production-ready server.
# Don't rely on it to run your site on the wider web.
# Use a proper WSGI server (like gunicorn or uWSGI) instead.

import argparse
import os
import sys

import yaml
from flask import Flask, render_template, request, make_response
from flask_socketio import SocketIO, join_room, leave_room
import logging.config
from lib.chat import User, Chat, ChatManager, new_chat_manager
from lib.database import DAO
from lib.hashing import HashManager, SHAKE256_3, SHA256
from lib.invites import InviteManager

CHAT_ID_HASH = SHAKE256_3
USER_ID_HASH = SHA256

# TODO this needs to be modified on RPi to web/
template_dir = os.path.abspath('../web/templates')
static_dir = os.path.abspath('../web/static')
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)


app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socket_io = SocketIO(app)

configs = None
dao = None
hm = None
im = None

chat_managers = {}


def _message_as_dict(message, chat):
    message_dict = message.as_dict()
    sent_by_user = chat.users.get(message.sent_by)
    if sent_by_user is not None:
        message_dict['sent_by'] = sent_by_user.as_dict()
    return message_dict


def _error_response(error_message):
    return make_response({'error': error_message})


# *** Sockets *** ---------------------------------------
@socket_io.on('join_room')
def on_join(data):
    join_room(data.get('chat_id'))


@socket_io.on('leave_room')
def on_leave(data):
    leave_room(data.get('chat_id'))


@socket_io.on('message_send')
def receive_message(data):
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(hm.decode(data.get('userId')))
    if isinstance(user, User):
        broadcast_message(chat, user, data.get('content'))


def broadcast_message(chat, user, content):
    hashed_id = hm.encode(chat.id, hash_method=CHAT_ID_HASH)
    cm = chat_managers.get(hashed_id)
    message = cm.new_message(user, content)
    socket_io.emit('broadcast_message', _message_as_dict(message, chat), to=hashed_id)


# *** API *** ---------------------------------------
@app.route('/api/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    cm = new_chat_manager(dao, data.get('chat_name'), configs.get('max_user_limit'), int(data.get('invite_only')))
    hashed_id = hm.encode(cm.chat_id, hash_method=CHAT_ID_HASH)
    chat_managers[hashed_id] = cm
    return make_response({'accepted': {'chat_id': hashed_id}})


@app.route('/api/new_user', methods=['POST'])
def new_user():
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    user = cm.new_user(data.get('display_name').lower())
    if isinstance(user, User):
        chat = cm.chat
        broadcast_message(chat, None, f'{user.display_name} has joined the chat')
        return make_response(
            {
                'accepted': {
                    'chat_id': data.get('chat_id'),
                    'user_id': hm.encode(user.id, USER_ID_HASH),
                    'display_name': user.display_name}
            })
    else:
        return _error_response(f'chat has reached user limit of {cm.max_user_limit}.')


@app.route('/api/change_user_colour', methods=['POST'])
def change_user_colour():
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    user = cm.chat.users.get(hm.decode(request.cookies.get('userId')))
    if isinstance(user, User):
        cm.change_colour(user, data.get('colour'))
        return make_response({'accepted': {'colour': data.get('colour')}})
    else:
        return _error_response(f'invalid user.')


@app.route('/api/get_messages', methods=['POST'])
def get_messages():
    # Client knows user_id, so use cookie.
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(hm.decode(request.cookies.get('userId')))
    if isinstance(user, User):
        return make_response({'messages': [_message_as_dict(m, chat) for m in chat.messages]})
    else:
        return _error_response(f'you are not allowed to view {data.get("chat_id")} messages.')


@app.route('/api/leave', methods=['POST'])
def leave():
    # Client knows user_id, so use cookie.
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(hm.decode(request.cookies.get('userId')))
    if isinstance(user, User):
        cm.delete_user(user.id)
        if isinstance(cm.chat, Chat):
            broadcast_message(chat, None, f'{user.display_name} left the chat')
        return make_response({'removed': True})
    else:
        return _error_response(f'failed to remove user from {data.get("chat_id")}.')


@app.route('/api/invite', methods=['POST'])
def generate_invite():
    data = request.get_json()
    cm = chat_managers.get(data.get('chat_id'))
    chat = cm.chat
    user = chat.users.get(hm.decode(request.cookies.get('userId')))
    if isinstance(user, User):
        return make_response({'accepted': {'key': im.generate_invite(chat)}})
    else:
        return _error_response(f'you are not allowed to invite users to {data.get("chat_id")}')


# *** HTML *** ---------------------------------------
@app.route('/')
def landing():
    return render_template('index.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=None, user=None)


@app.route('/<chat_id_hash>')
def chat_page(chat_id_hash):
    # Load chat and redirect if it doesn't exist.
    chat_id = hm.decode(chat_id_hash)
    if chat_id is None:
        # Chat id hash is not in map.
        return render_template('index.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=None, user=None)

    if chat_id_hash not in chat_managers:
        # Chat manager is not in cache so create one.
        chat_managers[chat_id_hash] = ChatManager(dao, chat_id, configs.get('max_user_limit'))

    chat = chat_managers.get(chat_id_hash).chat
    if not isinstance(chat, Chat):
        return render_template('index.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=None, user=None)

    # Handle returning user.
    user_id = request.args.get('u') if request.args.get('u') else request.cookies.get('userId')
    user = chat.users.get(hm.decode(user_id)) if user_id else None

    # Handle Invites.
    invite_key = request.args.get('i')
    valid_invite = im.validate_invite(chat, invite_key) if invite_key else False

    if isinstance(user, User):
        return render_template('chat.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=chat.as_dict(), user=user.as_dict())
    elif (valid_invite and chat.invite_only) or not chat.invite_only or not chat.users:
        return render_template('join.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=chat.as_dict(), user=None)
    else:
        return render_template('index.html', site_title=configs.get('site_title'), site_font=configs.get('site_font'), chat=None, user=None)


def parse_configs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configs', type=str, required=True)
    args = parser.parse_args()
    with open(args.configs, "r") as stream:
        try:
            yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yaml_dict


def main():
    global dao, hm, im, configs
    configs = parse_configs()
    logging.config.dictConfig(configs.get('log'))

    dao = DAO(configs.get('database').get('path'))
    hm = HashManager(dao)
    im = InviteManager(dao)

    socket_io.run(app, port=configs.get('port'), host="0.0.0.0", debug=configs.get('debug_mode'))

    return 0


if __name__ == '__main__':
    sys.exit(main())
