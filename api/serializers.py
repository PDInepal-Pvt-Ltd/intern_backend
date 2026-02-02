from rest_framework import serializers
from .models import Subscriber, Blog, ContactMessage, Internship, InternshipApplication, Task
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
import re
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

user = get_user_model()


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"


class ContactMessageSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

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
                queryset=InternshipApplication.objects.all(),
                fields=['email', 'internship'],
                message="You have already applied for this internship position."
            )
        ]
        extra_kwargs = {
            'cv_file': {'required': True}
        }

    def validate_contact_number(self, value):
        if value:
            return value.replace(" ", "")
        return value


class PasswordSetupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm = attrs.get('confirm_password')

        if not password:
            raise serializers.ValidationError({"password": "This field is required."})
        if not confirm:
            raise serializers.ValidationError({"confirm_password": "This field is required."})

        if password != confirm:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return attrs

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields.pop('username', None)

    def validate(self, attrs):
        
        attrs['username'] = attrs.get('email')
        data = super().validate(attrs)
        if self.user.is_superuser:
            role = "admin"
        elif self.user.is_staff:
            role = "staff"
        elif self.user.applications.exists():
            role = "intern"
        else:
            role = "user"
        
        data['role'] = role 
        data['full_name'] = self.user.first_name
        data['email'] = self.user.email
        return data

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.EmailField(
        source='assigned_to.email', read_only=True)
    assigned_by_name = serializers.CharField(
        source='assigned_by.first_name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'submission_link', 'admin_feedback', 'assigned_to_email',
            'assigned_by_name', 'created_at'
        ]

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date']

    def validate_assigned_to(self, value):
        app = value.applications.first()
        if not app:
            raise serializers.ValidationError("The selected user is not an intern.")
        
        if app.status != 'accepted':
            raise serializers.ValidationError("This intern has not been 'accepted' yet.")
            
        return value

class AdminTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.first_name', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to_email', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.first_name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'assigned_to_name', 'assigned_to_email', 'assigned_by_name',
            'submission_link', 'admin_feedback', 'created_at'
        ]

class TaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['submission_link']

    def update(self, instance, validated_data):
        instance.submission_link = validated_data.get(
            'submission_link', instance.submission_link)
        instance.status = 'completed'
        instance.save()
        return instance

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']

    def validate_assigned_to(self, value):
        app = value.applications.first()
        if not app:
            raise serializers.ValidationError("The selected user is not an intern.")
        
        if app.status != 'accepted':
            raise serializers.ValidationError("This intern has not been 'accepted' yet.")
            
        return value

class TaskReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['admin_feedback', 'status']

class AdminUserListSerializer(serializers.ModelSerializer):
    internship_title = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()
    application_id = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'id', 
            'first_name', 
            'email', 
            'is_staff', 
            'internship_title', 
            'application_status', 
            'application_id'
        ]

    def get_internship_title(self, obj):
        app = obj.applications.first() 
        if app and app.internship:
            return app.internship.title
        return "N/A"

    def get_application_status(self, obj):
        app = obj.applications.first()
        return app.status if app else "N/A"

    def get_application_id(self, obj):
        app = obj.applications.first()
        return app.id if app else None
    
    
