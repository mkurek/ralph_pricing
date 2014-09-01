# -*- coding: utf-8 -*-
"""The pluggable app definitions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from ralph.app import RalphModule


class Scrooge(RalphModule):
    """Scrooge main application. The 'ralph_pricing' name is retained
    internally for historical reasons, while we try to use 'scrooge' as
    displayed name."""

    url_prefix = 'scrooge'
    module_name = 'ralph_pricing'
    disp_name = 'Scrooge'
    icon = 'fugue-money-coin'
    default_settings_module = 'ralph_pricing.settings'

    @property
    def required_permission(self):
        from ralph.account.models import Perm
        return Perm.has_scrooge_access

    @property
    def home_url(self):
        return reverse('scrooge_home')

    def __init__(self, **kwargs):
        super(Scrooge, self).__init__(
            'ralph_pricing',
            distribution='scrooge',
            **kwargs
        )
        self.append_app()
        self.insert_templates(__file__)
        self.register_logger('ralph_pricing', {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        })
        self.register_logger('ralph_pricing.plugins', {
            'handlers': ['console'],
        })
        self.register_logger('ralph_pricing.management', {
            'handlers': ['console'],
        })
