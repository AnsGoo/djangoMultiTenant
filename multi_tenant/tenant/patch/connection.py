import logging
from django.db.utils import ConnectionHandler
from multi_tenant.tenant import get_tenant_db
logger = logging.getLogger('django.db.backends')

def __connection_handler__getitem__(self, alias: str) -> ConnectionHandler:
    if isinstance(alias, str):
        try:
            return getattr(self._connections, alias)
        except AttributeError:
            if alias not in self.settings:
                tenant_db = get_tenant_db(alias)
                if tenant_db:
                    self.settings[alias] = tenant_db
                else:
                    logger.error(f"The connection '{alias}' doesn't exist.")
                    raise self.exception_class(f"The connection '{alias}' doesn't exist.")
        conn = self.create_connection(alias)
        setattr(self._connections, alias, conn)
        return conn

    else:
        logger.error(f'The  connection alias [{alias}] must be string')
        raise Exception(f'The  connection alias [{alias}] must be string')

ConnectionHandler.__getitem__ = __connection_handler__getitem__