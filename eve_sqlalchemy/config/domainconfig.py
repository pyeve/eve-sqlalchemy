# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from eve.utils import config


class DomainConfig(object):
    """Create an Eve `DOMAIN` dict out of :class:`ResourceConfig`s.

    Upon rendering the `DOMAIN` dictionary, we will first collect all given
    :class:`ResourceConfig` objects and pass them as `related_resource_configs`
    to their `render` methods. This way each :class:`ResourceConfig` knows
    about all existent endpoints in `DOMAIN` and can properly set up relations.

    A special case occurs if one model is referenced for more than one
    endpoint, e.g.:

        DomainConfig({
            'users': ResourceConfig(User),
            'admins': ResourceConfig(User),
            'groups': ResourceConfig(Group)
        })

    Here, we cannot reliably determine which resource should be used for
    relations to `User`. In this case you have to specify the target resource
    for all such relations:

        DomainConfig({
            'users': ResourceConfig(User),
            'admins': ResourceConfig(User),
            'groups': ResourceConfig(Group)
        }, related_resources={
            (Group, 'members'): 'users',
            (Group, 'admins'): 'admins'
        })

    """

    def __init__(self, resource_configs, related_resources={}):
        """Initializes the :class:`DomainConfig` object.

        :param resource_configs: mapping of endpoint names to
            :class:`ResourceConfig` objects
        :param related_resources: mapping of (model, field name) to a resource
        """
        self.resource_configs = resource_configs
        self.related_resources = related_resources

    def render(self, date_created=config.DATE_CREATED,
               last_updated=config.LAST_UPDATED, etag=config.ETAG):
        """Renders the Eve `DOMAIN` dictionary.

        If you change any of `DATE_CREATED`, `LAST_UPDATED` or `ETAG`, make
        sure you pass your new value.

        :param date_created: value of `DATE_CREATED`
        :param last_updated: value of `LAST_UPDATED`
        :param etag: value of `ETAG`
        """
        domain_def = {}
        related_resource_configs = self._create_related_resource_configs()
        for endpoint, resource_config in self.resource_configs.items():
            domain_def[endpoint] = resource_config.render(
                date_created, last_updated, etag, related_resource_configs)
        return domain_def

    def _create_related_resource_configs(self):
        """Creates a mapping from model to (resource, :class:`ResourceConfig`).

        This mapping will be passed to all :class:`ResourceConfig` objects'
        `render` methods.

        If there is more than one resource using the same model, relations for
        this model cannot be set up automatically. In this case you will have
        to manually set `related_resources` when creating the
        :class:`DomainConfig` object.
        """
        result = {}
        keys_to_remove = set()
        for resource, resource_config in self.resource_configs.items():
            model = resource_config.model
            if model in result:
                keys_to_remove.add(model)
            result[model] = (resource, resource_config)
        for key in keys_to_remove:
            del result[key]
        for field, resource in self.related_resources.items():
            result[field] = (resource, self.resource_configs[resource])
        return result
