# import json

# from django.contrib.auth.models import User
# from django.test import Client, TestCase
# from rest_framework.test import APIRequestFactory, force_authenticate

# from backoffice.models import LBARMProfile, LBARMTipoUser
# from jwt_auth.views import obtain_jwt_token
# from prev_log.views import StockPageBaseDataView


# class StockPageTestCase(TestCase):
#     fixtures = ["lbarmtipouser.json"]

#     def setUp(self):
#         pass

#     def test_can_get_basic_data(self):
#         """We can get the basic data successfully from an API call"""

#         ##### TODO: Move to test setup
#         client = APIRequestFactory()
#         USER_PASSWORD = "test"
#         user = User.objects.create_user(
#             username="test",
#             email="test@foo.com",
#             password=USER_PASSWORD,
#         )
#         profile = LBARMTipoUser.objects.get(tipo_utilizador="Admin")
#         LBARMProfile.objects.create(
#             tipo_utilizador=profile,
#             user=user,
#         )

#         auth_request = client.post(
#             "/",
#             {"username": user.username, "password": USER_PASSWORD},
#             format="json",
#         )
#         token_response = obtain_jwt_token(auth_request)
#         token = json.loads(token_response.content)["token"]
#         #########

#         view = StockPageBaseDataView.as_view()
#         request = client.get("", HTTP_AUTHORIZATION=f"Bearer {token}")

#         response = view(request)

#         assert response.status_code == 200
