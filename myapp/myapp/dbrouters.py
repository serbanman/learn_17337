class CustomRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if 'video' in db:
            if model_name == 'video':
                return True
            return False

        if db == 'default':
            if model_name == 'video' or model_name == 'history':
                return False

        if 'history' in db:
            if model_name == 'history':
                return True
            return False

        return None
