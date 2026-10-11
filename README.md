# LeadUp AI — landing pages

Мультилендинги для A/B тестов Meta Ads. Один вебхук на все страницы; страница сама себя идентифицирует.

## Структура

```
<landing_id>/<variant_id>/index.html
```

- `landing_id` — первый уровень (например, `ai-course`)
- `variant_id` — второй уровень, вариант A/B (например, `v1`, `v2`)

Пример: `ai-course/v1/index.html` → https://leadup-ai.github.io/leadup-landings/ai-course/v1/

## Передача лидов

Все формы POST-ят JSON на единый вебхук n8n:
`https://n8n.flowstudio.cloud/webhook/landing-leads`

Обязательное поле — `event_name`. Анти-спам — `honeypot` (должно быть пустым).

Поля заявки: `name`, `email`, `messenger`, `plan`, `consent`, `consent_text_version`.
Страница: `landing_id`, `variant_id`, `page_url`, `page_lang`.
Атрибуция: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `fbclid`, `referrer`, `fbp`, `fbc`.
Служебные: `event_id`, `ts`.

События воронки: `page_view`, `cta_click`, `form_start`, `lead`, `form_error`.
Метрики по варианту: CTR страницы = `cta_click/page_view`; конверсия = `lead/page_view`.

## Meta Pixel

Единый пиксель для всех лендингов: **`28714651278203294`** — «MBS Ads AI Agent», привязан к рекламному кабинету `act_1421380076636776`. Задаётся в `window.__LANDING__.pixel_id` внутри `index.html`.

- Загрузчик `fbevents.js`, `fbq('init', id)` и `fbq('track', 'PageView')` есть на каждой странице и срабатывают только если `pixel_id` задан (страница без ID остаётся рабочей).
- Событие `Lead` (с `eventID` для дедупликации с Conversions API) отправляется при успешной заявке.
- Массовое подключение или смена ID: `python3 tools/pixel/set_pixel.py` — идемпотентный скрипт: обновляет `pixel_id`, переносит страницы со старых ID из `PREVIOUS_PIXEL_IDS` и при необходимости добавляет загрузчик и `PageView`.
- Пока ID не задан — заявки всё равно логируются через вебхук.

Страницы с подключённым пикселем: `ai-course/v1`, `ai-practicum/v1`, `lab/ai-longread/v1`, `lab/ai-longread/v2`, `lab/cosmo-ai/v1`, `lab/cosmo-ai/v2`.

Предыдущий ID `581042486157971` («Пиксель компании MBS») не привязан к кабинету `act_1421380076636776` и больше не используется.
