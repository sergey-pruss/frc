(function () {
  const script = document.currentScript;
  const depth = Number(script?.dataset.depth || 0);
  const root = depth ? "../".repeat(depth) : "./";
  const assetV = script?.src?.match(/[?&]v=([^&]+)/)?.[1] || "";
  const markSrc = `${root}assets/u-mark-green.png${assetV ? `?v=${assetV}` : ""}`;
  const markLightSrc = `${root}assets/u-mark-light.png${assetV ? `?v=${assetV}` : ""}`;
  const ncLogoSrc = `${root}assets/nc-logo-white.png${assetV ? `?v=${assetV}` : ""}`;

  const headerMount = document.querySelector("[data-site-header]");
  const footerMount = document.querySelector("[data-site-footer]");
  const docsRoot = depth ? `${root}../` : "../";

  const nav = [
    { href: `${root}catalog/`, label: "Каталог" },
    { href: `${root}catalog/#odezhda`, label: "Одежда" },
    { href: `${root}catalog/aksessuary/`, label: "Аксессуары" },
    { href: `${root}stores/`, label: "Магазины" },
    { href: `${root}gift-cards/`, label: "Подарочные карты" },
  ];

  if (headerMount) {
    headerMount.innerHTML = `
      <div class="site-topbar">
        <div class="site-topbar__tabs">
          <a class="site-topbar__tab" href="${docsRoot}seo/">SEO-стратегия</a>
          <a class="site-topbar__tab" href="${docsRoot}analysis/">Анализ конкурентов</a>
          <a class="site-topbar__tab is-active">Дизайн-прототип</a>
        </div>
      </div>
      <header class="site-header">
        <div class="wrap header-inner">
          <a class="logo" href="${docsRoot}design/" aria-label="Универмаг «Россия»">
            <img class="logo-mark" src="${markSrc}" alt="" width="56" height="56">
            <span class="logo-wordmark">
              <span class="logo-wordmark__line">Универмаг</span>
              <span class="logo-wordmark__line logo-wordmark__line--brand">«Россия»</span>
            </span>
          </a>
          <nav class="site-nav" aria-label="Основное меню">
            ${nav.map((item) => `<a href="${item.href}">${item.label}</a>`).join("")}
          </nav>
          <div class="header-actions">
            <a class="btn btn-ghost" href="${root}login/" title="Личный кабинет">Кабинет</a>
            <a class="btn btn-ghost" href="${root}search/">Поиск</a>
            <a class="btn btn-primary" href="${root}cart/">Корзина</a>
          </div>
        </div>
      </header>`;
  }

  if (footerMount) {
    footerMount.innerHTML = `
      <footer class="site-footer">
        <div class="wrap site-footer__inner">
          <div class="footer-grid">
            <div class="footer-col footer-col--brand">
              <a class="footer-brand" href="${docsRoot}design/">
                <img class="footer-mark" src="${markLightSrc}" alt="Универмаг «Россия»" width="56" height="56">
              </a>
              <p class="footer-tagline">Официальный интернет-магазин одежды, аксессуаров и подарков Национального центра «Россия».</p>
              <a class="footer-nc" href="https://russia.ru/" target="_blank" rel="noopener noreferrer">
                <img src="${ncLogoSrc}" alt="Национальный центр «Россия»" width="200" height="40">
              </a>
            </div>
            <div class="footer-col">
              <h4>Покупателям</h4>
              <ul>
                <li><a href="${root}catalog/">Каталог</a></li>
                <li><a href="${root}login/">Личный кабинет</a></li>
                <li><a href="${root}cart/">Корзина</a></li>
                <li><a href="${root}sizes/">Размеры</a></li>
                <li><a href="${root}delivery/">Доставка и оплата</a></li>
                <li><a href="${root}stores/">Магазины</a></li>
              </ul>
            </div>
          <div class="footer-col">
            <h4>Каталог</h4>
            <ul>
                <li><a href="${root}catalog/khudi/">Худи</a></li>
                <li><a href="${root}catalog/svitshoty/">Свитшоты</a></li>
                <li><a href="${root}catalog/futbolki/">Футболки</a></li>
                <li><a href="${root}catalog/vetrovki/">Ветровки</a></li>
                <li><a href="${root}catalog/kurtki/">Куртки</a></li>
                <li><a href="${root}catalog/aksessuary/">Аксессуары</a></li>
                <li><a href="${root}gift-cards/">Подарочные карты</a></li>
              </ul>
            </div>
            <div class="footer-col">
              <h4>Контакты</h4>
              <ul>
                <li><a href="${root}contacts/">Связаться с нами</a></li>
                <li><a href="${root}corporate/">Корпоративным</a></li>
                <li><a href="${root}about/">О бренде</a></li>
              </ul>
            </div>
          </div>
          <div class="footer-bottom">
            <span>© 2026 Универмаг «Россия»</span>
            <a class="made-by" href="https://serenity.agency/" target="_blank" rel="noreferrer">
              <img src="${root}assets/serenity-logo.svg" alt="" width="18" height="18">
              <span>Сделано в Serenity</span>
            </a>
          </div>
        </div>
      </footer>`;
  }

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
