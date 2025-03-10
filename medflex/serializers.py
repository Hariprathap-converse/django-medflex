import re
from datetime import datetime, time

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Doctor, DoctorAvailability


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "username": {
                "required": True,
                "allow_blank": False,
                "error_messages": {
                    "blank": "Username should not be empty.",
                    "required": "Username is required.",
                },
            },
            "email": {
                "required": True,
                "allow_blank": False,
                "error_messages": {
                    "blank": "Email should not be empty.",
                    "required": "Email is required.",
                },
            },
            "password": {
                "required": True,
                "allow_blank": False,
                "error_messages": {
                    "blank": "Password should not be empty.",
                    "required": "Password is required.",
                },
            },
        }

    def validate(self, data):
        required_fields = ["username", "email", "password"]
        errors = {}
        for field in required_fields:
            if field not in data or not str(data.get(field, "")).strip():
                errors[field] = (
                    f"{field.capitalize()} is required and should not be empty."
                )
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 8 or len(value) > 20:
            raise serializers.ValidationError(
                "Password must be between 8 and 20 characters."
            )
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            "blank": "Email should not be empty.",
            "required": "Email is required.",
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": "Password should not be empty.",
            "required": "Password is required.",
        },
    )

    def validate(self, data):
        request = self.context.get("request")
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        errors = {}
        if errors:
            raise serializers.ValidationError(errors)
        user = authenticate(request, email=email, password=password)
        if not user:
            raise serializers.ValidationError(
                {
                    "email": "Invalid email or password.",
                    "password": "Invalid email or password.",
                }
            )

        data["user"] = user
        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ["created_by"]

    def validate_mobile_number(self, value):
        if not re.fullmatch(r"^\+\d{1,14}$|^\d{10,15}$", value):
            raise serializers.ValidationError(
                "Mobile number should be between 10 and 15 digits and may start with '+'."
            )
        return value

    def validate_email(self, value):
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise serializers.ValidationError("Enter a valid email address.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered. Please use a different email."
            )
        return value

    def validate_age(self, value):
        if value <= 22 or value >= 100:
            raise serializers.ValidationError(
                "Age must be greater than 23 and less than 100."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class DoctorUpdateSerializer(serializers.ModelSerializer):
    update_profile = serializers.ImageField(required=False)

    class Meta:
        model = Doctor
        fields = ["update_profile", "bio"]

    def update(self, instance, validated_data):
        instance.update_profile = validated_data.get(
            "update_profile", instance.update_profile
        )
        instance.bio = validated_data.get("bio", instance.bio)
        instance.save()
        return instance


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = "__all__"

    def validate_day_of_week(self, value):
        valid_days = [choice[0] for choice in DoctorAvailability.DaysOfWeek.choices]
        if value not in valid_days:
            raise serializers.ValidationError(
                f"Invalid day_of_week: {value}. Must be one of {valid_days}."
            )
        return value

    @staticmethod
    def fix_time_format(value):

        if isinstance(value, str):
            try:
                value = value.replace(".", ":")
                return datetime.strptime(value, "%H:%M").time()
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid time format: {value}. Use HH:MM format."
                )

        elif isinstance(value, int):
            try:
                value_str = str(value).zfill(4)
                hours, minutes = int(value_str[:2]), int(value_str[2:])
                return time(hours, minutes)
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid time format: {value}. Expected format HHMM (e.g., 930 for 09:30)."
                )

        elif isinstance(value, time):
            return value

        raise serializers.ValidationError(f"Unsupported time format: {value}.")

    def validate_start_time(self, value):
        return self.fix_time_format(value)

    def validate_end_time(self, value):
        return self.fix_time_format(value)

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            doctor_id = request.session.get("doctor_id")
            if not doctor_id:
                raise serializers.ValidationError(
                    {"doctor": "Doctor ID not found in session."}
                )

            doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
            validated_data["doctor"] = doctor

        return DoctorAvailability.objects.create(**validated_data)


class DoctorUserNamePasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Doctor
        fields = ["user_name", "password", "confirm_password"]

    def validate_user_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Username is required and cannot be empty."
            )
        if not re.match(r"^\w+$", value):
            raise serializers.ValidationError(
                "Username must contain only letters, numbers, and underscores."
            )
        return value

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match.",
                    "password": "Passwords do not match.",
                }
            )

        return data

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get("user_name", instance.user_name)

        if "password" in validated_data:
            instance.password = make_password(validated_data["password"])

        instance.save()
        return instance


class UpdateDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        exclude = ["updated_at"]
        read_only_fields = ["created_by"]

    def validate_mobile_number(self, value):
        if not re.fullmatch(r"^\+\d{1,14}$|^\d{10,15}$", value):
            raise serializers.ValidationError(
                "Mobile number should be between 10 and 15 digits and may start with '+'."
            )
        return value

    def validate_email(self, value):
        if (
            self.instance
            and User.objects.filter(email=value).exclude(pk=self.instance.pk).exists()
        ):
            raise serializers.ValidationError(
                "This email is already registered. Please use a different email."
            )
        return value

    def validate_age(self, value):
        if value <= 22 or value >= 100:
            raise serializers.ValidationError(
                "Age must be greater than 23 and less than 100."
            )
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UpdateDoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = "__all__"

    def validate_day_of_week(self, value):
        valid_days = [choice[0] for choice in DoctorAvailability.DaysOfWeek.choices]
        if value not in valid_days:
            raise serializers.ValidationError(
                f"Invalid day_of_week: {value}. Must be one of {valid_days}."
            )
        return value

    @staticmethod
    def fix_time_format(value):
        if isinstance(value, str):
            try:
                value = value.replace(".", ":")
                return datetime.strptime(value, "%H:%M").time()
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid time format: {value}. Use HH:MM format."
                )

        elif isinstance(value, int):
            try:
                value_str = str(value).zfill(4)
                hours, minutes = int(value_str[:2]), int(value_str[2:])
                return time(hours, minutes)
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid time format: {value}. Expected format HHMM (e.g., 930 for 09:30)."
                )

        elif isinstance(value, time):
            return value

        raise serializers.ValidationError(f"Unsupported time format: {value}.")

    def validate_start_time(self, value):
        return self.fix_time_format(value)

    def validate_end_time(self, value):
        return self.fix_time_format(value)

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        return data

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
