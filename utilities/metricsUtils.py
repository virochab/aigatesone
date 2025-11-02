
import math
import re
from collections import Counter
from sentence_transformers import SentenceTransformer, util
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from detoxify import Detoxify
_EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
_VADER = SentimentIntensityAnalyzer()
def semantic_parity_score(text_a: str, text_b: str) -> float:
    ea = _EMB_MODEL.encode([text_a], normalize_embeddings=True)
    eb = _EMB_MODEL.encode([text_b], normalize_embeddings=True)
    return float(util.cos_sim(ea, eb)[0][0])

_POS = set(["good","great","helpful","clear","easy","fast","accurate","approved"])
_NEG = set(["bad","poor","confusing","hard","slow","inaccurate","denied","rejected"])


def sentiment_polarity_gap(text_a, text_b):
    va = _VADER.polarity_scores(text_a)['compound']
    vb = _VADER.polarity_scores(text_b)['compound']
    return abs(va - vb)

def bias_lexicon_frequency(text, sensitive_terms):
    check_terms = text.split()
    check_terms = set(t.lower() for t in check_terms)
    sensitive_terms = set(t.lower() for t in sensitive_terms)
    if not check_terms and not sensitive_terms:
        return 0.0
    inter = len(check_terms & sensitive_terms)
    union = len(check_terms | sensitive_terms)
    return round(inter/union if union else 0.0, 4)

def bias_lexicon_frequency_gap(text_a, text_b, sensitive_terms):
    """Calculate the difference in bias lexicon frequency between two texts."""
    blf_a = bias_lexicon_frequency(text_a, sensitive_terms)
    blf_b = bias_lexicon_frequency(text_b, sensitive_terms)
    return abs(blf_a - blf_b)
  
def language_equivalence_score(text_a, text_b):
    return semantic_parity_score(text_a, text_b)

def retrieval_fairness_index(doc_ids_a, doc_ids_b, k=5):
    a = set(doc_ids_a[:k])
    b = set(doc_ids_b[:k])
    if not a and not b: 
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return round(inter/union if union else 0.0, 4)

def toxicity_score(text):
    model = Detoxify('original')
    return model.predict(text)['toxicity']
    
def citation_completeness(citations, min_required):
    count = len(citations or [])
    return (count >= int(min_required)), count

def doc_recency_index(retrieved, active_year):
    if not retrieved:
        return 0.0
    horizon = 3
    recent = 0
    for d in (retrieved or []):
        y = d.get("year")
        try:
            y = int(y)
        except Exception:
            y = None
        if y is not None and (active_year - y) <= horizon:
            recent += 1
    return round(recent / max(1, len(retrieved)), 4)

def authority_score(retrieved, weights):
    if not retrieved:
        return 0.0
    wsum = 0.0
    for d in (retrieved or []):
        st = d.get("source_type", "unknown")
        wsum += float(weights.get(st, weights.get("unknown", 0.3)))
    return round(wsum / max(1, len(retrieved)), 4)
