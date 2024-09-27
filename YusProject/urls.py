"""
URL configuration for YusProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from YusApp import views
from django.contrib import admin  # <-- Add this import for the admin site
from django.shortcuts import redirect  # <-- Add this import for redirecting
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('file-issue/', views.file_issue_view, name='file_issue'),
    path('recommendation/<str:ticket_id>/', views.ticket_recommendation_view, name='ticket_recommendation'),
    path('recommendation/<str:ticket_id>/<str:predicted_priority>/', views.ticket_recommendation_view, name='ticket_recommendation'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('feedback-form/', views.feedback_form, name='feedback_form'),  # Feedback Form URL
    #path('feedback-form/', views.feedback_view, name='feedback_form'),
    path('', lambda request: redirect('login')),  # Redirect root URL to login page
    path('helpdesk-dashboard/', views.feedback_sentiment_view, name='admin_dashboard'),
    path('employee-register/', views.register_employee, name='register_employee'),
    path('employee-success/', views.employee_success, name='employee_success'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('employee-logout/', views.employee_logout, name='employee_logout'),
]