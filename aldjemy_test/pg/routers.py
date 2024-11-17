class PgRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "pg":
            return "pg"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "pg" or db == "pg":
            return app_label == "pg" and db == "pg"
