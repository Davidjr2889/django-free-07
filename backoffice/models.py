from django.db import models
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin


class LBBOPermissionRequiredMixin(PermissionRequiredMixin):

    raise_exception = True

    call_all_permission = None
    get_permission = None
    post_permission = None
    put_permission = None
    patch_permission = None
    delete_permission = None

    def has_permission(self):
        if self.call_all_permission is not None and self.request.user.has_perm(self.call_all_permission):
            return True
        if self.request.method == "GET":
            if self.get_permission is not None and self.request.user.has_perm(self.get_permission):
                return True
        elif self.request.method == "POST":
            if self.post_permission is not None and self.request.user.has_perm(self.post_permission):
                return True
        elif self.request.method == "PUT":
            if self.put_permission is not None and self.request.user.has_perm(self.put_permission):
                return True
        elif self.request.method == "PATCH":
            if self.patch_permission is not None and self.request.user.has_perm(self.patch_permission):
                return True
        elif self.request.method == "DELETE":
            if self.delete_permission is not None and self.request.user.has_perm(self.delete_permission):
                return True

        return False


class UserDataPerm(models.Model):
    """
    Modelo que contém as permissões de acesso por Empresa e BrandOwner para cada User
    Neste momento para facilidade de desenvolvimento é uma table (para poder ser preenchida e sererem feitos testes)
    Será na integração final convertida numa View (gerada a apartir de outras fontes) e managed=False


    Em TODOS os acessos aos dados para apresentar, exemplo:

    prods = Product.objects.filter(planingsys="M")

    deverá ser feito:

    prods = USerDataPerm.get_safe_qs(Product.objects.filter(planingsys="M", request.user_id)

    """

    user = models.ForeignKey(User)

    empresa = models.CharField(max_length=2)

    bo = models.CharField(max_length=50)

    empresa_bo = models.CharField(max_length=60)

    class Meta:
        unique_together = (('user', 'empresa', 'bo',),)
        db_table = 'user_data_perm'

    @staticmethod
    def get_safe_qs(qs, user_id):
        return qs.annotate(
            company_bo=Concat('empresa', V('_'), 'bo'),
        ).filter(
            company_bo__in=UserDataPerm.objects.filter(user_id=user_id).values_list("empresa_bo", flat=1)
        )


class LBARMTipoUser(models.Model):
    ADMIN = 0

    tipo_utilizador = models.CharField(max_length=100)

    class Meta:
        db_table = "LBARM_TIPO_USER"
        verbose_name = "Tipo Utilizador"
        verbose_name_plural = "Tipos Utilizador"

    def __str__(self):
        return self.tipo_utilizador


class LBARMProfile(models.Model):
    """ Profile extendido para users do LBARM """

    user = models.OneToOneField(User, related_name="profile")
    tipo_utilizador = models.ForeignKey(LBARMTipoUser, verbose_name="Tipo de Utilizador")

    class Meta:
        db_table = "LBARM_USER_PROFILE"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ("user__username",)

    def __str__(self):
        return f"{self.user.username} ({self.tipo_utilizador})"

    @property
    def is_admin(self):
        return self.tipo_utilizador_id == LBARMTipoUser.ADMIN


class LoginLog(models.Model):
    """ Log dos logins dos utilizadores do LBARM """

    user = models.ForeignKey(User)
    data = models.DateTimeField(auto_now_add=True)
    login_ip = models.GenericIPAddressField()

    class Meta:
        db_table = "LBARM_LOGIN_LOG"


class InvalidLoginLog(models.Model):
    """ Log dos erros de login ou tentativas de entrada ilegal """

    username = models.CharField(max_length=100)
    data = models.DateTimeField(auto_now_add=True)
    login_ip = models.GenericIPAddressField()

    class Meta:
        db_table = "LBARM_LOGIN_INVALID_LOG"
