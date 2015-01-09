import os

from flask import url_for
from openpyxl import load_workbook

from . import factories

MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def test_export_companies(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('misc.company-list-export'))
    assert resp.status_code == 200
    assert resp.content_type == MIMETYPE
    fn = 'test_file.xlsx'
    with open(fn, 'w') as f:
        f.write(resp.body)
        f.close()
    wb = load_workbook(fn)
    assert len(wb.worksheets) == 1
    rows = wb.worksheets[0].rows
    assert len(rows) == 2
    assert rows[0][0].value == 'company_id'
    assert rows[1][0].value == undertaking.external_id
    assert rows[0][1].value == 'name'
    assert rows[1][1].value == undertaking.name
    assert rows[0][2].value == 'domain'
    assert rows[1][2].value == undertaking.domain
    assert rows[0][3].value == 'status'
    assert rows[1][3].value == undertaking.status
    assert rows[0][4].value == 'undertaking_type'
    assert rows[1][4].value == undertaking.undertaking_type
    assert rows[0][5].value == 'website'
    assert rows[1][5].value == undertaking.website
    os.remove(fn)
