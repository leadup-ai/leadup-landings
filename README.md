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

Пиксель подключается в `window.__LANDING__.pixel_id` внутри `index.html`.
Пока ID не задан — заявки всё равно логируются через вебхук.
