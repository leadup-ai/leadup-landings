#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Подключение Meta Pixel к лендингам LeadUp AI.

Ставит `pixel_id` в `window.__LANDING__` каждой страницы, при необходимости
добавляет загрузчик пикселя и событие `PageView`.

Идемпотентен: повторный запуск ничего не ломает.
Запуск из корня репозитория:  python3 tools/pixel/set_pixel.py
"""
import pathlib
import re
import sys

PIXEL_ID = "581042486157971"

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Страницы-кампании (папка = репозиторий лендингов).
PAGES = [
    "ai-course/v1/index.html",
    "ai-practicum/v1/index.html",
    "lab/ai-longread/v1/index.html",
    "lab/ai-longread/v2/index.html",
    "lab/cosmo-ai/v1/index.html",
    "lab/cosmo-ai/v2/index.html",
]

# Ожидаемый landing_id для каждой страницы — защита от правки не той страницы.
EXPECTED_LANDING_ID = {
    "ai-course/v1/index.html": "ai-course",
    "ai-practicum/v1/index.html": "ai-practicum",
    "lab/ai-longread/v1/index.html": "ai-longread",
    "lab/ai-longread/v2/index.html": "ai-longread",
    "lab/cosmo-ai/v1/index.html": "cosmo-ai",
    "lab/cosmo-ai/v2/index.html": "cosmo-ai",
}

# Загрузчик пикселя — только для страниц, где его ещё нет (cosmo-ai/v1).
LOADER = """  /* --- Meta Pixel: подключается, если задан pixel_id --- */
  (function(){
    var id = window.__LANDING__ && window.__LANDING__.pixel_id;
    if (!id) return;
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', id); fbq('track', 'PageView');
  })();
"""

# Служебные комментарии, оставшиеся от шаблона, — обновляем на «ID задан».
COMMENT_FIXES = [
    (
        "pixel_id оставьте пустым, пока не задан Meta Pixel ID в Events Manager.",
        "pixel_id — ID пикселя из Events Manager (задан).",
    ),
    ("/* TODO: вставить Meta Pixel ID */", "/* Meta Pixel ID (Events Manager) */"),
]


def patch(rel: str) -> tuple[int, int, list[str]]:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    before = len(text.encode("utf-8"))
    notes = []

    # --- защита: страница та, за которую себя выдаёт ---
    assert text.count("<title>") == 1, f"{rel}: неожиданное число <title>"
    assert 'property="og:site_name"' in text or "<html" in text, f"{rel}: нет <html>"
    lid = EXPECTED_LANDING_ID[rel]
    assert f"landing_id: '{lid}'" in text, f"{rel}: landing_id != {lid}"

    # --- 1. pixel_id ---
    if f"pixel_id: '{PIXEL_ID}'" in text:
        notes.append("pixel_id уже задан")
    else:
        text, n = re.subn(r"pixel_id:\s*''", f"pixel_id: '{PIXEL_ID}'", text)
        assert n == 1, f"{rel}: pixel_id:'' найден {n} раз (ожидался 1)"
        notes.append("pixel_id: '' -> задан")

    # --- 2. загрузчик пикселя (если его нет) ---
    if "fbevents.js" not in text:
        anchor = "window.__LANDING__ = LANDING;"
        assert text.count(anchor) == 1, f"{rel}: не найден якорь для вставки загрузчика"
        text = text.replace(anchor, anchor + "\n\n" + LOADER, 1)
        notes.append("добавлен загрузчик пикселя")

    # --- 3. стандартное событие PageView ---
    if "fbq('track', 'PageView')" not in text:
        text, n = re.subn(
            r"( *)fbq\('init', CFG\.pixel_id\);",
            r"\1fbq('init', CFG.pixel_id);\n\1fbq('track', 'PageView');",
            text,
        )
        assert n == 1, f"{rel}: fbq('init', CFG.pixel_id) найден {n} раз (ожидался 1)"
        notes.append("добавлен fbq('track','PageView')")

    # --- 3.5. убрать из шаблона пометки «pixel_id не задан» ---
    for old_c, new_c in COMMENT_FIXES:
        if old_c in text:
            text = text.replace(old_c, new_c, 1)

    # --- 4. cosmo-ai/v1: не отправлять в пиксель воронку вебхука как кастомные события ---
    old = "try { window.fbq('track', eventName === 'lead' ? 'Lead' : eventName, {}, { eventID: payload.event_id }); } catch(e){}"
    new = "try { if (eventName === 'lead') window.fbq('track', 'Lead', {}, { eventID: payload.event_id }); } catch(e){}"
    if old in text:
        text = text.replace(old, new, 1)
        notes.append("в пиксель уходит только Lead (без page_view/cta_click)")

    # --- проверки результата ---
    assert text.count(PIXEL_ID) == 1, f"{rel}: ID пикселя встречается {text.count(PIXEL_ID)} раз"
    assert text.count("fbq('track', 'PageView')") == 1, f"{rel}: PageView не ровно 1 раз"
    assert "fbevents.js" in text, f"{rel}: нет загрузчика пикселя"
    assert text.count("<title>") == 1, f"{rel}: <title> поехал"

    path.write_text(text, encoding="utf-8")
    after = len(path.read_bytes())
    print(f"{rel}: {before} -> {after} bytes | {'; '.join(notes)}")
    return before, after, notes


def main() -> int:
    for rel in PAGES:
        patch(rel)
    print("OK: Meta Pixel", PIXEL_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
