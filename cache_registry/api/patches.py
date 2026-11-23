import json

from flask import Response, current_app, request

from cache_registry.api.views import ApiView
from cache_registry.models import PATCH_SETTINGS, PatchSetting, db, get_patch


class PatchSettingsExport(ApiView):
    """Export the patch settings currently in use as a JSON file.

    The values stored in the database are returned; for the settings that are
    not in the database, the values from localsettings.py are returned.
    """

    def get(self, **kwargs):
        data = {
            name: get_patch(name, value_type())
            for name, value_type in PATCH_SETTINGS.items()
        }
        return Response(
            json.dumps(data, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=patches.json"},
        )


class PatchSettingsImport(ApiView):
    """Save patch settings from an uploaded JSON file into the database.

    Only the settings present in the file are changed. A setting set to null
    is removed from the database, so the value from localsettings.py is used
    again.
    """

    def error(self, message):
        self.status_code = 400
        return {"status": "error", "message": message}

    def post(self, **kwargs):
        file = request.files.get("file", None)
        if not file:
            return self.error("No file uploaded.")
        try:
            data = json.loads(file.read())
        except ValueError as e:
            return self.error(f"Invalid JSON: {e}")
        if not isinstance(data, dict):
            return self.error("The file must contain a JSON object.")

        errors = []
        for name, value in data.items():
            if name not in PATCH_SETTINGS:
                errors.append(f"Unknown setting {name}.")
            elif value is not None and not isinstance(value, PATCH_SETTINGS[name]):
                expected = PATCH_SETTINGS[name].__name__
                errors.append(f"{name} must be a {expected} or null.")
        if errors:
            return self.error(" ".join(errors))

        updated, removed = [], []
        for name, value in data.items():
            setting = PatchSetting.query.filter_by(name=name).first()
            if value is None:
                if setting:
                    db.session.delete(setting)
                    removed.append(name)
                continue
            if not setting:
                setting = PatchSetting(name=name)
                db.session.add(setting)
            setting.value = value
            updated.append(name)
        db.session.commit()
        current_app.logger.info(
            f"Patch settings updated: {updated}; removed from database: {removed}"
        )
        return {"status": "success", "updated": updated, "removed": removed}
