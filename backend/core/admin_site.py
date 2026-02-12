from typing import Any

from django.apps import apps
from django.contrib import admin
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst
from django_stubs_ext import StrOrPromise

from bot.loader import logger


class AdminSite(admin.AdminSite):
    site_title = 'Soulmate Matching'
    site_header = 'Admin panel'
    index_title = 'Administration'

    def _build_app_dict(
        self,
        request: HttpRequest,
        label: StrOrPromise | None = None,
    ) -> dict[str, Any]:
        """
        Allow to split models from one app into separate tables in admin.

        Usage:

            @admin.register(User)
            class UserAdmin(admin.ModelAdmin):
                group = 'Main Group'

        """
        app_dict = {}
        logger.info(label)

        if label:
            models = {
                m: m_a
                for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            origin_app_label = model._meta.app_label
            model_group_label = getattr(model_admin, 'group', None)
            app_label = model_group_label or origin_app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = f'{origin_app_label}_{model._meta.model_name}'
            model_dict: dict[str, Any] = {
                'model': model,
                'name': capfirst(model._meta.verbose_name_plural),
                'object_name': model._meta.object_name,
                'perms': perms,
                'admin_url': None,
                'add_url': None,
            }
            if perms.get('change') or perms.get('view'):
                model_dict['view_only'] = not perms.get('change')
                try:
                    model_dict['admin_url'] = reverse(
                        f'admin:{info}_changelist',
                        current_app=self.name,
                    )
                except NoReverseMatch:
                    pass
            if perms.get('add'):
                try:
                    model_dict['add_url'] = reverse(
                        f'admin:{info}_add',
                        current_app=self.name,
                    )
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]['models'].append(model_dict)
            else:
                app_dict[app_label] = {
                    'name': model_group_label
                    or apps.get_app_config(app_label).verbose_name,
                    'app_label': app_label,
                    'app_url': reverse(
                        'admin:app_list',
                        kwargs={'app_label': origin_app_label},
                        current_app=self.name,
                    ),
                    'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }

        return app_dict
