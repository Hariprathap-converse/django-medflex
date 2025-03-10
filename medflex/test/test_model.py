from datetime import time
from django.utils import timezone
import uuid

import pytest
from django.core.exceptions import ValidationError

from medflex.models import Doctor, DoctorAvailability


@pytest.mark.django_db
def test_doctor_creation(create_doctor):
    assert create_doctor.first_name == "John"
    assert create_doctor.last_name == "Doe"
    assert create_doctor.age == 35
    assert create_doctor.gender == Doctor.GenderChoices.MALE
    assert create_doctor.create_id == "DOC12345"
    assert create_doctor.email == "john.doe@example.com"
    assert create_doctor.mobile_number == "9876543210"
    assert create_doctor.qualification == "MBBS"
    assert create_doctor.designation == Doctor.DesignationChoices.DOCTOR
    assert create_doctor.blood_group == "O+"
    assert create_doctor.address == "123 Street, NY"
    assert create_doctor.city == "NYC"
    assert create_doctor.postal_code == "10001"


@pytest.mark.django_db
def test_doctor_id_is_uuid(create_doctor):
    assert isinstance(create_doctor.doctor_id, uuid.UUID)


@pytest.mark.django_db
def test_doctor_str_method(create_doctor):
    assert str(create_doctor) == "John Doe - doctor"


@pytest.mark.django_db
def test_unique_email_constraint(create_doctor):
    with pytest.raises(Exception):
        Doctor.objects.create(
            first_name="Duplicate",
            last_name="Email",
            age=45,
            gender=Doctor.GenderChoices.MALE,
            create_id="DOC99999",
            email="john.doe@example.com",
            mobile_number="1234567890",
        )


@pytest.mark.django_db
def test_unique_mobile_number_constraint(create_doctor):
    with pytest.raises(Exception):
        Doctor.objects.create(
            first_name="Bob",
            last_name="Brown",
            age=37,
            gender=Doctor.GenderChoices.MALE,
            create_id="DOC88888",
            email="bob@example.com",
            mobile_number="9876543210",
        )


@pytest.mark.django_db
def test_null_optional_fields():
    doctor = Doctor.objects.create(
        first_name="Lisa",
        last_name="Ray",
        age=30,
        gender=Doctor.GenderChoices.FEMALE,
        create_id="DOC99999",
        email="lisa.ray@example.com",
        mobile_number="5554443333",
    )
    assert doctor.marital_status is None
    assert doctor.qualification is None
    assert doctor.designation is None
    assert doctor.address is None


@pytest.mark.django_db
def test_invalid_option_gender():

    doctor = Doctor.objects.create(
        first_name="Bob",
        last_name="Brown",
        age=37,
        gender="Other",
        create_id="DOC88888",
        email="bob@example.com",
        mobile_number="9876543210",
        blood_group="A+",
    )
    with pytest.raises(ValidationError):
        doctor.full_clean()


@pytest.mark.django_db
def test_invalid_option_designation():

    doctor = Doctor.objects.create(
        first_name="Bob",
        last_name="Brown",
        age=37,
        gender=Doctor.GenderChoices.MALE,
        designation="Teacher",
        create_id="DOC88888",
        email="bob@example.com",
        mobile_number="9876543210",
        blood_group="A+",
    )
    with pytest.raises(ValidationError):
        doctor.full_clean()


@pytest.mark.django_db
def test_invalid_option_marital_status():

    doctor = Doctor.objects.create(
        first_name="Bob",
        last_name="Brown",
        age=37,
        gender=Doctor.GenderChoices.MALE,
        marital_status="single",
        create_id="DOC88888",
        email="bob@example.com",
        mobile_number="9876543210",
        blood_group="A+",
    )
    with pytest.raises(ValidationError):
        doctor.full_clean()


@pytest.mark.django_db
def test_doctor_availability_creation(create_doctor_availability,create_doctor):
   
    assert create_doctor_availability.doctor == create_doctor
    assert create_doctor_availability.day_of_week == "monday"
    assert create_doctor_availability.start_time == time(9, 0)
    assert create_doctor_availability.end_time == time(17, 0)
    assert create_doctor_availability.created_at is not None
    assert create_doctor_availability.updated_at is  None

@pytest.mark.django_db
def test_invalid_day_of_week(create_doctor):
  

        availability= DoctorAvailability.objects.create(
            doctor=create_doctor,
            day_of_week="invalid_day", 
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        with pytest.raises(ValidationError):
            availability.full_clean()

@pytest.mark.django_db
def test_invalid_type_start_time(create_doctor):
  
    with pytest.raises(TypeError):
        DoctorAvailability.objects.create(
            doctor=create_doctor,
            day_of_week=DoctorAvailability.DaysOfWeek.MONDAY, 
            start_time=time("12", 0),
            end_time=time(17, 0)
        )

@pytest.mark.django_db
def test_invalid_start_time(create_doctor):
    with pytest.raises(ValueError):
        DoctorAvailability.objects.create(
            doctor=create_doctor,
            day_of_week=DoctorAvailability.DaysOfWeek.MONDAY, 
            start_time=time(34, 0),
            end_time=time(17, 0)
        )

@pytest.mark.django_db
def test_invalid_type_end_time(create_doctor):
    with pytest.raises(TypeError):
        DoctorAvailability.objects.create(
            doctor=create_doctor,
            day_of_week=DoctorAvailability.DaysOfWeek.MONDAY, 
            start_time=time(12, 0),
            end_time=time("12", 0)
        )
       
@pytest.mark.django_db
def test_invalid_end_time(create_doctor):
    with pytest.raises(ValueError):
        DoctorAvailability.objects.create(
            doctor=create_doctor,
            day_of_week=DoctorAvailability.DaysOfWeek.MONDAY, 
            start_time=time(12, 0),
            end_time=time(26, 0)
        )


@pytest.mark.django_db
def test_doctor_availability__str_method(create_doctor_availability):
    assert str(create_doctor_availability) == "John - monday (09:00:00 - 17:00:00)"

@pytest.mark.django_db
def test_update_doctor_availability_changes_updated_at(create_doctor_availability):
   
    updated_at=create_doctor_availability.updated_at
    create_doctor_availability.start_time = time(10, 0)
    create_doctor_availability.save()

    assert create_doctor_availability.updated_at is not None
    assert create_doctor_availability.updated_at > updated_at if updated_at else True

@pytest.mark.django_db
def test_updated_at_not_set_when_no_changes(create_doctor_availability):

    updated_at=create_doctor_availability.updated_at
    create_doctor_availability.save()
    assert create_doctor_availability.updated_at == updated_at 

@pytest.mark.django_db
def test_updated_at_invalid_type(create_doctor_availability):
    with pytest.raises(ValidationError):
        create_doctor_availability.updated_at="1212"
        create_doctor_availability.save()

   