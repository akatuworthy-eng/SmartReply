"""Document ingestion for the support knowledge base.

Lean, deterministic MVP: reads a plain-text file (one FAQ entry per block of
lines) and normalises it into a small in-memory knowledge bank, so the support
assistant can be seeded with real answers without needing an external embedding
pipeline.

CLI usage:

    python ingest.py --file FAQ.txt
"""

import argparse
import re


class KnowledgeBank:
    """In-memory store of FAQ entries, keyed by the first line of each block."""

    def __init__(self):
        self.entries: dict[str, str] = {}

    @staticmethod
    def _normalise(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def add(self, question: str, answer: str) -> None:
        self.entries[self._normalise(question)] = self._normalise(answer)

    def lookup(self, question: str) -> str | None:
        return self.entries.get(self._normalise(question))

    def count(self) -> int:
        return len(self.entries)


def ingest_documents(path: str, bank: KnowledgeBank | None = None) -> KnowledgeBank:
    """Read a text file of 'question line, then answer lines' blocks into a bank."""
    bank = bank or KnowledgeBank()
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]

    question = None
    answer_lines: list[str] = []
    for i, line in enumerate(lines):
        # A new question starts a block; store the previous one first.
        if _looks_like_question(i, line):
            if question is not None:
                bank.add(question, " ".join(answer_lines))
            question = line
            answer_lines = []
        else:
            answer_lines.append(line)
    if question is not None:
        bank.add(question, " ".join(answer_lines))
    return bank


def _looks_like_question(index: int, line: str) -> bool:
    """Heuristic: a line ending in '?' or the first line of the file."""
    return index == 0 or line.endswith("?")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the support knowledge base")
    parser.add_argument("--file", required=True, help="Path to the FAQ text file")
    args = parser.parse_args()

    bank = ingest_documents(args.file)
    print(f"Ingested {bank.count()} entries")
    for question in bank.entries:
        print(f"  - {question}")


if __name__ == "__main__":
    main()
