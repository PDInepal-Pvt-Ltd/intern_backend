from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from api.serializers import SubscriberSerializer, BlogSerializer, ContactMessageSerializer, InternshipSerializer
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Subscriber, Blog, ContactMessage, Internship
import json
from django.views.decorators.csrf import csrf_exempt


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


@api_view(['GET', 'POST'])
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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
