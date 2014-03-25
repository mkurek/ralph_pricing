# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from ralph_pricing.views.devices import Devices
from ralph_pricing.views.extra_costs import ExtraCosts
from ralph_pricing.views.home import Home
from ralph_pricing.views.usages import Usages
from ralph_pricing.views.teams import Teams
from ralph_pricing.views.teams_percent import TeamsPercent
from ralph_pricing.views.ventures import AllVentures


urlpatterns = patterns(
    '',
    url(r'^$', login_required(Home.as_view()), name='home'),
    url(
        r'^extra-costs/$',
        login_required(ExtraCosts.as_view()),
        name='extra_costs',
        kwargs={'venture': None},
    ),
    url(
        r'^extra-costs/(?P<venture>\d+)/$',
        login_required(ExtraCosts.as_view()),
        name='extra_costs',
    ),
    url(
        r'^usages/$',
        login_required(Usages.as_view()),
        name='usages',
        kwargs={'usage': None},
    ),
    url(
        r'^usages/(?P<usage>[^/]+)/$',
        login_required(Usages.as_view()),
        name='usages',
        kwargs={'type': 'price'},
    ),
    url(
        r'^teams/$',
        login_required(Teams.as_view()),
        name='teams',
        kwargs={'team': None, 'daterange': None},
    ),
    url(
        r'^teams/(?P<team>[^/]+)/$',
        login_required(Teams.as_view()),
        name='teams',
        kwargs={'daterange': None},
    ),
    url(
        r'^teams/(?P<team>[^/]+)/(?P<daterange>[^/]+)/$',
        login_required(TeamsPercent.as_view()),
        name='teams',
    ),
    url(
        r'^all-ventures/$',
        login_required(AllVentures.as_view()),
        name='all_ventures',
    ),
    url(
        r'^devices/$',
        login_required(Devices.as_view()),
        name='devices',
    ),
    url(
        r'^devices/(?P<venture>\d+)/$',
        login_required(Devices.as_view()),
        name='devices',
    ),
)
