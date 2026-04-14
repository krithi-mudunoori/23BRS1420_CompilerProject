"""
Flask application — Web interface for the compiler-based spelling checker.
"""

import os
from flask import Flask, render_template, request, jsonify

from compiler.lexer import tokenize
from compiler.spell_checker import check_spelling
from compiler.grammar_checker import check_grammar

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB upload limit

ALLOWED_EXTENSIONS = {"txt", "md", "text"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _analyze(text: str) -> dict:
    """Run the full compiler pipeline on *text* and return a JSON-ready dict."""
    # Phase 1 — Lexical analysis
    lexer_result = tokenize(text)

    # Phase 2 — Spelling validation
    spell_result = check_spelling(lexer_result.tokens, text)

    # Phase 3 — Grammar checking
    grammar_result = check_grammar(lexer_result.tokens)

    return {
        "original_text": text,
        "lexer": lexer_result.to_dict(),
        "spelling": spell_result.to_dict(),
        "grammar": grammar_result.to_dict(),
    }


# ---- Routes ----------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_text():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"]
    if not isinstance(text, str) or len(text) == 0:
        return jsonify({"error": "Text must be a non-empty string"}), 400
    if len(text) > 100_000:
        return jsonify({"error": "Text too long (max 100 000 characters)"}), 400

    result = _analyze(text)
    return jsonify(result)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only .txt and .md files are allowed"}), 400

    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({"error": "File must be UTF-8 encoded text"}), 400

    if len(text) == 0:
        return jsonify({"error": "Uploaded file is empty"}), 400

    result = _analyze(text)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
