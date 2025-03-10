from unittest.mock import MagicMock, patch

import pytest

from medflex.models import DoctorAvailability, User
from medflex.serializers import DoctorAvailabilitySerializer, DoctorSerializer, DoctorUpdateSerializer, DoctorUserNamePasswordSerializer, LoginSerializer, PasswordResetSerializer, SignupSerializer


@pytest.mark.django_db
def test_doctor_serializer_valid_data(valid_data):
    """Test DoctorSerializer with valid data"""
    user = User.objects.create(username="testuser", email="user@example.com")
    serializer = DoctorSerializer(
        data=valid_data, context={"request": MagicMock(user=user)}
    )
    assert serializer.is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        (
            {"marital_status": "single"},
            "marital_status",
            '"single" is not a valid choice.',
        ),
        ({"designation": "Doctor"}, "designation", '"Doctor" is not a valid choice.'),
        ({"gender": ""}, "gender", '"" is not a valid choice.'),
        ({"gender": None}, "gender", "This field may not be null."),
        ({"create_id": ""}, "create_id", "his field may not be blank."),
        ({"create_id": None}, "create_id", "This field may not be null."),
        ({"first_name": ""}, "first_name", "This field may not be blank."),
        ({"first_name": None}, "first_name", "This field may not be null."),
        ({"last_name": ""}, "last_name", "This field may not be blank."),
        ({"last_name": None}, "last_name", "This field may not be null."),
        ({"email": "samgmail.com"}, "email", "Enter a valid email address."),
        ({"email": 432432643926492464}, "email", "Enter a valid email address."),
        ({"email": ""}, "email", "This field may not be blank."),
        ({"email": None}, "email", "This field may not be null."),
        ({"mobile_number": ""}, "mobile_number", "This field may not be blank."),
        ({"mobile_number": None}, "mobile_number", "This field may not be null."),
        ({"blood_group": ""}, "blood_group", "This field may not be blank."),
        ({"blood_group": None}, "blood_group", "This field may not be null."),
        ({"age": 3}, "age", "Age must be greater than 23 and less than 100"),
        ({"age": 300}, "age", "Age must be greater than 23 and less than 100"),
        ({"age": "23q"}, "age", "A valid integer is required."),
        ({"age": None}, "age", "This field may not be null."),
        ({"age": ""}, "age", "A valid integer is required."),
    ],
)
def test_doctor_serializer_invalid_data(
    invalid_data, expected_field, expected_error, valid_data
):

    valid_data.update(invalid_data)
    serializer = DoctorSerializer(data=valid_data)
    assert not serializer.is_valid()
    error_message = serializer.errors.get(expected_field, [])[0]
    assert expected_error in str(error_message)


@pytest.mark.django_db
def test_doctor_serializer_invalid_age():
    data = {"age": 20}
    serializer = DoctorSerializer(data=data)
    assert not serializer.is_valid()
    assert "age" in serializer.errors


@pytest.mark.django_db
def test_doctor_serializer_invalid_email():
    data = {"email": "invalid-email"}
    serializer = DoctorSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_doctor_serializer_duplicate_email():
    User.objects.create(username="existinguser", email="existing@example.com")
    data = {"email": "existing@example.com"}
    serializer = DoctorSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_doctor_serializer_invalid_mobile():
    data = {"mobile_number": "123"}
    serializer = DoctorSerializer(data=data)
    assert not serializer.is_valid()
    assert "mobile_number" in serializer.errors


@pytest.mark.django_db
def test_doctor_update_valid_serializer(doctor_instance, generate_test_image):
    data = {"bio": "Updated doctor bio", "update_profile": generate_test_image}
    serializer = DoctorUpdateSerializer(doctor_instance, data, partial=True)
    assert serializer.is_valid()
    updated_doctor = serializer.save()
    assert updated_doctor.bio == "Updated doctor bio"
    assert updated_doctor.update_profile is not None


@pytest.mark.django_db
def test_doctor_bio_update_serializer(doctor_instance):
    data = {"bio": "Updated doctor bio"}
    serializer = DoctorUpdateSerializer(doctor_instance, data, partial=True)

    assert serializer.is_valid()
    updated_doctor = serializer.save()
    assert updated_doctor.bio == "Updated doctor bio"


@pytest.mark.django_db
def test_doctor_profile_update_serializer(doctor_instance, generate_test_image):
    data = {
        "update_profile": generate_test_image,
    }
    serializer = DoctorUpdateSerializer(doctor_instance, data, partial=True)
    assert serializer.is_valid()
    updated_doctor = serializer.save()
    assert updated_doctor.update_profile is not None


@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        (
            {"update_profile": "profile.jpg"},
            "update_profile",
            "The submitted data was not a file. Check the encoding type on the form.",
        ),
        (
            {"update_profile": 1223434343434},
            "update_profile",
            "The submitted data was not a file. Check the encoding type on the form.",
        ),
        ({"update_profile": None}, "update_profile", "This field may not be null."),
    ],
)
@pytest.mark.django_db
def test_doctor_profile_update_invalid_serializer(
    doctor_instance, invalid_data, expected_field, expected_error
):
    serializer = DoctorUpdateSerializer(doctor_instance, invalid_data, partial=True)
    assert not serializer.is_valid()
    assert serializer.errors[expected_field][0] == expected_error

@pytest.mark.django_db
def test_doctor_valid_available_success():
    request=MagicMock()
    request.session.get.return_value = 1  # Mock doctor_id from session

    availability_data = [
        {
            "day_of_week": DoctorAvailability.DaysOfWeek.MONDAY,
            "start_time": "09:00",
            "end_time": "17:00",
        },
        {
            "day_of_week": DoctorAvailability.DaysOfWeek.TUESDAY,
            "start_time": "10:00",
            "end_time": "15:00",
        },
    ]

    serializer = DoctorAvailabilitySerializer(
        data=availability_data, many=True, context={"request": request}
    )
    assert serializer.is_valid()

@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        (
           "09:00b",
            "start_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        (
           "",
            "start_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        (
           121212,
            "start_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        
        (
           "09:00b",
            "end_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        (
           "",
            "end_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        (
           1222111,
            "end_time",
            'Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]].',
        ),
        (
           "Monday",
            "day_of_week",
            '"Monday" is not a valid choice.',
        ),
        (
           "",
            "day_of_week",
            "Invalid day_of_week: . Must be one of ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']."
        ),
        
       
    ],
)
@pytest.mark.django_db
def test_doctor_available_invalid_data(invalid_data,expected_field,expected_error):
    request=MagicMock()
    request.session.get.return_value = 1  

    availability_data = [
        {
            "day_of_week": DoctorAvailability.DaysOfWeek.MONDAY,
            "start_time":"09:00",
            "end_time": "17:00",
        }
    ]
    availability_data[0][expected_field]=invalid_data

    serializer = DoctorAvailabilitySerializer(
        data=availability_data, many=True, context={"request": request}
    )
    assert not serializer.is_valid()
    serializer.errors
    errors = serializer.errors[0]  
    error_message = errors.get(expected_field, [])[0]  
    # print('error_message: ', error_message)
    assert error_message==expected_error

@pytest.mark.django_db
def test_doctor_user_name_password_serializer_valid_data(doctor_instance):
  
    data={
        "user_name":"dasswxa12",
        "password":"Z_A007@passkey",
        "confirm_password":"Z_A007@passkey"
    }

    serializer=DoctorUserNamePasswordSerializer(doctor_instance,data)
    assert serializer.is_valid()

@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        (
          {"user_name":"aaa12@"},
          "user_name",
            'Username must contain only letters, numbers, and underscores.',
        ),
        (
          {"user_name":"AAAA12@"},
          "user_name",
            'Username must contain only letters, numbers, and underscores.',
        ),
        (
          {"password":""},
          "password",
            'Password must be at least 8 characters long.',
        ),
        (
          {"password":"qwwqq"},
          "password",
            'Password must be at least 8 characters long.',
        ),
        (
          {"password":111111111111111},
          "password",
            'Password must contain at least one uppercase letter.',
        ),
        (
          {"password":"SDWSDSDD"},
          "password",
            'Password must contain at least one lowercase letter.',
        ),
        (
          {"password":"aaaaaaaaaaaaa"},
          "password",
            'Password must contain at least one uppercase letter.',
        ),
        (
          {"password":"WSAX@"},
          "password",
            'Password must be at least 8 characters long.',
        ),
        (
          {"password":"@@@@@@@@@@@"},
          "password",
            'Password must contain at least one uppercase letter.',
        ),
        (
          {"password":"A_Z@333_4as_2001"},
          "password",
            'Passwords do not match.',
        ),
        (
          {"confirm_password":"A_Z@333_4as_2001"},
          "confirm_password",
            'Passwords do not match.',
        ),

       
    ],
)
@pytest.mark.django_db
def test_doctor_user_name_password_serializer_invalid_data(doctor_instance,invalid_data,expected_field,expected_error):
  
    data={
        "user_name":"CDN00S50",
        "password":"Z_A007@passkey",
        "confirm_password":"Z_A007@passkey"
    }
    data.update(invalid_data)
    serializer=DoctorUserNamePasswordSerializer(doctor_instance,data)
    assert not serializer.is_valid()
    error_message = serializer.errors
    assert error_message[expected_field][0]==expected_error
    
@pytest.mark.django_db
def test_signup_serializer_valid_data():
    data={
        "username":"AS000S50",
        "password":"A_ZPass007@1!",
        "email":"uses@gmail.com"

    }
    serializer=SignupSerializer(data=data)
   
    assert  serializer.is_valid()


@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        ({"username":""},"username","Username should not be empty."),
        ({"username":None},"username","This field may not be null."),
        ({"password":"@@@@@@@@@@"},"password","Password must contain at least one uppercase letter."),
        ({"password":"aaaaaaaaaaa"},"password","Password must contain at least one uppercase letter."),
        ({"password":"AAAAAAAAAAA"},"password","Password must contain at least one lowercase letter."),
        ({"password":"11111111111"},"password","Password must contain at least one uppercase letter."),
        ({"password":111111111111},"password","Password must contain at least one uppercase letter."),
        ({"password":None},"password","This field may not be null."),
        ({"password":"qw22@"},"password","Password must be between 8 and 20 characters."),
        ({"password":""},"password","Password should not be empty."),
        ({"email":"aaaaaaaaaaaa"},"email","Enter a valid email address."),
        ({"email":"user@.com"},"email","Enter a valid email address."),
        ({"email":"usergmail.com"},"email","Enter a valid email address."),
        ({"email":None},"email","This field may not be null."),
        ({"email":""},"email","Email should not be empty."), 
    ],
)
@pytest.mark.django_db
def test_signup_serializer_invalid_data(invalid_data,expected_field,expected_error):
    data={
        "username":"AS000S50",
        "password":"A_ZPass007@1!",
        "email":"uses@gmail.com"
    }
    data.update(invalid_data)
    serializer=SignupSerializer(data=data)
    assert  not serializer.is_valid()
    error_message = serializer.errors
    assert error_message[expected_field][0]==expected_error

@pytest.mark.django_db
def test_login_serializer_authenticate_success():
    """Test case where authentication is successful"""
    with patch("medflex.serializers.authenticate", return_value=True):
        serializer = LoginSerializer(data={"email": "test@example.com", "password": "password123"})
        assert serializer.is_valid() 

@pytest.mark.parametrize(
    "invalid_data, expected_field, expected_error",
    [
        ({"password":""},"password","Password should not be empty."),
        ({"email":""},"email","Email should not be empty."),
        ({"password":None},"password","This field may not be null."),
        ({"email":None},"email","This field may not be null."),
        ({"email":"usergmail.com"},"email","Enter a valid email address."),
        ({"email":"user@gmail"},"email","Enter a valid email address."),
       
    ],
)
@pytest.mark.django_db
def test_login_serializer_authenticate_success(invalid_data,expected_field,expected_error):
    with patch("medflex.serializers.authenticate", return_value=True):
        data={"email": "user@gmail.com", "password": "A_ZPass007@1!"}
        data.update(invalid_data)
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid() 
        error_message = serializer.errors
        assert error_message[expected_field][0]==expected_error

@pytest.mark.django_db
def test_password_reset_serializer_valid_data():
    data={
        "email":"user@gmail.com"
    }
    serializer=PasswordResetSerializer(data=data)
    assert serializer.is_valid()

@pytest.mark.parametrize(
        "invalid_data, expected_field, expected_error" ,[
            ({ "email":""},"email","This field may not be blank."),
            ({ "email":None},"email","This field may not be null."),
            ({ "email":"user"},"email","Enter a valid email address."),
            ({ "email":"usergmail.com"},"email","Enter a valid email address."),
            ({ "email":"user@mail"},"email","Enter a valid email address."),
        ]
)
@pytest.mark.django_db
def test_password_reset_serializer_invalid_data(invalid_data, expected_field, expected_error):
    data={
        "email":"user@gmail.com"
    }
    data.update(invalid_data)
    serializer=PasswordResetSerializer(data=data)
    assert not serializer.is_valid()
    error_message = serializer.errors
    assert error_message[expected_field][0]==expected_error