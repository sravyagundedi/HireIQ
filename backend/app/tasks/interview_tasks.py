from pathlib import Path
from celery import Task
from ..celery_app import celery_app
from ..database import SessionLocal
from ..models import Response, Evaluation, Interview
from ..services.whisper_service import transcribe_audio
from ..services.nlp_service import analyze_text, confidence_heuristic
from ..services.llm_service import evaluate_answer


class RetryableTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_kwargs = {"max_retries": 3}


@celery_app.task(bind=True, base=RetryableTask)
def process_response(self, response_id: int, audio_path: str):
    db = SessionLocal()
    response = None

    try:
        response = db.get(Response, response_id)

        if not response:
            raise ValueError("Response not found")

        # Check that the audio file still exists
        if not Path(audio_path).exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        response.transcription_status = "processing"
        db.commit()

        # -------------------------
        # 1. Transcription
        # -------------------------
        transcript = transcribe_audio(audio_path)

        response.transcript = transcript
        response.transcription_status = "transcribed"
        db.commit()

        # -------------------------
        # 2. NLP analysis
        # -------------------------
        nlp = analyze_text(transcript)

        # -------------------------
        # 3. LLM evaluation
        # -------------------------
        result = evaluate_answer(
            response.question.text,
            transcript,
            response.question.question_type,
        )

        # -------------------------
        # 4. Confidence
        # -------------------------
        confidence = confidence_heuristic(
            transcript,
            result.score,
            nlp["sentiment"],
        )

        # -------------------------
        # 5. Save evaluation
        # -------------------------
        evaluation = Evaluation(
            response_id=response.id,
            score=result.score,
            criteria_scores=result.criteria_scores,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            keywords=nlp["keywords"],
            entities=nlp["entities"],
            sentiment=nlp["sentiment"],
            confidence=confidence,
            recommendation=result.recommendation,
        )

        db.add(evaluation)

        response.transcription_status = "completed"

        db.commit()

        # -------------------------
        # 6. Delete audio ONLY
        #    after successful completion
        # -------------------------
        try:
            Path(audio_path).unlink(missing_ok=True)
        except Exception:
            pass

        return {
            "response_id": response_id,
            "status": "completed",
        }

    except Exception:
        if response:
            response.transcription_status = "failed"
            db.commit()

        # IMPORTANT:
        # Do NOT delete the audio here.
        # Celery may retry this task.

        raise

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=10)
def finalize_interview(self, interview_id: int):
    db = SessionLocal()
    try:
        interview = db.get(Interview, interview_id)
        if not interview or not interview.session:
            return

        responses = list(interview.session.responses)
        if not responses:
            interview.status = "completed"
            interview.overall_score = 0
            interview.recommendation = "Hold"
            db.commit()
            return

        pending = [r for r in responses if r.transcription_status not in ("completed", "failed")]
        if pending:
            raise self.retry(countdown=5)

        evaluations = [r.evaluation for r in responses if r.evaluation]
        if not evaluations:
            interview.status = "completed"
            interview.overall_score = 0
            interview.recommendation = "Hold"
            db.commit()
            return

        interview.overall_score = sum(e.score for e in evaluations) / len(evaluations)
        if interview.overall_score >= 7.5:
            interview.recommendation = "Proceed"
        elif interview.overall_score >= 5:
            interview.recommendation = "Hold"
        else:
            interview.recommendation = "Reject"
        interview.status = "completed"
        db.commit()
    finally:
        db.close()
