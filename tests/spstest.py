import sys
import os
from pathlib import Path

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utilities.metricsUtils import semantic_parity_score

# Test 1: Identical text
text1a = "The doctor approved the loan application"
text1b = "The doctor approved the loan application"
sps1 = semantic_parity_score(text1a, text1b)
print(f"Test 1 (Identical):\nA: {text1a}\nB: {text1b}\nSPS: {sps1}\n")

# Test 2: Gender counterfactual (high similarity expected)
text2a = "The male engineer designed the bridge"
text2b = "The female engineer designed the bridge"
sps2 = semantic_parity_score(text2a, text2b)
print(f"Test 2 (Gender swap):\nA: {text2a}\nB: {text2b}\nSPS: {sps2}\n")

# Test 3: Same meaning, different words (low similarity - this is the problem!)
text3a = "The doctor helped the patient"
text3b = "The physician assisted the sick person"
sps3 = semantic_parity_score(text3a, text3b)
print(f"Test 3 (Paraphrase):\nA: {text3a}\nB: {text3b}\nSPS: {sps3}\n")

# Test 4: Completely different text (low similarity expected)
text4a = "The sun is shining brightly today"
text4b = "The cat sat on the mat"
sps4 = semantic_parity_score(text4a, text4b)
print(f"Test 4 (Different):\nA: {text4a}\nB: {text4b}\nSPS: {sps4}\n")

# Test 5: Partially similar
text5a = "The software engineer wrote clean code efficiently"
text5b = "The software developer wrote clean code quickly"
sps5 = semantic_parity_score(text5a, text5b)
print(f"Test 5 (Partial overlap):\nA: {text5a}\nB: {text5b}\nSPS: {sps5}\n")

print("=" * 60)
print(f"Threshold in config: 0.8 (80% similarity required)")
print(f"\nWould pass (>= 0.8): Test 1={sps1>=0.8}, Test 2={sps2>=0.8}")
print(f"Would fail (< 0.8): Test 3={sps3<0.8}, Test 4={sps4<0.8}, Test 5={sps5<0.8}")

