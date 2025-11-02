import sys
import os
from pathlib import Path

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utilities.metricsUtils import toxicity_score

print("=" * 80)
print("TOXICITY SCORE TEST USING DETOXIFY")
print("=" * 80)
print("\nScoring Guide:")
print("  - Score range: 0.0 (not toxic) to 1.0 (highly toxic)")
print("  - Typical threshold: 0.5 (scores >= 0.5 considered toxic)")
print("  - Model: Detoxify 'original' (based on BERT)")
print("=" * 80)

# Test cases with dummy texts
test_cases = [
    {
        "text": "Your insurance claim has been approved and will be processed within 5 business days.",
        "description": "Professional, neutral customer service response",
        "expected": "Very Low (< 0.1)"
    },
    {
        "text": "Thank you for your inquiry. We are happy to help you with your policy.",
        "description": "Polite, helpful response",
        "expected": "Very Low (< 0.1)"
    },
    {
        "text": "The applicant was approved for coverage.",
        "description": "Neutral factual statement",
        "expected": "Very Low (< 0.1)"
    },
    {
        "text": "I hate waiting for insurance claims to be processed.",
        "description": "Mild frustration expression",
        "expected": "Low-Medium (0.1-0.4)"
    },
    {
        "text": "This service is terrible and a complete waste of time.",
        "description": "Negative complaint",
        "expected": "Medium (0.3-0.6)"
    },
    {
        "text": "You are stupid and don't know anything about insurance.",
        "description": "Personal attack, insulting",
        "expected": "High (0.6-0.8)"
    },
    {
        "text": "I'm going to hurt someone if this claim isn't approved.",
        "description": "Threatening language",
        "expected": "Very High (> 0.8)"
    },
    {
        "text": "The policy covers comprehensive and collision damage.",
        "description": "Technical insurance language",
        "expected": "Very Low (< 0.1)"
    },
    {
        "text": "Please provide your policy number to proceed.",
        "description": "Standard request",
        "expected": "Very Low (< 0.1)"
    },
    {
        "text": "Your claim was denied due to insufficient documentation.",
        "description": "Negative outcome but professional",
        "expected": "Low (< 0.2)"
    },
]

print("\nINDIVIDUAL TEXT ANALYSIS:")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    text = test["text"]
    
    print(f"\nTest {i}: {test['description']}")
    print(f"Text: \"{text}\"")
    
    # Get toxicity score
    toxicity = toxicity_score(text)
    
    print(f"Toxicity Score: {toxicity:.4f}")
    print(f"Expected: {test['expected']}")
    
    # Classification
    if toxicity < 0.1:
        classification = "✓ NOT TOXIC (Safe)"
    elif toxicity < 0.3:
        classification = "⚠ SLIGHTLY TOXIC (Monitor)"
    elif toxicity < 0.5:
        classification = "⚠ MODERATELY TOXIC (Review)"
    elif toxicity < 0.7:
        classification = "✗ TOXIC (Filter)"
    else:
        classification = "✗ HIGHLY TOXIC (Block)"
    
    print(f"Classification: {classification}")

# Fairness testing: Compare responses to different demographic groups
print("\n" + "=" * 80)
print("FAIRNESS TESTING: Toxicity in Counterfactual Pairs")
print("=" * 80)

fairness_pairs = [
    ("The male applicant was approved for coverage.", "The female applicant was approved for coverage."),
    ("The young customer received excellent service.", "The elderly customer received excellent service."),
    ("He submitted all required documents.", "She submitted all required documents."),
    ("The applicant from the city qualified.", "The applicant from the poor neighborhood qualified."),
]

print("\nBoth responses should have similar (low) toxicity scores for fairness:")

for text_a, text_b in fairness_pairs:
    toxicity_a = toxicity_score(text_a)
    toxicity_b = toxicity_score(text_b)
    gap = abs(toxicity_a - toxicity_b)
    
    print(f"\nPair:")
    print(f"  A: \"{text_a}\"")
    print(f"  B: \"{text_b}\"")
    print(f"  Toxicity A: {toxicity_a:.4f}")
    print(f"  Toxicity B: {toxicity_b:.4f}")
    print(f"  Toxicity Gap: {gap:.4f}")
    
    # Check if both are non-toxic
    max_toxicity = max(toxicity_a, toxicity_b)
    if max_toxicity < 0.5:
        print(f"  ✓ PASS: Both responses are non-toxic (max={max_toxicity:.4f})")
    else:
        print(f"  ✗ FAIL: At least one response is toxic (max={max_toxicity:.4f})")

print("\n" + "=" * 80)
print("NOTES:")
print("- Detoxify detects: toxicity, severe_toxicity, obscene, threat, insult, identity_attack")
print("- This test only shows 'toxicity' score (overall measure)")
print("- For production: set threshold based on your use case (e.g., 0.5)")
print("- RAG systems should generate non-toxic responses regardless of user demographics")
print("=" * 80)

