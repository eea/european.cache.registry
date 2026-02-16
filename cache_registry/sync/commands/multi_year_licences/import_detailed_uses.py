import pandas

from cache_registry.models import (
    DetailedUse,
    db,
)
from cache_registry.sync import sync_manager


@sync_manager.command("import_detailed_uses")
def import_combined_nomenclature():
    file_path = "cache_registry/fixtures/multi_year_licenses/detailed_uses.xlsx"
    df = pandas.read_excel(file_path)

    for _, row in df.iterrows():
        if row["No reporting obligation"] == "Yes":
            continue
        if not row["Detailed Use short code"] == "NaN":
            continue
        detailed_use = DetailedUse.query.filter_by(
            short_code=row["Detailed Use short code"],
            code=row["Detailed use code"],
        ).first()
        if not detailed_use:
            detailed_use = DetailedUse(
                licence_type=row["Lic Type code"],
                short_code=row["Detailed Use short code"],
                code=row["Detailed use code"],
                lic_use_desc=row["Lic Use Desc"],
                lic_type=row["Lic Type"],
                obsolete=row["Obsolete"] == "Yes",
            )
            db.session.add(detailed_use)
            db.session.commit()
        else:
            detailed_use.licence_type = row["Lic Type code"]
            detailed_use.lic_use_desc = row["Lic Use Desc"]
            detailed_use.lic_type = row["Lic Type"]
            detailed_use.obsolete = row["Obsolete"] == "Yes"
            db.session.commit()
