from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from api.serializers import SubscriberSerializer, BlogListSerializer, BlogDetailSerializer, ContactMessageSerializer
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Subscriber, Blog, ContactMessage
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
    
    html_content = render_to_string('emails/welcome_subscription.html', context)
    text_content = render_to_string('emails/welcome_subscription.txt', context)
    
    subject = 'Welcome to Pravidhi Newsletter! 🎉'
    
    email_msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.REPLY_TO_EMAIL] if hasattr(settings, 'REPLY_TO_EMAIL') else None,
    )
    
    email_msg.attach_alternative(html_content, "text/html")
    return email_msg.send()

@api_view(['GET'])
def blog_list(request):
    blogs = Blog.objects.order_by('-date_created_at')
    serializer = BlogListSerializer(blogs, many=True)
    return Response(serializer.data)
    
    
@api_view(['GET'])
def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    serializer = BlogDetailSerializer(blog)
    return Response(serializer.data)

@api_view(['POST'])
def create_contact(request):
    serializer = ContactMessageSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "The request was submitted successfully."},
            status = status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)









        

