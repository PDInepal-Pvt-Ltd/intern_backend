from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import (
    SubscriberSerializer, BlogSerializer, ContactMessageSerializer, 
    InternshipSerializer, InternshipAppSerializer, PasswordSetupSerializer, 
    MyTokenObtainPairSerializer, TaskSerializer, TaskSubmissionSerializer, 
    TaskCreateSerializer, TaskUpdateSerializer, TaskReviewSerializer,
    AdminTaskSerializer, AdminUserListSerializer
    )
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import (
    Subscriber, Blog, ContactMessage, 
    Internship, InternshipApplication, Task
    )
from django.views.decorators.csrf import csrf_exempt
from djangorestframework_camel_case.parser import CamelCaseMultiPartParser, CamelCaseFormParser, CamelCaseJSONParser
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User  
from .permissions import IsIntern, IsAcceptedIntern, IsOwner, IsStaffOrAdmin
import json

User = get_user_model()
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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
        if not (request.user.is_authenticated and request.user.is_staff):
            return Response({"detail": "Admin access required"}, status=403)
        
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


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

        return Response(serializer.errors, status=400)

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
        }, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([CamelCaseJSONParser, CamelCaseFormParser, CamelCaseMultiPartParser])
def setup_password(request):
    print("DEBUG DATA RECEIVED:", request.data)
    serializer = PasswordSetupSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Use __iexact to be safe with Capital Letters
        user = get_object_or_404(User, email__iexact=email)
        
        if user.has_usable_password():
            return Response({"success": False, "message": "Password already set."}, status=400)
        
        user.set_password(password)
        user.is_active = True
        user.save()
        return Response({"success": True, "message": "Password set successfully!"})
    print("SERIALIZER ERRORS:", serializer.errors) 
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsIntern])
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
    queryset = Internship.objects.filter(status='open').exclude(id=application.internship_id)

    serializer = InternshipSerializer(queryset, many=True)
    return Response({
        "status": 200,
        "success": True,
        "data": serializer.data,
    },status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAcceptedIntern])
def intern_task_list(request):
    # Intern views their own assigned tasks
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response({
        "success": True,
        "data": serializer.data
    })

@api_view(['PATCH'])
@permission_classes([IsAcceptedIntern, IsOwner])
def intern_submit_task(request, pk):
    # Intern submits a link for a specific task.
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    
    # Checking to see if already submitted (Optional logic)
    if task.status == 'completed' and task.submission_link:
         return Response({"message": "Task already submitted."}, status=400)

    serializer = TaskSubmissionSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Task submitted successfully.",
            "data": serializer.data
        })
    return Response(serializer.errors, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsStaffOrAdmin])
def admin_assign_task(request):
    """Admin assigns a task to an accepted intern."""
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(assigned_by=request.user) # Set current admin as creator
        return Response({
            "success": True,
            "message": "Task assigned successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsStaffOrAdmin])
def admin_view_tasks(request):
    if request.query_params.get('my_tasks') == 'true':
        tasks = tasks.filter(assigned_by = request.user)

    intern_id = request.query_params.get('intern')
    if intern_id:
        tasks = tasks.filter(assigned_to = intern_id)

    serializer = AdminTaskSerializer(tasks, many = True)
    return Response({
        "success": True,
        "count": tasks.count(),
        "data": serializer.data
    })

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsStaffOrAdmin])
def admin_edit_task(request, pk):
    task = get_object_or_404(Task, pk = pk)
    if request.method == 'DELETE':
        task.delete()
        return Response({
            "status": 200,
            "success": True,
            "message": "Task deleted successfully.",
            "data": []
        }, status=status.HTTP_200_OK)
    
    serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": 200,
            "success": True,
            "message": "Task updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=400)

@api_view(['PATCH'])
@permission_classes([IsStaffOrAdmin])
def admin_review_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskReviewSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": 200,
            "success": True,
            "message": "Feedback updated.",
            "data": serializer.data
        }, status = status.HTTP_200_OK)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsStaffOrAdmin])
def admin_user_manager(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    users = User.objects.all().order_by('-id')

    role = request.query_params.get('role')
    if role == 'intern':
        users = users.filter(application__isnull=False)
    elif role == 'staff':
        users = users.filter(is_staff=True)

    serializer = AdminUserListSerializer(users, many=True)
    return Response({
        "success": True,
        "count": users.count(),
        "data": serializer.data
    })