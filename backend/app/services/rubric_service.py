from pathlib import Path
import yaml

# Project root /rubric directory
RUBRIC_DIR = Path(__file__).resolve().parents[3] / "rubric"


def load_rubric(question_type: str) -> dict:
    path = RUBRIC_DIR / f"{question_type}.yaml"
    if not path.exists():
        path = RUBRIC_DIR / "technical.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
