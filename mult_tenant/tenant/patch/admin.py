
from django.contrib.admin import AdminSite
from django.conf import settings
from django.contrib.auth  import get_user_model


def get_app_list(self, request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = self._build_app_dict(request)
    public_apps = set()
    for app_label, database in settings.DATABASE_APPS_MAPPING.items():
        if  database == 'default':
            public_apps.add((app_label))
    all_apps = set(app_dict.keys())
    able_apps = set()
    user = request.user
    if user.is_authenticated:
        if user.tenant:
            able_apps = all_apps - public_apps
        else:
            able_apps = public_apps

    able_app_dict = {}
    for app_name in able_apps:
        app = app_dict.get(app_name, None)
        if app:
            able_app_dict[app_name] = app
    
    app_list = sorted(able_app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])

    return app_list

AdminSite.get_app_list = get_app_list