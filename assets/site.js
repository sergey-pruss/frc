(function () {
  const script = document.currentScript;
  const prototypeDepth = Number(script?.dataset.depth || 0);
  const root = prototypeDepth ? "../".repeat(prototypeDepth) : "./";
  const assetRoot = prototypeDepth ? "../".repeat(prototypeDepth + 1) : "../";
  const assetV = script?.src?.match(/[?&]v=([^&]+)/)?.[1] || "";
  const markSrc = `${assetRoot}assets/u-mark-green.png${assetV ? `?v=${assetV}` : ""}`;
  const markLightSrc = `${assetRoot}assets/u-mark-light.png${assetV ? `?v=${assetV}` : ""}`;
  const markSourceSrc = `${assetRoot}assets/u-mark-source.png${assetV ? `?v=${assetV}` : ""}`;
  const univermagLogoSrc = `${assetRoot}assets/univermag-logo.png${assetV ? `?v=${assetV}` : ""}`;
  const univermagLogoVerticalSrc = `${assetRoot}assets/univermag-logo-vertical.png${assetV ? `?v=${assetV}` : ""}`;
  const ncLogoSrc = `${assetRoot}assets/nc-logo-white.png${assetV ? `?v=${assetV}` : ""}`;
  const ncLogoBlackSrc = `${assetRoot}assets/nc-logo-black.png${assetV ? `?v=${assetV}` : ""}`;
  const FOOTER_TAGLINE =
    "Официальный интернет-магазин одежды, аксессуаров и подарков Национального центра «Россия».";

  const headerMount = document.querySelector("[data-site-header]");
  const footerMount = document.querySelector("[data-site-footer]");
  const docsRoot = assetRoot;

  const nav = [
    { href: `${root}catalog/`, label: "Каталог" },
    { href: `${root}catalog/#odezhda`, label: "Одежда" },
    { href: `${root}catalog/aksessuary/`, label: "Аксессуары" },
    { href: `${root}stores/`, label: "Магазины" },
    { href: `${root}gift-cards/`, label: "Подарочные карты" },
  ];

  const DESIGN_VARIANT_KEY = "frc-design-variant";
  const DESIGN_VARIANTS = ["default", "the-act", "etudes", "rains", "cromia", "soroboka", "shu"];
  const path = location.pathname.replace(/\/index\.html$/, "/");

  const designVariantFromPath = () => {
    if (/\/design\/refs\/the-act\//.test(path)) return "the-act";
    if (/\/design\/refs\/(etudes|sergeenko)\//.test(path)) return "etudes";
    if (/\/design\/refs\/rains\//.test(path)) return "rains";
    if (/\/design\/refs\/cromia\//.test(path)) return "cromia";
    if (/\/design\/refs\/soroboka\//.test(path)) return "soroboka";
    if (/\/design\/refs\/shu\//.test(path)) return "shu";
    if (/\/design\/?$/.test(path)) return "default";
    return null;
  };

  const inDesignPrototype = /\/design\//.test(path);
  const pathVariant = designVariantFromPath();
  let designVariant = pathVariant;

  if (inDesignPrototype) {
    if (pathVariant) {
      try {
        sessionStorage.setItem(DESIGN_VARIANT_KEY, pathVariant);
      } catch (e) {
        /* ignore */
      }
    } else {
      try {
        let stored = sessionStorage.getItem(DESIGN_VARIANT_KEY);
        if (stored === "sergeenko") stored = "etudes";
        designVariant = DESIGN_VARIANTS.includes(stored) ? stored : "default";
      } catch (e) {
        designVariant = "default";
      }
    }
  } else {
    designVariant = null;
  }

  const isRefLanding = /\/design\/refs\/(the-act|etudes|sergeenko|rains|cromia|soroboka|shu)\/?$/.test(path);

  if (inDesignPrototype && designVariant) {
    document.body.classList.add(`is-design-variant-${designVariant}`);
    if (designVariant !== "default") {
      const sharedCss = document.createElement("link");
      sharedCss.rel = "stylesheet";
      sharedCss.href = `${assetRoot}assets/refs/shared.css${assetV ? `?v=${assetV}` : ""}`;
      document.head.appendChild(sharedCss);
      const footerCss = document.createElement("link");
      footerCss.rel = "stylesheet";
      footerCss.href = `${assetRoot}assets/refs/footers.css${assetV ? `?v=${assetV}` : ""}`;
      document.head.appendChild(footerCss);
    }
    if (!isRefLanding && designVariant !== "default") {
      const headerCss = document.createElement("link");
      headerCss.rel = "stylesheet";
      headerCss.href = `${assetRoot}assets/refs/header-variants.css${assetV ? `?v=${assetV}` : ""}`;
      document.head.appendChild(headerCss);
    }
    if (designVariant === "shu") {
      const shuCss = document.createElement("link");
      shuCss.rel = "stylesheet";
      shuCss.href = `${assetRoot}assets/refs/shu.css${assetV ? `?v=${assetV}` : ""}`;
      document.head.appendChild(shuCss);
    }
  }

  const designHomeHref = (variant) => {
    const homes = {
      default: `${docsRoot}design/`,
      "the-act": `${docsRoot}design/refs/the-act/`,
      etudes: `${docsRoot}design/refs/etudes/`,
      rains: `${docsRoot}design/refs/rains/`,
      cromia: `${docsRoot}design/refs/cromia/`,
      soroboka: `${docsRoot}design/refs/soroboka/`,
      shu: `${docsRoot}design/refs/shu/`,
    };
    return homes[variant] || homes.default;
  };

  const navLinks = (items) => items.map((item) => `<a href="${item.href}">${item.label}</a>`).join("");

  const renderRefLogo = ({ home, tone = "light", layout = "full", stack = false, lockupSize = "" }) => {
    const toneClass = tone === "dark" ? "ref-logo--on-dark" : "ref-logo--on-light";
    const sizeClass = lockupSize ? ` ref-logo--${lockupSize}` : "";
    const stackClass = stack ? " ref-logo--stack" : "";

    if (layout === "mark") {
      const markFile = tone === "dark" ? markLightSrc : markSrc;
      return `<a class="ref-logo ${toneClass} ref-logo--mark-only" href="${home}" aria-label="Универмаг «Россия»">
        <img class="ref-logo__mark" src="${markFile}" alt="" width="56" height="56">
      </a>`;
    }

    if (layout === "vertical" || stack) {
      return `<a class="ref-logo ${toneClass} ref-logo--vertical${stackClass}${sizeClass}" href="${home}" aria-label="Универмаг «Россия»">
        <img class="ref-logo__img" src="${univermagLogoVerticalSrc}" alt="Универмаг «Россия»" width="120" height="140">
      </a>`;
    }

    return `<a class="ref-logo ${toneClass}${sizeClass}" href="${home}" aria-label="Универмаг «Россия»">
      <img class="ref-logo__img" src="${univermagLogoSrc}" alt="Универмаг «Россия»" width="240" height="56">
    </a>`;
  };

  const renderRefFooterBrand = ({ home, tone = "dark" }) => {
    const onDark = tone === "dark";
    const markImg = onDark ? markLightSrc : markSrc;
    const markMonoClass = onDark ? "" : " ref-footer-brand__mark-img--mono";
    const ncImg = onDark ? ncLogoSrc : ncLogoBlackSrc;
    return `<div class="ref-footer-brand ref-footer-brand--${onDark ? "dark" : "light"}">
      <a class="ref-footer-brand__mark" href="${home}">
        <img class="ref-footer-brand__mark-img${markMonoClass}" src="${markImg}" alt="" width="56" height="56">
      </a>
      <p class="ref-footer-brand__tagline">${FOOTER_TAGLINE}</p>
      <a class="ref-footer-brand__nc" href="https://russia.ru/" target="_blank" rel="noopener noreferrer">
        <img src="${ncImg}" alt="Национальный центр «Россия»" width="200" height="40">
      </a>
    </div>`;
  };

  const renderStoreHeader = (variant) => {
    const home = designHomeHref(variant);
    const logo = `
      <img class="logo-mark" src="${markSrc}" alt="" width="56" height="56">
      <span class="logo-wordmark">
        <span class="logo-wordmark__line">Универмаг</span>
        <span class="logo-wordmark__line logo-wordmark__line--brand">«Россия»</span>
      </span>`;
    if (variant === "the-act") {
      return `
      <header class="site-header site-header--the-act">
        <div class="wrap header-inner header-inner--the-act">
          <nav class="site-nav site-nav--the-act-left" aria-label="Основное меню">
            ${navLinks(nav.slice(0, 3))}
          </nav>
          ${renderRefLogo({ home, tone: "light", layout: "full" })}
          <div class="header-actions header-actions--the-act">
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
    }

    if (variant === "etudes") {
      return `
      <header class="site-header site-header--etudes">
        <div class="wrap header-inner header-inner--etudes">
          <nav class="site-nav site-nav--etudes-left" aria-label="Каталог">
            ${navLinks(nav.slice(0, 3))}
          </nav>
          ${renderRefLogo({ home, tone: "light", layout: "full" })}
          <div class="header-actions header-actions--etudes">
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-ghost" href="${root}login/">Аккаунт</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
    }

    if (variant === "rains") {
      return `
      <header class="site-header site-header--rains">
        <div class="wrap header-inner header-inner--rains">
          ${renderRefLogo({ home, tone: "light", layout: "mark" })}
          <nav class="site-nav site-nav--rains" aria-label="Основное меню">
            ${navLinks(nav)}
          </nav>
          <div class="header-actions header-actions--rains">
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
    }

    if (variant === "cromia") {
      return `
      <header class="site-header site-header--cromia">
        <div class="wrap header-inner header-inner--cromia">
          <nav class="site-nav site-nav--cromia-left" aria-label="Основное меню">
            ${navLinks(nav.slice(0, 3))}
          </nav>
          ${renderRefLogo({ home, tone: "light", layout: "full", lockupSize: "lg" })}
          <div class="header-actions header-actions--cromia">
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
    }

    if (variant === "soroboka") {
      return `
      <header class="site-header site-header--soroboka">
        <div class="wrap header-inner header-inner--soroboka">
          ${renderRefLogo({ home, tone: "light", layout: "full" })}
          <nav class="site-nav site-nav--soroboka" aria-label="Основное меню">
            ${navLinks(nav)}
          </nav>
          <div class="header-actions header-actions--soroboka">
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
    }

    if (variant === "shu") {
      const announce =
        "Скидка 10% на первый заказ при подписке на рассылку Универмага «Россия» · ";
      return `
      <div class="shu-store-chrome">
        <div class="shu-announce" aria-hidden="true">
          <div class="shu-announce__track">
            <span>${announce}</span><span>${announce}</span><span>${announce}</span><span>${announce}</span>
          </div>
        </div>
        <header class="site-header site-header--shu shu-header">
          <div class="shu-header__inner">
            <nav class="shu-header__left" aria-label="Каталог">
              <a class="shu-header__search" href="${root}search/" title="Поиск" aria-label="Поиск">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/></svg>
              </a>
              <a href="${root}catalog/#odezhda">Одежда</a>
              <a href="${root}catalog/aksessuary/">Аксессуары</a>
              <a href="${root}catalog/new/">Новинки</a>
              <a href="${root}collections/russia-capsule/">Капсула</a>
              <a href="${root}gift-cards/">Подарки</a>
            </nav>
            ${renderRefLogo({ home, tone: "light", layout: "full" }).replace('class="ref-logo', 'class="shu-header__logo ref-logo')}
            <nav class="shu-header__right" aria-label="Сервис">
              <a href="${root}about/">О бренде</a>
              <a href="${root}stores/">Магазины</a>
              <a href="${root}delivery/">Помощь</a>
              <a href="${root}login/">Аккаунт</a>
              <a class="shu-header__cart" href="${root}cart/">Корзина <span class="shu-header__cart-count" aria-hidden="true">0</span></a>
            </nav>
          </div>
        </header>
      </div>`;
    }

    return `
      <header class="site-header">
        <div class="wrap header-inner">
          <a class="logo" href="${home}" aria-label="Универмаг «Россия»">${logo}</a>
          <nav class="site-nav" aria-label="Основное меню">
            ${navLinks(nav)}
          </nav>
          <div class="header-actions">
            <a class="btn btn-ghost" href="${root}login/" title="Личный кабинет">Кабинет</a>
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
  };

  const designVariantTabs =
    designVariant === null
      ? ""
      : [
          { id: "default", label: "Дизайн по умолчанию", href: `${docsRoot}design/` },
          { id: "the-act", label: "the act", href: `${docsRoot}design/refs/the-act/` },
          { id: "etudes", label: "Études Studio", href: `${docsRoot}design/refs/etudes/` },
          { id: "rains", label: "RAINS", href: `${docsRoot}design/refs/rains/` },
          { id: "cromia", label: "Cromia", href: `${docsRoot}design/refs/cromia/` },
          { id: "soroboka", label: "SOROBOKA", href: `${docsRoot}design/refs/soroboka/` },
          { id: "shu", label: "SHU", href: `${docsRoot}design/refs/shu/` },
        ]
          .map(
            (item) =>
              `<a class="site-topbar__tab${item.id === designVariant ? " is-active" : ""}" href="${item.href}" data-design-variant-tab="${item.id}">${item.label}</a>`
          )
          .join("");

  if (headerMount) {
    headerMount.innerHTML = `
      <div class="site-topbar-stack">
        <div class="site-topbar">
          <div class="site-topbar__tabs">
            <a class="site-topbar__tab" href="${docsRoot}seo/">SEO-стратегия</a>
            <a class="site-topbar__tab" href="${docsRoot}analysis/">Анализ конкурентов</a>
            <a class="site-topbar__tab" href="${docsRoot}content-strategy/">Контент-стратегия</a>
            <a class="site-topbar__tab is-active">Дизайн-прототип</a>
          </div>
        </div>
        ${
          designVariantTabs
            ? `<div class="site-topbar site-topbar--sub" aria-label="Вариант главной">
          <div class="site-topbar__tabs site-topbar__tabs--design">${designVariantTabs}</div>
        </div>`
            : ""
        }
      </div>
      ${isRefLanding ? "" : renderStoreHeader(designVariant || "default")}`;

    headerMount.querySelectorAll("[data-design-variant-tab]").forEach((tab) => {
      tab.addEventListener("click", () => {
        try {
          sessionStorage.setItem(DESIGN_VARIANT_KEY, tab.dataset.designVariantTab || "default");
        } catch (e) {
          /* ignore */
        }
      });
    });

    if (designVariantTabs) {
      document.body.classList.add("has-design-variant-tabs");
      const syncDesignTabsHeight = () => {
        const sub = headerMount.querySelector(".site-topbar--sub");
        if (!sub) return;
        document.documentElement.style.setProperty("--design-tabs-height", `${sub.offsetHeight}px`);
      };
      syncDesignTabsHeight();
      window.addEventListener("resize", syncDesignTabsHeight);
    }
  }

  const footerBottom = `
    <div class="ref-footer__bottom">
      <span>© 2026 Универмаг «Россия»</span>
      <a class="made-by" href="https://serenity.agency/" target="_blank" rel="noreferrer">
        <img src="${assetRoot}assets/serenity-logo.svg" alt="" width="18" height="18">
        <span>Сделано в Serenity</span>
      </a>
    </div>`;

  const renderStoreFooter = (variant) => {
    const home = designHomeHref(variant);
    const buyersLinks = `
      <li><a href="${root}catalog/">Каталог</a></li>
      <li><a href="${root}delivery/">Доставка и оплата</a></li>
      <li><a href="${root}sizes/">Размеры</a></li>
      <li><a href="${root}stores/">Магазины</a></li>
      <li><a href="${root}gift-cards/">Подарочные карты</a></li>`;
    const catalogLinks = `
      <li><a href="${root}catalog/hudi/">Худи</a></li>
      <li><a href="${root}catalog/svitshoty/">Свитшоты</a></li>
      <li><a href="${root}catalog/futbolki/">Футболки</a></li>
      <li><a href="${root}catalog/kurtki/">Куртки</a></li>
      <li><a href="${root}catalog/aksessuary/">Аксессуары</a></li>`;
    const contactLinks = `
      <li><a href="${root}contacts/">Связаться с нами</a></li>
      <li><a href="${root}about/">О бренде</a></li>
      <li><a href="${root}corporate/">Корпоративным</a></li>
      <li><a href="${root}login/">Личный кабинет</a></li>`;

    if (variant === "the-act") {
      return `
      <footer class="ref-footer ref-footer--the-act">
        <div class="wrap ref-footer__inner">
          <div class="ref-footer__grid">
            <div>
              ${renderRefFooterBrand({ home, tone: "dark" })}
              <ul class="ref-footer__links ref-footer__links--after-brand">${catalogLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Покупателям</p>
              <ul class="ref-footer__links">${buyersLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Центр</p>
              <ul class="ref-footer__links">${contactLinks}</ul>
            </div>
            <div class="ref-footer__newsletter">
              <p class="ref-footer__heading">Рассылка</p>
              <p>Новинки мерча и события центра — раз в месяц, без спама.</p>
              <form class="ref-footer__field" action="#" onsubmit="return false">
                <input type="email" placeholder="E-mail" aria-label="E-mail">
                <button type="submit">→</button>
              </form>
            </div>
          </div>
          ${footerBottom}
        </div>
      </footer>`;
    }

    if (variant === "etudes") {
      return `
      <footer class="ref-footer ref-footer--etudes">
        <div class="wrap ref-footer__inner">
          <div class="ref-footer__grid ref-footer__grid--etudes">
            <div class="ref-footer__etudes-mark">
              ${renderRefFooterBrand({ home, tone: "light" })}
            </div>
            <div>
              <p class="ref-footer__heading">Покупателям</p>
              <ul class="ref-footer__links">${buyersLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Каталог</p>
              <ul class="ref-footer__links">${catalogLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Контакты</p>
              <ul class="ref-footer__links">${contactLinks}</ul>
            </div>
          </div>
          ${footerBottom}
        </div>
      </footer>`;
    }

    if (variant === "rains") {
      return `
      <footer class="ref-footer ref-footer--rains">
        <div class="wrap ref-footer__inner">
          <div class="ref-footer__grid">
            <div>
              ${renderRefFooterBrand({ home, tone: "dark" })}
            </div>
            <div>
              <p class="ref-footer__heading">Company</p>
              <ul class="ref-footer__links">${contactLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Service</p>
              <ul class="ref-footer__links">${buyersLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Follow</p>
              <ul class="ref-footer__links ref-footer__archive">
                <li><a href="${root}catalog/new/">Коллекция 2025</a></li>
                <li><a href="${root}catalog/hudi/">Худи</a></li>
                <li><a href="${root}catalog/aksessuary/">Аксессуары</a></li>
              </ul>
            </div>
          </div>
          ${footerBottom}
        </div>
      </footer>`;
    }

    if (variant === "cromia") {
      const ticker =
        "Мерч с характером · Универмаг «Россия» · Качество и спокойный стиль · ";
      return `
      <footer class="ref-footer ref-footer--cromia">
        <div class="ref-footer__ticker" aria-hidden="true"><span>${ticker.repeat(4)}</span></div>
        <div class="wrap ref-footer__inner">
          <div class="ref-footer__grid">
            <div>
              ${renderRefFooterBrand({ home, tone: "light" })}
              <div class="ref-footer__pay"><span>Visa</span><span>Mastercard</span><span>Мир</span></div>
            </div>
            <div>
              <p class="ref-footer__heading">Shop</p>
              <ul class="ref-footer__links">${catalogLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Help</p>
              <ul class="ref-footer__links">${buyersLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Legal</p>
              <ul class="ref-footer__links">
                <li><a href="${root}about/">О бренде</a></li>
                <li><a href="${root}contacts/">Контакты</a></li>
                <li><a href="${root}corporate/">Корпоративным</a></li>
              </ul>
            </div>
          </div>
          ${footerBottom}
        </div>
      </footer>`;
    }

    if (variant === "soroboka") {
      return `
      <footer class="ref-footer ref-footer--soroboka">
        <div class="wrap ref-footer__inner">
          <div class="ref-footer__grid">
            <div>
              ${renderRefFooterBrand({ home, tone: "light" })}
              <div class="ref-footer__social">
                <a href="${root}catalog/" title="Каталог">VK</a>
                <a href="${root}stores/" title="Магазины">TG</a>
              </div>
            </div>
            <div>
              <p class="ref-footer__heading">Каталог</p>
              <ul class="ref-footer__links">${catalogLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Покупателям</p>
              <ul class="ref-footer__links">${buyersLinks}</ul>
            </div>
            <div>
              <p class="ref-footer__heading">Связь с нами</p>
              <ul class="ref-footer__links">${contactLinks}</ul>
              <p style="margin-top:16px"><a href="${root}cart/">Корзина</a></p>
            </div>
          </div>
          ${footerBottom}
        </div>
      </footer>`;
    }

    if (variant === "shu") {
      return `
      <footer class="ref-footer ref-footer--shu shu-footer">
        <div class="shu-footer__grid wrap">
          <div>
            <div class="shu-footer__contact">
              <a href="tel:+78000000000">8 800 000-00-00</a>
              <a href="mailto:shop@russia.ru">shop@russia.ru</a>
            </div>
            <div class="shu-footer__social">
              <a href="${root}catalog/">Вконтакте</a>
              <a href="${root}catalog/">Telegram</a>
            </div>
          </div>
          <div>
            <p class="shu-footer__heading">О бренде</p>
            <ul class="shu-footer__links">
              <li><a href="${root}about/">История</a></li>
              <li><a href="${root}about/">Дизайн</a></li>
              <li><a href="${root}catalog/new/">Коллекции</a></li>
              <li><a href="${root}stores/">Магазины</a></li>
              <li><a href="${root}contacts/">Контакты</a></li>
            </ul>
          </div>
          <div>
            <p class="shu-footer__heading">Помощь</p>
            <ul class="shu-footer__links">${buyersLinks}</ul>
          </div>
          <div>
            <p class="shu-footer__heading">Подписка</p>
            <p class="shu-footer__sub-note"><a href="${root}catalog/">Скидка 10% за подписку на e-mail рассылку</a></p>
          </div>
        </div>
        <p class="shu-footer__copy wrap">© 2025 Универмаг «Россия»</p>
      </footer>`;
    }

    return `
      <footer class="site-footer">
        <div class="wrap site-footer__inner">
          <div class="footer-grid">
            <div class="footer-col footer-col--brand">
              <a class="footer-brand" href="${home}">
                <img class="footer-mark" src="${markLightSrc}" alt="Универмаг «Россия»" width="56" height="56">
              </a>
              <p class="footer-tagline">Официальный интернет-магазин одежды, аксессуаров и подарков Национального центра «Россия».</p>
              <a class="footer-nc" href="https://russia.ru/" target="_blank" rel="noopener noreferrer">
                <img src="${ncLogoSrc}" alt="Национальный центр «Россия»" width="200" height="40">
              </a>
            </div>
            <div class="footer-col">
              <h4>Покупателям</h4>
              <ul>${buyersLinks}</ul>
            </div>
            <div class="footer-col">
              <h4>Каталог</h4>
              <ul>${catalogLinks}</ul>
            </div>
            <div class="footer-col">
              <h4>Контакты</h4>
              <ul>${contactLinks}</ul>
            </div>
          </div>
          <div class="footer-bottom">
            <span>© 2026 Универмаг «Россия»</span>
            <a class="made-by" href="https://serenity.agency/" target="_blank" rel="noreferrer">
              <img src="${assetRoot}assets/serenity-logo.svg" alt="" width="18" height="18">
              <span>Сделано в Serenity</span>
            </a>
          </div>
        </div>
      </footer>`;
  };

  if (footerMount) {
    const activeFooterVariant = inDesignPrototype && designVariant ? designVariant : "default";
    footerMount.innerHTML = renderStoreFooter(activeFooterVariant);
  }

  document.querySelectorAll("[data-ref-logo]").forEach((el) => {
    const tone = el.dataset.refLogoTone === "dark" ? "dark" : "light";
    let layout = el.dataset.refLogoLayout || "full";
    if (layout === "lockup" || layout === "lockup-only") layout = "full";
    const stack = el.hasAttribute("data-ref-logo-stack");
    const lockupSize = el.dataset.refLogoLockupSize || "";
    const home = el.getAttribute("href") || "./";
    const wrap = document.createElement("div");
    wrap.innerHTML = renderRefLogo({ home, tone, layout, stack, lockupSize }).trim();
    const link = wrap.firstElementChild;
    el.classList.forEach((cls) => {
      if (!cls.startsWith("ref-logo")) link.classList.add(cls);
    });
    el.replaceWith(link);
  });

  document.querySelectorAll("[data-demo-cart]").forEach((btn) => {
    btn.addEventListener("click", () => {
      alert("Товар добавлен в корзину.");
    });
  });

  document.querySelectorAll(".size-grid button").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.parentElement.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
    });
  });

  const filterPanels = Array.from(document.querySelectorAll(".store-filter-panel"));
  filterPanels.forEach((panel) => {
    const scope = panel.closest(".store-layout") || document;
    const cards = Array.from(scope.querySelectorAll("[data-product-card]"));
    const count = scope.querySelector("[data-filter-count]");
    const empty = scope.querySelector("[data-filter-empty]");
    const sizeInputs = Array.from(panel.querySelectorAll("[data-filter-size]"));
    const priceInputs = Array.from(panel.querySelectorAll("[data-filter-price]"));
    const colorButtons = Array.from(panel.querySelectorAll("[data-filter-color]"));
    const categoryLinks = Array.from(panel.querySelectorAll("[data-filter-category]"));
    const subcategoryButtons = Array.from(panel.querySelectorAll("[data-filter-subcategory]"));

    function selectedValues(inputs, attr) {
      return inputs.filter((input) => input.checked).map((input) => input.dataset[attr]);
    }

    function syncOptionStates() {
      sizeInputs.forEach((input) => input.closest("label")?.classList.toggle("is-active", input.checked));
      priceInputs.forEach((input) => input.closest("label")?.classList.toggle("is-active", input.checked));
    }

    function applyFilters() {
      const category = panel.querySelector("[data-filter-category].is-active")?.dataset.filterCategory || "all";
      const sizes = selectedValues(sizeInputs, "filterSize");
      const prices = selectedValues(priceInputs, "filterPrice").map((range) => range.split("-").map(Number));
      const color = panel.querySelector("[data-filter-color].is-active")?.dataset.filterColor || "";
      const subcategory = panel.querySelector("[data-filter-subcategory].is-active")?.dataset.filterSubcategory || "";
      let visible = 0;

      cards.forEach((card) => {
        const cardPrice = Number(card.dataset.price || 0);
        const okCategory = category === "all" || card.dataset.category === category;
        const okSize = sizes.length === 0 || sizes.some((size) => (card.dataset.sizes || "").split(" ").includes(size));
        const okColor = !color || (card.dataset.colors || "").split(" ").includes(color);
        const okPrice = prices.length === 0 || prices.some(([min, max]) => cardPrice >= min && cardPrice <= max);
        const okSubcategory = !subcategory || card.dataset.subcategory === subcategory;
        const shown = okCategory && okSize && okColor && okPrice && okSubcategory;
        card.hidden = !shown;
        if (shown) visible += 1;
      });

      if (count) count.textContent = String(visible);
      if (empty) empty.classList.toggle("is-visible", visible === 0);
      syncOptionStates();
    }

    categoryLinks.forEach((link) => {
      link.addEventListener("click", (event) => {
        if (!cards.length) return;
        event.preventDefault();
        categoryLinks.forEach((item) => item.classList.remove("is-active"));
        link.classList.add("is-active");
        applyFilters();
      });
    });

    colorButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const wasActive = button.classList.contains("is-active");
        colorButtons.forEach((item) => item.classList.remove("is-active"));
        if (!wasActive) button.classList.add("is-active");
        applyFilters();
      });
    });

    subcategoryButtons.forEach((button) => {
      button.addEventListener("click", () => {
        subcategoryButtons.forEach((item) => item.classList.remove("is-active"));
        button.classList.add("is-active");
        applyFilters();
      });
    });

    [...sizeInputs, ...priceInputs].forEach((input) => {
      input.addEventListener("change", applyFilters);
    });

    panel.querySelector("[data-filter-reset]")?.addEventListener("click", (event) => {
      if (!cards.length) return;
      event.preventDefault();
      categoryLinks.forEach((item) => item.classList.toggle("is-active", item.dataset.filterCategory === "all"));
      colorButtons.forEach((button) => button.classList.remove("is-active"));
      subcategoryButtons.forEach((button) => button.classList.toggle("is-active", button.dataset.filterSubcategory === ""));
      [...sizeInputs, ...priceInputs].forEach((input) => {
        input.checked = false;
      });
      applyFilters();
    });

    applyFilters();
  });

  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const parallaxItems = Array.from(document.querySelectorAll("[data-parallax]")).map((element) => ({
    element,
    current: 0,
    target: 0,
    speed: Number(element.dataset.parallaxSpeed || (element.dataset.parallax === "image" ? 0.055 : 0.022)),
    limit: Number(element.dataset.parallaxLimit || (element.dataset.parallax === "image" ? 46 : 18)),
  }));
  let lastScrollY = window.scrollY;
  let headerTicking = false;
  let parallaxTicking = false;
  let parallaxAnimating = false;

  function updateParallax() {
    if (motionQuery.matches || parallaxItems.length === 0) return;

    const viewportMid = window.innerHeight / 2;
    parallaxItems.forEach((item) => {
      const rect = item.element.getBoundingClientRect();
      const itemMid = rect.top + rect.height / 2;
      item.target = Math.max(-item.limit, Math.min(item.limit, (viewportMid - itemMid) * item.speed));
    });
    animateParallax();
  }

  function requestParallaxUpdate() {
    if (parallaxTicking) return;
    parallaxTicking = true;
    window.requestAnimationFrame(() => {
      updateParallax();
      parallaxTicking = false;
    });
  }

  function animateParallax() {
    if (parallaxAnimating || motionQuery.matches || parallaxItems.length === 0) return;
    parallaxAnimating = true;

    const tick = () => {
      let moving = false;
      parallaxItems.forEach((item) => {
        item.current += (item.target - item.current) * 0.12;
        if (Math.abs(item.target - item.current) > 0.08) moving = true;
        item.element.style.setProperty("--parallax-y", `${item.current.toFixed(2)}px`);
      });

      if (moving) {
        window.requestAnimationFrame(tick);
      } else {
        parallaxAnimating = false;
      }
    };

    window.requestAnimationFrame(tick);
  }

  function updateSmartHeader() {
    const y = window.scrollY;
    const delta = y - lastScrollY;
    const pastFirstScreen = y > Math.max(window.innerHeight * 0.82, 620);

    document.body.classList.toggle("smart-header-active", pastFirstScreen);

    if (!pastFirstScreen) {
      document.body.classList.remove("smart-header-visible");
    } else if (delta < -8) {
      document.body.classList.add("smart-header-visible");
    } else if (delta > 8) {
      document.body.classList.remove("smart-header-visible");
    }

    lastScrollY = y;
    headerTicking = false;
  }

  function requestSmartHeaderUpdate() {
    if (headerTicking) return;
    headerTicking = true;
    window.requestAnimationFrame(updateSmartHeader);
  }

  if (parallaxItems.length > 0 && !motionQuery.matches) {
    updateParallax();
    window.addEventListener("scroll", requestParallaxUpdate, { passive: true });
    window.addEventListener("resize", requestParallaxUpdate);
  }

  updateSmartHeader();
  window.addEventListener("scroll", requestSmartHeaderUpdate, { passive: true });
  window.addEventListener("resize", requestSmartHeaderUpdate);
})();
