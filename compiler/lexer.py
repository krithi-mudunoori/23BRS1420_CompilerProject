"""
Lexical Analyzer (Tokenizer) — Compiler Phase 1
Breaks input text into a stream of classified tokens,
similar to how a compiler front-end tokenizes source code.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    WORD = auto()
    NUMBER = auto()
    PUNCTUATION = auto()
    WHITESPACE = auto()
    SYMBOL = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    position: int          # character offset in the original text
    line: int
    column: int

    def to_dict(self):
        return {
            "type": self.type.name,
            "value": self.value,
            "position": self.position,
            "line": self.line,
            "column": self.column,
        }


# Ordered list of (token-type, compiled regex).
# The lexer tries each pattern in order; first match wins.
_TOKEN_SPEC: List[tuple] = [
    (TokenType.WORD,        re.compile(r"[A-Za-z'-]+")),
    (TokenType.NUMBER,      re.compile(r"\d+(?:\.\d+)?")),
    (TokenType.PUNCTUATION, re.compile(r"[.!?,;:\"()\[\]{}\-]")),
    (TokenType.WHITESPACE,  re.compile(r"\s+")),
    (TokenType.SYMBOL,      re.compile(r"[^\s]")),
]


@dataclass
class LexerResult:
    tokens: List[Token] = field(default_factory=list)
    total_tokens: int = 0
    word_count: int = 0
    sentence_count: int = 0
    char_count: int = 0

    def to_dict(self):
        return {
            "tokens": [t.to_dict() for t in self.tokens],
            "total_tokens": self.total_tokens,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "char_count": self.char_count,
        }


def tokenize(text: str) -> LexerResult:
    """Scan *text* and return a LexerResult with all tokens and statistics."""
    result = LexerResult()
    result.char_count = len(text)

    pos = 0
    line = 1
    col = 1

    while pos < len(text):
        matched = False
        for tok_type, pattern in _TOKEN_SPEC:
            m = pattern.match(text, pos)
            if m:
                value = m.group()
                token = Token(
                    type=tok_type,
                    value=value,
                    position=pos,
                    line=line,
                    column=col,
                )
                result.tokens.append(token)

                # Update statistics
                if tok_type == TokenType.WORD:
                    result.word_count += 1
                if tok_type == TokenType.PUNCTUATION and value in ".!?":
                    result.sentence_count += 1

                # Advance line / column counters
                newlines = value.count("\n")
                if newlines:
                    line += newlines
                    col = len(value) - value.rfind("\n")
                else:
                    col += len(value)

                pos = m.end()
                matched = True
                break

        if not matched:
            # Should not happen given SYMBOL catches everything, but be safe.
            result.tokens.append(
                Token(TokenType.UNKNOWN, text[pos], pos, line, col)
            )
            pos += 1
            col += 1

    result.total_tokens = len(result.tokens)
    # If there are words but no sentence-ending punctuation, count as 1 sentence.
    if result.word_count > 0 and result.sentence_count == 0:
        result.sentence_count = 1

    return result
