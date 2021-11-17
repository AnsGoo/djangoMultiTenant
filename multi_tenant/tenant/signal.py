from threading import Thread
from multi_tenant.tenant.models import Tenant, GlobalUser
from django.db.models.signals import post_save   # 另外一个内置的常用信号
import logging
from django.dispatch import receiver
from multi_tenant.tenant import get_tenant_model, get_tenant_user_model


Tenant = get_tenant_model()
logger = logging.getLogger('django.request')


@receiver(post_save, sender=Tenant)
def create_data_handler(sender, signal, instance, created, **kwargs):
    if created:
        try:
            instance.create_database()
            logger.info(f'create database : [{instance.db_name}] successfuly for {instance.code}')
            thread = Thread(target=migrate,args=[instance.code])
            thread.start()
        except Exception as e:
            logger.error(e)
            instance.delete(force=True)

        

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
    execute_from_command_line(['manage.py', 'migrate', f'--database={database}'])
    logger.info('migrate successfuly!')

@receiver(post_save, sender=GlobalUser)
def assign_user_handler(sender, signal, instance, created, **kwargs):
    if instance.tenant:
        TenantUser = get_tenant_user_model()
        TenantUser.objects.using(instance.tenant.code).get_or_create(
            defaults={
                'is_active':instance.is_active,
                'is_staff':instance.is_staff,
                'is_superuser':instance.is_superuser
                },
            username=instance.username,
            
        )
