import hashlib
import re
import uuid
from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import validate_email
from django.db.models import Q
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView, UpdateView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from medflex.models import Doctor, DoctorAvailability, LoginLogs
from medflex.serializers import (
    DoctorAvailabilitySerializer,
    DoctorSerializer,
    DoctorUpdateSerializer,
    DoctorUserNamePasswordSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    SignupSerializer,
    UpdateDoctorAvailabilitySerializer,
    UpdateDoctorSerializer,
)
from rest_framework import generics, status
from rest_framework.decorators import schema
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()
from django.core.paginator import Paginator


class SignupView(generics.CreateAPIView, TemplateView):
    template_name = "signup.html"
    serializer_class = SignupSerializer

    @swagger_auto_schema(
        tags=["Singup"],
    )
    def get(self, request):
        return render(request, self.template_name)

    @swagger_auto_schema(
        tags=["Signup"],
        request_body=SignupSerializer,
        responses={201: "Account Created succesfully", 400: "Invalid data"},
    )
    def post(self, request):
        is_api_request = request.content_type == "application/json"
        data = request.data if is_api_request else request.POST
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if is_api_request:
                return Response(
                    {"message": "Account created successfully."},
                    status=status.HTTP_201_CREATED,
                )
            return redirect("login")
        if is_api_request:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return render(request, self.template_name, {"error_fields": serializer.errors})


class LoginView(APIView, TemplateView):
    template_name = "login.html"

    def get(self, request):
        return render(request, "login.html")

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: "Login successful", 401: "Invalid credentials"},
    )
    def post(self, request):
        is_api_request = request.content_type == "application/json"
        data = request.data if is_api_request else request.POST

        serializer = LoginSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            LoginLogs.objects.create(name=user.username, email=user.email)

            if is_api_request:
                return Response(
                    {"message": "Login successfully"}, status=status.HTTP_201_CREATED
                )
            return redirect("dashboard")
        if is_api_request:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return render(request, "login.html", {"error_fields": serializer.errors})


@receiver(user_logged_in)
def log_google_login(sender, request, user, **kwargs):
    LoginLogs.objects.create(name=user.get_full_name(), email=user.email)


class LogoutView(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect("login")

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"message": "User is already logged out"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logout(request)
        return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)


class CustomPasswordResetView(APIView):
    template_name = "forgetpassword.html"
    success_url = reverse_lazy("password_reset_done")

    def send_reset_email(self, email, request):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = email
        if isinstance(user, User):
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        else:
            token = hashlib.sha256(get_random_string(32).encode()).hexdigest()
            uidb64 = "qw@" + token + "$"
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
        )

        subject = "Reset Your Password"
        message = render_to_string(
            "password_reset_email.html",
            {
                "reset_url": reset_url,
                "user": user if isinstance(user, User) else None,
                "uidb64": uidb64,
                "token": token,
            },
        )

        plain_message = strip_tags(message)
        email_message = EmailMultiAlternatives(
            subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email]
        )
        email_message.attach_alternative(message, "text/html")
        email_message.send()
        return reset_url

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @swagger_auto_schema(
        tags=["ForgetPassword"],
        request_body=PasswordResetSerializer,
        responses={200: "Post received", 400: "Invalid data"},
    )
    def post(self, request, *args, **kwargs):
        is_api_request = request.content_type == "application/json"

        if is_api_request:
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                url = self.send_reset_email(email, request)
                return Response(
                    {
                        "message": f"A password reset link has been sent to your email.   '{url}'"
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            email = request.POST.get("email")
            if not email:
                return render(
                    request,
                    self.template_name,
                    {"error_fields": {"email": "Please enter an email address."}},
                    status=400,
                )

            try:
                validate_email(email)
            except ValidationError:
                return render(
                    request,
                    self.template_name,
                    {"error_fields": {"email": "Please enter a valid email address."}},
                    status=400,
                )
            self.send_reset_email(email, request)
            return redirect(self.success_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetConfirmAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Confirm password reset by providing uid, token, and new password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["reset_url", "new_password1", "new_password2"],
            properties={
                "reset_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Password reset URL containing uid and token",
                ),
                "new_password1": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="New password",
                ),
                "new_password2": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Confirm new password",
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Password successfully reset"),
            400: openapi.Response(description="Invalid token or mismatched passwords"),
        },
    )
    def post(self, request):
        reset_url = request.data.get("reset_url")
        new_password1 = request.data.get("new_password1")
        new_password2 = request.data.get("new_password2")

        if not reset_url:
            return Response(
                {"error": "Reset URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        match = re.search(
            r"/password-reset/confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/", reset_url
        )
        if not match:
            return Response(
                {"error": "Invalid reset URL format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uidb64 = match.group("uidb64")
        token = match.group("token")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if new_password1 != new_password2:
            return Response(
                {"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST
            )

        form = SetPasswordForm(
            user, {"new_password1": new_password1, "new_password2": new_password2}
        )
        if form.is_valid():
            form.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class Dashboard(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    template_name = "dashboard.html"
    login_url = "/login/"

    @swagger_auto_schema(
        tags=["Dashboard"],
        responses={200: "Welcome to dashboard", 401: "Invalid credentials"},
    )
    def get(self, request):

        is_api_request = (
            request.content_type == "application/json"
            or request.headers.get("Accept") == "application/json"
        )

        if is_api_request:
            return Response(
                {"message": "Welcome to the dashboard", "user": str(request.user)},
                status=status.HTTP_200_OK,
            )
        doctor = (
            Doctor.objects.filter(email=request.user.email).first()
            if request.user.is_authenticated
            else None
        )

        if doctor:
            return render(
                request, self.template_name, {"user": request.user, "doctor": doctor}
            )

        return render(request, self.template_name, {"user": request.user})

    def post(self, request):
        is_api_request = request.content_type == "application/json"
        step = request.POST.get("step")

        if step == "3":
            doctor_id = request.session.get("doctor_id")
            if not doctor_id:
                return render(
                    request,
                    self.template_name,
                    {"errors": "Doctor ID not found in session"},
                    status=404,
                )
            doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
            availability_data = []
            for day in request.data.getlist("day_of_week"):
                start_time = request.data.get(f"start_time_{day}")
                end_time = request.data.get(f"end_time_{day}")
                if start_time and end_time:
                    availability_data.append(
                        {
                            "day_of_week": day,
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                    )
            DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week__in=[item["day_of_week"] for item in availability_data],
            ).delete()
            serializer = DoctorAvailabilitySerializer(
                data=availability_data, many=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return render(
                    request,
                    self.template_name,
                    {"success": True, "errors": None},
                    status=200,
                )
            return render(
                request,
                self.template_name,
                {"success": False, "errors": serializer.errors},
                status=400,
            )
        else:

            data = request.data if is_api_request else request.POST
            serializer = DoctorSerializer(data=data, context={"request": request})
            if serializer.is_valid():
                doctor = serializer.save()
                request.session["doctor_id"] = str(doctor.doctor_id)
                response_data = {
                    "message": "Doctor is added",
                    "doctor_id": str(doctor.doctor_id),
                }
                if is_api_request:
                    return Response(response_data, status=status.HTTP_201_CREATED)
                return render(
                    request,
                    self.template_name,
                    {"success": True, "errors": None},
                    status=200,
                )

            if is_api_request:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return render(
                request,
                self.template_name,
                {"success": False, "errors": serializer.errors},
                status=400,
            )

    def put(self, request):
        doctor_id = request.session.get("doctor_id")
        if not doctor_id:
            return Response(
                {"error": "Doctor ID not found in session"},
                status=status.HTTP_404_NOT_FOUND,
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        step = request.data.get("step")

        if step == "2":
            serializer = DoctorUpdateSerializer(doctor, data=request.data, partial=True)
        elif step == "4":
            serializer = DoctorUserNamePasswordSerializer(
                doctor, data=request.data, partial=True
            )
        else:
            return Response(
                {"error": "Invalid step"}, status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save()
            if step == "4":
                password = request.data.get("password")
                if not password:
                    return Response(
                        {"error": "Password is required for this step"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user, created = User.objects.get_or_create(email=doctor.email)

                if created:
                    user.set_password(password)
                    user.username = doctor.user_name
                    user.first_name = doctor.first_name
                    user.last_name = doctor.last_name
                    user.email = doctor.email
                    user.save()
                if user:
                    user.set_password(password)
                    user.username = doctor.user_name
                    user.save()
            return render(
                request,
                self.template_name,
                {"success": True, "errors": None},
                status=200,
            )
        return JsonResponse({"success": False, "errors": serializer.errors}, status=400)


class DoctorAvailabilityAPIView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=["Api"],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    "day_of_week": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Day of the week"
                    ),
                    "start_time": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format="time",
                        description="Start time (HH:MM)",
                    ),
                    "end_time": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format="time",
                        description="End time (HH:MM)",
                    ),
                },
                required=["day_of_week", "start_time", "end_time"],
            ),
        ),
        manual_parameters=[
            openapi.Parameter(
                "step",
                openapi.IN_PATH,
                description="Step number for the update process",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "doctor_id",
                openapi.IN_QUERY,
                description="UUID of the doctor",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={201: "Doctor availability created", 400: "Invalid data"},
    )
    def post(self, request, step):
        if step != 3:
            return Response(
                {"error": "Invalid step. Expected step=3."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        doctor_id = request.query_params.get("doctor_id")
        if not doctor_id:
            return Response(
                {"error": "Doctor ID is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

        if not isinstance(request.data, list):
            return Response(
                {"error": "Request body must be a list of availability data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        DoctorAvailability.objects.filter(doctor=doctor).delete()
        serializer = DoctorAvailabilitySerializer(
            data=request.data, many=True, context={"doctor": doctor, "request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Availability created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorUpdateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=["Profile_upload"],
        request_body=DoctorUpdateSerializer,
        responses={200: "Doctor record updated", 400: "Invalid data"},
    )
    def put(self, request, doctor_id):
        try:
            doctor_uuid = UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_uuid)
        serializer = DoctorUpdateSerializer(doctor, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorUserNamePasswordUpdateAPIView(APIView):
    parser_classes = (JSONParser,)

    @swagger_auto_schema(
        tags=["Account_details"],
        request_body=DoctorUserNamePasswordSerializer,
        manual_parameters=[
            openapi.Parameter(
                "doctor_id",
                openapi.IN_PATH,
                description="Doctor ID (UUID format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            )
        ],
        responses={200: "Doctor record updated", 400: "Invalid data"},
    )
    def put(self, request, doctor_id):
        try:
            doctor_uuid = UUID(str(doctor_id))
            doctor = get_object_or_404(Doctor, doctor_id=doctor_uuid)
        except ValueError:
            return Response(
                {"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = DoctorUserNamePasswordSerializer(
            doctor, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            password = request.data.get("password")
            user, created = User.objects.get_or_create(email=doctor.email)

            if created:
                user.set_password(password)
                user.username = doctor.user_name
                user.first_name = doctor.first_name
                user.last_name = doctor.last_name
                user.email = doctor.email
                user.save()
            if user:
                user.set_password(password)
                user.username = doctor.user_name
                user.save()
            return Response(
                {"message": "Account  updated successfully"}, status=status.HTTP_200_OK
            )
        return JsonResponse({"success": False, "errors": serializer.errors}, status=400)


class DoctorListView(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    template_name = "view_doctor.html"
    login_url = "/login/"

    def get(self, request):

        search_query = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "first_name")
        order = request.GET.get("order", "asc")
        # Get `page` and `per_page` values from the request
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))  # Default to 6 records per page

        # Apply pagination
        doctors = Doctor.objects.prefetch_related(
            "availabilities"
        ).all()  # Get all doctors
        if search_query:
            doctors = doctors.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(designation__icontains=search_query)
            )
        if order == "desc":
            sort_by = f"-{sort_by}"
        doctors = doctors.order_by(sort_by)
        paginator = Paginator(doctors, per_page)  # Paginate BEFORE processing data
        page_obj = paginator.get_page(page)

        days_of_week = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        doctor_data = []

        for (
            doctor
        ) in page_obj.object_list:  # Now only the required page's doctors are processed
            availability_map = {
                day: "NA" for day in days_of_week
            }  # Default all days to "NA"

            for availability in doctor.availabilities.all():
                time_range = f"{availability.start_time.strftime('%#I%p')}-{availability.end_time.strftime('%#I%p')}"
                if availability_map[availability.day_of_week] == "NA":
                    availability_map[availability.day_of_week] = time_range
                else:
                    availability_map[availability.day_of_week] += f" <br> {time_range}"

            doctor_data.append(
                {
                    "id": doctor.create_id,
                    "name": f"{doctor.first_name} {doctor.last_name}",
                    "profile_image": (
                        doctor.update_profile.url if doctor.update_profile else None
                    ),
                    "designation": doctor.get_designation_display(),
                    "availability": availability_map,
                    "doctor_id": doctor.doctor_id,
                }
            )

        return render(
            request,
            "view_doctor.html",
            {
                "doctors": doctor_data,
                "days_of_week": days_of_week,
                "page_obj": page_obj,
                "per_page": per_page,
                "search_query": search_query,
                "sort_by": sort_by.replace("-", ""),
                "order": order,
            },
        )


class DoctorListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Doctor_list"],
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search doctors by name or designation",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "sort_by",
                openapi.IN_QUERY,
                description="Sort field (first_name, last_name, designation)",
                type=openapi.TYPE_STRING,
                default="first_name",
            ),
            openapi.Parameter(
                "order",
                openapi.IN_QUERY,
                description="Sort order (asc or desc)",
                type=openapi.TYPE_STRING,
                default="asc",
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                default=1,
            ),
            openapi.Parameter(
                "per_page",
                openapi.IN_QUERY,
                description="Number of records per page",
                type=openapi.TYPE_INTEGER,
                default=10,
            ),
        ],
        responses={200: "Success", 400: "Bad Request", 401: "Unauthorized"},
    )
    def get(self, request):
        search_query = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "first_name")
        order = request.GET.get("order", "asc")
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 10)

        valid_sort_fields = [field.name for field in Doctor._meta.fields]
        if sort_by not in valid_sort_fields:
            return Response(
                {
                    "error": f"Invalid sort_by field: {sort_by}. Available fields: {valid_sort_fields}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order not in ["asc", "desc"]:
            return Response(
                {"error": "Invalid order parameter. Allowed values: asc, desc."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            page = int(page)
            per_page = int(per_page)
            if page < 1 or per_page < 1:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Page and per_page must be positive integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doctors = Doctor.objects.prefetch_related("availabilities").all()

        if search_query:
            doctors = doctors.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(designation__icontains=search_query)
            )

        if order == "desc":
            sort_by = f"-{sort_by}"
        doctors = doctors.order_by(sort_by)

        paginator = Paginator(doctors, per_page)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            return Response(
                {"error": "Page must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmptyPage:
            return Response(
                {"error": "Page number out of range."}, status=status.HTTP_404_NOT_FOUND
            )

        days_of_week = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        doctor_data = []

        for doctor in page_obj.object_list:
            availability_map = {day: "NA" for day in days_of_week}
            for availability in doctor.availabilities.all():
                time_range = f"{availability.start_time.strftime('%#I%p')}-{availability.end_time.strftime('%#I%p')}"
                if availability_map[availability.day_of_week] == "NA":
                    availability_map[availability.day_of_week] = time_range
                else:
                    availability_map[availability.day_of_week] += f" <br> {time_range}"

            doctor_data.append(
                {
                    "id": doctor.create_id,
                    "name": f"{doctor.first_name} {doctor.last_name}",
                    "profile_image": (
                        doctor.update_profile.url if doctor.update_profile else None
                    ),
                    "designation": doctor.get_designation_display(),
                    "availability": availability_map,
                }
            )

        return Response(
            {
                "doctors": doctor_data,
                "days_of_week": days_of_week,
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "per_page": per_page,
                "search_query": search_query,
                "sort_by": sort_by.replace("-", ""),
                "order": order,
            },
            status=status.HTTP_200_OK,
        )


@schema(None)
class DoctorUpdateView(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    template_name = "update_doctor.html"
    login_url = "/login/"

    def get(self, request, doctor_id):

        doctor = get_object_or_404(
            Doctor.objects.prefetch_related("availabilities"), doctor_id=doctor_id
        )

        # Fetch related availabilities
        availabilities = {
            availability.day_of_week: availability
            for availability in doctor.availabilities.all()
        }
        print("Availabilities:")
        days_of_week = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]

        return render(
            request,
            "update_doctor.html",
            {
                "doctor": doctor,
                "availabilities": availabilities,
                "days_of_week": days_of_week,
            },
        )

    def put(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        data = request.POST.copy()
        step = data.get("step")

        if not step:
            return Response(
                {"success": False, "message": "Step is required"}, status=400
            )

        if step == "1":
            serializer = UpdateDoctorSerializer(doctor, data=data, partial=True)
        elif step == "2":
            serializer = DoctorUpdateSerializer(doctor, data=data, partial=True)
        elif step == "3":
            availability_data = []
            errors = {}

            # Collect availability data from the request
            for day in request.data.getlist("day_of_week"):
                start_time = request.data.get(f"start_time_{day}")
                end_time = request.data.get(f"end_time_{day}")

                if start_time and end_time:
                    availability_data.append(
                        {
                            "day_of_week": day,
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                    )

            existing_availabilities = DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week__in=[item["day_of_week"] for item in availability_data],
            )
            existing_availabilities_map = {
                av.day_of_week: av for av in existing_availabilities
            }

            updated_instances = []

            for item in availability_data:
                day_of_week = item["day_of_week"]

                # If availability already exists, update it
                if day_of_week in existing_availabilities_map:
                    instance = existing_availabilities_map[day_of_week]
                    serializer = UpdateDoctorAvailabilitySerializer(
                        instance, data=item, partial=True
                    )

                    if serializer.is_valid():
                        saved_instance = serializer.save()
                        updated_instances.append(saved_instance)
                    else:
                        errors[day_of_week] = serializer.errors

                else:
                    item["doctor"] = (
                        doctor.doctor_id
                    )  # Assign doctor ID for new availability
                    serializer = UpdateDoctorAvailabilitySerializer(
                        data=item, context={"request": request}
                    )

                    if serializer.is_valid():
                        print("Validated Data:", serializer.validated_data)
                        saved_instance = serializer.save()
                        updated_instances.append(saved_instance)
                    else:
                        print(
                            f"Validation Failed for {day_of_week}: {serializer.errors}"
                        )  # Debugging
                        errors[day_of_week] = serializer.errors
            if errors:
                return Response({"success": False, "errors": errors}, status=400)
        elif step == "4":
            serializer = DoctorUserNamePasswordSerializer(doctor, data=data)
            if serializer.is_valid():
                serializer.save()
                password = request.data.get("password")
                user, created = User.objects.get_or_create(email=doctor.email)

                if created:
                    user.username = doctor.user_name
                    user.first_name = doctor.first_name
                    user.last_name = doctor.last_name
                    user.set_password(password)
                    user.save()
                if user:
                    user.set_password(password)
                    user.username = doctor.user_name
                    user.save()
        else:
            return Response(
                {"success": False, "message": "Invalid step provided"}, status=400
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": f"Doctor updated successfully for step {step}",
                },
                status=200,
            )

        return Response({"success": False, "errors": serializer.errors}, status=400)


@schema(None)
class DeleteDoctorView(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, doctor_id):
        doctor = Doctor.objects.filter(doctor_id=doctor_id).first()
        user = User.objects.filter(email=doctor.email).first()
        if not doctor:
            return Response({"error": "Doctor not found"}, status=404)
        doctor.delete()
        if user:
            user.delete()
        return Response({"message": "Doctor deleted successfully"}, status=200)


class DeleteDoctorViewApi(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, doctor_id):
        try:
            doctor_uuid = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = Doctor.objects.filter(doctor_id=doctor_uuid).first()
        user = User.objects.filter(email=doctor.email).first()

        if not doctor:
            return JsonResponse({"error": "Doctor not found"}, status=404)

        doctor.delete()
        if user:
            user.delete()

        return JsonResponse({"message": "Doctor deleted successfully"}, status=200)


class DoctorUpdateApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get doctor details along with availability",
        manual_parameters=[
            openapi.Parameter(
                "doctor_id",
                openapi.IN_PATH,
                description="Doctor ID (UUID format)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "Doctor details fetched successfully",
            400: "Invalid UUID format",
            401: "Authentication required",
            404: "Doctor not found",
        },
    )
    def get(self, request, doctor_id):
        try:
            doctor_uuid = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = get_object_or_404(
            Doctor.objects.prefetch_related("availabilities"), doctor_id=doctor_uuid
        )

        availabilities_list = [
            {
                "day_of_week": availability.day_of_week,
                "start_time": availability.start_time.strftime("%H:%M"),
                "end_time": availability.end_time.strftime("%H:%M"),
            }
            for availability in doctor.availabilities.all()
        ]

        days_of_week = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]

        return Response(
            {
                "doctor_name": doctor.first_name,
                "doctor_id": str(doctor.create_id),
                "availabilities": availabilities_list,
                "days_of_week": days_of_week,
            },
            status=200,
        )


class DoctorUpdateApiViewPersonal(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update doctor details",
        request_body=UpdateDoctorSerializer,
        responses={
            200: "Doctor updated successfully",
            400: "Validation error",
            404: "Doctor not found",
        },
    )
    def put(self, request, doctor_id, step):
        try:
            step = int(step)
            if step != 1:
                return Response(
                    {"error": f"Invalid step {step}. Expected step 1."}, status=400
                )
        except ValueError:
            return Response({"error": "Step must be an integer."}, status=400)

        try:
            doctor_id = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        if not doctor:
            print(f"Doctor with ID {doctor_id} not found in the database.")
            return Response({"error": "Doctor not found"}, status=404)
        serializer = UpdateDoctorSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor updated successfully."}, status=200)

        return Response({"errors": serializer.errors}, status=400)


class DoctorUpdateApiViewProfile(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Update doctor details",
        request_body=DoctorUpdateSerializer,
        responses={
            200: "Doctor updated successfully",
            400: "Validation error",
            404: "Doctor not found",
        },
    )
    def put(self, request, doctor_id, step):
        try:
            step = int(step)
            if step != 2:
                return Response(
                    {"error": f"Invalid step {step}. Expected step 2."}, status=400
                )
        except ValueError:
            return Response({"error": "Step must be an integer."}, status=400)

        try:
            doctor_id = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        if not doctor:
            print(f"Doctor with ID {doctor_id} not found in the database.")
            return Response({"error": "Doctor not found"}, status=404)
        serializer = DoctorUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Doctor updated successfully."}, status=200)

        return Response({"errors": serializer.errors}, status=400)


class DoctorUpdateApiViewAvailability(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser,)

    @swagger_auto_schema(
        tags=["Api"],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    "day_of_week": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Day of the week"
                    ),
                    "start_time": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format="time",
                        description="Start time (HH:MM)",
                    ),
                    "end_time": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format="time",
                        description="End time (HH:MM)",
                    ),
                },
                required=["day_of_week", "start_time", "end_time"],
            ),
        ),
        responses={201: "Doctor availability created", 400: "Invalid data"},
    )
    def put(self, request, doctor_id, step):
        try:
            step = int(step)
            if step != 3:
                return Response(
                    {"error": f"Invalid step {step}. Expected step 3."}, status=400
                )
        except ValueError:
            return Response({"error": "Step must be an integer."}, status=400)

        try:
            doctor_id = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        if not doctor:
            print(f"Doctor with ID {doctor_id} not found in the database.")
            return Response({"error": "Doctor not found"}, status=404)
        availability_data = []
        errors = {}

        for item in request.data:
            day = item.get("day_of_week")
            start_time = item.get("start_time")
            end_time = item.get("end_time")

            if day and start_time and end_time:
                availability_data.append(
                    {"day_of_week": day, "start_time": start_time, "end_time": end_time}
                )

        existing_availabilities = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week__in=[item["day_of_week"] for item in availability_data],
        )
        existing_availabilities_map = {
            av.day_of_week: av for av in existing_availabilities
        }

        updated_instances = []

        for item in availability_data:
            day_of_week = item["day_of_week"]

            if day_of_week in existing_availabilities_map:
                instance = existing_availabilities_map[day_of_week]
                serializer = UpdateDoctorAvailabilitySerializer(
                    instance, data=item, partial=True
                )
                if serializer.is_valid():
                    saved_instance = serializer.save()
                    updated_instances.append(saved_instance)
                else:
                    errors[day_of_week] = serializer.errors
            else:
                item["doctor"] = doctor.doctor_id
                serializer = UpdateDoctorAvailabilitySerializer(
                    data=item, context={"request": request}
                )
                if serializer.is_valid():
                    saved_instance = serializer.save()
                    updated_instances.append(saved_instance)
                else:
                    errors[day_of_week] = serializer.errors

        if errors:
            return Response({"success": False, "errors": errors}, status=400)

        return Response(
            {"success": True, "message": "Doctor availability updated successfully"},
            status=200,
        )


class DoctorUpdateApiViewAccount(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update doctor details",
        request_body=DoctorUserNamePasswordSerializer,
        responses={
            200: "Doctor updated successfully",
            400: "Validation error",
            404: "Doctor not found",
        },
    )
    def put(self, request, doctor_id, step):
        try:
            step = int(step)
            if step != 4:
                return Response(
                    {"error": f"Invalid step {step}. Expected step 4."}, status=400
                )
        except ValueError:
            return Response({"error": "Step must be an integer."}, status=400)

        try:
            doctor_id = uuid.UUID(str(doctor_id))
        except ValueError:
            return Response(
                {"error": "Invalid doctor ID format. Must be a valid UUID."}, status=400
            )

        doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
        if not doctor:
            return Response({"error": "Doctor not found"}, status=404)
        serializer = DoctorUserNamePasswordSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            password = request.data.get("password")
            user, created = User.objects.get_or_create(email=doctor.email)
            if created:
                user.username = doctor.user_name
                user.first_name = doctor.first_name
                user.last_name = doctor.last_name
                user.set_password(password)
                user.save()
            if user:
                user.set_password(password)
                user.username = doctor.user_name
                user.save()

            # ✅ Add this return statement to prevent the error
            return Response(
                {"success": True, "message": "Doctor account updated successfully"},
                status=200,
            )


class SingleDoctorView(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, "single_doctor_view.html")
