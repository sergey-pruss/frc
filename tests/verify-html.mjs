import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));
const html = readFileSync(join(root, 'seo/index.html'), 'utf8');
const contentStrategyPath = join(root, 'content-strategy/index.html');
const contentStrategy = existsSync(contentStrategyPath)
  ? readFileSync(contentStrategyPath, 'utf8')
  : '';
const css = readFileSync(join(root, 'assets/styles.css'), 'utf8');
const robots = readFileSync(join(root, 'robots.txt'), 'utf8');
const catalogWordstatPath = join(root, 'data/catalog-wordstat-full.json');
const catalogWordstat = existsSync(catalogWordstatPath)
  ? JSON.parse(readFileSync(catalogWordstatPath, 'utf8'))
  : null;

function hasFrequency(phrase, frequency) {
  return new RegExp(`${phrase}(?:\\s*—\\s*|<\\/td>\\s*<td>)${frequency}`).test(html);
}

const checks = [
  ['document has Russian language', /<html lang="ru">/.test(html)],
  ['page title reflects SEO strategy', /<title>SEO-стратегия интернет-магазина Универмаг Россия<\/title>/.test(html)],
  ['meta description exists', /<meta\s+name="description"/.test(html)],
  ['published page is closed from indexing', /<meta name="robots" content="noindex, nofollow">/.test(html)],
  ['SEO document uses crest favicon', /assets\/favicon-32\.png/.test(html) && /apple-touch-icon/.test(html)],
  ['robots.txt disallows all crawlers', /User-agent: \*\s+Disallow: \//.test(robots)],
  ['client questions were removed', !/Вопросы к заказчику/.test(html) && !/Что выясняем сами/.test(html)],
  ['redundant intro explanations are absent', !/Дальше отчет строится только/.test(html) && !/не требует дополнительных\s+вопросов/.test(html) && !/Брендовые запросы убраны из ядра продвижения/.test(html)],
  ['brand query cluster was removed', !/Брендовые<\/td>/.test(html) && !/Национальный центр Россия мерч/.test(html)],
  ['client input section exists', /id="client-input"/.test(html) && /Зафиксированные ответы клиента/.test(html)],
  ['confirmed categories are covered', /Худи/.test(html) && /свитшоты с флисом \/ без флиса/.test(html) && /детские игры/.test(html)],
  ['collections are handled through core structure', /Основная структура: категории и статичные фильтры/.test(html)],
  ['recommended site structure is explicit', /id="recommended-structure"/.test(html) && /Рекомендуемая структура сайта/.test(html) && /\/catalog\/hudi\//.test(html) && /\/catalog\/futbolki\/belye\//.test(html) && /\/gift-cards\//.test(html)],
  ['recommended filters by category block exists', /id="recommended-filters-by-category"/.test(html) && /Рекомендуемые фильтры по категориям/.test(html)],
  ['catalog filter CMS requirements documented', /Требования к фильтрам каталога/.test(html) && /Сотбит/.test(html) && /Yoast SEO/.test(html) && /мультифильтр/.test(html)],
  ['books cluster in keyword table', /<td>Книги<\/td>[\s\S]*?подарочные книги/.test(html)],
  ['excluded badge noise absent from doc', !/значок бмв купить/.test(html) && !/значки купить сайт/.test(html)],
  ['recommended structure has tree code view', /id="recommended-structure-tree"/.test(html) && /Структура сайта в формате дерева/.test(html) && /<pre><code>\/\s*├── catalog\//.test(html) && /└── blog\/\s*# после запуска каталога/.test(html)],
  ['transactional semantic core exists', /id="transactional-core"/.test(html) && /Транзакционная семантика каталога/.test(html)],
  ['frequency threshold is 100 plus', /собираем запросы от 100 показов\/мес/.test(html) && /В ядро берем запросы от 100 показов\/мес и выше/.test(html)],
  ['keyword tables use query, frequency and priority columns', /Ключевые запросы 100\+ для структуры/.test(html) && /Ключевые запросы для статичных фильтров/.test(html) && /<th>Запрос<\/th>\s*<th>Частота<\/th>/.test(html) && /<th>Как использовать<\/th>\s*<th>Приоритет<\/th>/.test(html)],
  ['duplicate semantic mask table is absent', !/Запросы для снятия частотности/.test(html)],
  ['wordstat frequencies are included', hasFrequency('худи купить', 16847) && hasFrequency('футболки купить', 191270) && hasFrequency('подарочные книги', 16021)],
  ['full wordstat export exists', catalogWordstat && catalogWordstat.total_clean_queries >= 900 && catalogWordstat.threshold === '100 показов/мес и выше'],
  ['semantic clusters include all launch groups', /ветровка купить/.test(html) && /значок купить/.test(html) && /шопер купить/.test(html) && /детская игра купить/.test(html) && /подарочный сертификат/.test(html) && /подарочные книги/.test(html)],
  ['semantic clusters separate service pages from promotion core', /Итоговая кластеризация семантики по страницам/.test(html) && /как SEO-кластер продвижения не берем на старт/.test(html) && /Служебные страницы с мета-тегами отделены от SEO-кластеров/.test(html)],
  ['semantic collection masks are expanded', /Поле сбора семантики 100\+ показов/.test(html) && /свитшот на флисе/.test(html) && /тканевый шопер/.test(html)],
  ['top 20 competitor section exists', /id="top-competitors"/.test(html) && /Топ-20 конкурентов по семантике каталога/.test(html)],
  ['top 20 competitor table has key domains', /wildberries\.ru/.test(html) && /ozon\.ru/.test(html) && /vsemayki\.ru/.test(html) && /putin-team\.ru/.test(html) && /gloryseason\.ru/.test(html)],
  ['semantic competitors are separated from direct competitors', /семантические конкуренты/.test(html) && /[Пп]рямые конкуренты/.test(html) && /Маркетплейсы оставляем/.test(html)],
  ['ux competitor summary covers all 20 competitors', /Проведён детальный аудит 20 конкурентов из 4 сегментов/.test(html) && !/детальный аудит 7 прямых конкурентов/.test(html)],
  ['competitor domains are clickable external links', /<a href="https:\/\/www\.wildberries\.ru\/" target="_blank" rel="noopener">wildberries\.ru<\/a>/.test(html) && /<a href="https:\/\/www\.ozon\.ru\/" target="_blank" rel="noopener">ozon\.ru<\/a>/.test(html) && /<a href="https:\/\/putin-team\.ru\/" target="_blank" rel="noopener">putin-team\.ru<\/a>/.test(html)],
  ['page theses section exists', /id="page-theses"/.test(html) && /Тезисы по типам страниц/.test(html)],
  ['static filter strategy exists', /id="static-filters"/.test(html) && /\/catalog\/hudi\/krasnye\//.test(html) && /Категория \+ размер/.test(html) && /Категория \+ цвет \+ размер[\s\S]*<td>Нет<\/td>/.test(html)],
  ['static filter frequencies are included', hasFrequency('купить белую футболку', 6880) && hasFrequency('купить черный худи', 568) && hasFrequency('купить куртку размера', 9102)],
  ['static filter usage is explained', /Правила индексации фильтров/.test(html) && /динамическими AJAX-фильтрами/.test(html) && /\/catalog\/futbolki\/belye\//.test(html)],
  ['static filter canonical examples are labeled and escaped', /Пример canonical для статичного фильтра/.test(html) && /&lt;link rel="canonical"/.test(html) && /&lt;meta name="robots" content="noindex, follow"&gt;/.test(html)],
  ['meta generation rules exist', /id="generation-rules"/.test(html) && /Пример генерации мета-тегов/.test(html) && /Откуда берутся значения в шаблонах/.test(html) && /&lt;title&gt;Худи/.test(html)],
  ['page-level meta tag table exists', /id="meta-tags-by-page"/.test(html) && /Мета-теги по страницам/.test(html) && /\/catalog\/hudi\//.test(html) && /Худи — купить с доставкой по России/.test(html) && /Подарочный сертификат Универмага «Россия»/.test(html)],
  ['page-level meta tags include modern head fields', /Open Graph \/ Twitter/.test(html) && /Canonical/.test(html) && /Robots/.test(html) && /og:title=Title/.test(html) && /twitter:card=summary_large_image/.test(html) && /OG image 1200x630/.test(html) && /BreadcrumbList, ItemList/.test(html)],
  ['structured data section exists', /id="structured-data"/.test(html) && /Пример Product JSON-LD/.test(html) && /"@type": "Product"/.test(html) && /BreadcrumbList/.test(html) && /Schema.org Validator/.test(html) && /Rich Results Test/.test(html)],
  ['indexation section exists', /id="indexation"/.test(html) && /Пример robots\.txt/.test(html) && /Пример sitemap\.xml/.test(html) && /Disallow: \/checkout\//.test(html) && /Disallow: \/\*\?filter=/.test(html)],
  ['development handoff is framed as post-approval constraints', /id="implementation-constraints"/.test(html) && /Что передать в разработку после согласования/.test(html) && !/id="dev-brief"/.test(html) && /CMS-ТЗ/.test(html)],
  ['technical requirements include schema and sitemap', /Product schema/.test(html) && /sitemap/.test(html) && /canonical/.test(html)],
  ['custom domain CNAME targets frc.serenity-dev.ru', readFileSync(join(root, 'CNAME'), 'utf8').trim() === 'frc.serenity-dev.ru'],
  ['code blocks are styled and spaced', /pre\s*\{/.test(css) && /--code-bg/.test(css) && /\.code-block \+ \.code-block/.test(css)],
  ['seo topbar links to content strategy', /href="\.\.\/content-strategy\/">Контент-стратегия<\/a>/.test(html)],
  ['content strategy page exists', Boolean(contentStrategy)],
  [
    'content strategy page has doc sections and competitor matrix',
    /<title>Контент-стратегия для разработки сайта — Универмаг «Россия»<\/title>/.test(contentStrategy) &&
      /Контент-стратегия для разработки сайта Универмаг/.test(contentStrategy) &&
      /\.toc-grid\s*\{[\s\S]*display:\s*grid/.test(contentStrategy) &&
      /class="cs-matrix-table"/.test(contentStrategy) &&
      /class="table-wrap"/.test(contentStrategy) &&
      /id="matrix-putin-team"/.test(contentStrategy) &&
      /id="tone-of-voice"/.test(contentStrategy) &&
      /class="checklist"/.test(contentStrategy) &&
      /cs-audience-cards/.test(contentStrategy) &&
      /Putin Team/.test(contentStrategy) &&
      /GLORY SEASON/.test(contentStrategy) &&
      /современный российский lifestyle-бренд/.test(contentStrategy) &&
      !/class="cs-block card"/.test(contentStrategy),
  ],
  [
    'content strategy sync metadata is cached',
    existsSync(join(root, 'data/content-strategy-meta.json')) &&
      existsSync(join(root, 'data/content-strategy-doc.txt')),
  ],
];

const failed = checks.filter(([, passed]) => !passed);

if (failed.length > 0) {
  for (const [name] of failed) {
    console.error(`FAIL: ${name}`);
  }
  process.exit(1);
}

for (const [name] of checks) {
  console.log(`PASS: ${name}`);
}
