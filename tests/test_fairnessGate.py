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

@pytest.mark.parametrize("row_idx", [0,1,2,3,4,5,6,7,8,9,10])
def test_fairness_metrics(counterfactual_pairs, rag_client, thresholds, authority_weights, scorecard, row_idx):
    row = counterfactual_pairs[row_idx]
    qa, qb = row["query_a"], row["query_b"]
    lang_pair = bool(row.get("is_lang_pair", False))

    ra = rag_client.query(qa)
    rb = rag_client.query(qb)
    print("--------------------------------")
    print(qa)
    print(ra.text)
    print(qb)
    print(rb.text)
    print(lang_pair)
    print("--------------------------------")
    # SPS
    sps = semantic_parity_score(ra.text, rb.text)
    assert sps >= thresholds["SPS"], f"SPS={sps:.2f} below threshold {thresholds['SPS']}"

    spg = sentiment_polarity_gap(ra.text, rb.text)
    assert spg <= thresholds["SPG"], f"SPG={spg:.2f} above threshold {thresholds['SPG']}"

    blf_gap = bias_lexicon_frequency_gap(ra.text, rb.text, SENSITIVE_TERMS)
    assert blf_gap <= thresholds["BLF"], f"BLF Gap={blf_gap} > {thresholds['BLF']}"

    les = None
    if lang_pair:
        les = language_equivalence_score(ra.text, rb.text)
        assert les >= thresholds["LES"], f"LES={les:.2f} below {thresholds['LES']}"

    rfi = retrieval_fairness_index([d["doc_id"] for d in ra.retrieved],
                                   [d["doc_id"] for d in rb.retrieved], k=5)
    assert rfi >= thresholds["RFI"], f"RFI={rfi:.2f} below {thresholds['RFI']}"

    ok_a, count_a = citation_completeness(ra.citations, thresholds["CitationMin"])
    ok_b, count_b = citation_completeness(rb.citations, thresholds["CitationMin"])
    assert ok_a and ok_b, f"Citations insufficient: A={count_a}, B={count_b}, need ≥{thresholds['CitationMin']}"

    dri_a = doc_recency_index(ra.retrieved, ACTIVE_YEAR)
    dri_b = doc_recency_index(rb.retrieved, ACTIVE_YEAR)
    for i, dri in enumerate([dri_a, dri_b], start=1):
        assert dri >= thresholds["DocRecency"], f"DocRecency[{i}]={dri:.2f} below {thresholds['DocRecency']}"

    auth_a = authority_score(ra.retrieved, authority_weights)
    auth_b = authority_score(rb.retrieved, authority_weights)
    for i, auth in enumerate([auth_a, auth_b], start=1):
        assert auth >= thresholds["Authority"], f"Authority[{i}]={auth:.2f} below {thresholds['Authority']}"

    scorecard.append({
        "pair_id": row.get("id", f"pair_{row_idx}"),
        "query_a": qa,
        "query_b": qb,
        "is_lang_pair": lang_pair,
        "SPS": sps,
        "SPG": spg,
        "BLF": blf_gap,
        "LES": les if les is not None else "",
        "RFI": rfi,
        "Citations_A": count_a,
        "Citations_B": count_b,
        "DRI_A": dri_a,
        "DRI_B": dri_b,
        "Authority_A": auth_a,
        "Authority_B": auth_b,
        "ACTIVE_YEAR": 2025,
        "Thresholds": thresholds
    })

    print(scorecard)

