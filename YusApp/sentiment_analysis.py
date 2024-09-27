import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from YusApp.models import UserFeedback

def perform_sentiment_analysis():
    # Fetch all comments from UserFeedback model
    feedbacks = UserFeedback.objects.filter(comment__isnull=False).values('comment')
    df = pd.DataFrame(feedbacks)
    
    if df.empty:
        return None

    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Perform sentiment analysis
    def get_sentiment_score(text):
        return analyzer.polarity_scores(text)['compound']

    df['sentiment_score'] = df['comment'].apply(get_sentiment_score)

    # Classify sentiments as positive, neutral, or negative
    def classify_sentiment(score):
        if score >= 0.05:
            return 'Very Helpful'
        elif score <= -0.05:
            return 'Not Helpful'
        else:
            return 'Somewhat Helpful'

    df['sentiment'] = df['sentiment_score'].apply(classify_sentiment)

    # Return the dataframe with sentiments
    return df

import matplotlib.pyplot as plt
from io import BytesIO
import base64
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render


def show_sentiment_plot(request):

  # Perform sentiment analysis and get the dataframe
    df = perform_sentiment_analysis()

    if df is None or df.empty:
        return render(request, 'admin_dashboard.html', {'message': 'No feedback found'})

    # Count the occurrences of each sentiment type
    sentiment_counts = df['sentiment'].value_counts()

    # Define custom colors for the sentiments (Positive, Neutral, Negative)
    colors = ['#2ECC71', '#F1C40F', '#E74C3C']  # Green for Positive, Yellow for Neutral, Red for Negative

    # Create the funnel chart using Plotly with enhanced styling
    fig = go.Figure(go.Funnel(
        y=sentiment_counts.index,  # Sentiment labels
        x=sentiment_counts.values,  # Corresponding counts
        textinfo="value+percent initial",  # Show both values and percentage of initial value
        marker=dict(color=colors),  # Apply the custom colors
        textposition="inside",  # Place text inside the funnel sections
    ))

    # Customize the layout for better aesthetics
    fig.update_layout(
        #title_text="Sentiment Funnel Chart",
        #title_font_size=24,
        title_x=0.5,  # Center the title
        font=dict(
            size=16,
            color="black"
        ),
        margin=dict(l=40, r=40, t=100, b=40),  # Adjust margins for better layout
        paper_bgcolor="white",  # Set background color
    )

    # Convert plotly figure to a base64 image to display in the HTML template
    image_buffer = BytesIO()
    fig.write_image(image_buffer, format='png')
    image_buffer.seek(0)
    image_png = image_buffer.getvalue()
    image_buffer.close()

    encoded_image = base64.b64encode(image_png).decode('utf-8')

    return encoded_image
