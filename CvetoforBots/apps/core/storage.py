class UserStorage:
    def __init__(self):
        self.local_cache = {}
        self.history = {}

    def get_user_filters(self, chat_id):
        # В будущем заменить на redis.smembers(chat_id)
        return set(self.local_cache.get(chat_id, set()))

    def add_filter(self, chat_id, filter_name):
        # В будущем заменить на redis.sadd(chat_id, filter_name)
        if chat_id not in self.local_cache:
            self.local_cache[chat_id] = set()
        self.local_cache[chat_id].add(filter_name)

    def remove_filter(self, chat_id, filter_name):
        # В будущем заменить на redis.srem(chat_id, filter_name)
        if chat_id in self.local_cache:
            self.local_cache[chat_id].discard(filter_name)

    def has_filters(self, chat_id):
        # В будущем заменить на redis.scard(chat_id) > 0
        return bool(self.local_cache.get(chat_id))

    def clear_filters(self, chat_id):
        self.local_cache[chat_id].clear()

    def push_state(self, chat_id, state_data):
        if chat_id not in self.history:
            self.history[chat_id] = []
        self.history[chat_id].append(state_data)

    def pop_state(self, chat_id):
        if chat_id in self.history and len(self.history[chat_id]) > 1:
            return self.history[chat_id].pop()
        return None

    def get_current_state(self, chat_id):
        if chat_id in self.history and self.history[chat_id]:
            return self.history[chat_id][-1]
        return None
