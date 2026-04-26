"""
accounts/views.py

Topic 6.2 – Session Management (login / logout / session creation + termination)
Topic 6.4 – RBAC (role-check before redirect)
Topic 6.5 – Login protection (simple brute-force lockout via session counter)
"""

from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.forms import LoginForm, RegisterForm

# Max failed attempts before temporary lockout (Topic 6.5)
MAX_FAILED_ATTEMPTS = 5


def login_view(request):

    if request.user.is_authenticated:
        return redirect('ngo:activity_list')

    # Read or initialise the failure counter stored in the session
    failed = request.session.get('login_failed_attempts', 0)

    if failed >= MAX_FAILED_ATTEMPTS:
        messages.error(
            request,
            f'Too many failed login attempts. Please contact an administrator.'
        )
        return render(request, 'accounts/login.html', {'form': LoginForm(request), 'locked': True})

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Topic 6.2 – session creation happens here
            login(request, user)
            # Reset failure counter on success
            request.session['login_failed_attempts'] = 0
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('ngo:activity_list')
        else:
            # Increment counter and persist in session
            request.session['login_failed_attempts'] = failed + 1
            remaining = MAX_FAILED_ATTEMPTS - (failed + 1)
            if remaining > 0:
                messages.error(
                    request,
                    f'Invalid username or password. {remaining} attempt(s) remaining.'
                )
            else:
                messages.error(request, 'Account locked due to too many failed attempts.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
  
    logout(request)                        # destroys the server-side session
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('ngo:activity_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Topic 6.2 – log the new user straight in (creates session)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Account created.')
            return redirect('ngo:activity_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
