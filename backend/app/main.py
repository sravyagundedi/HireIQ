from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import Base, engine, SessionLocal
from .models import Question
from .routes.interviews import router as interview_router
from .routes.dashboard import router as dashboard_router

settings = get_settings()
app = FastAPI(title="HireIQ API", version="1.0.0")

origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)
app.include_router(dashboard_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_questions()


def seed_questions():
    db = SessionLocal()
    try:
        if db.query(Question).count() == 0:
            questions = [
                Question(
                    text="Explain the main concepts of object-oriented programming in Python.",
                    question_type="technical",
                    order_index=1,
                ),
                Question(
                    text="What is the difference between INNER JOIN and LEFT JOIN in SQL?",
                    question_type="technical",
                    order_index=2,
                ),
                Question(
                    text="Describe a difficult technical problem you solved and how you approached it.",
                    question_type="behavioral",
                    order_index=3,
                ),
                Question(
                    text="How would you debug a production API that suddenly became slow?",
                    question_type="problem_solving",
                    order_index=4,
                ),
            ]
            db.add_all(questions)
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"name": "HireIQ API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
