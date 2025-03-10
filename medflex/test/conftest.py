from datetime import time
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from medflex.models import Doctor, DoctorAvailability
from medflex.views import User
from PIL import Image


@pytest.fixture
def doctor_instance():
    return Doctor.objects.create(
        first_name="John",
        last_name="Doe",
        age=40,
        gender="male",
        create_id="DOC123",
        email="doctor@example.com",
        mobile_number="1234567890",
        blood_group="O+",
    )


@pytest.fixture()
def generate_test_image():
    image = Image.new("RGB", (100, 100), "white")
    img_io = io.BytesIO()
    image.save(img_io, format="JPEG")
    img_io.seek(0)
    return SimpleUploadedFile("profile.jpg", img_io.read(), content_type="image/jpeg")


@pytest.fixture()
def valid_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "gender": "male",
        "create_id": "121",
        "email": "john@example.com",
        "mobile_number": "9384904893",
        "marital_status": "married",
        "qualification": "MBA",
        "designation": "doctor",
        "blood_group": "A+",
        "address": "123 Street",
        "country": "USA",
        "state": "California",
        "city": "Los Angeles",
        "postal_code": "90001",
        "bio": "Experienced doctor",
    }


@pytest.fixture
def create_user():
    return User.objects.create(username="admin", email="admin@example.com")


@pytest.fixture
def create_doctor(create_user):
    return Doctor.objects.create(
        first_name="John",
        last_name="Doe",
        age=35,
        gender=Doctor.GenderChoices.MALE,
        create_id="DOC12345",
        email="john.doe@example.com",
        mobile_number="9876543210",
        marital_status=Doctor.MaritalStatusChoices.UNMARRIED,
        qualification="MBBS",
        designation=Doctor.DesignationChoices.DOCTOR,
        blood_group="O+",
        address="123 Street, NY",
        country="USA",
        state="New York",
        city="NYC",
        postal_code="10001",
        created_by=create_user,
    )

@pytest.fixture
def create_doctor_availability(create_doctor):
    availability = DoctorAvailability.objects.create(
        doctor=create_doctor,
        day_of_week=DoctorAvailability.DaysOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(17, 0)
    )
    return availability
