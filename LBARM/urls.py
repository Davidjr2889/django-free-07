from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings

from jwt_auth import views as jwt_views

from .views import check_login_ajax
from .views import api_login
from backoffice import views as bko_views


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^_nested_admin/', include('nested_admin.urls')),

    # -------------------
    # AUTH & MAIN
    # -------------------

    url(r'^check_login/', check_login_ajax),
    url(r'^accounts/login/$', auth_views.login, {
        "template_name": "admin/login.html",
    }, name="login"),
    url(r'^accounts/logout/$', auth_views.logout_then_login, name="logout"),

    url(r'^lbb-api-token-auth/$', api_login),
    url(r'^lbb-api-token-refresh/$', jwt_views.refresh_jwt_token),
    url(r'^lbb-api-logout/$', jwt_views.invalidate_jwt_token),

    # redireccionar para o backoffice
    url(r'^$', bko_views.index, name='home'),

    # -------------------
    # BACKOFFICE
    # -------------------

    url(r'^get_user_profile/$', bko_views.LBArmProfileView.as_view(), name='get_user_profile'),

    # -------------------
    # Assets
    # -------------------

    url(r'prev_log/', include("prev_log.urls")),

]

if settings.DEBUG:
    from django.views import static

    urlpatterns += (
        url(r'^site_media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    )

    try:
        import debug_toolbar
        urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass
