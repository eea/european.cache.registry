revision = "0031"
down_revision = "0030"

from alembic import op


def upgrade():
    op.drop_constraint(
        "delivery_licence_undertaking_id_fkey", "delivery_licence", type_="foreignkey"
    )
    op.create_foreign_key(
        "delivery_licence_undertaking_id_fkey",
        "delivery_licence",
        "undertaking",
        ["undertaking_id"],
        ["id"],
    )
    op.drop_constraint("licence_substance_id_fkey", "licence", type_="foreignkey")
    op.create_foreign_key(
        "licence_substance_id_fkey", "licence", "substance", ["substance_id"], ["id"]
    )
    op.drop_constraint("substance_delivery_id_fkey", "substance", type_="foreignkey")
    op.create_foreign_key(
        "substance_delivery_id_fkey",
        "substance",
        "delivery_licence",
        ["delivery_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("substance_delivery_id_fkey", "substance", type_="foreignkey")
    op.create_foreign_key(
        "substance_delivery_id_fkey",
        "substance",
        "delivery_licence",
        ["delivery_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("licence_substance_id_fkey", "licence", type_="foreignkey")
    op.create_foreign_key(
        "licence_substance_id_fkey",
        "licence",
        "substance",
        ["substance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "delivery_licence_undertaking_id_fkey", "delivery_licence", type_="foreignkey"
    )
    op.create_foreign_key(
        "delivery_licence_undertaking_id_fkey",
        "delivery_licence",
        "undertaking",
        ["undertaking_id"],
        ["id"],
        ondelete="CASCADE",
    )
