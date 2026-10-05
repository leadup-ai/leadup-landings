#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch <head> of lab/ai-longread/v1 and v2: meta description, canonical, og:*, twitter:*.
Idempotent: managed tags are stripped first, then re-inserted in a fixed order.
Run from the repository root (CI) or from a directory containing lab/ai-longread/*/index.html.
"""
import hashlib
import pathlib
import re
import sys

TITLE = "Бесплатный ИИ-практикум за четыре вечера — LeadUp AI"
DESC = ("Бесплатный 4-дневный ИИ-практикум LeadUp AI: 9 вопросов ментору Владимиру Нагину — "
        "как проходят вечера и чему учишься. Старт 27 октября, 19:00, 0 €.")
OGD = ("Четыре вечера, 0 €: 9 вопросов ментору — как проходит практикум, "
       "чему на нём учишься и что делать после.")
TWD = "Четыре вечера, 0 € — 9 вопросов ментору о практикуме LeadUp AI."
IMG = "https://leadup-ai.github.io/leadup-landings/assets/og/ai-longread-1200x630.png"
IMG_ALT = "Бесплатный ИИ-практикум LeadUp AI: четыре вечера, 0 €, старт 27 октября"
BASE = "https://leadup-ai.github.io/leadup-landings/lab/ai-longread"

ROOT = pathlib.Path(__file__).resolve().parents[2]
print("repo root:", ROOT, file=sys.stderr)


def block_for(variant: str) -> str:
    url = f"{BASE}/{variant}/"
    return "\n".join([
        f'<title>{TITLE}</title>',
        f'<meta name="description" content="{DESC}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:site_name" content="LeadUp AI">',
        '<meta property="og:locale" content="ru_RU">',
        '<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{TITLE}">',
        f'<meta property="og:description" content="{OGD}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{IMG}">',
        f'<meta property="og:image:secure_url" content="{IMG}">',
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{IMG_ALT}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{TITLE}">',
        f'<meta name="twitter:description" content="{TWD}">',
        f'<meta name="twitter:image" content="{IMG}">',
    ]) + "\n"


def patch(variant: str) -> None:
    path = ROOT / "lab" / "ai-longread" / variant / "index.html"
    text = path.read_text(encoding="utf-8")
    before = len(text.encode("utf-8"))

    # safety: the page must still be the ai-longread longread we expect
    assert text.count("<title>") == 1, f"{variant}: unexpected <title> count"
    assert "leadup-logo.svg" in text, f"{variant}: brand logo reference missing"
    assert "Участник" in text, f"{variant}: expected «Участник» label missing"
    assert 'id="form"' in text, f"{variant}: registration form missing"

    text = re.sub(r'\n?<meta\s+name="description"[^>]*>', "", text)
    text = re.sub(r'\n?<meta\s+property="og:[^"]*"[^>]*>', "", text)
    text = re.sub(r'\n?<meta\s+name="twitter:[^"]*"[^>]*>', "", text)
    text = re.sub(r'\n?<link\s+rel="canonical"[^>]*>', "", text)

    new, n = re.subn(r"<title>[^<]*</title>", block_for(variant), text, count=1)
    assert n == 1, f"{variant}: <title> not replaced"

    for marker in ('name="description"', 'rel="canonical"', 'property="og:image"',
                   'property="og:title"', 'name="twitter:card"'):
        assert new.count(marker) == 1, f"{variant}: {marker} count != 1"

    path.write_text(new, encoding="utf-8")
    out = path.read_bytes()
    print(f"{variant}: {before} -> {len(out)} bytes md5 {hashlib.md5(out).hexdigest()}")


for v in ("v1", "v2"):
    patch(v)
print("OK")
