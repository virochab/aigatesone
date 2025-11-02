import pytest
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
from utilities.lexiconUtil import SENSITIVE_TERMS
from utilities.metricsUtils import (
    semantic_parity_score, sentiment_polarity_gap, bias_lexicon_frequency_gap,
    language_equivalence_score, retrieval_fairness_index, citation_completeness,
    doc_recency_index, authority_score
)

ACTIVE_YEAR = 2025

def get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries):
    """Helper function to get RAG responses with caching to avoid duplicate queries"""
    if row_idx not in cached_rag_queries:
        row = counterfactual_pairs[row_idx]
        qa, qb = row["query_a"], row["query_b"]
        
        # Query RAG client once
        ra = rag_client.query(qa)
        rb = rag_client.query(qb)
        
        # Cache the results
        cached_rag_queries[row_idx] = {
            'ra': ra,
            'rb': rb,
            'row': row,
            'qa': qa,
            'qb': qb,
            'lang_pair': bool(row.get('is_lang_pair', False))
        }
        
        # Debug output (only once per row_idx)
        print("--------------------------------")
        print(f"Query A: {qa}")
        print(f"Response A: {ra.text}")
        print(f"Query B: {qb}")
        print(f"Response B: {rb.text}")
        print(f"Language Pair: {row.get('is_lang_pair', False)}")
        print("--------------------------------")
    
    return cached_rag_queries[row_idx]

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_semantic_parity_score(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Semantic Parity Score (SPS)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    sps = semantic_parity_score(ra.text, rb.text)
    assert sps >= thresholds["SPS"], f"SPS={sps:.2f} below threshold {thresholds['SPS']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_sentiment_polarity_gap(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Sentiment Polarity Gap (SPG)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    spg = sentiment_polarity_gap(ra.text, rb.text)
    assert spg <= thresholds["SPG"], f"SPG={spg:.2f} above threshold {thresholds['SPG']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_bias_lexicon_frequency_gap(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Bias Lexicon Frequency Gap (BLF)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    blf_gap = bias_lexicon_frequency_gap(ra.text, rb.text, SENSITIVE_TERMS)
    assert blf_gap <= thresholds["BLF"], f"BLF Gap={blf_gap} > {thresholds['BLF']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_language_equivalence_score(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Language Equivalence Score (LES)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    
    # Only test LES for language pairs
    if data['lang_pair']:
        ra, rb = data['ra'], data['rb']
        les = language_equivalence_score(ra.text, rb.text)
        assert les >= thresholds["LES"], f"LES={les:.2f} below {thresholds['LES']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_retrieval_fairness_index(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Retrieval Fairness Index (RFI)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    rfi = retrieval_fairness_index([d["doc_id"] for d in ra.retrieved],
                                   [d["doc_id"] for d in rb.retrieved], k=5)
    assert rfi >= thresholds["RFI"], f"RFI={rfi:.2f} below {thresholds['RFI']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_citation_completeness(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Citation Completeness"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    ok_a, count_a = citation_completeness(ra.citations, thresholds["CitationMin"])
    ok_b, count_b = citation_completeness(rb.citations, thresholds["CitationMin"])
    assert ok_a and ok_b, f"Citations insufficient: A={count_a}, B={count_b}, need ≥{thresholds['CitationMin']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_doc_recency_index(counterfactual_pairs, rag_client, thresholds, row_idx, cached_rag_queries):
    """Test Document Recency Index (DRI)"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    dri_a = doc_recency_index(ra.retrieved, ACTIVE_YEAR)
    dri_b = doc_recency_index(rb.retrieved, ACTIVE_YEAR)
    for i, dri in enumerate([dri_a, dri_b], start=1):
        assert dri >= thresholds["DocRecency"], f"DocRecency[{i}]={dri:.2f} below {thresholds['DocRecency']}"

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_authority_score(counterfactual_pairs, rag_client, thresholds, authority_weights, row_idx, cached_rag_queries):
    """Test Authority Score"""
    data = get_rag_responses(counterfactual_pairs, rag_client, row_idx, cached_rag_queries)
    ra, rb = data['ra'], data['rb']
    
    auth_a = authority_score(ra.retrieved, authority_weights)
    auth_b = authority_score(rb.retrieved, authority_weights)
    for i, auth in enumerate([auth_a, auth_b], start=1):
        assert auth >= thresholds["Authority"], f"Authority[{i}]={auth:.2f} below {thresholds['Authority']}"


