# coding=utf-8
import json

from flask import url_for
from instance.settings import FGAS, ODS
from cache_registry.sync.licences import (
    check_if_delivery_exists,
    get_new_delivery_order,
    get_or_create_delivery,
    parse_licence,
    get_substance,
    aggregate_licence_to_substance,
)

from . import factories


def test_check_if_delivery_exists(client):
    factories.DeliveryLicenceFactory(year=2019, name='2019-p3')
    result_true = check_if_delivery_exists(2019, '2019-p3')
    result_false = check_if_delivery_exists(2019, '2019-p1')

    assert result_false != True
    assert result_true == True

def test_get_new_delivery_order(client):
    undertaking = factories.UndertakingFactory(id=10)
    delivery = factories.DeliveryLicenceFactory(year=2019, name='2019-p1', order=1, undertaking_id=undertaking.id, undertaking=undertaking)
    factories.DeliveryLicenceFactory(year=2019, name='2019-p2', order=2, undertaking_id=undertaking.id, undertaking=undertaking)
    order = get_new_delivery_order(2019, undertaking.id)
    assert order == 3
    order = get_new_delivery_order(2018, undertaking.id)
    assert order == 1


def test_get_or_create_delivery(client):
    undertaking = factories.UndertakingFactory(id=10)
    delivery_name = '2019-p2'
    year = 2019
    delivery_object = factories.DeliveryLicenceFactory(year=2019, name='2019-p1', current=True,
                                                       undertaking=undertaking, order=1)
    delivery = get_or_create_delivery(year, delivery_name, undertaking.id)
    
    assert delivery.name == delivery_name
    assert delivery.order == 2
    assert delivery.current == True
    assert delivery.year == year
    assert delivery.undertaking_id == undertaking.id

    assert delivery_object.current == False

    delivery = get_or_create_delivery(year, '2019-p1', undertaking_id=undertaking.id)

    assert delivery == delivery_object


def test_aggregate_licence_to_substance(client):
    substance = factories.SubstanceFactory(quantity=0)
    licences = [
        factories.LicenceFactory(substance=substance, qty_percentage=0.1),
        factories.LicenceFactory(substance=substance, qty_percentage=0.2),
        factories.LicenceFactory(substance=substance, qty_percentage=0.4),
        factories.LicenceFactory(substance=substance, qty_percentage=0.5),
    ]

    for licence in licences:
        aggregate_licence_to_substance(substance, licence)

    assert round(substance.quantity, 1) == 1.2


def test_get_substance(client):
    delivery_licence = factories.DeliveryLicenceFactory()
    factories.SubstanceNameConversionFactory(
        ec_substance_name="Substance (virgin)",
        corrected_name="Substance (virgin)"
    )

    factories.LicenceDetailsConverstionFactory(
        template_detailed_use_code="code.for.use",
        lic_use_kind="kind",
        lic_use_desc="desc",
        lic_type="export"
    )

    licence = {
        "chemicalName": "Substance",
        "mixtureNatureType": "virgin",
        "templateDetailedUseCode": "code.for.use",
    }

    substance = get_substance(delivery_licence, licence)
    assert substance.lic_use_kind == 'kind'
    assert substance.lic_use_desc == 'desc'
    assert substance.lic_type == 'export'
    assert substance.substance == 'Substance (virgin)'
