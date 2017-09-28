revision = '52decb727dcb'
down_revision = 'beba44b3efb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table('old_company_link')
    op.drop_constraint('fk_old_company', 'undertaking', 'foreignkey')
    op.drop_column('undertaking', 'oldcompany_id')
    op.drop_table('old_company')
    op.drop_column('matching_log', 'oldcompany_id')


def downgrade():
    op.create_table('old_company_link',
        sa.Column('oldcompany_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=False),
        sa.Column('undertaking_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=False),
        sa.Column('verified', mysql.TINYINT(display_width=1),
                  autoincrement=False, nullable=True),
        sa.Column('date_added', mysql.DATETIME(), nullable=True),
        sa.Column('date_verified', mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('oldcompany_id', 'undertaking_id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'MyISAM'
    )
    op.create_table('old_company',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column('external_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=True),
        sa.Column('name', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('country_code', mysql.VARCHAR(length=10), nullable=True),
        sa.Column('account', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('vat_number', mysql.VARCHAR(length=32), nullable=True),
        sa.Column('eori', mysql.VARCHAR(length=32), nullable=True),
        sa.Column('active', mysql.TINYINT(display_width=1),
                  autoincrement=False, nullable=True),
        sa.Column('website', mysql.VARCHAR(length=255), nullable=True),
        sa.Column('date_registered', mysql.DATETIME(), nullable=True),
        sa.Column('valid', mysql.TINYINT(display_width=1),
                  autoincrement=False, nullable=True),
        sa.Column('obligation', mysql.VARCHAR(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset=u'utf8',
        mysql_engine=u'MyISAM'
    )
    op.add_column('undertaking',
        sa.Column('oldcompany_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=True, default=None))
    op.add_column('matching_log',
        sa.Column('oldcompany_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=True, default=None))
