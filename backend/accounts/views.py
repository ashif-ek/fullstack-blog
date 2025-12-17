from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import check_password
from .models import User

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

def register_view(request):
    """
    Handles new user signup. Shows the form on GET and saves the user on POST.
    Password hashing is done inside the form for safety.
    """
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # safe because RegisterForm hashes the password
            return redirect('login')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """
    Simple login view. Validates credentials and stores user ID in session.
    Compares the raw password with the hashed one for security.
    """
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.filter(email=email).first()

            # check_password handles secure comparison with the hashed password
            if user and check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect('home')

    return render(request, 'login.html', {'form': form})


def home_view(request):
    """
    Basic protected page. Only loads if the user has a valid session.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    return render(request, 'home.html')


def logout_view(request):
    """
    Clears all session data to fully log the user out.
    """
    request.session.flush()
    return redirect('login')


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

