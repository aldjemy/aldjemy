class LogsRouter(object):
    ALIAS = 'logs'

    def use_logs(self, model):
        return hasattr(model, '_DATABASE') and model._DATABASE == self.ALIAS

    def db_for_read(self, model, **hints):
        if self.use_logs(model):
            return self.ALIAS

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_syncdb(self, db, model):
        if db == 'logs':
            return self.use_logs(model)
        elif self.use_logs(model):
            return False
        return None
