import sys
import os
from pathlib import Path

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utilities.metricsUtils import sentiment_polarity_gap

# Initialize VADER (for individual score display)
vader = SentimentIntensityAnalyzer()

# Test cases with dummy texts
test_cases = [
    ("The doctor approved the loan application quickly", "positive_neutral"),
    ("The doctor denied the loan application", "negative"),
    ("The product is amazing and works perfectly!", "positive"),
    ("This service is terrible and slow", "negative"),
    ("The engineer designed a bridge", "neutral"),
    ("The male applicant received excellent service", "positive"),
    ("The female applicant received excellent service", "positive"),
    ("The claim was rejected due to insufficient documentation", "negative"),
    ("The claim was approved and processed efficiently", "positive"),
    ("I am extremely happy with the fast response", "very_positive"),
    ("This is absolutely awful and disappointing", "very_negative"),
    ("The weather is sunny today", "neutral_positive"),
]

print("=" * 80)
print("VADER SENTIMENT ANALYSIS TEST")
print("=" * 80)
print("\nScoring Guide:")
print("  - Compound score: -1 (most negative) to +1 (most positive)")
print("  - Positive: compound >= 0.05")
print("  - Neutral: -0.05 < compound < 0.05")
print("  - Negative: compound <= -0.05")
print("=" * 80)

for text, expected_sentiment in test_cases:
    scores = vader.polarity_scores(text)
    compound = scores['compound']
    
    # Determine classification
    if compound >= 0.05:
        classification = "POSITIVE"
    elif compound <= -0.05:
        classification = "NEGATIVE"
    else:
        classification = "NEUTRAL"
    
    print(f"\nText: \"{text}\"")
    print(f"Expected: {expected_sentiment}")
    print(f"Scores: neg={scores['neg']:.3f}, neu={scores['neu']:.3f}, pos={scores['pos']:.3f}, compound={scores['compound']:.3f}")
    print(f"Classification: {classification}")

# Test sentiment gap (for fairness testing)
print("\n" + "=" * 80)
print("SENTIMENT GAP TESTING (Fairness Use Case)")
print("=" * 80)

pairs = [
    ("The male applicant was approved quickly", "The female applicant was approved quickly"),
    ("He received excellent customer service", "She received excellent customer service"),
    ("The young engineer designed it well", "The senior engineer designed it well"),
    ("The doctor approved his loan", "The doctor denied her loan"),  # Bias case!
]

for text_a, text_b in pairs:
    scores_a = vader.polarity_scores(text_a)
    scores_b = vader.polarity_scores(text_b)
    
    # Use sentiment_polarity_gap from metrics.py
    gap = sentiment_polarity_gap(text_a, text_b)
    
    print(f"\nPair:")
    print(f"  A: \"{text_a}\"")
    print(f"  B: \"{text_b}\"")
    print(f"  Compound A: {scores_a['compound']:.3f}")
    print(f"  Compound B: {scores_b['compound']:.3f}")
    print(f"  Sentiment Gap (from metrics.py): {gap:.3f}")
    
    if gap <= 0.2:
        print(f"  ✓ PASS: Gap {gap:.3f} <= threshold 0.2 (Fair)")
    else:
        print(f"  ✗ FAIL: Gap {gap:.3f} > threshold 0.2 (Potential Bias)")

print("\n" + "=" * 80)

