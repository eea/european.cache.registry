revision = '100ea8b4b4e3'
down_revision = '3b6b91477843'

"""
 This migration takes data from undertaking types field which right now look
 like this:
        [value1,value2, value3]
 and creates relations between undertaking and type table with those values.
"""

from alembic import op
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base

from fcs.models import db

import sqlalchemy as sa

Session = sessionmaker()
Base = declarative_base()


class Type(Base):
    __tablename__ = 'type'

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String(255))
    domain = sa.Column(sa.String(38))


class Undertaking(Base):
    __tablename__ = 'undertaking'
    id = sa.Column(sa.Integer, primary_key=True)
    domain = sa.Column(sa.String(32), nullable=False)
    types = sa.Column(sa.String(255))


class UndertakingTypes(Base):
    __tablename__ = 'undertaking_types'

    undertaking_id = sa.Column(sa.ForeignKey('undertaking.id'),
                               primary_key=True)
    type_id = sa.Column(sa.ForeignKey('type.id'), primary_key=True)

    undertaking = relationship('Undertaking')
    type = relationship('Type')


def upgrade():
    op.create_table('type',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=255), nullable=True),
                    sa.Column('domain', sa.String(length=32), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('undertaking_types',
                    sa.Column('undertaking_id', sa.Integer(),
                              nullable=False),
                    sa.Column('type_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
                    sa.ForeignKeyConstraint(['undertaking_id'],
                                            ['undertaking.id'], ),
                    sa.PrimaryKeyConstraint('undertaking_id', 'type_id'),
                    mysql_default_charset=u'utf8',
                    mysql_engine=u'MyISAM'
                    )

    bind = op.get_bind()
    session = Session(bind=bind)
    undertakings = session.query(Undertaking)
    undertaking_types = []
    for undertaking in undertakings:
        for type in undertaking.types.split(','):
            if not type:
                continue
            type_object = session.query(Type).filter_by(type=type).first()
            if not type_object:
                type_object = Type(type=type, domain=undertaking.domain)
                session.add_all([type_object])
                session.commit()
            undertaking_types.append({
                'undertaking_id': undertaking.id,
                'type_id': type_object.id
            })
    print("Updated")
    op.bulk_insert(UndertakingTypes.__table__, undertaking_types)
    op.drop_column('undertaking', 'types')
    session.commit()


def downgrade():
    updated_undertakings = []
    bind = op.get_bind()
    op.add_column('undertaking',
                  sa.Column('types', mysql.VARCHAR(length=255), nullable=True))
    session = Session(bind=bind)
    undertakings = session.query(Undertaking).all()
    for undertaking in undertakings:
        undertaking.types = ",".join([
            relation.type.type for relation in session.query(
                UndertakingTypes).filter_by(undertaking_id=undertaking.id).all()
            ])
        updated_undertakings.append(undertaking)
    session.add_all(updated_undertakings)
    op.drop_table('undertaking_types')
    op.drop_table('type')
    session.commit()
