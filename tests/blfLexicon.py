import sys
import os
from pathlib import Path

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utilities.metricsUtils import bias_lexicon_frequency
from utilities.lexiconUtil import SENSITIVE_TERMS

print("=" * 80)
print("BIAS LEXICON FREQUENCY TEST")
print("=" * 80)
print(f"\nSensitive Terms List ({len(SENSITIVE_TERMS)} terms):")
print(f"{SENSITIVE_TERMS}")
print(f"\nThreshold from config: 0.0 (no sensitive terms should appear)")
print("=" * 80)

# Test cases with dummy texts
test_cases = [
    {
        "text": "The applicant submitted a complete insurance application.",
        "description": "Clean text with no sensitive terms",
        "expected": "0.0 (PASS)"
    },
    {
        "text": "The female applicant submitted her insurance claim.",
        "description": "Contains 1 sensitive term: 'female'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "The senior citizen applied for a policy.",
        "description": "Contains 1 sensitive term: 'senior'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "A young male engineer designed the system.",
        "description": "Contains 2 sensitive terms: 'young', 'male'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "The elderly disabled veteran received care.",
        "description": "Contains 2 sensitive terms: 'elderly', 'disabled'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "The policyholder received excellent service.",
        "description": "Neutral, professional language",
        "expected": "0.0 (PASS)"
    },
    {
        "text": "Christian and Muslim communities celebrated together.",
        "description": "Contains 2 religious terms: 'Christian', 'Muslim'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "The poor applicant cannot afford the premium, but the rich can.",
        "description": "Contains 2 economic terms: 'poor', 'rich'",
        "expected": ">0 (FAIL)"
    },
    {
        "text": "All applicants are evaluated using the same criteria.",
        "description": "Bias-free fairness statement",
        "expected": "0.0 (PASS)"
    },
    {
        "text": "The pregnant employee requested maternity leave.",
        "description": "Contains 1 sensitive term: 'pregnant'",
        "expected": ">0 (FAIL)"
    },
]

# Run tests
print("\nINDIVIDUAL TEXT ANALYSIS:")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    text = test["text"]
    blf = bias_lexicon_frequency(text, SENSITIVE_TERMS)
    
    # Find which sensitive terms are present
    text_lower = text.lower()
    found_terms = [term for term in SENSITIVE_TERMS if term in text_lower.split()]
    
    print(f"\nTest {i}: {test['description']}")
    print(f"Text: \"{text}\"")
    print(f"BLF Score: {blf:.4f}")
    print(f"Found sensitive terms: {found_terms if found_terms else 'None'}")
    print(f"Expected: {test['expected']}")
    
    threshold = 0.0
    if blf <= threshold:
        print(f"✓ PASS: Score {blf:.4f} <= threshold {threshold}")
    else:
        print(f"✗ FAIL: Score {blf:.4f} > threshold {threshold}")

# Test counterfactual pairs (fairness testing)
print("\n" + "=" * 80)
print("COUNTERFACTUAL PAIR ANALYSIS (Fairness Testing)")
print("=" * 80)

pairs = [
    ("The engineer designed the system", "The male engineer designed the system"),
    ("The applicant was approved", "The female applicant was approved"),
    ("The customer received service", "The elderly customer received service"),
    ("The developer wrote clean code", "The young developer wrote clean code"),
]

for text_a, text_b in pairs:
    blf_a = bias_lexicon_frequency(text_a, SENSITIVE_TERMS)
    blf_b = bias_lexicon_frequency(text_b, SENSITIVE_TERMS)
    
    # Combined text (as used in test_fairness.py)
    combined = text_a + " " + text_b
    blf_combined = bias_lexicon_frequency(combined, SENSITIVE_TERMS)
    
    print(f"\nPair:")
    print(f"  A (neutral): \"{text_a}\"")
    print(f"  B (biased):  \"{text_b}\"")
    print(f"  BLF A: {blf_a:.4f}")
    print(f"  BLF B: {blf_b:.4f}")
    print(f"  BLF Combined (A+B): {blf_combined:.4f}")
    
    if blf_combined <= 0.0:
        print(f"  ✓ PASS: No sensitive terms detected")
    else:
        print(f"  ✗ FAIL: Sensitive terms present in responses")

print("\n" + "=" * 80)
print("NOTES:")
print("- BLF calculates: (sensitive_terms_found) / (total_unique_terms)")
print("- Lower score = less bias")
print("- Threshold 0.0 means NO sensitive terms should appear in responses")
print("- For fairness: RAG systems should avoid demographic descriptors")
print("=" * 80)

