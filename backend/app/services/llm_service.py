import json
from ..config import get_settings
from ..schemas.schemas import EvaluationResult
from .rubric_service import load_rubric

settings = get_settings()


def _build_prompt(question: str, transcript: str, rubric: dict) -> str:
    return f'''
You are HireIQ, an interview evaluation assistant.

Evaluate the candidate answer ONLY against the job-relevant rubric.
Do not infer or use protected/demographic attributes such as age, gender,
race, religion, disability, nationality, accent, appearance, or socioeconomic
background. Do not reward or penalize a candidate for those attributes.

QUESTION:
{question}

CANDIDATE TRANSCRIPT:
{transcript}

RUBRIC:
{json.dumps(rubric, indent=2)}

Return ONLY valid JSON with this exact logical shape:
{{
  "score": 0-10,
  "criteria_scores": {{"criterion": 0-10}},
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendation": "Proceed|Hold|Reject",
  "rationale": "..."
}}
'''


def evaluate_with_openai(question: str, transcript: str, rubric: dict) -> EvaluationResult:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a fair, structured interview evaluator."},
            {"role": "user", "content": _build_prompt(question, transcript, rubric)},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    return EvaluationResult.model_validate(data)


def evaluate_with_gemini(question: str, transcript: str, rubric: dict) -> EvaluationResult:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    response = model.generate_content(
        _build_prompt(question, transcript, rubric),
        generation_config={"temperature": 0, "response_mime_type": "application/json"},
    )
    data = json.loads(response.text)
    return EvaluationResult.model_validate(data)


def evaluate_answer(question: str, transcript: str, question_type: str) -> EvaluationResult:
    rubric = load_rubric(question_type)
    provider = settings.llm_provider.lower()

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        return evaluate_with_gemini(question, transcript, rubric)

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return evaluate_with_openai(question, transcript, rubric)
