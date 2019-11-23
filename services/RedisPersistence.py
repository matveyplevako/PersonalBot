from telegram.ext import BasePersistence
import redis
from collections import defaultdict
import json
from telegram.utils.helpers import decode_user_chat_data_from_json


class RedisPersistence(BasePersistence):
    def __init__(self, redis_instance=redis.Redis(), store_user_data=True, store_chat_data=True):
        super().__init__(store_user_data, store_chat_data)
        self.db = redis_instance

    def get_user_data(self):
        data = self.db.get('user_data')
        if data is None:
            user_data = defaultdict(dict)
        else:
            user_data = defaultdict(dict, decode_user_chat_data_from_json(data.decode()))
        return user_data

    def get_chat_data(self):
        data = self.db.get('chat_data')
        if data is None:
            chat_data = defaultdict(dict)
        else:
            chat_data = defaultdict(dict, decode_user_chat_data_from_json(data.decode()))
        return chat_data

    def get_conversations(self, name):
        data = self.db.get(name)
        if data is None:
            conversation = {}
        else:
            tmp = json.loads(data.decode())
            conversation = {}
            for key, state in tmp.items():
                conversation[tuple(json.loads(key))] = state

        return conversation

    def update_conversation(self, name, key, new_state):
        tmp = self.get_conversations(name)

        tmp[key] = new_state

        conversation = {}
        for key, state in tmp.items():
            conversation[json.dumps(key)] = state

        self.db.set(name, json.dumps(conversation))

    def update_user_data(self, user_id, data):
        user_data = self.get_user_data()

        user_data[user_id] = data
        self.db.set('user_data', json.dumps(user_data))

    def update_chat_data(self, chat_id, data):
        chat_data = self.get_chat_data()
        chat_data[chat_id] = data
        self.db.set('chat_data', json.dumps(chat_data))
