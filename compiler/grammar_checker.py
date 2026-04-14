"""
Basic Grammar Checker — Compiler Phase 3 (Syntax/Semantic Validation)
Applies simple rule-based grammar checks on the token stream,
analogous to how a compiler validates syntax rules.
"""

import re
from dataclasses import dataclass, field
from typing import List

from .lexer import Token, TokenType


@dataclass
class GrammarIssue:
    message: str
    position: int
    line: int
    column: int
    severity: str = "warning"      # "warning" | "error"
    original: str = ""
    suggestion: str = ""

    def to_dict(self):
        return {
            "message": self.message,
            "position": self.position,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
            "original": self.original,
            "suggestion": self.suggestion,
        }


@dataclass
class GrammarResult:
    issues: List[GrammarIssue] = field(default_factory=list)
    issue_count: int = 0

    def to_dict(self):
        return {
            "issues": [i.to_dict() for i in self.issues],
            "issue_count": self.issue_count,
        }


# ---------------------------------------------------------------------------
# Rule helpers
# ---------------------------------------------------------------------------

def _word_tokens(tokens: List[Token]) -> List[Token]:
    return [t for t in tokens if t.type == TokenType.WORD]


def _add(issues: List[GrammarIssue], token: Token, msg: str,
         severity: str = "warning", suggestion: str = ""):
    issues.append(GrammarIssue(
        message=msg,
        position=token.position,
        line=token.line,
        column=token.column,
        severity=severity,
        original=token.value,
        suggestion=suggestion,
    ))


# ---------------------------------------------------------------------------
# Grammar rules
# ---------------------------------------------------------------------------

_ARTICLES = {"a", "an", "the"}
_VOWELS = set("aeiouAEIOU")


def _check_capitalization(tokens: List[Token], issues: List[GrammarIssue]):
    """First word of each sentence should be capitalized."""
    expect_cap = True
    for token in tokens:
        if token.type == TokenType.WORD and expect_cap:
            if token.value[0].islower():
                _add(issues, token,
                     f"Sentence should start with a capital letter: '{token.value}'",
                     suggestion=token.value.capitalize())
            expect_cap = False
        if token.type == TokenType.PUNCTUATION and token.value in ".!?":
            expect_cap = True


def _check_repeated_words(tokens: List[Token], issues: List[GrammarIssue]):
    """Detect immediately repeated words (e.g., 'the the')."""
    words = _word_tokens(tokens)
    for i in range(1, len(words)):
        if words[i].value.lower() == words[i - 1].value.lower():
            _add(issues, words[i],
                 f"Repeated word: '{words[i].value}'",
                 suggestion=f"Remove duplicate '{words[i].value}'")


def _check_a_an(tokens: List[Token], issues: List[GrammarIssue]):
    """Check a/an usage before vowels/consonants."""
    words = _word_tokens(tokens)
    for i in range(len(words) - 1):
        current = words[i].value.lower()
        next_word = words[i + 1].value
        if current == "a" and next_word[0] in _VOWELS:
            _add(issues, words[i],
                 f"Consider using 'an' before '{next_word}' (starts with a vowel sound)",
                 suggestion="an")
        elif current == "an" and next_word[0] not in _VOWELS:
            _add(issues, words[i],
                 f"Consider using 'a' before '{next_word}' (starts with a consonant sound)",
                 suggestion="a")


def _check_double_punctuation(tokens: List[Token], issues: List[GrammarIssue]):
    """Flag double punctuation like '..' or '!!'."""
    for i in range(1, len(tokens)):
        if (tokens[i].type == TokenType.PUNCTUATION and
                tokens[i - 1].type == TokenType.PUNCTUATION and
                tokens[i].value == tokens[i - 1].value and
                tokens[i].value not in ('"', "'", "-")):
            _add(issues, tokens[i],
                 f"Repeated punctuation: '{tokens[i].value}{tokens[i].value}'",
                 suggestion=f"Use a single '{tokens[i].value}'")


def _check_spacing(tokens: List[Token], issues: List[GrammarIssue]):
    """Flag multiple consecutive spaces."""
    for token in tokens:
        if token.type == TokenType.WHITESPACE and "  " in token.value and "\n" not in token.value:
            _add(issues, token,
                 "Multiple consecutive spaces detected",
                 suggestion="Use a single space")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_grammar(tokens: List[Token]) -> GrammarResult:
    """Run all grammar rules on the token list and return a GrammarResult."""
    issues: List[GrammarIssue] = []

    _check_capitalization(tokens, issues)
    _check_repeated_words(tokens, issues)
    _check_a_an(tokens, issues)
    _check_double_punctuation(tokens, issues)
    _check_spacing(tokens, issues)

    result = GrammarResult(issues=issues, issue_count=len(issues))
    return result
