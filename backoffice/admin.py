from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin

import nested_admin

from .models import LBARMProfile
from .models import LBARMTipoUser


admin.site.register(LBARMTipoUser)
admin.site.unregister(User)


class LBARMProfileInline(nested_admin.NestedStackedInline):
    model = LBARMProfile


@admin.register(User)
class LBARMUserAdmin(nested_admin.NestedModelAdmin, UserAdmin):
    inlines = [LBARMProfileInline]

    list_display = ("username", "email", "first_name", "last_name", "get_tipo", "is_staff", "is_active")

    def get_tipo(self, obj):
        return obj.profile.tipo_utilizador

    get_tipo.short_description = 'Tipo Utilizador'
    get_tipo.admin_order_field = 'profile__tipo_utilizador'

    class Media:
        css = {
            "all": ("css/admin_per.css",)
        }


admin.site.unregister(Group)


class LBARMGroupAdmin(GroupAdmin):

    class Media:
        css = {
            "all": ("css/admin_per.css",)
        }


admin.site.register(Group, LBARMGroupAdmin)
