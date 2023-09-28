import json

from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.http import JsonResponse
from django.http import HttpResponseNotAllowed
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from dascat_utils.django.user_utils import get_client_ip

from jwt_auth.views import obtain_jwt_token
from jwt_auth.core import User

from backoffice.models import LoginLog
from backoffice.models import InvalidLoginLog


# --------------------
# LOGIN
# --------------------

@csrf_exempt
@never_cache
def check_login_ajax(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return JsonResponse({"success": True})
        else:
            request.session.set_test_cookie()
            return JsonResponse({"success": False, "reason": "Dados Inválidos"})
    else:
        return HttpResponseNotAllowed(("POST",))


@csrf_exempt
@never_cache
def api_login(request):
    response = obtain_jwt_token(request)
    st = response.status_code
    if st == 200:
        LoginLog.objects.create(
            user=request.user,
            login_ip=get_client_ip(request)
        )
    else:
        request_json = json.loads(request.body)
        InvalidLoginLog.objects.create(
            username=request_json[User.USERNAME_FIELD],
            login_ip=get_client_ip(request)
        )
    return response
