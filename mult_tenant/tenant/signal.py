from threading import Thread
from mult_tenant.tenant.models import Tenant
from django.db.models.signals import post_save   # 另外一个内置的常用信号
import logging
from django.dispatch import receiver
from mult_tenant.tenant.utils.model import get_tenant_model


Tenant = get_tenant_model()
logger = logging.getLogger('django.request')


@receiver(post_save, sender=Tenant)
def create_data_handler(sender, signal, instance, created, **kwargs):
    if created:
        instance.create_database()
        logger.info(f'create database : [{instance.db_name}] successfuly for {instance.code}')


        thread = Thread(target=migrate,args=[instance.code])
        thread.start()
        

def migrate(database: str):
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error('migrate fail')
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(['manage.py', 'multmigrate', f'--database={database}'])
    logger.error('migrate successfuly, create_table successfuly')
