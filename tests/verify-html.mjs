import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));
const html = readFileSync(join(root, 'seo/index.html'), 'utf8');
const css = readFileSync(join(root, 'assets/styles.css'), 'utf8');
const robots = readFileSync(join(root, 'robots.txt'), 'utf8');
const catalogWordstatPath = join(root, 'data/catalog-wordstat-100plus.json');
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
  ['transactional semantic core exists', /id="transactional-core"/.test(html) && /Транзакционная семантика каталога/.test(html)],
  ['frequency threshold is 100 plus', /собираем запросы от 100 показов\/мес/.test(html) && /В ядро берем запросы от 100 показов\/мес и выше/.test(html)],
  ['keyword tables use query, frequency and priority columns', /Ключевые запросы 100\+ для структуры/.test(html) && /Ключевые запросы для статичных фильтров/.test(html) && /<th>Запрос<\/th>\s*<th>Частота<\/th>/.test(html) && /<th>Как использовать<\/th>\s*<th>Приоритет<\/th>/.test(html)],
  ['duplicate semantic mask table is absent', !/Запросы для снятия частотности/.test(html)],
  ['wordstat frequencies are included', hasFrequency('худи купить', 16847) && hasFrequency('футболки купить', 191270) && hasFrequency('купить подарочный сертификат', 33502)],
  ['full wordstat export exists', catalogWordstat && catalogWordstat.total_clean_queries >= 1000 && catalogWordstat.threshold === '100 показов/мес и выше'],
  ['semantic clusters include all launch groups', /ветровка купить/.test(html) && /значок купить/.test(html) && /подарочный сертификат купить/.test(html)],
  ['semantic collection masks are expanded', /Поле сбора семантики 100\+ показов/.test(html) && /свитшот на флисе/.test(html) && /тканевый шопер/.test(html)],
  ['top 20 competitor section exists', /id="top-competitors"/.test(html) && /Топ-20 конкурентов по семантике каталога/.test(html)],
  ['top 20 competitor table has key domains', /wildberries\.ru/.test(html) && /ozon\.ru/.test(html) && /vsemayki\.ru/.test(html) && /putin-team\.ru/.test(html) && /gloryseason\.ru/.test(html)],
  ['competitor domains are clickable external links', /<a href="https:\/\/www\.wildberries\.ru\/" target="_blank" rel="noopener">wildberries\.ru<\/a>/.test(html) && /<a href="https:\/\/www\.ozon\.ru\/" target="_blank" rel="noopener">ozon\.ru<\/a>/.test(html) && /<a href="https:\/\/putin-team\.ru\/" target="_blank" rel="noopener">putin-team\.ru<\/a>/.test(html)],
  ['page theses section exists', /id="page-theses"/.test(html) && /Тезисы по типам страниц/.test(html)],
  ['static filter strategy exists', /id="static-filters"/.test(html) && /\/catalog\/hudi\/krasnye-xs\//.test(html) && /Категория \+ размер/.test(html)],
  ['static filter frequencies are included', hasFrequency('купить белую футболку', 6880) && hasFrequency('купить черный худи', 568) && hasFrequency('купить куртку размера', 9102)],
  ['static filter usage is explained', /Правила индексации фильтров/.test(html) && /какие типы URL должны быть\s+индексируемыми/.test(html) && /\/catalog\/futbolki\/belye\//.test(html)],
  ['static filter canonical examples are labeled and escaped', /Пример canonical для статичного фильтра/.test(html) && /&lt;link rel="canonical"/.test(html) && /&lt;meta name="robots" content="noindex, follow"&gt;/.test(html)],
  ['meta generation rules exist', /id="generation-rules"/.test(html) && /Пример генерации мета-тегов/.test(html) && /&lt;title&gt;Худи/.test(html)],
  ['structured data section exists', /id="structured-data"/.test(html) && /Пример Product JSON-LD/.test(html) && /"@type": "Product"/.test(html) && /BreadcrumbList/.test(html)],
  ['indexation section exists', /id="indexation"/.test(html) && /Пример robots\.txt/.test(html) && /Пример sitemap\.xml/.test(html) && /Disallow: \/checkout\//.test(html)],
  ['development SEO brief exists', /id="dev-brief"/.test(html) && /SEO-ТЗ для разработки/.test(html)],
  ['technical requirements include schema and sitemap', /Product schema/.test(html) && /sitemap/.test(html) && /canonical/.test(html)],
  ['custom domain CNAME targets frc.serenity-dev.ru', readFileSync(join(root, 'CNAME'), 'utf8').trim() === 'frc.serenity-dev.ru'],
  ['code blocks are styled and spaced', /pre\s*\{/.test(css) && /--code-bg/.test(css) && /\.code-block \+ \.code-block/.test(css)]
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
