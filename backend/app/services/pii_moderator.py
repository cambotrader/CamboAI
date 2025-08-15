from __future__ import annotations
from typing import Tuple, Dict
import re

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d\-\s\(\)]{7,}\d)\b")
URL_RE = re.compile(r"\b(?:https?://|www\.)\S+\b", re.IGNORECASE)
ADDRESS_RE = re.compile(r"\b\d{1,6}\s+\w[\w\s]{1,30}\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Terrace|Ter|Place|Pl)\b", re.IGNORECASE)

REPLACEMENTS = {
    EMAIL_RE: "[REDACTED EMAIL]",
    PHONE_RE: "[REDACTED PHONE]",
    URL_RE: "[REDACTED URL]",
    ADDRESS_RE: "[REDACTED ADDRESS]",
}

def sanitize(text: str) -> Tuple[str, Dict[str, bool]]:
    flags = {"email": False, "phone": False, "url": False, "address": False}
    out = text
    for regex, token in REPLACEMENTS.items():
        if regex.search(out):
            out = regex.sub(token, out)
            if token == "[REDACTED EMAIL]":
                flags["email"] = True
            elif token == "[REDACTED PHONE]":
                flags["phone"] = True
            elif token == "[REDACTED URL]":
                flags["url"] = True
            elif token == "[REDACTED ADDRESS]":
                flags["address"] = True
    return out, flags

__all__ = ["sanitize"]