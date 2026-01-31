from rest_framework import serializers
from .models import Subscriber, Blog, ContactMessage, Internship, InternshipApplication
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.password_validation import validate_password
import re


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = "__all__"

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"

class ContactMessageSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required = True)
    class Meta:
        model = ContactMessage
        fields = (
            'id',
            'name',
            'email',
            'phone',
            'address',
            'subject',
            'message',
            'created_at',
            'status',
        )
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        pattern = r'^\+977\d{10}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Phone number must start with +977 and must be of 10 digits."
            )
        return value
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Messages must be at least a sentence and more than 10 characters long as possible."
            )
        return value

class InternshipSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Internship
        fields = [
            'id',
            'title',
            'description',
            'image',
            'total_seats',
            'available_seats'
        ]
        read_only_fields = ['id', 'created_by']

class InternshipAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ['user', 'status']

        validators = [
            UniqueTogetherValidator(
                queryset = InternshipApplication.objects.all(),
                fields = ['email', 'internship'],
                message = "You have already applied for this internship position."
            )
        ]
        extra_kwargs = {
            'cv_file': {'required': True}
        }

    def validate_contact_number(self, value):
        if value:
            return value.replace(" ", "")
        return value
    
class PasswordSetupSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    password = serializers.CharField(
        write_only = True,
        required = True,
        validators = [validate_password]
    )
    confirm_password = serializers.CharField(
        write_only = True,
        required = True
    )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords fields didn't match."})
        return attrs