# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
)

from ralph_scrooge.models._history import (
    IntervalHistoricalRecords,
    ModelDiffMixin,
)
from ralph_scrooge.models.base import BaseUsage, BaseUsageType
from ralph_scrooge.models.usage import DailyUsage
from ralph_scrooge.models.pricing_object import PricingObjectType


class BusinessLine(Named):
    ci_uid = db.CharField(
        unique=True,
        null=False,
        blank=False,
        verbose_name='CMDB CI UID',
        max_length=100,
    )

    class Meta:
        app_label = 'ralph_scrooge'


class Environment(Named):
    environment_id = db.IntegerField(
        verbose_name=_("ralph environment id"),
        unique=True,
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['name']


class Service(ModelDiffMixin, EditorTrackable, TimeTrackable):
    name = db.CharField(
        verbose_name=_("name"),
        max_length=256,
    )
    business_line = db.ForeignKey(
        BusinessLine,
        null=False,
        blank=False,
        default=1,
        related_name='services',
        verbose_name=_('business line')
    )
    ci_uid = db.CharField(
        unique=True,
        null=False,
        blank=False,
        verbose_name=_('CMDB CI UID'),
        max_length=100,
    )
    ownership = db.ManyToManyField(
        'Owner',
        through='ServiceOwnership',
        related_name='services'
    )
    environments = db.ManyToManyField(
        Environment,
        through='ServiceEnvironment',
        related_name='services',
    )
    pricing_service = db.ForeignKey(
        'PricingService',
        related_name='services',
        null=True,
        blank=True,
    )
    history = IntervalHistoricalRecords()

    class Meta:
        app_label = 'ralph_scrooge'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_plugin_name(self):
        if self.use_universal_plugin:
            return 'service_plugin'
        return self.symbol or self.name.lower().replace(' ', '_')


class PricingService(BaseUsage):
    use_universal_plugin = db.BooleanField(
        verbose_name=_("Use universal plugin"),
        default=True,
    )
    usage_types = db.ManyToManyField(
        'UsageType',
        through='ServiceUsageTypes',
        related_name='services',
    )
    excluded_services = db.ManyToManyField(
        'Service',
        verbose_name=_("Excluded services"),
        related_name='excluded_from_pricing_services',
        help_text=_(
            'Services excluded from cost distribution (besides usage '
            'type excluded services)'
        ),
        blank=True,
        null=True,
    )
    excluded_base_usage_types = db.ManyToManyField(
        'UsageType',
        related_name='excluded_from_pricing_service',
        limit_choices_to={
            'usage_type': 'BU',
        },
        blank=True,
        null=True,
    )
    regular_usage_types = db.ManyToManyField(
        'UsageType',
        related_name='pricing_services',
        limit_choices_to={
            'usage_type': 'RU',
        },
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("pricing service")
        verbose_name_plural = _("pricing services")
        app_label = 'ralph_scrooge'

    def save(self, *args, **kwargs):
        self.type = BaseUsageType.pricing_service
        super(PricingService, self).save(*args, **kwargs)

    @property
    def service_environments(self):
        """
        Returns all services environments related with this pricing service.
        """
        return ServiceEnvironment.objects.filter(
            service__in=self.services.all()
        )

    def get_plugin_name(self):
        """
        Returns plugin name for pricing service.
        """
        if self.use_universal_plugin:
            return 'pricing_service_plugin'
        return self.symbol or self.name.lower().replace(' ', '_')

    def get_dependent_services(self, date):
        """
        Returns pricing services, which resources (usage types) are used by
        this service (for given date).
        """
        return PricingService.objects.filter(
            serviceusagetypes__usage_type__id__in=DailyUsage.objects.filter(
                type__usage_type='SU',
                service_environment__in=ServiceEnvironment.objects.filter(
                    service__in=self.services.all(),
                ),
                date=date,
            ).values_list('type', flat=True).distinct()
        ).distinct()


class ServiceUsageTypes(db.Model):
    usage_type = db.ForeignKey(
        'UsageType',
        verbose_name=_("Usage type"),
        related_name="service_division",
        limit_choices_to={
            'usage_type': 'SU',
        },
    )
    pricing_service = db.ForeignKey(
        PricingService,
        verbose_name=_("Pricing Service"),
    )
    start = db.DateField()
    end = db.DateField()
    percent = db.FloatField(
        validators=[
            MaxValueValidator(100.0),
            MinValueValidator(0.0)
        ]
    )

    class Meta:
        verbose_name = _("service usage type")
        verbose_name_plural = _("service usage types")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{}/{} ({} - {})'.format(
            self.pricing_service,
            self.usage_type,
            self.start,
            self.end,
        )


class ServiceEnvironment(db.Model):
    service = db.ForeignKey(
        Service,
        related_name="environments_services",
    )
    environment = db.ForeignKey(
        Environment,
        related_name='services_environments',
    )

    class Meta:
        verbose_name = _("service environment")
        verbose_name_plural = _("service environments")
        app_label = 'ralph_scrooge'

    def __unicode__(self):
        return '{} - {}'.format(self.service, self.environment)

    @property
    def dummy_pricing_object(self):
        """
        Returns dummy pricing object for service environment
        """
        return self.pricing_objects.get_or_create(
            type=PricingObjectType.dummy
        )[0]

    def save(self, *args, **kwargs):
        result = super(ServiceEnvironment, self).save(*args, **kwargs)
        self.dummy_pricing_object  # create dummy pricing object if not exists
        return result
