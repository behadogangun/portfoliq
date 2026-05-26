from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('login')


@login_required
def profile(request):
    from portfolio.models import Portfolio, Asset, Transaction
    portfolios = Portfolio.objects.filter(user=request.user)
    total_assets = Asset.objects.filter(portfolio__user=request.user).count()
    total_transactions = Transaction.objects.filter(asset__portfolio__user=request.user).count()
    total_value = sum(p.total_value() for p in portfolios)
    total_cost = sum(sum(a.total_cost() for a in p.assets.all()) for p in portfolios)
    total_pl = total_value - total_cost
    total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0

    context = {
        'portfolios_count': portfolios.count(),
        'total_assets': total_assets,
        'total_transactions': total_transactions,
        'total_value': total_value,
        'total_pl': total_pl,
        'total_pl_percent': total_pl_percent,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif new != confirm:
            messages.error(request, 'New passwords do not match.')
        elif len(new) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully!')
        return redirect('profile')
    return redirect('profile')