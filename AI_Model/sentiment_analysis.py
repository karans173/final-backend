import pandas as pd
from supabase import create_client
from transformers import pipeline
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
sentiment_analyzer = None

SUPABASE_URL = "https://rizamamuiwyyplawssvr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpemFtYW11aXd5eXBsYXdzc3ZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIxMzA3MDIsImV4cCI6MjA2NzcwNjcwMn0.Qfno-pgz05Fjs0_K5WKMLdUFtVeg-NuNVoZhPIwLjvg"
BUCKET_NAME = "news-summary"
FILE_NAME = "generated_text.txt"

def get_sentiment_analyzer():
    global sentiment_analyzer
    if sentiment_analyzer is None:
        try:
            print("🤖 Initializing sentiment analysis pipeline...")
            sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                local_files_only=True
            )
            print("✅ Model pipeline loaded successfully.")
        except Exception as e:
            print(f"❌ Pipeline Initialization Error: {e}")
            return None
    return sentiment_analyzer

def analyze_text_file_sentiment(file_name: str = "generated_text.txt"):
    from supabase import create_client
    import os

    SUPABASE_URL = os.getenv("https://rizamamuiwyyplawssvr.supabase.co")
    SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpemFtYW11aXd5eXBsYXdzc3ZyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjEzMDcwMiwiZXhwIjoyMDY3NzA2NzAyfQ.RYVgSqjNiHcWWTrhrmUl5BuCBxiZeZjfQwo3pI3EjFw")
    BUCKET_NAME = "news-summary"
    FILE_NAME = file_name

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"📥 Downloading file `{FILE_NAME}` from Supabase bucket `{BUCKET_NAME}`...")
        content = supabase.storage.from_(BUCKET_NAME).download(FILE_NAME).decode("utf-8")
        print("✅ File downloaded and decoded successfully.")
    except Exception as e:
        print(f"❌ Error downloading file from Supabase: {e}")
        return {
            "error": str(e),
            "stage": "supabase_download"
        }

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    analyzer = get_sentiment_analyzer()
    if analyzer is None:
        print("❌ Sentiment analysis pipeline not available.")
        return {
            "error": "Sentiment analyzer could not be initialized.",
            "stage": "pipeline_init"
        }

    results = []
    for line in lines:
        if len(line) < 10:
            print(f"⏭️ Skipping short line: {line}")
            continue
        try:
            result = analyzer(line)[0]
            results.append({
                'text': line,
                'sentiment': result['label'],
                'score': result['score']
            })
        except Exception as e:
            print(f"⚠️ Error analyzing line: {line[:30]}... | {e}")

    if not results:
        print("❌ No valid sentiment results returned.")
        return {
            "error": "All lines failed to analyze or were too short.",
            "stage": "analysis"
        }

    positive_lines = [r for r in results if r['sentiment'] == 'POSITIVE']
    positive_ratio = len(positive_lines) / len(results)
    avg_sentiment_score = sum(r['score'] for r in results) / len(results)
    normalized_sentiment = (positive_ratio - 0.5) * 2

    print(f"✅ Sentiment Analysis Complete")
    print(f"🔍 Overall Sentiment: {'POSITIVE' if positive_ratio > 0.5 else 'NEGATIVE'}")
    print(f"📊 Positive Ratio: {positive_ratio:.2f}")
    print(f"📈 Normalized Sentiment: {normalized_sentiment:.2f}")
    print(f"🔢 Average Sentiment Score: {avg_sentiment_score:.2f}")

    return {
        'results': results,
        'overall_sentiment': 'POSITIVE' if positive_ratio > 0.5 else 'NEGATIVE',
        'positive_ratio': positive_ratio,
        'normalized_sentiment': normalized_sentiment,
        'avg_sentiment_score': avg_sentiment_score
    }






def generate_trading_signals(price_data, sentiment_result, risk_profile='moderate'):
    """
    Generate trading signals based on technical indicators and sentiment analysis
    """
    sentiment_score = sentiment_result['normalized_sentiment']
    
    risk_weights = {
        'conservative': {'technical': 0.8, 'sentiment': 0.2},
        'moderate': {'technical': 0.6, 'sentiment': 0.4},
        'aggressive': {'technical': 0.4, 'sentiment': 0.6}
    }
    
    weights = risk_weights.get(risk_profile, risk_weights['moderate'])
    
    signals = {}
    
    for ticker in price_data:
        ticker_data = price_data[ticker]
        
        sma_10 = ticker_data['Close'].rolling(window=10).mean().iloc[-1]
        sma_30 = ticker_data['Close'].rolling(window=30).mean().iloc[-1]
        
        technical_signal = 1 if sma_10 > sma_30 else -1
        
        combined_signal = (technical_signal * weights['technical'] + 
                           sentiment_score * weights['sentiment'])
        
        if combined_signal > 0.3:
            action = 'buy'
        elif combined_signal < -0.3:
            action = 'sell'
        else:
            action = 'hold'
        
        confidence = abs(combined_signal)
        
        signals[ticker] = {
            'action': action,
            'confidence': round(confidence, 2),
            'technical_signal': technical_signal,
            'sentiment_signal': sentiment_score,
            'combined_signal': round(combined_signal, 2)
        }
        print (f"Ticker: {ticker}, Action: {action}, Confidence: {confidence:.2f}, "
               f"Technical Signal: {technical_signal}, Sentiment Signal: {sentiment_score:.2f}, "
               f"Combined Signal: {combined_signal:.2f}")
    
    return signals

# if __name__ == "__main__":
#     analyze_text_file_sentiment(file_path)
#     # Example usage
#     file_path = 'C:/Users/Manmeet/Desktop/AI-Thon/Trade-AI/AI Model/generated_text.txt'
#     sentiment_result = analyze_text_file_sentiment(file_path)
    
#     # Example price data (replace with actual data)
#     price_data = {
#         'AAPL': pd.DataFrame({
#             'Close': [150, 152, 153, 151, 155, 157, 158]
#         }),
#         'GOOGL': pd.DataFrame({
#             'Close': [2800, 2820, 2810, 2830, 2840, 2850, 2860]
#         })
#     }
    
#     signals = generate_trading_signals(price_data, sentiment_result)