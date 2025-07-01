class ReadOnlyRemoteDbRouter:
    """
    Направляет запросы на ЧТЕНИЕ для моделей из route_app_labels в 'cvetofor_db'.
    """
    route_app_labels = {'flowers'}
    db_name = 'cvetofor_db'

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.db_name
        return None

    def db_for_write(self, model, **hints):
        """
        ЗАПРЕЩАЕМ операции записи (INSERT, UPDATE, DELETE).
        """
        if model._meta.app_label in self.route_app_labels:
            # Возвращая None, мы запрещаем запись.
            # Django поднимет исключение, т.к. не найдет подходящей БД.
            return None
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return obj1._meta.app_label == obj2._meta.app_label
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == self.db_name
        elif db == self.db_name:
            return False
        return None
