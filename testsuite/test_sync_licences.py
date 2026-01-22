# coding=utf-8

from . import factories

from cache_registry.sync.licences import (
    get_or_create_delivery,
    get_or_create_substance,
    aggregate_licence_to_substance,
)


def test_get_or_create_delivery(client):
    undertaking = factories.UndertakingFactory(id=10)
    year = 2019
    delivery_object = factories.DeliveryLicenceFactory(
        year=2019, undertaking=undertaking
    )
    delivery = get_or_create_delivery(year, undertaking)

    assert delivery.id == delivery_object.id
    assert delivery.year == delivery_object.year
    assert delivery.undertaking_id == delivery_object.undertaking.id


def test_aggregate_licence_to_substance(client):
    delivery_object = factories.DeliveryLicenceFactory(year=2019)
    substance = factories.SubstanceFactory(quantity=0, deliverylicence=delivery_object)

    factories.LicenceFactory(substance=substance, net_mass=0.1)
    factories.LicenceFactory(substance=substance, net_mass=0.2)
    factories.LicenceFactory(substance=substance, net_mass=0.4)
    factories.LicenceFactory(substance=substance, net_mass=0.5)

    aggregate_licence_to_substance(delivery_object, 2019)

    assert round(substance.quantity, 1) == 2


def test_get_or_create_substance(client):
    delivery_licence = factories.DeliveryLicenceFactory()
    factories.SubstanceNameConversionFactory(
        ec_substance_name="Substance (virgin)", corrected_name="Substance (virgin)"
    )

    factories.LicenceDetailsConversionFactory(
        template_detailed_use_code="code.for.use",
        lic_use_kind="kind",
        lic_use_desc="desc",
        lic_type="export",
    )

    factories.CountryCodesConversionFactory(
        country_name_short_en="USA", country_code_alpha2="US"
    )

    licence = {
        "chemicalName": "Substance",
        "licenceState": "EXPIRED",
        "customProcedureName": "Re-export",
        "mixtureNatureType": "virgin",
        "templateDetailedUseCode": "code.for.use",
        "organizationCountryName": "USA",
        "internationalPartyCountryName": "USA",
    }

    substance = get_or_create_substance(delivery_licence, licence)
    assert substance.lic_use_kind == "re-export"
    assert substance.lic_use_desc == "desc"
    assert substance.lic_type == "export"
    assert substance.substance == "Substance (virgin)"
    assert substance.organization_country_name == "US"
    assert substance.s_orig_country_name == "US"
