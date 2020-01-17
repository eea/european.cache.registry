# coding=utf-8
import json

from flask import url_for
from instance.settings import FGAS, ODS
from . import factories


def test_substance_year_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=1, name='2019-p1', current=False)
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=2, name='2019-p2', current=True)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.2)
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    resp = client.post(url_for('api.licence-current_substances_per_undertaking', domain='ODS', pk=undertaking.external_id, year=2019), json.dumps(dict()), headers=headers)
    data = resp.json

    assert len(data) == 2
    assert data[0]['substance'] in [substance.substance for substance in deliverylicence.substances.all()]
    assert data[1]['substance'] in [substance.substance for substance in deliverylicence.substances.all()]

def test_substance_year_list_view_filter_substances(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=2, name='2019-p2', current=True)
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
    assert data[0]['substance'] == 'Substance name 1'

def test_substance_year_list_view_filter_types(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=2, name='2019-p2', current=True)
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
    assert data[0]['type'] == 'Action'

def test_licence_year_all_deliveries_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=1, name='2019-p1')
    factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=2, name='2019-p2', current=True)

    resp = client.get(url_for('api.licence-deliveries', domain='ODS', pk=undertaking.external_id, year=2019))

    data = resp.json
    assert data[0]['current'] == False
    assert data[0]['name'] == '2019-p1'
    assert data[0]['order'] == 1 

    assert data[1]['current'] == True
    assert data[1]['name'] == '2019-p2'
    assert data[1]['order'] == 2


def test_substance_of_one_delivery_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=1, name='2019-p1')
    substance = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance = factories.SubstanceFactory()

    resp = client.get(url_for('api.licence-substances_per_delivery', domain='ODS', pk=undertaking.external_id,
                                                                     year=2019, delivery_name=deliverylicence.name))
    data = resp.json

    assert len(data) == 1
    assert data[0]['substance'] == 'Substance name 2'
    assert data[0]['quantity'] == 0.5


def test_licences_of_one_delivery_list_view(client):
    undertaking = factories.UndertakingFactory(domain='ODS')
    deliverylicence = factories.DeliveryLicenceFactory(undertaking=undertaking, year=2019, order=1, name='2019-p1')
    substance1 = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 2', quantity=0.5)
    substance2 = factories.SubstanceFactory(deliverylicence=deliverylicence, substance='Substance name 1', quantity=0.3)
    licences = [
        factories.LicenceFactory(year=2019, licence_id=1, chemical_name='Substance name 1',
                                 qty_percentage=0.2, substance=substance1),
        factories.LicenceFactory(year=2019, licence_id=2, chemical_name='Substance name 1',
                                 qty_percentage=0.3, substance=substance1),
        factories.LicenceFactory(year=2019, licence_id=3, chemical_name='Substance name 2',
                                 qty_percentage=0.1, substance=substance2),
        factories.LicenceFactory(year=2019, licence_id=4, chemical_name='Substance name 2',
                                 qty_percentage=0.2, substance=substance2),
    ]
    licences_ids = [licence.licence_id for licence in licences]
    resp = client.get(url_for('api.licence-licences_per_delivery', domain='ODS', pk=undertaking.external_id,
                                                                   year=2019, delivery_name=deliverylicence.name))
    data = resp.json
    assert len(data) == 4
    assert data[0]['licence_id'] in licences_ids
    assert data[1]['licence_id'] in licences_ids
    assert data[2]['licence_id'] in licences_ids
    assert data[3]['licence_id'] in licences_ids
