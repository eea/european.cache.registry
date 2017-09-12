revision = '100ea8b4b4e3'
down_revision = 'cbe30f17ed0'

from alembic import op
import sqlalchemy as sa
from fcs.models import Type, Undertaking,  UndertakingTypes, db

"""
 This migration takes data from undertaking types field which right now look
 like this:
        [value1,value2, value3]
 and creates relations between undertaking and type table with those values.
"""


def upgrade():
    undertakings = Undertaking.query.all()
    undertaking_types = {}
    for undertaking in undertakings:
        for type in undertaking.types.split(','):
            if not type:
                continue
            type_object = Type.query.filter_by(type=type).first()
            if not type_object:
                type_object = Type(type=type, domain=undertaking.domain)
                db.session.add(type_object)
                db.session.commit()
            undertaking_types[(undertaking, type_object)] = 1
            db.session.remove()
    print "Updated"


def downgrade():
    pass