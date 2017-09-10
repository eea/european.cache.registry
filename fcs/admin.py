from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from fcs import models

admin = Admin(name="fcs")


class UndertakingView(ModelView):
    form_excluded_columns = ('candidates', )


admin.add_view(UndertakingView(models.Undertaking, models.db.session))
admin.add_view(UndertakingView(models.User, models.db.session))
