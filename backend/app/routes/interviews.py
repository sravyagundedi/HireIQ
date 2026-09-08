from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..database import get_db
from ..models import Candidate, Interview, Question, Session as InterviewSession, Response, Evaluation
from ..schemas import CandidateCreate, CandidateOut, InterviewCreate, InterviewOut, InterviewStartOut, QuestionOut, ResponseStatus
from ..celery_app import celery_app
from ..tasks.interview_tasks import process_response, finalize_interview

router = APIRouter(prefix="/api", tags=["interviews"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/candidates", response_model=CandidateOut)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(name=data.name, email=data.email)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/interviews", response_model=InterviewOut)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, data.candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    interview = Interview(candidate_id=candidate.id, title=data.title)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.post("/interviews/{interview_id}/start", response_model=InterviewStartOut)
def start_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")

    session = db.query(InterviewSession).filter_by(interview_id=interview_id).first()
    if not session:
        session = InterviewSession(interview_id=interview_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    questions = db.query(Question).filter_by(active=True).order_by(Question.order_index).all()
    return {"interview": interview, "session_id": session.id, "questions": questions}


@router.post("/sessions/{session_id}/responses")
async def upload_response(
    session_id: int,
    question_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    session = db.get(InterviewSession, session_id)
    question = db.get(Question, question_id)
    if not session or not question:
        raise HTTPException(404, "Session or question not found")

    suffix = Path(audio.filename or ".webm").suffix or ".webm"
    filename = f"{uuid.uuid4().hex}{suffix}"
    path = UPLOAD_DIR / filename

    content = await audio.read()
    path.write_bytes(content)

    response = Response(
        session_id=session.id,
        question_id=question.id,
        audio_filename=filename,
        transcription_status="queued",
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    task = process_response.delay(response.id, str(path))
    response.task_id = task.id
    db.commit()

    return {"response_id": response.id, "task_id": task.id, "status": "queued"}


@router.get("/responses/{response_id}", response_model=ResponseStatus)
def response_status(response_id: int, db: Session = Depends(get_db)):
    response = (
        db.query(Response)
        .options(joinedload(Response.evaluation), joinedload(Response.question))
        .filter(Response.id == response_id)
        .first()
    )
    if not response:
        raise HTTPException(404, "Response not found")

    evaluation = None
    if response.evaluation:
        e = response.evaluation
        evaluation = {
            "score": e.score,
            "criteria_scores": e.criteria_scores,
            "strengths": e.strengths,
            "weaknesses": e.weaknesses,
            "recommendation": e.recommendation,
            "rationale": "",
            "keywords": e.keywords,
            "entities": e.entities,
            "sentiment": e.sentiment,
            "confidence": e.confidence,
        }

    return {
        "response_id": response.id,
        "status": response.transcription_status,
        "transcript": response.transcript,
        "evaluation": evaluation,
    }


@router.post("/sessions/{session_id}/finish")
def finish_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = "processing"
    db.commit()
    task = finalize_interview.delay(session.interview_id)
    return {"status": "processing", "task_id": task.id}


@router.get("/questions", response_model=list[QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    return db.query(Question).filter_by(active=True).order_by(Question.order_index).all()
