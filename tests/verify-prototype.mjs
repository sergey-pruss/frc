import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = fileURLToPath(new URL('..', import.meta.url));

const checks = [
  ['shop home exists', existsSync(join(root, 'index.html'))],
  ['seo doc moved', existsSync(join(root, 'seo/index.html'))],
  ['catalog page', existsSync(join(root, 'catalog/index.html'))],
  ['category futbolki', existsSync(join(root, 'catalog/futbolki/index.html'))],
  ['product page', existsSync(join(root, 'product/futbolka-oranzhevaya/index.html'))],
  ['collection capsule', existsSync(join(root, 'collections/russia-capsule/index.html'))],
  ['delivery page', existsSync(join(root, 'delivery/index.html'))],
  ['shop styles', existsSync(join(root, 'assets/shop.css'))],
  [
    'home has products',
    /Футболка «Оранжевая линия»/.test(readFileSync(join(root, 'index.html'), 'utf8')),
  ],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  for (const [name] of failed) console.error(`FAIL: ${name}`);
  process.exit(1);
}
for (const [name] of checks) console.log(`PASS: ${name}`);
