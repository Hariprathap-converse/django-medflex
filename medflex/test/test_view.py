from uuid import uuid4
from django.http import Http404
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.test import Client
from django.urls import reverse
from medflex.models import Doctor, User
from medflex.views import Dashboard
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.test import RequestFactory
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

from medflex.models import Doctor, User
from medflex.views import CustomPasswordResetConfirmAPIView, CustomPasswordResetView, Dashboard,DoctorAvailabilityAPIView, DoctorUserNamePasswordUpdateAPIView, LoginView,SignupView


@pytest.mark.django_db
def test_dashboard_get_html_authenticated():
    """Test if authenticated users get the dashboard HTML page"""
    client = Client()
    user = User.objects.create_user(username="testuser", password="testpass" )
    client.force_login(user)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert "dashboard.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_dashboard_get_html_unauthenticated():
    """Test if authenticated users get the dashboard HTML page"""
    client = Client()
    response = client.get(reverse("dashboard"))

    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_dashboard_get_json_response():
    factory = APIRequestFactory()
    user = User.objects.create_user(username="testuser", password="testpass")
    request = factory.get("/dashboard/", HTTP_ACCEPT="application/json")
    request.user = user
    response = Dashboard.as_view()(request)
    assert response.status_code == 200
    assert response.data == {"message": "Welcome to the dashboard", "user": "testuser"}


@pytest.mark.django_db
def test_dashboard_get_json_response_unauthenticated():
    factory = APIRequestFactory()
    request = factory.get("/dashboard/", HTTP_ACCEPT="application/json")
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    auth_middleware = AuthenticationMiddleware(lambda req: None)
    auth_middleware.process_request(request)
    request.user = AnonymousUser()
    response = Dashboard.as_view()(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_post_success_html_request():
    request = MagicMock()
    request.content_type = "text/html"
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True

    with patch("medflex.views.DoctorSerializer", return_value=serializer_mock):
        Dashboard().post(request)
        render(request, "dashboard.html", {"success": True, "errors": None}, status=200)


@pytest.mark.django_db
def test_post_error_html_request():
    request = MagicMock()
    request.content_type = "text/html"
    request.POST = {}
    request.session = {"name": "Gowtham"}
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"This field is required"}
    with patch("medflex.views.DoctorSerializer", return_value=serializer_mock):
        Dashboard().post(request)
        render(
            request,
            "dashboard.html",
            {"success": False, "errors": serializer_mock.errors},
            status=400,
        )


@pytest.mark.django_db
def test_post_success_json_request():
    request = MagicMock()
    request.content_type = "application/json"
    request.session = {}
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    serializer_mock.save.return_value = MagicMock(doctor_id="123")
    with patch("medflex.views.DoctorSerializer", return_value=serializer_mock):
        response = Dashboard().post(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"message": "Doctor is added", "doctor_id": "123"}
    assert request.session["doctor_id"] == "123"


@pytest.mark.django_db
def test_post_error_json_request():
    request = MagicMock()
    request.content_type = "application/json"
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"name": ["This field is required."]}
    with patch("medflex.views.DoctorSerializer", return_value=serializer_mock):
        response = Dashboard().post(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_put_doctor_not_found():
    request = MagicMock()
    request.session.get.return_value = None
    response = Dashboard().put(request)
    assert response.status_code == 404
    assert response.data["error"] == "Doctor ID not found in session"


@pytest.mark.django_db
def test_put_success():
    request = MagicMock()
    request.data.get.return_value="2"
    request.session.get.return_value = 1
    doctor_mock = MagicMock(spec=Doctor)
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    serializer_mock.data = {"name": "Updated Doctor"}
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUpdateSerializer", return_value=serializer_mock
    ):
        response = Dashboard().put(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_put_error():
    request = MagicMock()
    request.session.get.return_value = 1
    request.data.get.return_value=None
    doctor_mock = MagicMock(spec=Doctor)
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock):
        response = Dashboard().put(request)
        assert response.status_code == 400

@pytest.mark.django_db
def test_put_error():
    request = MagicMock()
    request.session.get.return_value = 1
    request.data.get.return_value = "2"
    
    doctor_mock = MagicMock()
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"name": ["This field is required"]}  

    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUpdateSerializer", return_value=serializer_mock
    ):
        response = Dashboard().put(request)

    assert response.status_code == 400

@pytest.mark.django_db
def test_put_not_found_error():
    request = MagicMock()
    request.session.get.return_value = 1
    request.data.get.return_value = "2"
    with patch("medflex.views.get_object_or_404", side_effect=Http404):
        with pytest.raises(Http404):  
            Dashboard().put(request)


@pytest.mark.django_db
def test_post_step_3_section_success():
    request = MagicMock()
    request.session.get.return_value = 1
    request.POST.get.return_value = "3"
    doctor_mock = MagicMock()  
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True 

    mock_query_set = MagicMock()
    # mock_filter.return_value = mock_query_set  # filter() returns a QuerySet
    mock_query_set.delete.return_value = None

    with patch("medflex.views.get_object_or_404",return_value=doctor_mock),patch(
        "medflex.views.DoctorAvailabilitySerializer",return_value=serializer_mock),patch("medflex.views.DoctorAvailability.objects.filter",return_value=True):
         response=Dashboard().post(request)



@pytest.mark.django_db
def test_post_step_3_section_success():
    request = MagicMock()
    request.session.get.return_value = 1  
    request.POST.get.return_value = "3"  
    
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True

    mock_doctor = MagicMock()
    mock_query_set = MagicMock() 
    mock_query_set.delete.return_value = None  
   
    with patch("medflex.views.get_object_or_404",return_value=mock_doctor):
       with patch("medflex.views.DoctorAvailability.objects.filter",return_value=mock_query_set):
            with patch("medflex.views.DoctorAvailabilitySerializer",return_value=serializer_mock):
                response = Dashboard().post(request)
                assert response.status_code==200

               
@pytest.mark.django_db
def test_post_step_3_user_not_found():
    request = MagicMock()
    request.content_type = "application/json"
    request.session.get.return_value = None
    response = Dashboard().post(request)
    assert response.status_code == 400 

@pytest.mark.django_db
def test_post_step_3_error():
    request=MagicMock()
    request = MagicMock()
    request.content_type = "application/json"
    request.session.get.return_value = 1  
    request.POST.get.return_value = "3"  
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    mock_doctor = MagicMock()
    mock_query_set = MagicMock() 
    mock_query_set.delete.return_value = None 
    with patch("medflex.views.get_object_or_404",return_value=mock_doctor):
       with patch("medflex.views.DoctorAvailability.objects.filter",return_value=mock_query_set):
            with patch("medflex.views.DoctorAvailabilitySerializer",return_value=serializer_mock):
                response = Dashboard().post(request)
                assert response.status_code==400

@pytest.mark.django_db
def test_post_step_3_error_doctor_not_found():
    request = MagicMock()
    request.content_type = "application/json"
    request.session.get.return_value = 1  
    request.POST.get.return_value = "3"  
    with patch("medflex.views.get_object_or_404", side_effect=Http404):
        with pytest.raises(Http404):  
            Dashboard().post(request)

@pytest.mark.django_db
def test_post_step_3_section_success_json():
    request = MagicMock()
    request.session.get.return_value = 1  
    request.data=[
        {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}
    ]
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True

    mock_doctor = MagicMock()

    mock_query_set = MagicMock() 
    mock_query_set.delete.return_value = None 
    with patch("medflex.views.get_object_or_404",return_value=mock_doctor):
         with patch("medflex.views.DoctorAvailability.objects.filter",return_value=mock_query_set):
            with patch("medflex.views.DoctorAvailabilitySerializer",return_value=serializer_mock):
                response=DoctorAvailabilityAPIView().post(request,3)
                assert response.status_code==201
                

@pytest.mark.parametrize("invalid_data ,expected_error",[(4,400),(None,400)])
@pytest.mark.django_db
def test_post_invalid_step_3_section_error_json(invalid_data,expected_error):
    request=MagicMock()
    request.session.get.return_value = 1 
    response=DoctorAvailabilityAPIView().post(request,invalid_data)
    assert response.status_code==expected_error

@pytest.mark.django_db
def test_post_invalid_doctor_code():
    request = MagicMock()
    request.query_params = {"doctor_id": None}
    response=DoctorAvailabilityAPIView().post(request,3)
    response.status_code==400

@pytest.mark.django_db
def test_post_doctor_not_found():
    request=MagicMock()
    request.query_params = {"doctor_id": 1}
    with patch("medflex.views.get_object_or_404", side_effect=Http404):
        with pytest.raises(Http404):  
            DoctorAvailabilityAPIView().post(request,3)

@pytest.mark.django_db
def test_post_serializers_error():
    request = MagicMock()
    request.session.get.return_value = 1  
    request.data=[
        {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}
    ]
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False

    mock_doctor = MagicMock()

    mock_query_set = MagicMock() 
    mock_query_set.delete.return_value = None 
    with patch("medflex.views.get_object_or_404",return_value=mock_doctor):
         with patch("medflex.views.DoctorAvailability.objects.filter",return_value=mock_query_set):
            with patch("medflex.views.DoctorAvailabilitySerializer",return_value=serializer_mock):
                response=DoctorAvailabilityAPIView().post(request,3)
                assert response.status_code==400



@pytest.mark.django_db
def test_put_success_step_3():
    request = MagicMock()
    request.data.get.return_value="4"
    request.session.get.return_value = 1
    doctor_mock = MagicMock(spec=Doctor)
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    
    user_mock=MagicMock()
    user_mock.email="gowtham@gmail.com"
    user_mock.username="gowtham1422"
    user_mock.first_name="Gowtham"
    user_mock.last_name="sakthivel"
 
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUserNamePasswordSerializer", return_value=serializer_mock
    ):
        with patch("medflex.views.User.objects.get_or_create",return_value=(user_mock,True)):
            response = Dashboard().put(request)
            assert response.status_code == 200
        with patch("medflex.views.User.objects.get_or_create",return_value=(user_mock,False)):
            response = Dashboard().put(request)
            assert response.status_code == 200
        
@pytest.mark.django_db
def test_put_serializer_error_step_4():
    request = MagicMock()
    request.data.get.return_value="4"
    request.session.get.return_value = 1
    doctor_mock = MagicMock(spec=Doctor)
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"error": "Invalid data"}
    
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUserNamePasswordSerializer", return_value=serializer_mock
    ):
            response = Dashboard().put(request)
            assert response.status_code == 400

@pytest.mark.django_db
def test_put_doctor_user_name_password_update_api_view_success():
    request=MagicMock()
    
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    doctor_mock = MagicMock(spec=Doctor)

    user_mock=MagicMock()
    user_mock.email="gowtham@gmail.com"
    user_mock.username="gowtham1422"
    user_mock.first_name="Gowtham"
    user_mock.last_name="sakthivel"
    doctor_id = str(uuid4())
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUserNamePasswordSerializer", return_value=serializer_mock
    ):
        with patch("medflex.views.User.objects.get_or_create",return_value=(user_mock,True)):
            response =DoctorUserNamePasswordUpdateAPIView().put(request,doctor_id)
            assert response.status_code == 200
        with patch("medflex.views.User.objects.get_or_create",return_value=(user_mock,False)):
            response =DoctorUserNamePasswordUpdateAPIView().put(request,doctor_id)
            assert response.status_code == 200
            
@pytest.mark.django_db
def test_put_doctor_user_name_password_update_api_view_uid_error():
    request=MagicMock()
    
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True 
    response=DoctorUserNamePasswordUpdateAPIView().put(request,1)
    assert response.status_code==400
  
@pytest.mark.django_db
def test_put_doctor_user_name_password_update_api_view_doctor_not_found_error():
    request=MagicMock()
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    doctor_mock = MagicMock(spec=Doctor)

    user_mock=MagicMock()
    user_mock.email="gowtham@gmail.com"
    user_mock.username="gowtham1422"
    user_mock.first_name="Gowtham"
    user_mock.last_name="sakthivel"
    doctor_id = str(uuid4())
    with patch("medflex.views.get_object_or_404", side_effect=Http404):
        with pytest.raises(Http404):  
            DoctorUserNamePasswordUpdateAPIView().put(request,doctor_id)

@pytest.mark.django_db
def test_put_doctor_user_name_password_update_api_view_serializer_error():
    request=MagicMock()
    
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"error": "Invalid data"}

    doctor_mock = MagicMock(spec=Doctor)
    doctor_id = str(uuid4())
    with patch("medflex.views.get_object_or_404", return_value=doctor_mock), patch(
        "medflex.views.DoctorUserNamePasswordSerializer", return_value=serializer_mock
    ):
        response =DoctorUserNamePasswordUpdateAPIView().put(request,doctor_id)
        response.status_code==400


@pytest.mark.django_db
def test_signup_success_api():
        request_factory =APIRequestFactory()
        request = request_factory.post("/",data={},format="json")
        serializer_mock = MagicMock()
        serializer_mock.is_valid.return_value = True
        serializer_mock.save.return_value = None
        with patch.object(SignupView, "get_serializer", return_value=serializer_mock):
            response = SignupView.as_view()(request)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"message": "Account created successfully."}

@pytest.mark.django_db
def test_signup_failure_api():
        request_factory =APIRequestFactory()
        request = request_factory.post("/",data={},format="json")
        serializer_mock = MagicMock()
        serializer_mock.is_valid.return_value = False
        serializer_mock.errors = {"email": ["This field is required."]}
        with patch.object(SignupView, "get_serializer", return_value=serializer_mock):
            response = SignupView.as_view()(request)
         
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data==serializer_mock.errors
      
@pytest.mark.django_db
def test_signup_success_html():
        request_factory =APIRequestFactory()
        request = request_factory.post("/", data={"email": "test@example.com", "password": "securepass"}, format="multipart")
        serializer_mock = MagicMock()
        serializer_mock.is_valid.return_value = True
        serializer_mock.save.return_value = None
        with patch.object(SignupView, "get_serializer", return_value=serializer_mock):
            response = SignupView.as_view()(request)
        assert response.status_code==302
        assert response.url=="/login/"

@pytest.mark.django_db
def test_signup_failure_html():
    site = Site.objects.get_or_create(domain="example.com", name="example.com")[0]
    app, created = SocialApp.objects.get_or_create(
        provider="google",
        name="Google",
        defaults={"client_id": "fake_id", "secret": "fake_secret"}
    )
    app.sites.add(site)
    app.save()

    request_factory = RequestFactory()
    request = request_factory.post(reverse("signup"), data={"email": ""})

    request_factory = APIRequestFactory()
    request = request_factory.post(reverse("signup"), data={"email": ""}, format="multipart")

    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"email": ["This field is required."]}

    with patch.object(SignupView, "get_serializer", return_value=serializer_mock):
        response = SignupView.as_view()(request)
    assert response.status_code == 200
    assert b"This field is required." in response.content


@pytest.mark.django_db
def test_login_success_api():
    request_factory = APIRequestFactory()
    request = request_factory.post("/", data={}, format="json")

    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    user = User.objects.create_user(username="test_user", email="test@example.com", password="testpass")
    user.backend = "django.contrib.auth.backends.ModelBackend" 

    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    serializer_mock.validated_data = {"user": user}

    with patch("medflex.views.LoginSerializer", return_value=serializer_mock):
        with patch("django.contrib.auth.login"):
            response = LoginView.as_view()(request)
            assert response.status_code==status.HTTP_201_CREATED
            assert response.data == {'message': 'Login successfully'}

@pytest.mark.django_db
def test_login_failure_api():
    request_factory = APIRequestFactory()
    request = request_factory.post("/", data={}, format="json")

    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    user = User.objects.create_user(username="test_user", email="test@example.com", password="testpass")
    user.backend = "django.contrib.auth.backends.ModelBackend" 

    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"email": ["This field is required."]}

    with patch("medflex.views.LoginSerializer", return_value=serializer_mock):
        with patch("django.contrib.auth.login"):
            response = LoginView.as_view()(request)
            assert response.status_code==status.HTTP_400_BAD_REQUEST
            assert response.data == serializer_mock.errors

@pytest.mark.django_db
def test_login_success_html():
    request_factory = APIRequestFactory()
    request = request_factory.post("/", data={}, format="multipart")

    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    user = User.objects.create_user(username="test_user", email="test@example.com", password="testpass")
    user.backend = "django.contrib.auth.backends.ModelBackend" 

    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    serializer_mock.validated_data = {"user": user}

    with patch("medflex.views.LoginSerializer", return_value=serializer_mock):
        with patch("django.contrib.auth.login"):
            response = LoginView.as_view()(request)
            assert response.status_code==302
            assert response.url=="/dashboard/"
           
@pytest.mark.django_db
def test_login_failure_html():
    request_factory = APIRequestFactory()
    request = request_factory.post("/", data={}, format="multipart")
    site = Site.objects.get_or_create(domain="example.com", name="example.com")[0]
    app, created = SocialApp.objects.get_or_create(
        provider="google",
        name="Google",
        defaults={"client_id": "fake_id", "secret": "fake_secret"}
    )
    app.sites.add(site)
    app.save()
    
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    user = User.objects.create_user(username="test_user", email="test@example.com", password="testpass")
    user.backend = "django.contrib.auth.backends.ModelBackend" 

    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"email": ["This field is required."]}
    serializer_mock.validated_data = {"user": user}

    with patch("medflex.views.LoginSerializer", return_value=serializer_mock):
        with patch("django.contrib.auth.login"):
            response = LoginView.as_view()(request)
            assert response.status_code == 200
            assert b"This field is required." in response.content
           
@pytest.mark.django_db
def test_custom_password_reset_view_api_success():
    request=MagicMock()
    request.content_type = "application/json"
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = True
    with patch("medflex.views.PasswordResetSerializer",return_value=serializer_mock):
        with patch("medflex.views.CustomPasswordResetView.send_reset_email",return_value="http//medflex.com/password-reset/RInd4pORle66UYVI0wxS93m2diVS6bui8YrKKBCf"):
            response=CustomPasswordResetView().post(request)
    assert response.status_code==200

@pytest.mark.django_db
def test_custom_password_reset_view_failure_api():
    request=MagicMock()
    request.content_type = "application/json"
    serializer_mock = MagicMock()
    serializer_mock.is_valid.return_value = False
    serializer_mock.errors = {"email": ["This field is required."]}

    with patch("medflex.views.PasswordResetSerializer",return_value=serializer_mock):
            response=CustomPasswordResetView().post(request)
    assert response.status_code==400
    assert response.data==serializer_mock.errors

@pytest.mark.django_db
def test_custom_password_reset_view__success_html():
    request=MagicMock()
    request.content_type = "text/html"
    request.POST={"email":"user@gmail.com"}
    response=CustomPasswordResetView().post(request)
    assert response.status_code==302
    assert response.url=="/password-reset/done/"

@pytest.mark.django_db
def test_custom_password_reset_view_html_failure_not_email():
    request=MagicMock()
    request.content_type = "text/html"
    request.POST={"email":None}
    response=CustomPasswordResetView().post(request)
    assert response.status_code==400

@pytest.mark.django_db
def test_custom_password_reset_view_html_failure_invalid_email():
    request=MagicMock()
    request.content_type = "text/html"
    request.POST={"email":"use.com"}
    response=CustomPasswordResetView().post(request)
    assert response.status_code==400

@pytest.mark.django_db
def test_custom_password_reset_confirm_api_view_success():
    request=MagicMock()
    request.data={
        "reset_url":"/password-reset/confirm/MTU/abcd1234xyz/",
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    mock_user=MagicMock()
    with patch("medflex.views.User.objects.get",return_value=mock_user):
        with patch("medflex.views.default_token_generator.check_token",return_value=True):
            response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==200
    assert response.data["message"]=="Password has been reset successfully."

@pytest.mark.django_db
def test_custom_password_reset_confirm_api_view_error_whit_out_url():
    request=MagicMock()
    request.data={
        "reset_url":None,
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==400
    assert response.data["error"]=="Reset URL is required"
    
@pytest.mark.django_db
def test_custom_password_reset_confirm_api_view_error_invalid_url():
    request=MagicMock()
    request.data={
        "reset_url":"/passweset/confirm/MTU/ab",
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==400
    assert response.data["error"]=="Invalid reset URL format"

@pytest.mark.django_db
def test_custom_password_reset_confirm_api_view_invalid_user():
    request=MagicMock()
    request.data={
        "reset_url":"/password-reset/confirm/MTU/abcd1234xyz/",
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    with patch("medflex.views.User.objects.get",side_effect=User.DoesNotExist):
        response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==400
    assert response.data["error"]=="Invalid user ID"

@pytest.mark.django_db
def test_custom_password_reset_confirm_api_view_invalid_token():
    request=MagicMock()
    request.data={
        "reset_url":"/password-reset/confirm/MTU/abcd1234xyz/",
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    mock_user=MagicMock()
    with patch("medflex.views.User.objects.get",return_value=mock_user):
        with patch("medflex.views.default_token_generator.check_token",return_value=False):
            response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==400
    assert response.data["error"]=="Invalid token"

@pytest.mark.parametrize(
        "invalid_data,expected_status_code" ,[
            ({ "new_password1":"","new_password2":""},400),
            ({ "new_password1":None,"new_password2":None},400),
            ({ "new_password1":11111,"new_password2":11111},400),
            ({ "new_password1":"12345678","new_password2":"12345678"},400),
            ({ "new_password1":"Us@129","new_password2":"Us@129"},400),
        ]
)
@pytest.mark.django_db
def test_custom_password_reset_confirm_api_invalid_password(invalid_data,expected_status_code):
    request=MagicMock()
    dat1={
        "reset_url":"/password-reset/confirm/MTU/abcd1234xyz/",
        "new_password1":"User007!@203A",
        "new_password2":"User007!@203A"
    }
    dat1.update(invalid_data)
    request.data=dat1
    mock_user=MagicMock()
    with patch("medflex.views.User.objects.get",return_value=mock_user):
        with patch("medflex.views.default_token_generator.check_token",return_value=True):
            response=CustomPasswordResetConfirmAPIView().post(request)
    assert response.status_code==expected_status_code