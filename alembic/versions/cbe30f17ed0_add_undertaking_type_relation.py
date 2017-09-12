revision = 'cbe30f17ed0'
down_revision = '1197731f470d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('undertaking_types',
        sa.Column('undertaking_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
        sa.ForeignKeyConstraint(['undertaking_id'], ['undertaking.id'], ),
        sa.PrimaryKeyConstraint('undertaking_id', 'type_id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'MyISAM'
    )


def downgrade():
    op.drop_table('undertaking_types')