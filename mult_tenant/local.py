from threading import local

_thread_local = local()


def get_current_db():
    return getattr(_thread_local, 'db_name', 'default')


def set_current_db(db_name):
    
    setattr(_thread_local, 'db_name', db_name)
