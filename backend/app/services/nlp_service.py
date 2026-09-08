import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    import spacy
    NLP = spacy.load("en_core_web_sm")
except Exception:
    NLP = None

analyzer = SentimentIntensityAnalyzer()


def analyze_text(text: str) -> dict:
    keywords = []
    entities = []

    if NLP:
        doc = NLP(text)
        entities = [ent.text for ent in doc.ents][:20]
        candidates = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop and len(token.text) > 2
        ]
        freq = {}
        for word in candidates:
            freq[word] = freq.get(word, 0) + 1
        keywords = [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:15]]
    else:
        words = re.findall(r"[A-Za-z]{4,}", text.lower())
        keywords = list(dict.fromkeys(words))[:15]

    scores = analyzer.polarity_scores(text)
    return {
        "keywords": keywords,
        "entities": entities,
        "sentiment": scores,
    }


def confidence_heuristic(text: str, score: float, sentiment: dict) -> float:
    # Demo heuristic only. It should be validated against a real labeled dataset.
    length_factor = min(len(text.split()) / 100, 1.0)
    positivity = (sentiment.get("compound", 0) + 1) / 2
    confidence = 100 * (0.55 * (score / 10) + 0.25 * length_factor + 0.20 * positivity)
    return round(max(0, min(100, confidence)), 2)
