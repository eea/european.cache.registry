import json

from flask import url_for

from cache_registry.models import PatchSetting, get_patch


def upload(client, data, **kwargs):
    content = data if isinstance(data, bytes) else json.dumps(data).encode()
    return client.post(
        url_for("api.patches-import"),
        upload_files=[("file", "patches.json", content)],
        **kwargs,
    )


def test_get_patch_falls_back_to_settings(app):
    app.config["PATCH_COMPANIES"] = {"1": {"website": "from-file"}}
    assert get_patch("PATCH_COMPANIES", {}) == {"1": {"website": "from-file"}}
    assert get_patch("PATCH_AUDITORS", {}) == {}


def test_import_and_export(client):
    client.app.config["PATCH_USERS"] = {"9": [{"username": "from-file"}]}
    patch_companies = {"1": {"website": "from-db"}}
    resp = upload(
        client,
        {"PATCH_COMPANIES": patch_companies, "OVERRIDE_LICENCES": [{"company_id": 1}]},
    )
    assert resp.json["status"] == "success"
    assert sorted(resp.json["updated"]) == ["OVERRIDE_LICENCES", "PATCH_COMPANIES"]
    assert get_patch("PATCH_COMPANIES") == patch_companies

    exported = json.loads(client.get(url_for("api.patches-export")).body)
    assert exported["PATCH_COMPANIES"] == patch_companies
    # Not in the database: the value from the settings file is exported
    assert exported["PATCH_USERS"] == {"9": [{"username": "from-file"}]}
    assert exported["PATCH_AUDITORS"] == {}
    assert exported["PATCH_MULTI_YEAR_LICENCES"] == []

    # Importing an exported file again works and changes nothing
    resp = upload(client, exported)
    assert resp.json["status"] == "success"
    assert json.loads(client.get(url_for("api.patches-export")).body) == exported


def test_import_null_removes_database_value(client):
    client.app.config["PATCH_COMPANIES"] = {"1": {"website": "from-file"}}
    upload(client, {"PATCH_COMPANIES": {"1": {"website": "from-db"}}})
    resp = upload(client, {"PATCH_COMPANIES": None})
    assert resp.json["removed"] == ["PATCH_COMPANIES"]
    assert PatchSetting.query.count() == 0
    assert get_patch("PATCH_COMPANIES") == {"1": {"website": "from-file"}}


def test_import_invalid_files_change_nothing(client):
    for data in (
        b"not json",
        [1, 2],
        {"PATCH_UNKNOWN": {}},
        {"PATCH_COMPANIES": {}, "PATCH_LICENCES": {}},
    ):
        resp = upload(client, data, expect_errors=True)
        assert resp.status_code == 400
        assert resp.json["status"] == "error"
    assert PatchSetting.query.count() == 0

    resp = client.post(url_for("api.patches-import"), expect_errors=True)
    assert resp.status_code == 400


def test_patches_require_authentication(client):
    for resp in (
        client.get(
            url_for("api.patches-export"),
            headers={"Authorization": "wrong"},
            expect_errors=True,
        ),
        upload(
            client,
            {"PATCH_COMPANIES": {}},
            headers={"Authorization": "wrong"},
            expect_errors=True,
        ),
    ):
        assert resp.status_code == 401
    assert PatchSetting.query.count() == 0
