# Whisper WER Analysis

Word Error Rate (WER) can be calculated as:

WER = (Substitutions + Deletions + Insertions) / Reference Words

## Suggested evaluation procedure

1. Collect several representative interview recordings.
2. Produce a manually verified reference transcript.
3. Run Whisper on each recording.
4. Compare the hypothesis transcript with the reference.
5. Record substitutions, deletions and insertions.
6. Calculate WER for every sample.
7. Report mean WER and notable failure cases.

Do not invent accuracy numbers. Fill this document with measured results from your sample audio.
