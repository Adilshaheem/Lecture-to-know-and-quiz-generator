# Recall Studio

Recall Studio is a local Flask study app that turns pasted lecture notes into a structured outline, concept flashcards, and a scored multiple-choice quiz. It uses simple Python text heuristics, so lecture text stays on your computer and no API key is needed.

## Run on Windows

```powershell
Set-Location "C:\path\to\lecture_recall_studio"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>, paste at least 60 characters of lecture text, choose 3, 5, or 8 questions, and build the study set. Select a concept card to flip it. Choose answers in the quiz and check your score.

## What it creates

- An outline of likely key sentences
- Concept cards with a prompt and lecture context
- Multiple-choice recall questions with an answer key and score

Question and outline quality depends on the clarity and length of the source text. Review generated material against the original lecture.
