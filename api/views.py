from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import SubscriberSerializer, BlogSerializer, ContactMessageSerializer, InternshipSerializer, InternshipAppSerializer, PasswordSetupSerializer
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Subscriber, Blog, ContactMessage, Internship, InternshipApplication
from django.views.decorators.csrf import csrf_exempt
from djangorestframework_camel_case.parser import CamelCaseMultiPartParser, CamelCaseFormParser
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User  
from rest_framework import status
import json

def PravidhiView(request):
    return render(request, 'index.html')


@csrf_exempt
@api_view(['GET', 'POST'])
def subscribe(request):
    if request.method == "GET":
        emails = Subscriber.objects.all()
        serializer = SubscriberSerializer(emails, many=True)
        return JsonResponse({'data': serializer.data})

    elif request.method == "POST":

        email = request.data.get('email')
        # data = json.loads(request.body)
        # email = data.get("email")

        if not email:
            return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format!"}, status=status.HTTP_400_BAD_REQUEST)

        if Subscriber.objects.filter(email=email).exists():
            return Response({"error": "This email is already subscribed!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscriber = Subscriber.objects.create(email=email)
            email_sent = send_welcome_subscription(email)

            return Response({
                "success": True,
                "message": "Thank you for subscribing! Welcome email has been sent.",
                "data": {
                    "email": email,
                    "subscribed_at": subscriber.created_at
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log the actual error for debugging
            print(f"Subscription error for {email}: {str(e)}")
            return Response({
                "error": "Something went wrong. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_welcome_subscription(email):
    """
    Send welcome email to new subscriber
    """
    context = {
        'email': email,
        'website_url': 'http://localhost:8000',
        'unsubscribe_link': f'http://localhost:8000/unsubscribe/?email={email}'
    }

    html_content = render_to_string(
        'emails/welcome_subscription.html', context)
    text_content = render_to_string('emails/welcome_subscription.txt', context)

    subject = 'Welcome to Pravidhi Newsletter! 🎉'

    email_msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.REPLY_TO_EMAIL] if hasattr(
            settings, 'REPLY_TO_EMAIL') else None,
    )

    email_msg.attach_alternative(html_content, "text/html")
    return email_msg.send()


@api_view(['GET', 'POST'])
def blog_list(request):
    if request.method == 'GET':
        blogs = Blog.objects.order_by('-date_created_at')
        serializer = BlogSerializer(blogs, many=True)
        return Response({
            "status": 200,
            "success": True,
            "message": "The blogs list is fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({
                "status": 403,
                "success": False,
                "message": "You are not authorized to perform this action",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "success": True,
                "message": "The blog was created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": 400,
            "success": False,
            "message": "Invalid data",
            "data": serializer.data
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == 'GET':
        serializer = BlogSerializer(blog)
        return Response({
            "status": 200,
            "success": True,
            "message": "Blog detail fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # for admin control
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({
            "status": 403,
            "success": False,
            "message": "You are not authorized to perform this action",
            "data": []
        }, status=status.HTTP_403_FORBIDDEN)

    # for update or patch
    if request.method in ['PUT', 'PATCH']:
        serializer = BlogSerializer(
            blog,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "success": True,
                "message": "Blog updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": 400,
            "success": False,
            "message": "Invalid data",
            "data": serializer.data
        }, status=status.HTTP_400_BAD_REQUEST)

    # for deleting the blogs
    if request.method == 'DELETE':
        blog.delete()
        return Response({
            "status": 200,
            "success": True,
            "message": "Blog deleted successfully",
            "data": []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_contact(request):
    serializer = ContactMessageSerializer(data=request.data)

    # if request.method == 'GET':
    #     contacts = get_object_or_404(pk = pk)
    #     serializer = ContactMessageSerializer(contacts)
    #     return Response({
    #         "status": 200,
    #         "success": True,
    #         "message": "The list of the contacted form is shown successfully",
    #         "data": serializer.data
    #     })

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": 201,
            "success": True,
            "message": "The request was submitted successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "success": False,
        "message": "Validation failed.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def internship_list(request):
    if request.method == 'GET':
        internships = Internship.objects.all().order_by('-created_at')
        serializer = InternshipSerializer(internships, many=True)
        return Response({
            "status": 200,
            "success": True,
            "message": "The internship is shown successfully",
            "data": serializer.data
        })

    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({
                "status": 403,
                "success": False,
                "message": "You are not authorized to perform this action",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = InternshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "success": True,
                "message": "Internship created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": 400,
            "success": False,
            "message": "Invalid data",
            "data": serializer.data
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def internship_detail(request, pk):
    internship = get_object_or_404(Internship, pk=pk)

    if request.method == 'GET':
        serializer = InternshipSerializer(internship)
        return Response({
            "status": 200,
            "success": True,
            "message": "Internship fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # admin le garni kam
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response({
            "status": 403,
            "success": False,
            "message": "You are not authorized to perform this action",
            "data": []
        }, status=status.HTTP_403_FORBIDDEN)

    # update
    if request.method in ['PUT', 'PATCH']:
        serializer = InternshipSerializer(
            internship,
            data=request.data,
            partial=(request.method == 'PATCH')
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 200,
                "success": True,
                "message": "Internship updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": 400,
            "success": False,
            "message": "Invalid data",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_rEQUEST)

    # delete ko lagi
    if request.method == 'DELETE':
        internship.delete()
        return Response({
            "status": 200,
            "success": True,
            "message": "Internship deleted successfully",
            "data": []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([CamelCaseMultiPartParser, CamelCaseFormParser])
def create_internship_application(request):

    serializer = InternshipAppSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            with transaction.atomic():
                email = serializer.validated_data['email']
                full_name = serializer.validated_data['full_name']

                user = User.objects.filter(email=email).first()

                internship = get_object_or_404(
                    Internship,
                    id=serializer.validated_data['internship'].id
                )

                if internship.available_seats <= 0:
                    return Response({
                        "success": False,
                        "message": "This internship is full."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if user and hasattr(user, 'application'):
                    return Response({
                        "success": False,
                        "message": "You have already applied with this email."
                    }, status=status.HTTP_400_BAD_REQUEST)

                if not user:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=full_name,
                        is_active=False
                    )

                # Saves the application and links it to the newly created user
                application = serializer.save(user=user)

                return Response({
                    "status": 201,
                    "success": True,
                    "message": "Application submitted! Now, please set your password.",
                    "data": {
                        "email": user.email,
                        "user_id": user.id,
                        "requires_password_setup": True  # Nirdosh will use this to redirect
                    }
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "success": False,
        "message": "Validation failed.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def setup_password(request):
    serializer = PasswordSetupSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        password = serializer.validated_data['password']

        user = get_object_or_404(User, id=user_id)
        # to check whether the user has the password to prevent overwriting
        if user.has_usable_password():
            return Response({
                'success': False,
                "message": "Password has already been set for this account."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # now setting password and activating user
        user.set_password(password)
        user.is_active=True
        user.save()
        return Response({
            "status": 200,
            "success": True,
            "message": "Password is set successfully! You can login now.",
            "data": {
                "email": user.email
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        "status": 400,
        "success": False,
        "message": "Validation Failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_application_status(request):
    try: 
        application = request.user.application
        data = {
            "internship": application.internship.title,
            "status": application.status,
            "applied_at": application.applied_at,
        }
        return Response({
            "status": 200,
            "success": True,
            "message": "Your application status fetched successfully",
            "data": data
        }, status= status.HTTP_200_OK)
    
    except InternshipApplication.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "You haven't applied for any internship yet.",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_internship(request):
    application = getattr(request.user, 'application', None)
    queryset = Internship.objects.filter(status='open')

    if application:
        queryset = queryset.exclude(id = application.internship_id)

    serializer = InternshipSerializer(queryset, many=True)
    return Response({
        "status": 200,
        "success": True,
        "data": serializer.data,
    },status=status.HTTP_200_OK)
