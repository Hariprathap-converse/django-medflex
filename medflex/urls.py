from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from medflex.views import (
    CustomPasswordResetConfirmAPIView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    Dashboard,
    DeleteDoctorView,
    DeleteDoctorViewApi,
    DoctorAvailabilityAPIView,
    DoctorListAPIView,
    DoctorListView,
    DoctorUpdateAPIView,
    DoctorUpdateApiView,
    DoctorUpdateApiViewAccount,
    DoctorUpdateApiViewAvailability,
    DoctorUpdateApiViewPersonal,
    DoctorUpdateApiViewProfile,
    DoctorUpdateView,
    DoctorUserNamePasswordUpdateAPIView,
    LoginView,
    LogoutView,
    SignupView,
    SingleDoctorView,
)

urlpatterns = [
    path("", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/confirm/",
        CustomPasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm_api",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "dashboard/<uuid:doctor_id>/",
        DoctorUpdateAPIView.as_view(),
        name="doctor-update",
    ),
    path(
        "doctor/step/<int:step>/",
        DoctorAvailabilityAPIView.as_view(),
        name="doctor-availability-update",
    ),
    path(
        "doctor/<uuid:doctor_id>/",
        DoctorUserNamePasswordUpdateAPIView.as_view(),
        name="doctor-account",
    ),
    path("doctor/view/", DoctorListView.as_view(), name="doctor-list-view"),
    path("doctor/api/", DoctorListAPIView.as_view(), name="doctor-list-api"),
    path(
        "doctor/update/<uuid:doctor_id>/",
        DoctorUpdateView.as_view(),
        name="update_doctor_data",
    ),
    path(
        "doctor/update/api/get/<str:doctor_id>/",
        DoctorUpdateApiView.as_view(),
        name="update_doctor_data_api",
    ),
    path(
        "doctor/update/api/personal/<int:step>/<str:doctor_id>/",
        DoctorUpdateApiViewPersonal.as_view(),
        name="update_doctor_data_profile_api",
    ),
    path(
        "doctor/update/api/profile/<int:step>/<str:doctor_id>/",
        DoctorUpdateApiViewProfile.as_view(),
        name="update_doctor_data_personal_api",
    ),
    path(
        "doctor/update/api/availability/<int:step>/<str:doctor_id>/",
        DoctorUpdateApiViewAvailability.as_view(),
        name="update_doctor_data_availability_api",
    ),
    path(
        "doctor/update/api/account/<int:step>/<str:doctor_id>/",
        DoctorUpdateApiViewAccount.as_view(),
        name="update_doctor_data_account_api",
    ),
    path(
        "delete_doctor_data/delete/<uuid:doctor_id>/",
        DeleteDoctorView.as_view(),
        name="delete_doctor",
    ),
    path(
        "delete_doctor_data/delete/<str:doctor_id>/",
        DeleteDoctorViewApi.as_view(),
        name="delete_doctor_api",
    ),
    path("doctor/data", SingleDoctorView.as_view(), name="doctor_data"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
