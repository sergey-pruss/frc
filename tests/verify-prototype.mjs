import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));
const home = readFileSync(join(root, 'index.html'), 'utf8');
const shopCss = readFileSync(join(root, 'assets/shop.css'), 'utf8');
const siteJs = readFileSync(join(root, 'assets/site.js'), 'utf8');
const contentPy = readFileSync(join(root, 'scripts/content.py'), 'utf8');

const productDirs = readdirSync(join(root, 'product')).filter((name) =>
  existsSync(join(root, 'product', name, 'index.html')),
);

const requiredStructure = [
  'catalog/index.html',
  'product/futbolka-oranzhevaya/index.html',
  'product/mystery-box/index.html',
  'product/bomber-fluffy/index.html',
  'about/index.html',
  'delivery/index.html',
  'blog/index.html',
  'stores/index.html',
  'cart/index.html',
  'checkout/index.html',
  'search/index.html',
  '404.html',
  'collections/index.html',
  'gift-cards/index.html',
];

const checks = [
  ['shop home exists', existsSync(join(root, 'index.html'))],
  ['seo doc moved', existsSync(join(root, 'seo/index.html'))],
  ['expanded catalog has at least 26 products', productDirs.length >= 26],
  ['all brief structure pages exist', requiredStructure.every((file) => existsSync(join(root, file)))],
  ['shop styles use brand green from guidebook', /--brand-green:\s*#3f5927/.test(shopCss)],
  ['shop uses Golos Text', /Golos Text/.test(shopCss)],
  [
    'home follows client references presentation',
    /hero-mosaic/.test(home) &&
      /hero-nav-cta/.test(home) &&
      /btn-xl/.test(home) &&
      /editorial-strip/.test(home) &&
      /category-visual-grid/.test(home),
  ],
  [
    'header nav matches presentation',
    /label: "Мерч"/.test(siteJs) &&
      /Подарочные карты/.test(siteJs) &&
      /Кабинет/.test(siteJs),
  ],
  [
    'public chrome uses delivery topbar',
    /site-topbar/.test(siteJs) && !/prototype-ribbon/.test(siteJs),
  ],
  [
    'known broken image URL is absent',
    !/photo-1622445275463-79c04033fbaa/.test(contentPy),
  ],
  [
    'cart checkout search templates are styled',
    /\.checkout-layout/.test(shopCss) &&
      /\.search-panel/.test(shopCss) &&
      /\.account-shell/.test(shopCss),
  ],
  [
    'footer has Serenity credit',
    /Сделано в Serenity/.test(siteJs) && existsSync(join(root, 'assets/serenity-logo.svg')),
  ],
  [
    'header uses client wordmark',
    /rossiya-wordmark\.svg/.test(siteJs) && existsSync(join(root, 'assets/rossiya-wordmark.svg')),
  ],
  [
    'about includes brand quote',
    /brand-quote\.jpeg/.test(readFileSync(join(root, 'about/index.html'), 'utf8')),
  ],
  [
    'about mentions brand colors from guidebook',
    /Pantone 4216/.test(readFileSync(join(root, 'about/index.html'), 'utf8')),
  ],
  [
    'product pages include schema.org Product',
    /"@type": "Product"/.test(readFileSync(join(root, 'product/futbolka-oranzhevaya/index.html'), 'utf8')),
  ],
  ['custom domain targets frc.sergeypruss.ru', readFileSync(join(root, 'CNAME'), 'utf8').trim() === 'frc.sergeypruss.ru'],
  [
    'home canonical and favicon',
    /<link rel="canonical" href="https:\/\/frc\.sergeypruss\.ru\/">/.test(home) &&
      existsSync(join(root, 'assets/favicon.png')),
  ],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  for (const [name] of failed) console.error(`FAIL: ${name}`);
  process.exit(1);
}
for (const [name] of checks) console.log(`PASS: ${name}`);
