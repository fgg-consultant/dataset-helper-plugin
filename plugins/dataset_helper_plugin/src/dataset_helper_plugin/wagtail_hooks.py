from django.urls import path, reverse, include
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import urls as plugin_urls


@hooks.register('register_admin_urls')
def register_dataset_helper_url():
    return [
        path('dataset_helper/', include((plugin_urls, 'dataset_helper_plugin'))),
    ]


@hooks.register('register_admin_menu_item')
def register_admin_menu_item():
    url = reverse('dataset_helper_plugin:index')
    return MenuItem('Dataset helper', url, icon_name='globe', order=300)
