# coding=utf-8
from flask import url_for


def test_undertaking_list(client):
    page = client.get(url_for('api.company-list'))
    assert page.json == []

