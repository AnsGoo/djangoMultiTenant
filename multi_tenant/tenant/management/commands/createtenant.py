"""
Management utility to create superusers.
"""
import getpass
import sys

from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import capfirst
from multi_tenant.tenant import get_tenant_model
from django.conf import settings


class NotRunningInTTYException(Exception):
    pass


PASSWORD_FIELD = 'password'


class Command(BaseCommand):
    help = 'Used to create a superuser.'
    requires_migrations_checks = True
    stealth_options = ('stdin',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TenantModel = get_tenant_model()
        self.code_field = self.TenantModel._meta.get_field(self.TenantModel.CODE_FIED)
        self.require_fields = ['']
        self.engine_choices = [item[0] for item in self.TenantModel.engine_choices]

    def add_arguments(self, parser):
        parser.add_argument(
            '--code',
            help='code of tenant.',
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        tenant_code = options[self.TenantModel.CODE_FIED]
        tenant_data = dict()
        if tenant_code:
            tenant_data[self.TenantModel.CODE_FIED] = tenant_code
        verbose_field_name = self.code_field.verbose_name
        try:
            if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
                raise NotRunningInTTYException
            if tenant_code:
                error_msg = self._validate_tenant_code(tenant_code, verbose_field_name)
                if error_msg:
                    self.stderr.write(error_msg)
                    tenant_code = None
            elif tenant_code == '':
                raise CommandError('%s cannot be blank.' % capfirst(self.code_field))
            # Prompt for username.
            while tenant_code is None:
                message = 'code of tenant: '
                tenant_code = input(message)
                if tenant_code:
                    error_msg = self._validate_tenant_code(tenant_code, verbose_field_name)
                    if error_msg:
                        self.stderr.write(error_msg)
                        username = None
                        continue
            tenant_data[self.TenantModel.CODE_FIED] = tenant_code
            tenant_name =  None
            while True:
                input_value = input('connection name: ')
                error_msg = self._validate_tenant_name('name', 'connection')
                if not error_msg:
                    tenant_name = input_value
                    tenant_data['name'] = tenant_name
                    break
                else:
                    self.stderr.write(error_msg)
                    
            is_some_default = True
            while True:
                input_value = input('Use the same database configuration as the primary database (y/N)?: ')
                if input_value.lower() =='y':
                    is_some_default = True
                    break
                elif input_value.lower() == 'n':
                    is_some_default = False
                    break
                else:
                    self.stderr.write('error input，please input y or N.')
                # Prompt for required fields.
            if not is_some_default:
                database_engine = None
                while True:
                    input_value = input('database schema: ')
                    error_msg = self._validate_database_engine(input_value, 'database schema')
                    if not error_msg:
                        database_engine = input_value
                        tenant_data['engine'] = input_value
                        break
                    else:
                        self.stderr.write('error input, schema must be in %s' %','.join(self.engine_choices))
                others_required_fields = ['db_name','db_password','user','host', 'port']
                option_fields = ['user','host', 'port']
                if database_engine.lower() == 'sqlite3':
                    others_required_fields = ['db_name']
                for field in others_required_fields:
                    if field.lower() == 'db_password':
                        while True:
                            password = getpass.getpass()
                            password2 = getpass.getpass('Password (again): ')
                            if password != password2:
                                self.stderr.write("Error: Your passwords didn't match.")
                                continue
                            if password.strip() == '':
                                self.stderr.write("Error: Blank passwords aren't allowed.")
                                # Don't validate blank passwords.
                                continue
                            tenant_data[field] = password.strip()
                            break
                    else:
                        input_value = input( field + ': ')
                        if field in option_fields:
                            if not tenant_data.get('options'):
                                tenant_data['options'] = dict()
                            tenant_data['options'][field] = input_value
                        else:
                            tenant_data[field] = input_value
            else:
                DAFAULT_DB = settings.DATABASES['default']
                # tenant_data['engine'] = DAFAULT_DB['ENGINE']
                default_engine = DAFAULT_DB['ENGINE']
                engine_name = self.TenantModel.inject_engine(default_engine)
                tenant_data['engine'] = engine_name
                tenant_data['db_name'] = tenant_data['name']
                tenant_data['label'] = tenant_data['name']
            tenant = self.TenantModel._default_manager.db_manager('default').create_tenant(**tenant_data)
            try:
                tenant.create_database()
            except Exception as e:
                self.stderr.write(e)
                tenant.delete(force=True)
        except KeyboardInterrupt:
            self.stderr.write('\nOperation cancelled.')
            sys.exit(1)
        except exceptions.ValidationError as e:
            raise CommandError('; '.join(e.messages))
        except NotRunningInTTYException:
            self.stdout.write(
                'Superuser creation skipped due to not running in a TTY. '
                'You can run `manage.py createsuperuser` in your project '
                'to create one manually.'
            )

    def _validate_tenant_code(self, tenant_code, verbose_field_name):
        """Validate tenant_code. If invalid, return a string error message."""
        try:
            self.TenantModel._default_manager.db_manager('default').get(code=tenant_code)
        except self.TenantModel.DoesNotExist:
            pass
        else:
            return 'Error: That tenant_code is already taken.'
        if not tenant_code:
            return '%s cannot be blank.' % capfirst(verbose_field_name)
    def _validate_tenant_name(self, name, verbose_field_name):
        """Validate tenant_name. If invalid, return a string error message."""
        try:
            self.TenantModel._default_manager.db_manager('default').get(name=name)
        except self.TenantModel.DoesNotExist:
            pass
        else:
            return 'Error: That tenant_name is already taken.'
        if not name:
            return '%s cannot be blank.' % capfirst(verbose_field_name)
        
    
    def _validate_database_engine(self, engine, verbose_field_name):
        """Validate tenant_code. If invalid, return a string error message."""
        engine_choices = [item.lower() for item in self.engine_choices]
        if engine in engine_choices:
            pass        
        else:
            return 'Error: That  %s of database is not exists.' %engine
        if not engine:
            return '%s cannot be blank.' % capfirst(verbose_field_name)