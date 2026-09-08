from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Interview, Candidate, Response, Report
from ..services.report_service import generate_report

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/candidates")
def candidates(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    page = max(1, page)
    page_size = min(max(1, page_size), 50)
    total = db.query(Interview).count()
    items = (
        db.query(Interview)
        .options(joinedload(Interview.candidate))
        .order_by(Interview.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [
            {
                "interview_id": i.id,
                "candidate_id": i.candidate_id,
                "candidate_name": i.candidate.name,
                "email": i.candidate.email,
                "title": i.title,
                "status": i.status,
                "score": i.overall_score,
                "recommendation": i.recommendation,
            }
            for i in items
        ],
    }


@router.get("/interviews/{interview_id}")
def interview_detail(interview_id: int, db: Session = Depends(get_db)):
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.candidate), joinedload(Interview.session))
        .filter(Interview.id == interview_id)
        .first()
    )
    if not interview:
        raise HTTPException(404, "Interview not found")

    responses = (
        db.query(Response)
        .options(joinedload(Response.question), joinedload(Response.evaluation))
        .filter(Response.session_id == interview.session.id)
        .order_by(Response.id)
        .all()
    )
    return {
        "interview": {
            "id": interview.id,
            "candidate": interview.candidate.name,
            "email": interview.candidate.email,
            "status": interview.status,
            "score": interview.overall_score,
            "recommendation": interview.recommendation,
        },
        "responses": [
            {
                "id": r.id,
                "question": r.question.text,
                "transcript": r.transcript,
                "status": r.transcription_status,
                "score": r.evaluation.score if r.evaluation else None,
                "strengths": r.evaluation.strengths if r.evaluation else [],
                "weaknesses": r.evaluation.weaknesses if r.evaluation else [],
                "keywords": r.evaluation.keywords if r.evaluation else [],
                "sentiment": r.evaluation.sentiment if r.evaluation else {},
                "confidence": r.evaluation.confidence if r.evaluation else None,
            }
            for r in responses
        ],
    }


@router.get("/interviews/{interview_id}/report")
def download_report(interview_id: int, db: Session = Depends(get_db)):
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.candidate), joinedload(Interview.session))
        .filter(Interview.id == interview_id)
        .first()
    )
    if not interview or not interview.session:
        raise HTTPException(404, "Interview not found")

    responses = (
        db.query(Response)
        .options(joinedload(Response.question), joinedload(Response.evaluation))
        .filter(Response.session_id == interview.session.id)
        .order_by(Response.id)
        .all()
    )
    path = generate_report(interview, interview.candidate, responses)

    existing = db.query(Report).filter_by(interview_id=interview_id).first()
    if existing:
        existing.filename = path.name
    else:
        db.add(Report(interview_id=interview_id, filename=path.name))
    db.commit()

    return FileResponse(path, media_type="application/pdf", filename=path.name)
