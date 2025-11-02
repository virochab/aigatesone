import json, csv, datetime, pathlib, pytest, sys

BASE = pathlib.Path(__file__).resolve().parents[1]
# Add BASE to Python path so imports from src work
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from utilities.rag_clientSample import MockRAGClient


DATA_DIR = BASE / "data"
REPORTS_DIR = BASE / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def counterfactual_pairs():
    with open(DATA_DIR / "counterfactual_pairs.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def thresholds():
    with open(DATA_DIR / "thresholds.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def authority_weights():
    with open(DATA_DIR / "authority_weights.json", "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def rag_client():
    return MockRAGClient()

@pytest.fixture(scope="session")
def scorecard():
    rows = []
    yield rows
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = REPORTS_DIR / f"fairness_scorecard_{ts}.csv"
    json_path = REPORTS_DIR / f"fairness_scorecard_{ts}.json"
    if rows:
        keys = list(rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        print(f"\n[Fairness Scorecard] CSV: {csv_path}")
        print(f"[Fairness Scorecard] JSON: {json_path}")
