# Отчёт по изменениям в проекте FRC

**Дата:** 27 мая 2026  
**Ветка:** `main`  
**Коммиты за день:** 4 (запушены) + локальные правки (не закоммичены)

---

## Сводная таблица

| № | Область | Что сделали | Где изменилось | Тип |
|---|---------|-------------|----------------|-----|
| 1 | Анализ конкурентов | Исправлена разметка секций на странице | `analysis/index.html` | Изменено |
| 2 | Дизайн-прототип | Весь клиентский прототип перенесён в отдельную зону `/design/`, скрыт от публичного сайта | `design/**` (каталог, товары, корзина, профиль и др.), `assets/site.js`, `index.html` | Перенос + добавлено |
| 3 | Прототип / assets | Починены пути к CSS/JS/картинкам внутри `/design/` | `design/**/*.html`, `assets/site.js` | Изменено |
| 4 | Wordstat / семантика | Обновлены выгрузки частот, семена и исключения для каталога | `data/catalog-keywords-top10.json`, `data/catalog-wordstat-*.json`, `data/wordstat-seeds-catalog.txt`, `data/wordstat-exclude-patterns.txt`, `data/wordstat-scraped-catalog.json` | Добавлено / изменено |
| 5 | SEO-стратегия | Доработана страница стратегии после встречи | `seo/index.html` | Изменено |
| 6 | Контент-стратегия | Новый раздел с материалами по конкурентам и стратегии | `content-strategy/index.html`, `data/content-strategy-*` | **Добавлено** |
| 7 | Каталог (прототип) | Убраны лишние страницы «цвет × размер»; фильтры по смыслу (цвет, размер, капюшон, молния и т.д.) | `design/catalog/futbolki/`, `hudi/`, `kurtki/`, `svitshoty/`, `vetrovki/`, `aksessuary/` | Удалено / переименовано / **добавлено** |
| 8 | Стили и UI | Мелкие правки витрины в прототипе | `assets/shop.css`, `assets/site.js` | Изменено |
| 9 | Скрипты сборки | Генератор прототипа, wordstat, экспорт фильтров в CSV, синк контент-стратегии | `scripts/generate-prototype.py`, `build-catalog-wordstat.py`, `export-static-filters-csv.py`, `sync-content-strategy.py`, `render-catalog-tables.py` | Изменено / **добавлено** |
| 10 | Google Drive | Синхронизация SEO-материалов и отчёта ОС менеджеров (итерация 26–27.05) | `scripts/sync-seo-drive.mjs`, `scripts/sync-manager-feedback-report.mjs` | **Добавлено** |
| 11 | Тесты | Проверки HTML и прототипа под новую структуру | `tests/verify-html.mjs`, `tests/verify-prototype.mjs` | Изменено |
| 12 | npm | Новые команды для PDF и выгрузки отчётов в Drive | `package.json` | Изменено (локально) |
| 13 | PDF-отчёты | PDF собираются напрямую из `seo/` и `analysis/` (print-стили), без промежуточных HTML | `scripts/generate-pdf.mjs` → `export/*.pdf` | Изменено (локально) |
| 14 | Drive: PDF | Скрипт заливки PDF в папку SEO на Google Drive | `scripts/sync-seo-reports-drive.mjs` | **Добавлено** (локально) |
| 15 | ОС менеджеров | Фикс фильтра в таблице, переименование файла отчёта | `scripts/sync-manager-feedback-report.mjs` | Изменено (локально) |
| 16 | Watch | Обновлён dev-watch под новые скрипты | `scripts/watch.mjs` | Изменено (локально) |

---

## Коммиты (хронология)

| Время | Hash | Сообщение |
|-------|------|-----------|
| 10:32 | `e547f2f` | Исправить разметку разделов анализа конкурентов |
| 10:39 | `97fd5b9` | Спрятать дизайн-прототип от клиента и вынести его в `/design/` |
| 10:44 | `9e20bad` | Исправить пути к assets для прототипа в `/design/` |
| 11:13 | `af5be3d` | Доработать SEO после встречи: семантика, фильтры и прототип каталога |

---

## Ключевые добавления

- `content-strategy/index.html` — страница контент-стратегии
- `data/content-strategy-competitors.csv`, `content-strategy-doc.txt`, `content-strategy-meta.json`
- `design/catalog/hudi/` — раздел «Худи» (латиница `hudi`, раньше `khudi`)
- Семантические лендинги каталога: `belye/`, `chernye/`, `s-printom/`, `bolshie-razmery/`, `na-molnii/`, `s-kapyushonom/`, `demisezonnye/` и др.
- `scripts/sync-content-strategy.py`, `sync-seo-drive.mjs`, `sync-manager-feedback-report.mjs`, `export-static-filters-csv.py`

## Ключевые удаления / упрощения

- Сотни страниц вида `цвет-размер` (например `futbolki/belye-m/`) — заменены осмысленными фильтрами
- Публичные копии страниц магазина из корня — остались в `design/` как внутренний прототип

---

## Текст для Slack

См. файл `2026-05-27-daily-changes-slack.txt` в этой же папке.
