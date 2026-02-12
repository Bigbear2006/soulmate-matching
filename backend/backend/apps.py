from django.contrib.admin import apps


class AdminConfig(apps.AdminConfig):
    default_site = 'core.admin_site.AdminSite'
    verbose_name = 'Админ-панель'
