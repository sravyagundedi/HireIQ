# AI Bias Review

## Risks

### Demographic bias
An LLM could make decisions using demographic information or proxies.

Mitigation:
- Prompt explicitly forbids demographic factors.
- Evaluation is tied to question/rubric evidence.
- Review sample evaluations manually.

### Accent and transcription
Speech-to-text errors may affect transcript quality.

Mitigation:
- Measure WER on representative sample audio.
- Inspect low-confidence or failed transcriptions.
- Do not treat accent itself as a scoring criterion.

### Confidence heuristic
The confidence signal in this starter is a heuristic, not a validated psychological measure.

Mitigation:
- Describe it as an engineering signal.
- Do not use it as the sole hiring decision factor.
- Validate against a labeled dataset before real hiring use.

### LLM consistency
LLM scoring can vary or miss context.

Mitigation:
- Low temperature.
- Structured JSON.
- Fixed rubric.
- Human review of borderline cases.

## Human oversight

HireIQ should be treated as decision support, not an autonomous hiring authority.
