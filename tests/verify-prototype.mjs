import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));
const home = readFileSync(join(root, 'index.html'), 'utf8');
const shopCss = readFileSync(join(root, 'assets/shop.css'), 'utf8');
const siteJs = readFileSync(join(root, 'assets/site.js'), 'utf8');
const requiredStructure = [
  'catalog/index.html',
  'product/futbolka-oranzhevaya/index.html',
  'about/index.html',
  'delivery/index.html',
  'blog/index.html',
  'blog/kak-vybrat-razmer/index.html',
  'stores/index.html',
  'favorites/index.html',
  'cart/index.html',
  'checkout/index.html',
  'search/index.html',
  '404.html',
  'collections/index.html',
  'loyalty/index.html',
  'gift-cards/index.html',
  'login/index.html',
  'profile/index.html',
  'orders/index.html',
  'wishlist/index.html',
];

const checks = [
  ['shop home exists', existsSync(join(root, 'index.html'))],
  ['seo doc moved', existsSync(join(root, 'seo/index.html'))],
  ['catalog page', existsSync(join(root, 'catalog/index.html'))],
  ['category longslivy', existsSync(join(root, 'catalog/longslivy/index.html'))],
  ['catalog new', existsSync(join(root, 'catalog/new/index.html'))],
  ['product page', existsSync(join(root, 'product/futbolka-oranzhevaya/index.html'))],
  ['all 11 products', existsSync(join(root, 'product/podarochnyj-nabor/index.html'))],
  ['collection mystery', existsSync(join(root, 'collections/mystery-box/index.html'))],
  ['delivery page', existsSync(join(root, 'delivery/index.html'))],
  ['contacts', existsSync(join(root, 'contacts/index.html'))],
  ['sizes', existsSync(join(root, 'sizes/index.html'))],
  ['loyalty', existsSync(join(root, 'loyalty/index.html'))],
  ['corporate', existsSync(join(root, 'corporate/index.html'))],
  ['blog article', existsSync(join(root, 'blog/kak-vybrat-razmer/index.html'))],
  ['all brief structure pages exist', requiredStructure.every((file) => existsSync(join(root, file)))],
  ['shop styles', existsSync(join(root, 'assets/shop.css'))],
  [
    'home looks like final shop, not internal prototype',
    /Универмаг «Россия»/.test(home) &&
      /спокойная современная витрина/.test(home) &&
      !/SEO-ТЗ|по практикам конкурентов|Прототип учитывает/.test(home),
  ],
  [
    'audience cards have real grid layout',
    /\.audience-grid\s*\{[\s\S]*display:\s*grid/.test(shopCss) &&
      /grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/.test(shopCss),
  ],
  [
    'public chrome does not say prototype',
    !/Прототип интернет-магазина|SEO-проектирование \(ТЗ\)|Прототип фиксирует/.test(siteJs),
  ],
  [
    'known broken image URL is absent',
    !/photo-1622445275463-79c04033fbaa/.test(readFileSync(join(root, 'scripts/content.py'), 'utf8')),
  ],
  [
    'cart checkout search and account templates are styled',
    /\.checkout-layout/.test(shopCss) &&
      /\.search-panel/.test(shopCss) &&
      /\.account-shell/.test(shopCss) &&
      /\.store-grid/.test(shopCss),
  ],
  [
    'search page includes result and empty states',
    /Результаты поиска/.test(readFileSync(join(root, 'search/index.html'), 'utf8')) &&
      /Ничего не найдено/.test(readFileSync(join(root, 'search/index.html'), 'utf8')),
  ],
  [
    'header links key ecommerce pages',
    /stores\//.test(siteJs) && /favorites\//.test(siteJs) && /cart\//.test(siteJs) && /search\//.test(siteJs),
  ],
  [
    'product has long description',
    /Плотный хлопок/.test(
      readFileSync(join(root, 'product/futbolka-oranzhevaya/index.html'), 'utf8'),
    ),
  ],
  [
    'about page includes brand references',
    /Фирменные материалы и референсы/.test(readFileSync(join(root, 'about/index.html'), 'utf8')) &&
      /Герб Универмага/.test(readFileSync(join(root, 'about/index.html'), 'utf8')),
  ],
  [
    'product pages include schema.org Product',
    /"@type": "Product"/.test(readFileSync(join(root, 'product/futbolka-oranzhevaya/index.html'), 'utf8')),
  ],
  ['custom domain targets frc.sergeypruss.ru', readFileSync(join(root, 'CNAME'), 'utf8').trim() === 'frc.sergeypruss.ru'],
  [
    'home canonical and favicon use custom domain and crest',
    /<link rel="canonical" href="https:\/\/frc\.sergeypruss\.ru\/">/.test(home) &&
      /assets\/favicon-32\.png/.test(home) &&
      existsSync(join(root, 'assets/favicon.png')) &&
      existsSync(join(root, 'assets/apple-touch-icon.png')),
  ],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  for (const [name] of failed) console.error(`FAIL: ${name}`);
  process.exit(1);
}
for (const [name] of checks) console.log(`PASS: ${name}`);
