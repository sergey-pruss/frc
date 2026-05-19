import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));

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
  ['shop styles', existsSync(join(root, 'assets/shop.css'))],
  [
    'home applies client brief principles',
    /В меру современно, аккуратно, без провокаций/.test(readFileSync(join(root, 'index.html'), 'utf8')),
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
  ['custom domain is disabled', !existsSync(join(root, 'CNAME'))],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  for (const [name] of failed) console.error(`FAIL: ${name}`);
  process.exit(1);
}
for (const [name] of checks) console.log(`PASS: ${name}`);
