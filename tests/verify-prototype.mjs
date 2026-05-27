import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import vm from 'node:vm';

const root = fileURLToPath(new URL('..', import.meta.url));
const shopRoot = join(root, 'design');
const home = readFileSync(join(shopRoot, 'index.html'), 'utf8');
const shopCss = readFileSync(join(root, 'assets/shop.css'), 'utf8');
const siteJs = readFileSync(join(root, 'assets/site.js'), 'utf8');
const contentPy = readFileSync(join(root, 'scripts/content.py'), 'utf8');
const generatorPy = readFileSync(join(root, 'scripts/generate-prototype.py'), 'utf8');
const productPage = readFileSync(join(shopRoot, 'product/kurtka-veter/index.html'), 'utf8');

function sectionCardCount(title) {
  const match = home.match(new RegExp(`<section class="apple-shop-preview">[\\s\\S]*?<h2>${title}<\\/h2>[\\s\\S]*?<\\/section>`));
  return match ? (match[0].match(/product-card--editorial/g) || []).length : 0;
}

function productSectionCardCount(title) {
  const match = productPage.match(new RegExp(`<section class="apple-shop-preview">[\\s\\S]*?<h2>${title}<\\/h2>[\\s\\S]*?<\\/section>`));
  return match ? (match[0].match(/product-card--editorial/g) || []).length : 0;
}

function sectionHtml(className) {
  const match = home.match(new RegExp(`<section class="${className}">[\\s\\S]*?<\\/section>`));
  return match ? match[0] : '';
}

const homeCategorySection = sectionHtml('apple-category-band');

const productDirs = readdirSync(join(shopRoot, 'product')).filter((name) =>
  existsSync(join(shopRoot, 'product', name, 'index.html')),
);
const generatedProductImages = readdirSync(join(root, 'assets/generated/products')).filter((name) =>
  /\.jpe?g$/.test(name),
);
const catalogDirs = readdirSync(join(shopRoot, 'catalog'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name);

function jpegSize(file) {
  const buffer = readFileSync(file);
  let offset = 2;
  while (offset < buffer.length) {
    if (buffer[offset] !== 0xff) break;
    const marker = buffer[offset + 1];
    const length = buffer.readUInt16BE(offset + 2);
    if (marker >= 0xc0 && marker <= 0xc3) {
      return { height: buffer.readUInt16BE(offset + 5), width: buffer.readUInt16BE(offset + 7) };
    }
    offset += 2 + length;
  }
  throw new Error(`Cannot read JPEG size: ${file}`);
}

const generatedImagesAreCoverCards = generatedProductImages.every((name) => {
  const size = jpegSize(join(root, 'assets/generated/products', name));
  return size.width === 800 && size.height === 1000;
});

function runTopbarHarness(initialCookie = '') {
  const classNames = new Set();
  const cookieJar = new Map();
  initialCookie.split(';').map((item) => item.trim()).filter(Boolean).forEach((item) => {
    const [name, value] = item.split('=');
    cookieJar.set(name, value);
  });

  let topbar = null;
  const closeButton = {
    listener: null,
    addEventListener(type, listener) {
      if (type === 'click') this.listener = listener;
    },
    click() {
      this.listener?.();
    },
  };
  const headerMount = {
    html: '',
    set innerHTML(value) {
      this.html = value;
      topbar = /class="site-topbar"/.test(value)
        ? { removed: false, remove() { this.removed = true; } }
        : null;
    },
    get innerHTML() {
      return this.html;
    },
    querySelector(selector) {
      if (selector === '[data-topbar-dismiss]') return topbar && !topbar.removed ? closeButton : null;
      if (selector === '.site-topbar') return topbar && !topbar.removed ? topbar : null;
      return null;
    },
  };
  const document = {
    currentScript: { dataset: { depth: '0' }, src: 'https://frc.serenity-dev.ru/design/assets/site.js?v=test' },
    body: {
      classList: {
        add: (...names) => names.forEach((name) => classNames.add(name)),
        remove: (...names) => names.forEach((name) => classNames.delete(name)),
        toggle(name, force) {
          const shouldAdd = force === undefined ? !classNames.has(name) : Boolean(force);
          if (shouldAdd) classNames.add(name);
          else classNames.delete(name);
          return shouldAdd;
        },
        contains: (name) => classNames.has(name),
      },
    },
    querySelector(selector) {
      if (selector === '[data-site-header]') return headerMount;
      if (selector === '[data-site-footer]') return null;
      return null;
    },
    querySelectorAll() {
      return [];
    },
    get cookie() {
      return Array.from(cookieJar, ([name, value]) => `${name}=${value}`).join('; ');
    },
    set cookie(value) {
      const [pair] = value.split(';');
      const [name, cookieValue] = pair.split('=');
      cookieJar.set(name, cookieValue);
    },
  };
  const window = {
    scrollY: 0,
    innerHeight: 900,
    matchMedia: () => ({ matches: true }),
    requestAnimationFrame: (callback) => callback(),
    addEventListener() {},
  };

  vm.runInNewContext(siteJs, { document, window, alert() {} });

  return {
    get cookie() {
      return document.cookie;
    },
    get topbarVisible() {
      return Boolean(headerMount.querySelector('.site-topbar'));
    },
    hasBodyClass: (name) => classNames.has(name),
  };
}

function topbarAlwaysVisibleWithoutDismiss() {
  const firstVisit = runTopbarHarness();
  const nextVisit = runTopbarHarness('frc_project_topbar_hidden=1');

  return firstVisit.topbarVisible &&
    nextVisit.topbarVisible &&
    !firstVisit.hasBodyClass('site-topbar-hidden') &&
    !nextVisit.hasBodyClass('site-topbar-hidden') &&
    !/data-topbar-dismiss/.test(siteJs) &&
    !/frc_project_topbar_hidden/.test(siteJs);
}

const requiredStructure = [
  'design/catalog/index.html',
  'design/product/futbolka-oranzhevaya/index.html',
  'design/product/mystery-box/index.html',
  'design/product/bomber-fluffy/index.html',
  'design/about/index.html',
  'design/delivery/index.html',
  'design/blog/index.html',
  'design/stores/index.html',
  'design/cart/index.html',
  'design/checkout/index.html',
  'design/search/index.html',
  '404.html',
  'design/collections/index.html',
  'design/gift-cards/index.html',
];

const checks = [
  ['shop home exists under design', existsSync(join(shopRoot, 'index.html'))],
  [
    'site root is gated and sends authed users to seo',
    /frc-gate-v1/.test(readFileSync(join(root, 'index.html'), 'utf8')) &&
      readFileSync(join(root, 'gate/index.html'), 'utf8').includes('gate-form'),
  ],
  ['seo doc moved', existsSync(join(root, 'seo/index.html'))],
  [
    'client docs hide design prototype tab',
    !/Дизайн-прототип/.test(readFileSync(join(root, 'seo/index.html'), 'utf8')) &&
      !/Дизайн-прототип/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')),
  ],
  [
    'internal design route exposes project doc tabs',
    /Дизайн-прототип/.test(siteJs) &&
      /docsRoot/.test(siteJs) &&
      /href="\$\{docsRoot\}seo\/"/.test(siteJs) &&
      /href="\$\{docsRoot\}content-strategy\/"/.test(siteJs),
  ],
  [
    'client docs expose content strategy tab',
    /href="\.\.\/content-strategy\/">Контент-стратегия<\/a>/.test(
      readFileSync(join(root, 'seo/index.html'), 'utf8'),
    ) &&
      /href="\.\.\/content-strategy\/">Контент-стратегия<\/a>/.test(
        readFileSync(join(root, 'analysis/index.html'), 'utf8'),
      ),
  ],
  ['expanded catalog has at least 26 products', productDirs.length >= 26],
  ['all products have generated local images', generatedProductImages.length >= productDirs.length],
  ['generated product images are full 4:5 card crops', generatedImagesAreCoverCards],
  ['catalog uses local generated product images', /\/assets\/generated\/products\//.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) && !/images\.unsplash\.com/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8'))],
  ['all brief structure pages exist', requiredStructure.every((file) => existsSync(join(root, file)))],
  ['shop styles use brand green from guidebook', /--brand-green:\s*#3f5927/.test(shopCss)],
  ['shop uses Golos Text', /Golos Text/.test(shopCss)],
  [
    'home uses Apple-style campaign structure',
      /apple-hero/.test(home) &&
      /apple-feature/.test(home) &&
      /apple-store-grid/.test(home) &&
      /assets\/generated\/editorial\/home-hero-apple-wall\.png/.test(home),
  ],
  [
    'home hero headline follows requested spacing and green title',
    /<section class="apple-hero">[\s\S]*<div class="apple-hero__content"[\s\S]*<h1>Мерч — как любимая вещь<\/h1>/.test(home) &&
      !/<section class="apple-hero">[\s\S]*<p class="eyebrow">Универмаг «Россия»<\/p>[\s\S]*<\/section>/.test(home) &&
      /\.apple-hero h1\s*\{[\s\S]*margin:\s*0 0 clamp\(22px,\s*2\.2vw,\s*32px\);[\s\S]*color:\s*var\(--brand-green\);/.test(shopCss) &&
      /\.apple-hero p:not\(\.eyebrow\)\s*\{[\s\S]*margin:\s*0 0 clamp\(34px,\s*3\.2vw,\s*48px\);/.test(shopCss) &&
      /\.eyebrow\s*\{[\s\S]*color:\s*var\(--muted\);/.test(shopCss) &&
      /\.apple-feature h2\s*\{[\s\S]*color:\s*var\(--brand-green\);/.test(shopCss),
  ],
  [
    'home product rails follow Apple Store layout with model first card',
      /product-card--editorial product-card--model/.test(home) &&
      /assets\/generated\/fashion\/futbolki-models\.png/.test(home) &&
      /assets\/generated\/fashion\/khudi-models\.png/.test(home) &&
      !/<section class="apple-shop-preview">[\s\S]*\/assets\/generated\/products\//.test(home) &&
      /<h2>Новинки<\/h2>[\s\S]*<h2>Популярное<\/h2>/.test(home) &&
      (home.match(/apple-shop-preview/g) || []).length >= 2 &&
      sectionCardCount('Новинки') >= 8 &&
      sectionCardCount('Популярное') >= 8 &&
      /apple-shop-preview \.apple-store-grid\s*\{[\s\S]*display:\s*flex;[\s\S]*overflow-x:\s*auto;[\s\S]*scroll-snap-type:\s*x mandatory;/.test(shopCss) &&
      /\.apple-shop-preview \.apple-store-grid\s*\{[\s\S]*width:\s*100vw;[\s\S]*margin-left:\s*calc\(-1 \* max\(16px,\s*\(100vw - 1180px\) \/ 2\)\);[\s\S]*padding:\s*0 max\(16px,\s*\(100vw - 1180px\) \/ 2\) 22px;[\s\S]*scroll-padding-left:\s*max\(16px,\s*\(100vw - 1180px\) \/ 2\);/.test(shopCss) &&
      /\.apple-store-grid \.product-card--editorial\s*\{[\s\S]*border-radius:\s*28px;[\s\S]*box-shadow:\s*none;/.test(shopCss) &&
      /\.apple-store-grid \.product-card--editorial:hover,[\s\S]*\.apple-store-grid \.product-card--editorial:focus-within\s*\{[\s\S]*box-shadow:\s*none;/.test(shopCss) &&
      /\.apple-store-grid \.product-card--editorial \.product-tag\s*\{[\s\S]*border-radius:\s*999px;[\s\S]*background:\s*var\(--brand-green\);/.test(shopCss) &&
      /\.apple-store-grid \.product-card--editorial \.product-body h3\s*\{[\s\S]*font-size:\s*clamp\(22px,\s*2vw,\s*30px\);/.test(shopCss) &&
      /\.apple-store-grid \.product-card--editorial a\s*\{[\s\S]*flex-direction:\s*column-reverse;/.test(shopCss),
  ],
  [
    'home category block is uniform, model-led, and has no category badges',
    !/category-visual category-visual--wide/.test(home) &&
      /assets\/generated\/fashion\/khudi-models\.png/.test(home) &&
      /assets\/generated\/fashion\/svitshoty-bez-flisa-models\.png/.test(home) &&
      !/category-visual__tag/.test(homeCategorySection) &&
      !/Новинка|Акция|Скидка|Скоро в наличии/.test(homeCategorySection) &&
      !/CATEGORY_TAGS/.test(generatorPy) &&
      !/--category-accent|--category-wash/.test(home) &&
      /\.apple-category-band\s*\{[\s\S]*padding:\s*clamp\(64px,\s*7vw,\s*104px\) 0;/.test(shopCss) &&
      /\.apple-category-row\s*\{[\s\S]*grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\);/.test(shopCss) &&
      /\.apple-category-row \.category-visual\s*\{[\s\S]*min-height:\s*390px;/.test(shopCss) &&
      /\.apple-category-row \.category-visual::before\s*\{[\s\S]*content:\s*"";/.test(shopCss) &&
      !/category-accent|category-wash|color-mix/.test(shopCss),
  ],
  [
    'home merchandising sections use one medium vertical rhythm',
    /\.apple-shop-preview,\s*[\s\S]*?\.apple-category-band,[\s\S]*?\.store-products,[\s\S]*?\{[\s\S]*?padding:\s*clamp\(64px,\s*7vw,\s*104px\) 0;/.test(shopCss) &&
      !/\.apple-category-band\s*\{[\s\S]*padding:\s*clamp\(96px,\s*10vw,\s*148px\) 0;/.test(shopCss),
  ],
  [
    'category photos zoom smoothly on hover and return smoothly',
    /\.category-visual::before\s*\{[\s\S]*background-image:\s*inherit;[\s\S]*transform:\s*scale\(1\);[\s\S]*transition:\s*transform 760ms cubic-bezier\(0\.2,\s*0\.8,\s*0\.2,\s*1\), filter 760ms cubic-bezier\(0\.2,\s*0\.8,\s*0\.2,\s*1\);/.test(shopCss) &&
      /\.category-visual:hover::before,[\s\S]*\.category-visual:focus-visible::before\s*\{[\s\S]*transform:\s*scale\(1\.075\);/.test(shopCss),
  ],
  [
    'site has broader smooth motion layer',
    /html\s*\{[\s\S]*scroll-behavior:\s*smooth;/.test(shopCss) &&
      /@media \(prefers-reduced-motion:\s*no-preference\)\s*\{[\s\S]*transition-duration:\s*220ms;[\s\S]*transition-timing-function:\s*cubic-bezier\(0\.2,\s*0\.8,\s*0\.2,\s*1\);/.test(shopCss) &&
      /\.btn:hover,[\s\S]*\.pill:focus-visible\s*\{[\s\S]*transform:\s*translateY\(-2px\);/.test(shopCss) &&
      /@media \(prefers-reduced-motion:\s*reduce\)/.test(shopCss),
  ],
  [
    'catalog uses Apple Store structure',
    /store-hero/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /store-category-row/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /apple-store-grid--catalog/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /store-filter-panel/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')),
  ],
  [
    'catalog categories match client brief',
    ['hudi', 'svitshoty', 'futbolki', 'vetrovki', 'kurtki', 'aksessuary'].every((slug) =>
      catalogDirs.includes(slug),
    ) &&
      !catalogDirs.includes('khudi') &&
      ['longslivy', 'svitshoty-flis', 'svitshoty-bez-flisa', 'kostyumy', 'kepki', 'sumki', 'podarki'].every((slug) => !catalogDirs.includes(slug)) &&
      /Худи/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /Свитшоты/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /data-subcategory="С флисом"/.test(readFileSync(join(shopRoot, 'catalog/svitshoty/index.html'), 'utf8')) &&
      /data-subcategory="Без флиса"/.test(readFileSync(join(shopRoot, 'catalog/svitshoty/index.html'), 'utf8')) &&
      /data-filter-subcategory="С флисом"/.test(readFileSync(join(shopRoot, 'catalog/svitshoty/index.html'), 'utf8')) &&
      /data-filter-subcategory="Без флиса"/.test(readFileSync(join(shopRoot, 'catalog/svitshoty/index.html'), 'utf8')) &&
      /Аксессуары/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')),
  ],
  [
    'catalog category row fits inside desktop wrap',
    /\.store-category-row\s*\{[\s\S]*display:\s*grid;[\s\S]*grid-template-columns:\s*repeat\(8,\s*minmax\(0,\s*1fr\)\);/.test(shopCss) &&
      /@media \(max-width:\s*960px\)\s*\{[\s\S]*\.store-category-row\s*\{[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\);/.test(shopCss) &&
      /@media \(max-width:\s*560px\)\s*\{[\s\S]*\.store-category-row\s*\{[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\);/.test(shopCss) &&
      !/\.store-category-row\s*\{[\s\S]*overflow-x:\s*auto;/.test(shopCss) &&
      !/\.store-category\s*\{[\s\S]*flex:\s*0\s+0\s+136px;/.test(shopCss),
  ],
  [
    'catalog starts product section after category row',
    !/store-promos/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      !/Купить проще/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /store-category-row[\s\S]*store-products[\s\S]*Все товары/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')),
  ],
  [
    'catalog filter panel sticks near viewport top',
    /\.store-filter-panel\s*\{[\s\S]*position:\s*sticky;[\s\S]*top:\s*10px;/.test(shopCss),
  ],
  [
    'catalog grid keeps three larger product columns',
    /\.apple-store-grid--catalog\s*\{[\s\S]*gap:\s*0;[\s\S]*grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\);[\s\S]*border-top:\s*1px solid #d2d2d7;/.test(shopCss) &&
      !/@media \(min-width:\s*1360px\)\s*\{[\s\S]*\.apple-store-grid--catalog\s*\{[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\);/.test(shopCss) &&
      !/@media \(min-width:\s*1760px\)\s*\{[\s\S]*\.apple-store-grid--catalog\s*\{[\s\S]*grid-template-columns:\s*repeat\(5,\s*minmax\(0,\s*1fr\)\);/.test(shopCss),
  ],
  [
    'catalog cards maximize photos and keep labels over image',
    /\.apple-store-grid--catalog \.product-card--editorial \.product-thumb\s*\{[\s\S]*aspect-ratio:\s*4 \/ 5;[\s\S]*background:\s*transparent;[\s\S]*overflow:\s*hidden;/.test(shopCss) &&
      /\.apple-store-grid--catalog \.product-card--editorial \.product-thumb img\s*\{[\s\S]*object-fit:\s*cover;[\s\S]*padding:\s*0;/.test(shopCss) &&
      /\.apple-store-grid--catalog \.product-card--editorial \.product-tag\s*\{[\s\S]*top:\s*12px;[\s\S]*left:\s*12px;[\s\S]*background:\s*var\(--brand-green\);/.test(shopCss) &&
      /\.apple-store-grid--catalog \.product-card--editorial \.product-body h3\s*\{[\s\S]*font-size:\s*clamp\(15px,\s*1\.05vw,\s*18px\);/.test(shopCss) &&
      /\.apple-store-grid--catalog \.product-card--editorial \.price\s*\{[\s\S]*font-size:\s*15px;/.test(shopCss),
  ],
  [
    'product detail page uses Apple-style model-led gallery',
    /<div class="product-gallery">/.test(readFileSync(join(shopRoot, 'product/bomber-fluffy/index.html'), 'utf8')) &&
      /gallery-main"><img src="\.\.\/\.\.\/\.\.\/assets\/generated\/fashion\/kurtki-models\.png" alt="Бомбер «Объём» на модели/.test(readFileSync(join(shopRoot, 'product/bomber-fluffy/index.html'), 'utf8')) &&
      /gallery-thumbs"><button type="button" class="is-active"><img src="\.\.\/\.\.\/\.\.\/assets\/generated\/fashion\/kurtki-models\.png"/.test(readFileSync(join(shopRoot, 'product/bomber-fluffy/index.html'), 'utf8')) &&
      /\.product-page\s*\{[\s\S]*grid-template-columns:\s*minmax\(0,\s*1\.08fr\) minmax\(360px,\s*0\.92fr\);[\s\S]*gap:\s*clamp\(56px,\s*7vw,\s*96px\);/.test(shopCss) &&
      /\.product-page \.gallery-main\s*\{[\s\S]*border:\s*0;[\s\S]*border-radius:\s*0;[\s\S]*box-shadow:\s*none;/.test(shopCss) &&
      /\.product-info\s*\{[\s\S]*position:\s*sticky;[\s\S]*top:\s*112px;/.test(shopCss),
  ],
  [
    'front-end filters are functional',
    /data-product-card/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /data-filter-size/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      /data-filter-subcategory/.test(readFileSync(join(shopRoot, 'catalog/svitshoty/index.html'), 'utf8')) &&
      /filter-demo-note/.test(readFileSync(join(shopRoot, 'catalog/futbolki/index.html'), 'utf8')) &&
      /applyFilters/.test(siteJs) &&
      /filterSubcategory/.test(siteJs) &&
      /card\.hidden = !shown/.test(siteJs),
  ],
  [
    'static SEO filter page has keyword metadata',
    existsSync(join(shopRoot, 'catalog/futbolki/chernye/index.html')) &&
      /купить черную футболку/.test(readFileSync(join(shopRoot, 'catalog/futbolki/chernye/index.html'), 'utf8')) &&
      /одиночный SEO-фильтр/.test(readFileSync(join(shopRoot, 'catalog/futbolki/chernye/index.html'), 'utf8')) &&
      !existsSync(join(shopRoot, 'catalog/futbolki/chernye-xs/index.html')),
  ],
  [
    'home parallax uses text and image layers',
    /data-parallax="text"/.test(home) &&
      /data-parallax="image"/.test(home) &&
      /animateParallax/.test(siteJs),
  ],
  [
    'hover zoom is applied to product photos',
    /product-card:hover \.product-thumb img/.test(shopCss) && /scale\(1\.075\)/.test(shopCss),
  ],
  [
    'header nav follows brief categories',
    /label: "Одежда"/.test(siteJs) &&
      /href: `\$\{root\}catalog\/#odezhda`, label: "Одежда"/.test(siteJs) &&
      /label: "Аксессуары"/.test(siteJs) &&
      /href: `\$\{root\}catalog\/aksessuary\/`, label: "Аксессуары"/.test(siteJs) &&
      /Подарочные карты/.test(siteJs) &&
      /Кабинет/.test(siteJs) &&
      /<section class="store-products" id="odezhda">/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      existsSync(join(shopRoot, 'catalog', 'aksessuary', 'index.html')),
  ],
  [
    'public chrome uses delivery topbar',
    /site-topbar/.test(siteJs) && !/prototype-ribbon/.test(siteJs),
  ],
  [
    'delivery topbar is always visible without dismiss cookie',
    topbarAlwaysVisibleWithoutDismiss() &&
      !/site-topbar-hidden/.test(shopCss),
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
    'competitor analysis has actionable recommendations',
    /id="conclusions"/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /Что рекомендуем взять в проект/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /Взять в MVP/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /Не брать на старт/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')),
  ],
  [
    'competitor analysis addresses product feedback',
    /id="commercial-seo"/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /Коммерческий SEO-анализ конкурентов/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /Рекомендации для проектирования/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /href="#screenshots"><span class="toc-num">2<\/span> Скриншоты конкурентов/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /id="screenshots"[\s\S]*<span class="section-label">Раздел 2<\/span>[\s\S]*<h2>Скриншоты конкурентов<\/h2>/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      /id="matrix"[\s\S]*<span class="section-label">Раздел 3<\/span>[\s\S]*<h2>Матрица структуры сайтов<\/h2>/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      !/id="screenshots" hidden/.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')) &&
      !/Print-on-demand|print-on-demand|наш прототип|Последний столбец|gap-анализ|Apple-style|JSON-LD schema/i.test(readFileSync(join(root, 'analysis/index.html'), 'utf8')),
  ],
  [
    'requested footer and filter helper texts are removed',
    !/проект Национального центра «Россия»/.test(siteJs) &&
      !/собраны в одном сценарии/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')) &&
      !/без разделения на мужское и женское/.test(readFileSync(join(shopRoot, 'catalog/index.html'), 'utf8')),
  ],
  [
    'header uses client mark',
    /u-mark-green\.png/.test(siteJs) && existsSync(join(root, 'assets/u-mark-green.png')),
  ],
  [
    'about includes brand quote',
    /brand-quote/.test(readFileSync(join(shopRoot, 'about/index.html'), 'utf8')) &&
      /<span class="brand-quote__accent">Россия<\/span>/.test(readFileSync(join(shopRoot, 'about/index.html'), 'utf8')) &&
      /brand-quote__dash/.test(readFileSync(join(shopRoot, 'about/index.html'), 'utf8')),
  ],
  [
    'about mentions brand colors from guidebook',
    /Pantone 4216/.test(readFileSync(join(shopRoot, 'about/index.html'), 'utf8')),
  ],
  [
    'product pages include schema.org Product',
    /"@type": "Product"/.test(readFileSync(join(shopRoot, 'product/futbolka-oranzhevaya/index.html'), 'utf8')),
  ],
  [
    'product pages use three Apple-style recommendation rails',
    !/Похожие товары/.test(productPage) &&
      /<h2>С этим смотрят<\/h2>[\s\S]*<h2>Популярное<\/h2>[\s\S]*<h2>Новинки<\/h2>/.test(productPage) &&
      (productPage.match(/apple-shop-preview/g) || []).length >= 3 &&
      productSectionCardCount('С этим смотрят') >= 8 &&
      productSectionCardCount('Популярное') >= 8 &&
      productSectionCardCount('Новинки') >= 8 &&
      /apple-store-grid/.test(productPage) &&
      /product-card--editorial/.test(productPage),
  ],
  ['custom domain targets frc.serenity-dev.ru', readFileSync(join(root, 'CNAME'), 'utf8').trim() === 'frc.serenity-dev.ru'],
  [
    'home canonical and favicon',
    /<link rel="canonical" href="https:\/\/frc\.serenity-dev\.ru\/design\/">/.test(home) &&
      existsSync(join(root, 'assets/favicon.png')),
  ],
];

const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  for (const [name] of failed) console.error(`FAIL: ${name}`);
  process.exit(1);
}
for (const [name] of checks) console.log(`PASS: ${name}`);
