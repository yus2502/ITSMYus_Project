import random
import string
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import KBA, ITSM_Ticket, UserFeedback
from sentence_transformers import SentenceTransformer, util
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder
from django.http import HttpResponse
import joblib  # For loading the pre-trained model
import os
from django.conf import settings

from django.contrib.auth.decorators import login_required

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Predefined categories
PREDEFINED_CATEGORIES = [
    "Application", "Authorization", "Change Request", "Continuous Improvement Non-Chargeable", 
    "Enquiry", "Others", "Policies and Procedures", "Service Request Chargeable", 
    "Service Request Non-Chargeable", "Technical", "War Room", "Webmethods", "ICT"
]

# Generate custom ticket ID
def generate_ticket_id():
    current_date = datetime.now().strftime('%Y%m%d')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return current_date + random_chars

# Function to load the pre-trained model
def load_pretrained_model():
    # Get the path of the .pkl file from the project directory
    model_path = os.path.join(settings.BASE_DIR, 'svm_model.pkl')
    
    # Load the model using joblib
    model = joblib.load(model_path)
    
    return model

# Use the pre-trained model to predict priority
def predict_with_model(description):
    model = load_pretrained_model()
    
    # Make the prediction using the input description
    prediction = model.predict([description])
    
    return prediction[0]  # Return the predicted priority

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Error creating an account.')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Home page view
@login_required
def home(request):
    return render(request, 'home.html')

# File New Issue view with Ticket ID generation and priority prediction using the pre-trained model
@login_required
def file_issue_view(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        category_1 = request.POST.get('category_1')

        # Generate a new Ticket ID after form submission
        ticket_id = generate_ticket_id()

        # Use the pre-trained model to predict priority
        predicted_priority = predict_with_model(description)

        # Provide default values for all required fields
        dummy_support_team_id = 1  # Replace this with an actual default or valid value from your database
        current_time = timezone.now()

        # Create a new ITSM_Ticket with predicted priority and default values for other required fields
        new_ticket = ITSM_Ticket.objects.create(
            ticket_id=ticket_id,
            description=description,
            priority=predicted_priority,
            category_1=category_1,
            support_team_id=dummy_support_team_id,  # Add the dummy value here
            created_on=current_time,  # Provide a default value for created_on
            last_changed_on=current_time,  # Provide a default value for last_changed_on
            # Add default values for other NOT NULL fields if needed
        )
        new_ticket.save()

        # Redirect to the recommendation view with the ticket_id and predicted priority
        return redirect('ticket_recommendation', ticket_id=ticket_id, predicted_priority=predicted_priority)

    # For GET request, render the form without ticket_id or predicted_priority
    distinct_categories = ITSM_Ticket.objects.values_list('category_1', flat=True).distinct()
    filtered_categories = [category for category in PREDEFINED_CATEGORIES if category in distinct_categories]

    return render(request, 'input_ticket.html', {'filtered_categories': filtered_categories})

# Ticket recommendation view with predictions from pre-trained model
@login_required
def ticket_recommendation_view(request, ticket_id, predicted_priority):
    # Retrieve the ticket using the ticket_id
    ticket = get_object_or_404(ITSM_Ticket, ticket_id=ticket_id)

    # Convert numeric predicted priority to text and color
    priority_text = get_priority_text(predicted_priority)
    priority_color = get_priority_color(priority_text)

    # We can now safely work with the description and category
    description = ticket.description
    category_1 = ticket.category_1

    # Combine the description and category for embedding
    new_ticket_combined = f"{description}.{category_1}"
    new_ticket_embedding = model.encode([new_ticket_combined], convert_to_tensor=True)

    # Retrieve all KBAs from the database and create their embeddings
    kbas = KBA.objects.all()
    kba_combined = [f"{kba.description}.{kba.category_1}.{kba.category_2}.{kba.category_3}.{kba.issue}" for kba in kbas]
    kba_embeddings = model.encode(kba_combined, convert_to_tensor=True)

    # Compute cosine similarity between the new ticket and KBAs
    cosine_scores = util.cos_sim(kba_embeddings, new_ticket_embedding)

    # Filter results based on cosine similarity scores
    filtered_results = []
    for idx, score in enumerate(cosine_scores):
        if score.item() > 0.50:  # Adjust similarity threshold
            kba = kbas[idx]
            filtered_results.append({
                'description': kba.description,
                'category_1': kba.category_1,
                'category_2': kba.category_2,
                'category_3': kba.category_3,
                'resolution': kba.resolution,
                'knowledge_article_id': kba.knowledge_article_id,
            })

    # Context with filtered results, priority prediction, and priority color
    context = {
        'ticket_id': ticket_id,
        'filtered_results': filtered_results,
        'predicted_priority': priority_text,
        'priority_color': priority_color
        
    }

    # Render the result page with the provided context
    return render(request, 'result.html', context)

    # If the request is not a POST, render the input ticket page again
    distinct_categories = ITSM_Ticket.objects.values_list('category_1', flat=True).distinct()
    filtered_categories = [category for category in PREDEFINED_CATEGORIES if category in distinct_categories]

    return render(request, 'input_ticket.html', {
        'ticket': ticket,
        'filtered_categories': filtered_categories
    })

# Helper function to determine color for priority
def get_priority_color(priority):
    if priority == 'Very High':
        return 'red'
    elif priority == 'High':
        return 'orange'
    elif priority == 'Medium':
        return 'yellow'
    elif priority == 'Low':
        return 'grey'
    return 'black'  # Fallback color

# Helper function to convert priority numbers to text
def get_priority_text(priority_number):
    priority_mapping = {
        '1': 'Very High',
        '2': 'High',
        '3': 'Medium',
        '4': 'Low'
    }
    return priority_mapping.get(str(priority_number), 'Low')  # Default to 'Low'

# Feedback submission view
@login_required
def feedback_view(request):
    feedback_submitted = False  # Flag to indicate whether feedback was submitted

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        ticket_id = request.POST.get('ticket_id')
        knowledge_article_id = request.POST.get('knowledge_article_id')

        # Save the feedback to the database
        try:
            feedback = UserFeedback.objects.create(
                ticket_id=ticket_id,
                helpfulness_rating=int(rating),
                comment=comment,
                timestamp=timezone.now(),  # Use timezone.now() for the timestamp
                knowledge_article_id=knowledge_article_id  # Save Knowledge Article ID
            )
            feedback.save()
            feedback_submitted = True  # Set the flag to True upon successful submission

        except ITSM_Ticket.DoesNotExist:
            return redirect('home')

        # Redirect to the feedback form again with a flag indicating submission success
        return render(request, 'feedback.html', {'feedback_submitted': feedback_submitted})

    # For GET request
    return render(request, 'feedback.html', {'feedback_submitted': feedback_submitted})

# Render feedback form with ticket ID
@login_required
def feedback_form(request):
    if request.method == 'POST':
        # Get form data
        ticket_id = request.POST.get('ticket_id')
        knowledge_article_id = request.POST.get('selected_knowledge_article_id')  # Use the selected knowledge_article_id
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Get the current time and set seconds and microseconds to 00
        current_time = timezone.now().replace(second=0, microsecond=0)

        # Check if feedback already exists for this ticket_id
        feedback = UserFeedback.objects.filter(ticket_id=ticket_id).first()
        
        if feedback:
            # Update the existing feedback
            feedback.knowledge_article_id = knowledge_article_id if knowledge_article_id else feedback.knowledge_article_id
            feedback.helpfulness_rating = rating
            feedback.comment = comment
            feedback.timestamp = current_time 
            feedback.save()
        else:
            # Create a new feedback entry
            feedback = UserFeedback(
                ticket_id=ticket_id,
                knowledge_article_id=knowledge_article_id,
                helpfulness_rating=rating,
                comment=comment,
                timestamp=current_time
            )
            feedback.save()

        # Return success message
        return render(request, 'feedback.html', {
            'ticket_id': ticket_id,
            'knowledge_article_id': knowledge_article_id,
            'message': 'Your Feedback Has Been Submitted'
        })

    # For GET request, just render the feedback form
    return render(request, 'feedback.html')


#===========================================================================================

#==============================ADMIN DASHBOARD ============================================from .sentiment_analysis import  show_sentiment_plot,perform_sentiment_analysis
from .plot_complain_type import plot_ticket_status_view
from .plot_priority import plot_ticket_priority_view
from .plot_category import plot_ticket_category_1_view
from .plot_category_status import plot_category_1_new_complaints_view
import pandas as pd

def feedback_sentiment_view(request):
    employee_name = request.session.get('employee_name', None)
    if not employee_name:
        return redirect('employee_login')  # Redirect if not logged in
    
    # Ensure this query is inside the view function and not run during module import
    tickets = ITSM_Ticket.objects.all().values('status')
    
    # Create a DataFrame from the query results
    df = pd.DataFrame(tickets)

    # Filter for the specific statuses 'Confirmed', 'New', 'In Progress'
    filtered_df = df[df['status'].isin(['Confirmed', 'New', 'In Progress'])]

    # Count the occurrences of each specific status
    status_counts = filtered_df['status'].value_counts()

    # Ensure we return the counts for all three statuses, even if some don't exist in the data
    confirmed_count = status_counts.get('Confirmed', 0)
    new_count = status_counts.get('New', 0)
    in_progress_count = status_counts.get('In Progress', 0)

    encoded_image_status = plot_ticket_status_view(request)
    encoded_image_priority = plot_ticket_priority_view(request)
    encoded_image_category = plot_ticket_category_1_view(request)
    encoded_image_category_status = plot_category_1_new_complaints_view(request)

    context = {
        'status_plot': encoded_image_status,
        'priority_plot': encoded_image_priority,
        'category_plot': encoded_image_category,
        'category_status_plot': encoded_image_category_status,
        'confirmed_count': confirmed_count,
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'employee_name': employee_name
    }

    return render(request, 'admin_dashboard.html', context)

#===============================ADMIN===================================
from django.shortcuts import render, redirect
from .forms import EmployeeRegistrationForm
from .forms import EmployeeRegistrationForm
from .forms import EmployeeLoginForm
from .models import Employee

def register_employee(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_success')
    else:
        form = EmployeeRegistrationForm()

    return render(request, 'employee_registration.html', {'form': form})


def employee_success(request):
    return render(request, 'employee_success.html')


def employee_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data.get('employee_id')
            password = form.cleaned_data.get('password')
            print("-----",employee_id)

            try:
                employee = Employee.objects.get(employee_id=employee_id)
                if employee.password == password:  # Simple password check (improve with hashing in production)
                    request.session['employee_id'] = employee_id  # Set session
                    request.session['employee_name'] = employee.first_name + ' ' + employee.last_name
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Invalid password. Please try again.')
            except Employee.DoesNotExist:
                messages.error(request, 'Employee ID does not exist. Please register.')
                return redirect('register_employee')
    else:
        form = EmployeeLoginForm()

    return render(request, 'employee_login.html', {'form': form})


def employee_logout(request):  
    request.session.flush()  # This clears all session data, including employee_name and employee_id
    return render(request,'employee_login.html')  
