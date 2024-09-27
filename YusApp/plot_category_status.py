import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from .models import ITSM_Ticket

def plot_category_1_new_complaints_view(request):
    # Fetch category_1 and status fields from the ITSM_Ticket model
    tickets = ITSM_Ticket.objects.all().values('category_1', 'status')
    
    # Create a DataFrame from the query results
    df = pd.DataFrame(tickets)

    # Filter for rows where status is 'New'
    new_complaints_df = df[df['status'] == 'New']

    # Count the occurrences of each category_1 for new complaints
    category_1_counts = new_complaints_df['category_1'].value_counts()

    # Set up the figure and axis for the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Plot the data using different colors for each category_1
    bars = ax.bar(category_1_counts.index, category_1_counts.values, color=plt.cm.Set3.colors)

    # Customize the plot
    ax.set_ylabel('Count of New Complaints')
    ax.set_xlabel('Category 1')  # Set x-axis label
    ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False, rotation=45)  # Rotate x-axis labels

# Add the legend manually with all the status labels, set at the bottom
    ax.legend(bars, category_1_counts.index, title='Status', fontsize='small', title_fontsize='small', 
              loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=3)
    
    # Display the values on top of the bars
    for bar, value in zip(bars, category_1_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(value), ha='center')

    # Adjust layout for better visibility
    plt.tight_layout()

    # Convert the plot to an image and encode it to display in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    plt.close(fig)

    # Encode the image as base64
    encoded_image_category_status = base64.b64encode(image_png).decode('utf-8')

    
    return encoded_image_category_status
