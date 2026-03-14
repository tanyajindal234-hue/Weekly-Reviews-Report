from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import emoji
from langdetect import detect, LangDetectException
def fetch_groww_play_store_reviews(max_results=1000, weeks_back=12):
    """
    Fetches up to `max_results` English reviews for the Groww app from the Google Play Store
    that were created within the last `weeks_back` weeks.
    
    Returns a list of standardized review dictionaries.
    """
    GROWW_APP_ID = 'com.nextbillion.groww'
    
    # Calculate cutoff date
    now = datetime.now()
    cutoff_date = now - timedelta(weeks=weeks_back)
    
    # Fetch reviews. The scraper provides pagination, fetching 100 at a time by default.
    result, continuation_token = reviews(
        GROWW_APP_ID,
        lang='en', # fetch only English reviews
        country='in', # default to India
        sort=Sort.NEWEST, # sort by newest first to easily check dates
        count=max_results, # initial count to fetch
        filter_score_with=None # fetch all ratings
    )
    
    filtered_reviews = []
    
    # Process the reviews we fetched
    for review in result:
        # review['at'] is a datetime object
        review_date = review['at']
        
        # We only want reviews from the last `weeks_back` weeks
        if review_date >= cutoff_date:
            content = review['content'] or ""
            
            # Filter reviews with emojis
            if emoji.emoji_count(content) > 0:
                continue

            # Filter non-English reviews using langdetect
            try:
                if detect(content) != 'en':
                    continue
            except LangDetectException:
                # If language cannot be detected (e.g. only numbers), skip it
                continue
                
            # Filter reviews with less than 5 words
            word_count = len(content.split())
            if word_count < 5:
                continue
                
            # Standardize the data format (title removed)
            standardized_review = {
                "source": "Play Store",
                "date": review_date.strftime("%Y-%m-%d %H:%M:%S"),
                "rating": review['score'],
                "text": content
            }
            filtered_reviews.append(standardized_review)
        else:
            # Since they are sorted by NEWEST, once we hit an older review, we can stop evaluating
            break
            
    # We enforce the maximum 1000 limit strictly
    return filtered_reviews[:max_results]
