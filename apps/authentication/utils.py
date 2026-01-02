import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, subject="Email Verification OTP"):
    message = f"Your OTP for verification is: {otp}. It will expire in 10 minutes."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
