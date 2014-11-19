# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.forms import PricingObjectsUsagesReportForm
from ralph_scrooge.report.report_pricing_objects_usages import (
    PricingObjectsUsagesReport
)
from ralph_scrooge.views.base_report import BaseReport


logger = logging.getLogger(__name__)


class PricingObjectsUsagesReportView(BaseReport):
    """
    Report with usages of resources (usage types) by pricing objects
    per days
    """
    template_name = 'ralph_scrooge/report_pricing_objects_usages.html'
    Form = PricingObjectsUsagesReportForm
    section = 'pricing-objects-usages-report'
    report_name = _('Pricing Objects Usages Report')
    submodule_name = 'pricing-objects-usages-report'
    allow_statement = False   # temporary
    report = PricingObjectsUsagesReport()
