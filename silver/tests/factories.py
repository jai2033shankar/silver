from decimal import Decimal
import datetime

import factory
import factory.fuzzy
from django.contrib.auth import get_user_model
from django.utils import timezone
from international.models import countries

from silver.models import (Provider, Plan, MeteredFeature, Customer,
                           Subscription, Invoice, ProductCode,
                           Proforma, MeteredFeatureUnitsLog, DocumentEntry)


class ProductCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCode

    value = factory.Sequence(lambda n: 'ProductCode{cnt}'.format(cnt=n))


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    name = factory.Sequence(lambda n: 'Name{cnt}'.format(cnt=n))
    company = factory.Sequence(lambda n: 'Company{cnt}'.format(cnt=n))
    email = factory.Sequence(lambda n: 'some{cnt}@email.com'.format(cnt=n))
    address_1 = factory.Sequence(lambda n: 'Address1{cnt}'.format(cnt=n))
    address_2 = factory.Sequence(lambda n: 'Address2{cnt}'.format(cnt=n))
    country = factory.Sequence(lambda n: countries[n % len(countries)][0])
    city = factory.Sequence(lambda n: 'City{cnt}'.format(cnt=n))
    state = factory.Sequence(lambda n: 'State{cnt}'.format(cnt=n))
    zip_code = factory.Sequence(lambda n: str(n))
    extra = factory.Sequence(lambda n: 'Extra{cnt}'.format(cnt=n))
    meta = factory.Sequence(lambda n: {"something": [n, n + 1]})

    customer_reference = factory.Sequence(lambda n: 'Reference{cnt}'.format(cnt=n))
    sales_tax_percent = Decimal(1.0)
    sales_tax_name = factory.Sequence(lambda n: 'VAT'.format(cnt=n))
    payment_due_days = 5


class MeteredFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeteredFeature

    name = factory.Sequence(lambda n: 'Name{cnt}'.format(cnt=n))
    unit = 'Unit'
    price_per_unit = factory.fuzzy.FuzzyDecimal(low=0.01, high=100.00,
                                                precision=4)
    included_units = factory.fuzzy.FuzzyDecimal(low=0.01, high=100000.00,
                                                precision=4)
    product_code = factory.SubFactory(ProductCodeFactory)


class ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.Sequence(lambda n: 'Name{cnt}'.format(cnt=n))
    company = factory.Sequence(lambda n: 'Company{cnt}'.format(cnt=n))
    email = factory.Sequence(lambda n: 'some{cnt}@email.com'.format(cnt=n))
    address_1 = factory.Sequence(lambda n: 'Address1{cnt}'.format(cnt=n))
    address_2 = factory.Sequence(lambda n: 'Address2{cnt}'.format(cnt=n))
    country = factory.Sequence(lambda n: countries[n % len(countries)][0])
    city = factory.Sequence(lambda n: 'City{cnt}'.format(cnt=n))
    state = factory.Sequence(lambda n: 'State{cnt}'.format(cnt=n))
    zip_code = factory.Sequence(lambda n: str(n))
    extra = factory.Sequence(lambda n: 'Extra{cnt}'.format(cnt=n))
    meta = factory.Sequence(lambda n: {"something": [n, n + 1]})

    flow = 'proforma'
    invoice_series = 'InvoiceSeries'
    invoice_starting_number = 1
    proforma_series = 'ProformaSeries'
    proforma_starting_number = 1


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    name = factory.Sequence(lambda n: 'Name{cnt}'.format(cnt=n))
    interval = factory.Sequence(lambda n: Plan.INTERVALS[n % 4][0])
    interval_count = factory.Sequence(lambda n: n)
    amount = factory.Sequence(lambda n: n)
    currency = 'USD'
    generate_after = factory.Sequence(lambda n: n)
    enabled = factory.Sequence(lambda n: n % 2 != 0)
    private = factory.Sequence(lambda n: n % 2 != 0)
    product_code = factory.SubFactory(ProductCodeFactory)
    provider = factory.SubFactory(ProviderFactory)

    @factory.post_generation
    def metered_features(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for metered_feature in extracted:
                self.metered_features.add(metered_feature)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    plan = factory.SubFactory(PlanFactory)
    customer = factory.SubFactory(CustomerFactory)
    start_date = timezone.now().date()
    trial_end = factory.LazyAttribute(
        lambda obj: obj.start_date +\
                        datetime.timedelta(days=obj.plan.trial_period_days)
                    if obj.plan.trial_period_days else None)
    meta = factory.Sequence(lambda n: {"something": [n, n + 1]})

    @factory.post_generation
    def metered_features(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for metered_feature in extracted:
                self.metered_features.add(metered_feature)


class MeteredFeatureUnitsLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeteredFeatureUnitsLog
    metered_feature = factory.SubFactory(MeteredFeatureFactory)
    subscription = factory.SubFactory(SubscriptionFactory)
    consumed_units = factory.fuzzy.FuzzyDecimal(low=0.01, high=50000.00,
                                                precision=4)


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    number = factory.Sequence(lambda n: n)
    customer = factory.SubFactory(CustomerFactory)
    provider = factory.SubFactory(ProviderFactory)
    currency = 'RON'

    @factory.post_generation
    def invoice_entries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for invoice_entry in extracted:
                self.proforma_entries.add(invoice_entry)


class ProformaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proforma

    number = factory.Sequence(lambda n: n)
    customer = factory.SubFactory(CustomerFactory)
    provider = factory.SubFactory(ProviderFactory)
    currency = 'RON'

    @factory.post_generation
    def subscriptions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for subscription in extracted:
                self.subscriptions.add(subscription)

    @factory.post_generation
    def proforma_entries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for proforma_entry in extracted:
                self.proforma_entries.add(proforma_entry)


class DocumentEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentEntry

    description = factory.Sequence(lambda n: 'Description{cnt}'.format(cnt=n))
    unit = factory.Sequence(lambda n: 'Unit{cnt}'.format(cnt=n))
    quantity = factory.fuzzy.FuzzyDecimal(low=0.00, high=50000.00, precision=4)
    unit_price = factory.fuzzy.FuzzyDecimal(low=0.01, high=100.00, precision=4)
    product_code = factory.SubFactory(ProductCodeFactory)
    end_date = factory.Sequence(
        lambda n: datetime.date.today() + datetime.timedelta(days=n))
    start_date = datetime.date.today()
    prorated = factory.Sequence(lambda n: n % 2 == 1)


class AdminUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = 'admin'
    email = 'admin@admin.com'
    password = factory.PostGenerationMethodCall('set_password', 'admin')
    is_active = True
    is_superuser = True
    is_staff = True
