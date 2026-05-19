import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));
const html = readFileSync(join(root, 'seo/index.html'), 'utf8');
const css = readFileSync(join(root, 'assets/styles.css'), 'utf8');
const robots = readFileSync(join(root, 'robots.txt'), 'utf8');

const checks = [
  ['document has Russian language', /<html lang="ru">/.test(html)],
  ['page title exists', /<title>SEO-проектирование интернет-магазина Универмаг Россия<\/title>/.test(html)],
  ['meta description exists', /<meta\s+name="description"/.test(html)],
  ['published page is closed from indexing', /<meta name="robots" content="noindex, nofollow">/.test(html)],
  ['robots.txt disallows all crawlers', /User-agent: \*\s+Disallow: \//.test(robots)],
  ['primary semantic core section exists', /Первичная семантика по текущему брифу/.test(html)],
  ['client catalog questions exist', /Вопросы к заказчику: ассортимент и каталог/.test(html) && /Что выясняем сами/.test(html) && /id="client-catalog-questions"/.test(html)],
  ['document table of contents exists', /Содержание/.test(html) && /doc-toc/.test(html) && /href="#client-catalog-questions"/.test(html)],
  ['custom domain CNAME is absent', !existsSync(join(root, 'CNAME'))],
  ['client brand references exist', /Фирменные материалы и референсы клиента/.test(html) && /Герб/.test(html) && /логотип/.test(html)],
  ['brand query cluster exists', /Универмаг Россия/.test(html) && /Национальный центр Россия мерч/.test(html)],
  ['category query cluster exists', /футболки Россия/.test(html) && /свитшоты Россия/.test(html)],
  ['delivery query cluster exists', /доставка по России/.test(html)],
  ['competitor SEO analysis exists', /Глубинный SEO-анализ конкурентов/.test(html)],
  ['Putin Team competitor is covered', /putin-team\.ru/.test(html) && /Глубина каталога/.test(html)],
  ['Glory Season competitor is covered', /gloryseason\.ru/.test(html) && /Коллекционные витрины/.test(html)],
  ['competitor semantic core analysis exists', /Семантическое ядро конкурентов по открытой структуре/.test(html)],
  ['competitor VH and SCH semantics exist', /Основная семантика конкурентов: ВЧ и СЧ \(Wordstat\)/.test(html) && /ВЧ-запросы по кластерам \(на основе Wordstat\)/.test(html) && /СЧ-запросы по кластерам \(на основе Wordstat\)/.test(html)],
  ['competitor wordstat frequencies exist', /putin team \(3/.test(html) && /сезон славы одежда \(514\)/.test(html) && /Показов\/мес/.test(html)],
  ['competitor semantics recommendations exist', /Сводные рекомендации по семантике конкурентов/.test(html)],
  ['semantic recommendations exist', /Рекомендации по семантике для нашего сайта/.test(html)],
  ['commercial semantic modifiers exist', /Коммерческие модификаторы/.test(html)],
  ['site structure recommendations exist', /Рекомендации по структуре сайта/.test(html)],
  ['catalog structure recommendations exist', /Рекомендации по структуре каталога/.test(html)],
  ['content structure recommendations exist', /Рекомендации по структуре контента/.test(html)],
  ['SEO page map section exists', /Карта страниц/.test(html)],
  ['URL structure code block exists', /\/catalog\/futbolki\//.test(html)],
  ['meta tag code sample is escaped', /&lt;meta name="description"/.test(html)],
  ['canonical sample exists', /rel="canonical"|rel=&quot;canonical&quot;|rel=&apos;canonical&apos;|rel=&lt;/.test(html) || /canonical/.test(html)],
  ['schema.org JSON-LD sample exists', /application\/ld\+json/.test(html)],
  ['robots sample exists', /User-agent: \*/.test(html)],
  ['product card requirements exist', /Требования к карточке товара/.test(html)],
  ['code blocks are styled', /pre\s*\{/.test(css) && /--code-bg/.test(css)]
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
