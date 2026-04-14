# Compiler-Based Spell Checker & Grammar Analyzer

A Flask-based web application that mimics a compiler pipeline to analyze text.
It performs **lexical analysis, spelling correction, and grammar checking** in multiple phases.

---

## Features

- **Lexical Analysis (Tokenizer)**

- Splits input into tokens (words, numbers, punctuation, etc.)
- Tracks position (line, column) for error reporting

- **Spell Checking (Semantic Analysis)**
  - Uses an embedded English dictionary
  - Detects misspelled words
  - Suggests corrections using **Damerau–Levenshtein Distance**
  - Generates corrected text

- **Grammar Checking (Syntax Analysis)**

- Capitalization errors
- Repeated words (e.g., _"the the"_)
- Article usage (_a/an_)
- Double punctuation (_!!, .._)
- Extra spacing issues

- **Web Interface**

- Built using Flask
- Analyze text via UI or API
- Upload `.txt` files

---

## Project Structure

```
COMPILER/
│
├── compiler/
│   ├── __init__.py
│   ├── lexer.py
│   ├── spell_checker.py
│   ├── grammar_checker.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
├── test_input.txt
├── .gitignore
```

---

## How It Works (Compiler Pipeline)

```
Input Text
   ↓
Lexical Analysis (Tokenization)
   ↓
Spelling Check (DL Distance)
   ↓
Grammar Check (Rule-Based)
   ↓
Output (JSON / Web UI)
```

---

## Example Input

```
this is a sampel sentense with speling erors. the the quick brown fox jumpd over a elefant.
```

---

## Output Highlights

- `sampel → sample`
- `sentense → sentence`
- `speling → spelling`
- `jumpd → jumped`
- `elefant → elephant`
- `the the → repeated word`
- `a elefant → an elephant`
- Capitalization fixes

---

## Installation & Setup

### Clone the repository

```
git clone https://github.com/krithi-mudunoori/23BRS1420_CompilerProject.git
cd 23BRS1420_CompilerProject
```

---

### 2Install dependencies

```
pip install -r requirements.txt
```

---

### Run the application

```
python app.py
```

---

### Open in browser

```
http://127.0.0.1:5000/
```

---

## API Endpoints

### 🔹 Analyze Text

**POST** `/analyze`

```json
{
  "text": "This is a sample text"
}
```

---

### 🔹 Upload File

**POST** `/upload`

- Accepts `.txt` files
- Returns JSON response

---

## Key Concepts Used

- Lexical Analysis (Tokenization)
- Regular Expressions (Regex)
- Token Streams
- Semantic Analysis (Dictionary-based validation)
- Damerau–Levenshtein Distance
- Rule-Based Grammar Checking
- Error Detection & Correction
- Flask Web Development

---

## Limitations

- Rule-based grammar
- Limited dictionary coverage
- No contextual understanding

---

## Future Improvements

- Add full parser (LL/LR parsing)
- Improve grammar using NLP models
- Expand dictionary
- Add real-time editor UI
- Multi-language support

---

## Author

Developed as part of a **Compiler Design-inspired project**

---

## License

This project is open-source and available under the MIT License.
