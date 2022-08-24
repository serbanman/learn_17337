from .database import sessions


class ConnectionManager:
    def __init__(self, shard_name):
        self.shard_name = shard_name
        self.sessionmaker = self._get_session()
        self.session = None

    def _get_session(self):
        return sessions[self.shard_name]

    def __enter__(self):
        self.session = self.sessionmaker()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
