# HireIQ Architecture

```text
React Candidate UI
      |
      v
FastAPI REST API
      |
      +---- PostgreSQL
      |
      +---- Redis -> Celery Worker
                       |
                       +-> PyDub
                       +-> Whisper
                       +-> spaCy
                       +-> VADER
                       +-> GPT/Gemini
      |
      +---- ReportLab -> PDF
      |
      +---- React Hiring Dashboard
```

## Async flow

1. Browser records an audio blob with MediaRecorder.
2. FastAPI saves it temporarily and creates a Response row.
3. Celery receives the response ID and audio path.
4. Worker normalizes/transcribes the audio.
5. Worker deletes the temporary audio file.
6. Transcript is enriched with spaCy/VADER.
7. LLM evaluates against YAML rubric.
8. Pydantic validates the LLM JSON.
9. Evaluation is stored in PostgreSQL.
10. Dashboard and PDF consume the stored evaluation.
