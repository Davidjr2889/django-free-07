from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import redirect
from jwt_auth.mixins import JSONWebTokenAuthMixin


class LBArmProfileView(JSONWebTokenAuthMixin, View):
    http_method_names = ['get']

    def get(self, request):

        return JsonResponse({
            "user_id": request.user.id,
            "username": request.user.get_username(),
            "profile_type": request.user.profile.tipo_utilizador_id,
            "os_perms": list(request.user.get_all_permissions())
        })


def index(request):
    return redirect("/backoffice/")
