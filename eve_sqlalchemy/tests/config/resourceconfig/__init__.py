# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from eve_sqlalchemy.config import ResourceConfig


class ResourceConfigTestCase(TestCase):

    def setUp(self):
        self._created = '_created'
        self._updated = '_updated'
        self._etag = '_etag'
        self._related_resource_configs = {}

    def _render(self, model_or_resource_config):
        if hasattr(model_or_resource_config, 'render'):
            rc = model_or_resource_config
        else:
            rc = ResourceConfig(model_or_resource_config)
        return rc.render(self._created, self._updated, self._etag,
                         self._related_resource_configs)
