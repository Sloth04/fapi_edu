from sqladmin import ModelView

import app.models as models


class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.username, models.User.email, models.User.role, models.User.disable]
