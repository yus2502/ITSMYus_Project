from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserFeedback

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = UserFeedback
        fields = ['helpfulness_rating', 'comment']

#==========================================================================================
#=========================================ADMIN=================================================
from .models import Employee

class EmployeeRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'employee_id', 'email', 'password']

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('An employee with this ID already exists.')
        return employee_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email=email).exists():
            raise forms.ValidationError('An employee with this email already exists.')
        return email

class EmployeeLoginForm(forms.Form):
    employee_id = forms.CharField(max_length=10, label="Employee ID")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")