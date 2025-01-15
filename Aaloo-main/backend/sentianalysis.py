import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import re

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
vader_analyzer = SentimentIntensityAnalyzer()

def clean_keywords(cuisine_keywords):

    cleaned_keywords = []
    
    # Tokenize each keyword and clean it
    for keyword in cuisine_keywords:
        # Convert to lowercase and tokenize
        keyword = keyword.lower()
        tokens = word_tokenize(keyword)
        
        # Remove stopwords and punctuation
        tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
        
        # Lemmatize the remaining words to their base form
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        
        # If after cleaning there are valid tokens, add them to the cleaned list
        if tokens:
            cleaned_keywords.append(' '.join(tokens))  # Join the tokens back into a single string
    
    return cleaned_keywords


# def extract_food_items(text,cuisine_keywords):
#     if isinstance(text, str):
#         text_lower = text.lower()
#         return [item for item in cuisine_keywords if item in text_lower]
#     return []
def extract_food_items(text, cuisine_keywords):
    """
    Extract food items by tokenizing the text and using set intersections.
    This avoids repeated regex matching for each keyword.
    """
    if isinstance(text, str):
        # Convert text and keywords to lowercase
        text_tokens = set(word_tokenize(text.lower()))  # Tokenize and create a set
        keywords_set = set(cuisine_keywords)  # Convert keywords to a set for faster lookup

        # Find intersection of text tokens and keywords
        matched_items = text_tokens.intersection(keywords_set)
        print(matched_items)
        return list(matched_items)  

    return []


def analyze_sentiment_label(text):
    if isinstance(text, str):
        text = text.strip()
        if  text == "N/A":  # Handle empty or "empty or N/A" cases
            return "Neutral"  # Treat "No review" as neutral sentiment
        vader_score = vader_analyzer.polarity_scores(text)["compound"]
        if vader_score > 0.05:
            return "Positive"
        elif vader_score < -0.05:
            return "Negative"
        else:
            return "Neutral"
    return "Neutral"


def create_food_sentiment_object(text,cuisine_keywords):
    food_items = extract_food_items(text,cuisine_keywords)
    sentiment = analyze_sentiment_label(text or "")
    if food_items:
        return [{"item": item, "sentiment": sentiment} for item in food_items]
    return [{"item": "No review"}]


def sentimentanalysis_google_reviews(drop3):
    dm = pd.read_csv("C:\\Users\\mehul\\OneDrive\\Desktop\\Aaloo\\backend\\Files\\menuitemss.csv", low_memory=False)
    menu_items = dm["itemname"]
    cuisine_keywords = [ 
        "biryani", "chicken", "pizza", "pasta", "burger", "sushi", 
        "paneer", "fish", "dal", "noodles", "ice cream", "salad", 
        "steak", "fries", "dessert", "cake", "sandwich",
    ]

    # Append menu items to cuisine keywords
    cuisine_keywords.extend(menu_items.dropna().tolist())  # Remove NaN values
    cuisine_keywords = list(set(cuisine_keywords))  # Remove duplicates
    cleaned_cuisine_keywords = clean_keywords(cuisine_keywords)
    #printing statements just to review the ouput
    # print(f"Total cuisine keywords: {len(cuisine_keywords)}")
    # print(f"Example: {cuisine_keywords[5]}")
    
    
    drop3["Food Item Sentiment"] = drop3["Review"].apply(lambda x: json.dumps(create_food_sentiment_object(x, cleaned_cuisine_keywords)))


    output_file = "C:\\Users\\mehul\\OneDrive\\Desktop\\Data Check\\googleReviews_with_sentimenthaha2.xlsx"
    drop3.to_excel(output_file, index=False)
    print(f"Dataset updated and saved")
    
    return drop3