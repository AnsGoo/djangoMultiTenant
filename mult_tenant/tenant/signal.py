from mult_tenant.tenant.models import Tenant
from django.db.models.signals import post_save   # 另外一个内置的常用信号
import logging
from django.dispatch import receiver
from mult_tenant.tenant.utils.model import get_tenant_model

Tenant = get_tenant_model()
logger = logging.getLogger('django.request')


@receiver(post_save, sender=Tenant)
def create_data_handler(sender, signal, instance, created:bool, **kwargs):
    if created:
        instance.create_database()
        logger.info(f'create database : [{instance.db_name}] successfuly for {instance.code}')