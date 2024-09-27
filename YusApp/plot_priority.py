import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from .models import ITSM_Ticket

def plot_ticket_priority_view(request):
    # Fetch the priority field from the ITSM_Ticket model
    tickets = ITSM_Ticket.objects.all().values('priority')
    
    # Create a DataFrame from the query results
    df = pd.DataFrame(tickets)
    
    # Count the occurrences of each priority
    priority_counts = df['priority'].value_counts()

    # Set up the figure and axis for the plot
    fig, ax = plt.subplots(figsize=(6,6))

    # Plot the data using different colors for each priority
    bars = ax.bar(priority_counts.index, priority_counts.values, color=plt.cm.Set2.colors)

    # Customize the plot
    ax.set_ylabel('Count')
    ax.set_xlabel('')  # Remove x-axis label
    ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)  # Hide x-axis ticks and labels

    # Add the legend manually with all the priority labels, set at the bottom
    ax.legend(bars, priority_counts.index, title='Priority', fontsize='small', title_fontsize='small', 
              loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=3)

    # Display the values on top of the bars
    for bar, value in zip(bars, priority_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, str(value), ha='center')

    # Adjust layout to make room for the legend at the bottom
    plt.tight_layout()

    # Convert the plot to an image and encode it to display in the template
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    plt.close(fig)

    # Encode the image as base64
    encoded_image_priority = base64.b64encode(image_png).decode('utf-8')



    return encoded_image_priority 
