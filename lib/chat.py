import random
from datetime import datetime

import bleach


def new_chat_manager(dao, display_name, max_users=10):
    created = datetime.now()
    chat_id = dao.insert('chats', [display_name, created.strftime(ChatManager.DT_FORMAT), max_users])[0]
    return ChatManager(dao, chat_id)


class ChatManager:

    DT_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, dao, chat_id):
        self.chat_id = chat_id
        self.dao = dao
        self.chat = self._load_chat()
        self.colours = [
            'primary',
            'success',
            'danger',
            'warning',
            'info'
        ]
        random.shuffle(self.colours)

    def _next_colour(self):
        colour = self.colours.pop(0)
        self.colours.append(colour)
        return colour

    def _load_users(self):
        results = self.dao.select('users', {'chat_id': self.chat_id})
        users = [User.from_list([int(r[0]), r[2], datetime.strptime(r[3], self.DT_FORMAT), r[4]]) for r in results]
        return {u.id: u for u in users}

    def _load_messages(self):
        results = self.dao.select('messages', {'chat_id': self.chat_id})
        return [
            Message.from_list([int(r[0]), int(r[2]) if r[2] else None, datetime.strptime(r[3], self.DT_FORMAT), r[4]]) for r in results]

    def _load_chat(self):
        results = self.dao.select('chats', {'id': self.chat_id}, return_one=True)
        chat_list = [int(results[0]), results[1], datetime.strptime(results[2], self.DT_FORMAT), int(results[3])]
        chat = Chat.from_list(chat_list)
        chat.users = self._load_users()
        chat.messages = self._load_messages()
        return chat

    def new_user(self, display_name):
        joined = datetime.now()
        colour = self._next_colour()
        user_id = self.dao.insert('users',
                                  [self.chat_id, display_name.lower(), joined.strftime(self.DT_FORMAT), colour])[0]
        user = User.from_list([user_id, display_name, joined, colour])
        self.chat.users[user_id] = user
        return user

    def delete_user(self, user_id):
        # TODO ON DELETE CASCADE
        self.dao.delete('users', {'id': user_id})
        self.chat.users.pop(user_id)

    def new_message(self, user_id, content):
        sent_at = datetime.now()
        message_id = self.dao.insert('messages', [self.chat_id, user_id, sent_at.strftime(self.DT_FORMAT), content])
        message = Message.from_list([message_id, user_id, sent_at, content.lower()])
        self.chat.messages.append(message)
        return message


class Message:

    @staticmethod
    def from_list(message_list):
        message = Message()
        message.id, message.sent_by, message.send_at, message.content = message_list
        return message

    def __init__(self):
        self.id = None
        self.sent_by = None
        self.send_at = None
        self.content = None

    def as_dict(self):
        # This goes straight out to the client so sanitize anything that is input but the user.
        return {
            'sent_at': self.send_at.strftime('%d/%m/%Y %H:%M'),
            'sent_by': self.sent_by,
            'content': bleach.clean(self.content)
        }


class User:

    @staticmethod
    def from_list(user_list):
        user = User()
        user.id, user.display_name, user.joined, user.colour = user_list
        return user

    def __init__(self):
        self.id = None
        self.display_name = None
        self.joined = None
        self.colour = None

    def as_dict(self):
        # This goes straight out to the client so sanitize anything that is input but the user.
        return {
            'details': {
                'joined': self.joined.strftime('%d/%m/%Y %H:%M'),
            },
            'display_name': bleach.clean(self.display_name),
            'colour': self.colour,
        }


class Chat:

    @staticmethod
    def from_list(chat_list):
        chat = Chat()
        chat.id, chat.display_name, chat.created, chat.max_users = chat_list
        return chat

    def __init__(self):
        self.id = None
        self.display_name = None
        self.max_users = None
        self.created = None
        # TODO Make this a user toggleable item. Needs to be False as default
        self.invite_only = False
        self.users = {}
        self.messages = []

    def as_dict(self):
        # This goes straight out to the client so sanitize anything that is input but the user.

        return {
            'details': {
                'created': self.created.strftime('%d/%m/%Y %H:%M'),
                'user count': len(self.users),
                'max users': self.max_users

            },
            'display_name': bleach.clean(self.display_name),
        }
