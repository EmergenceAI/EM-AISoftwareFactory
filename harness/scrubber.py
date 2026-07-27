"""Scrub secrets from text before writing to provenance."""

import re

PATTERNS = [
    # API keys / tokens / passwords in key=value form
    r'(?i)(api[_-]?key|token|secret|password|credential|auth)\s*[:=]\s*\S+',
    # Bearer tokens
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    # GitHub PATs
    r'ghp_[A-Za-z0-9]{36}',
    r'github_pat_[A-Za-z0-9_]{82}',
    # OpenAI / Anthropic key patterns
    r'sk-ant-[A-Za-z0-9\-_]{90,}',
    r'sk-[A-Za-z0-9\-]{40,}',
    # Long base64-like strings (>=32 chars) — kept last so more-specific patterns above take priority
    r'[A-Za-z0-9+/]{32,}={0,2}',
]

# Pre-compile all patterns for performance.
_COMPILED = [re.compile(p) for p in PATTERNS]

_REDACTED = "[REDACTED]"


def scrub(text: str) -> str:
    """Replace secret-like patterns with [REDACTED]. Returns cleaned text.

    Each pattern is applied in order; earlier (more-specific) patterns are
    replaced before the broad base64 catch-all so that context words such as
    ``api_key=`` are not left dangling after the value is removed.

    Parameters
    ----------
    text:
        Arbitrary string that may contain secrets (log lines, subprocess
        output, JSON blobs, etc.).

    Returns
    -------
    str
        A copy of *text* with every matched secret replaced by ``[REDACTED]``.
        If *text* is empty or ``None`` the original value is returned unchanged.
    """
    if not text:
        return text

    for compiled in _COMPILED:
        text = compiled.sub(_REDACTED, text)

    return text
