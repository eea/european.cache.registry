# coding=utf-8
import json

from flask import url_for
from instance.settings import FGAS, ODS
from . import factories


def test_substance_year_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.2)
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    resp = client.post(url_for('api.licence-current_substances_per_undertaking', domain='ODS', pk=undertaking.external_id, year=2019), json.dumps(dict()), headers=headers)
    data = resp.json

    assert len(data) == 1
    assert data['licences'][0]['substance'] in [substance.substance for substance in deliverylicence.substances.all()]
    assert data['licences'][1]['substance'] in [substance.substance for substance in deliverylicence.substances.all()]

def test_substance_year_list_view_filter_substances(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.2)
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    resp = client.post(url_for('api.licence-current_substances_per_undertaking', domain='ODS', pk=undertaking.external_id, year=2019),
                                                        json.dumps({"substances": ['Substance name 1']}), headers=headers)
    data =resp.json
    assert len(data) == 1
    assert data['licences'][0]['substance'] == 'Substance name 1'

def test_substance_year_list_view_filter_types(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.2,lic_type="Action")

    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    resp = client.post(url_for('api.licence-current_substances_per_undertaking', domain='ODS', pk=undertaking.external_id, year=2019),
                       json.dumps({"actions": ["Action"]}), headers=headers)

    data = resp.json
    assert len(data) == 1
    assert data['licences'][0]['type'] == 'Action'


def test_substance_of_one_delivery_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=1)
    substance = factories.SubstanceFactory()

    resp = client.get(url_for('api.licence-substances_per_delivery', domain='ODS', pk=undertaking.external_id,
                                                                     year=2019))
    data = resp.json

    assert len(data) == 1
    assert data[0]['substance'] == 'Substance name 2'
    assert data[0]['quantity'] == 1


def test_licences_of_one_delivery_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019)
    substance1 = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance2 = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.3)
    licences = [
        factories.LicenceFactory(year=2019, licence_id=1, chemical_name='Substance name 1',
                                 net_mass=0.2, substance=substance1),
        factories.LicenceFactory(year=2019, licence_id=2, chemical_name='Substance name 1',
                                 net_mass=0.3, substance=substance1),
        factories.LicenceFactory(year=2019, licence_id=3, chemical_name='Substance name 2',
                                 net_mass=0.1, substance=substance2),
        factories.LicenceFactory(year=2019, licence_id=4, chemical_name='Substance name 2',
                                 net_mass=0.2, substance=substance2),
    ]
    licences_ids = [licence.licence_id for licence in licences]
    resp = client.get(url_for('api.licence-licences_per_delivery', domain='ODS', pk=undertaking.external_id,
                                                                   year=2019))
    data = resp.json
    assert len(data) == 4
    assert data[0]['licence_id'] in licences_ids
    assert data[1]['licence_id'] in licences_ids
    assert data[2]['licence_id'] in licences_ids
    assert data[3]['licence_id'] in licences_ids
