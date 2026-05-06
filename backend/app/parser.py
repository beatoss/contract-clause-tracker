import re
from dataclasses import dataclass


CLAUSE_TYPES = [
    "Limitation of Liability",
    "Termination for Convenience",
    "Non-Compete",
]

LABEL_RE = re.compile(r"<!--\s*Clause Type:\s*(?P<label>.*?)\s*-->", re.IGNORECASE)
SENTENCE_RE = re.compile(r"[^.!?]+[.!?](?:[\"')\]]+)?|[^.!?]+$", re.MULTILINE)


@dataclass(frozen=True)
class ParsedSentence:
    text: str
    clause_type: str | None = None


def extract_title(filename: str, content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or filename
        if stripped and not LABEL_RE.fullmatch(stripped):
            return stripped[:120]
    return filename


def parse_contract(content: str) -> list[ParsedSentence]:
    sentences: list[ParsedSentence] = []
    pending_label: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        label_match = LABEL_RE.fullmatch(line)
        if label_match:
            label = normalize_clause_type(label_match.group("label"))
            if sentences and label:
                previous = sentences[-1]
                sentences[-1] = ParsedSentence(previous.text, label)
            else:
                pending_label = label
            continue

        if line.startswith("#"):
            continue

        for match in SENTENCE_RE.finditer(line):
            text = " ".join(match.group(0).split())
            if text:
                sentences.append(ParsedSentence(text=text, clause_type=pending_label))
                pending_label = None

    return sentences


def normalize_clause_type(clause_type: str | None) -> str | None:
    if not clause_type:
        return None
    cleaned = " ".join(clause_type.split())
    for known in CLAUSE_TYPES:
        if cleaned.casefold() == known.casefold():
            return known
    return None
