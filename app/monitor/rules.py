from __future__ import annotations


def find_matches(text: str | None, keywords: list[str]) -> list[str]:
    """Return keywords found in text (Contains, case-insensitive)."""
    haystack = (text or "").lower()
    if not haystack or not keywords:
        return []
    matched: list[str] = []
    for word in keywords:
        needle = word.lower()
        if needle and needle in haystack:
            matched.append(word)
    return matched
