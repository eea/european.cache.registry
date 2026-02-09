import pandas

from cache_registry.models import (
    CombinedNomenclature,
    SubstanceNomenclature,
    db,
)
from cache_registry.sync import sync_manager


@sync_manager.command("import_combined_nomenclature")
def import_combined_nomenclature():
    file_path = "cache_registry/fixtures/multi_year_licenses/combined_nomenclature.xlsx"
    df = pandas.read_excel(file_path)

    for _, row in df.iterrows():
        combined_nomenclature = CombinedNomenclature.query.filter_by(
            code=row["CN code"], description=row["description"]
        ).first()
        if not combined_nomenclature:
            combined_nomenclature = CombinedNomenclature(
                code=row["CN code"],
                description=row["description"],
            )
            db.session.add(combined_nomenclature)
            db.session.commit()
        substance_nomenclature = SubstanceNomenclature.query.filter_by(
            chemical_name=row["substance"],
            name=row["name"],
        ).first()
        if not substance_nomenclature:
            substance_nomenclature = SubstanceNomenclature(
                chemical_name=row["substance"],
                name=row["name"],
            )
            db.session.add(substance_nomenclature)
            db.session.commit()
        substance_nomenclature.combined_nomenclatures.append(combined_nomenclature)
        db.session.commit()
