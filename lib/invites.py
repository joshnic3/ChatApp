from datetime import datetime
from lib.hashing import HashManager


class InviteManager:

    DT_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, dao):
        self._dao = dao

    def generate_invite(self, chat):
        issued = datetime.now().strftime(self.DT_FORMAT)
        key = HashManager.sha256(issued + chat.display_name)
        self._dao.insert('invites', [chat.id, issued, key])
        return key

    def validate_invite(self, chat, key):
        # TODO Add expiry date.
        condition = {'chat_id': chat.id, 'key': key}
        result = self._dao.select('invites', condition, return_one=True)
        self._dao.delete('invites', condition)
        return True if result else False

