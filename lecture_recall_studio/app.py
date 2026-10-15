from __future__ import annotations

import random
import re
from collections import Counter

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

STOP_WORDS = set("a an and are as at be been by for from had has have he her his i in is it its of on or that the their them there these they this to was were what when where which who will with you your lecture topic important explain means defined refers into during about after before through using used such than then also can could may might should would".split())


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", re.sub(r"\s+", " ", text).strip()) if len(s.split()) >= 5]


def make_study_set(text: str, question_count: int = 5) -> dict:
    sentences = split_sentences(text)
    if not sentences:
        sentences = [s.strip() for s in re.split(r"[;\n]+", text) if len(s.split()) >= 4]

    words_by_sentence = []
    frequencies = Counter()
    for sentence in sentences:
        words = [w.lower() for w in re.findall(r"\b[A-Za-z][A-Za-z'-]{3,}\b", sentence) if w.lower() not in STOP_WORDS]
        words_by_sentence.append(words)
        frequencies.update(words)

    def score(index: int) -> float:
        words = words_by_sentence[index]
        signal = sum(frequencies[w] for w in set(words)) / max(len(words), 1)
        definition = 0.6 if re.search(r"\b(is|are|means|refers to|consists of|because|therefore)\b", sentences[index], re.I) else 0
        return signal + definition

    selected_indices = sorted(sorted(range(len(sentences)), key=score, reverse=True)[:max(3, min(7, question_count + 1))])
    outline = []
    for index in selected_indices:
        words = words_by_sentence[index]
        label = next((w.title() for w in words if frequencies[w] > 1), "Key idea")
        outline.append({"label": label, "detail": sentences[index]})

    key_terms = [word for word, _ in frequencies.most_common(12)]
    cards = []
    for term in key_terms:
        source = next((s for s in sentences if re.search(rf"\b{re.escape(term)}\b", s, re.I)), None)
        if source:
            cards.append({"front": f"How does this lecture use {term.title()}?", "back": source})
        if len(cards) >= 8:
            break

    quiz = []
    for sentence in sentences:
        candidates = [w for w in re.findall(r"\b[A-Za-z][A-Za-z'-]{4,}\b", sentence) if w.lower() not in STOP_WORDS]
        answer = next((w for w in candidates if frequencies[w.lower()] > 1), candidates[0] if candidates else None)
        if not answer or any(item["answer"].lower() == answer.lower() for item in quiz):
            continue
        prompt = re.sub(rf"\b{re.escape(answer)}\b", "________", sentence, count=1, flags=re.I)
        distractors = [w.title() for w in key_terms if w.lower() != answer.lower()]
        random.Random(f"{answer}:{sentence}").shuffle(distractors)
        choices = [answer.title(), *distractors[:3]]
        random.Random(sentence).shuffle(choices)
        quiz.append({"prompt": prompt, "answer": answer.title(), "choices": choices})
        if len(quiz) >= question_count:
            break
    return {"outline": outline, "cards": cards, "quiz": quiz, "terms": [w.title() for w in key_terms[:8]]}


@app.route("/", methods=["GET", "POST"])
def home():
    study_set = None
    source = ""
    error = None
    if request.method == "POST":
        source = request.form.get("lecture", "").strip()
        try:
            count = int(request.form.get("count", 5))
        except ValueError:
            count = 5
        if len(source) < 60:
            error = "Paste at least 60 characters so the study set has enough context."
        else:
            study_set = make_study_set(source, max(3, min(8, count)))
            if not study_set["quiz"]:
                error = "Add a few more complete sentences so the quiz can find useful terms."
                study_set = None
    return render_template("index.html", study_set=study_set, source=source, error=error)


@app.errorhandler(413)
def too_large(_error):
    return "Lecture text is too large. Keep it under 1 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)
