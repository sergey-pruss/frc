(function () {
  const script = document.currentScript;
  const depth = Number(script?.dataset.depth || 0);
  const root = depth ? "../".repeat(depth) : "./";

  const headerMount = document.querySelector("[data-site-header]");
  const footerMount = document.querySelector("[data-site-footer]");

  const nav = [
    { href: `${root}catalog/`, label: "Каталог" },
    { href: `${root}collections/`, label: "Мерч" },
    { href: `${root}stores/`, label: "Магазины" },
    { href: `${root}gift-cards/`, label: "Подарочные карты" },
    { href: `${root}contacts/`, label: "Контакты" },
  ];

  if (headerMount) {
    headerMount.innerHTML = `
      <div class="site-topbar">Бесплатная доставка по России от 7&nbsp;000&nbsp;₽ · <a href="${root}delivery/">условия доставки и возврата</a></div>
      <header class="site-header">
        <div class="wrap header-inner">
          <a class="logo" href="${root}" aria-label="Универмаг Россия">
            <img class="logo-mark" src="${root}assets/favicon.png" alt="" width="36" height="36">
            <img class="logo-wordmark" src="${root}assets/rossiya-wordmark.svg" alt="Универмаг Россия" width="150" height="44">
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
        <div class="wrap footer-grid">
          <div class="footer-col">
            <strong style="font-family:'PT Serif',serif;font-size:28px;">Универмаг «Россия»</strong>
            <p style="margin:12px 0 0;max-width:34ch;opacity:.8;">Официальный интернет-магазин одежды, аксессуаров и подарков Национального центра «Россия».</p>
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
            <h4>Коллекции</h4>
            <ul>
              <li><a href="${root}collections/russia-capsule/">Russia Capsule</a></li>
              <li><a href="${root}collections/mystery-box/">Mystery Box</a></li>
              <li><a href="${root}gift-cards/">Подарочные карты</a></li>
              <li><a href="${root}blog/">Журнал</a></li>
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
        <div class="wrap footer-bottom">
          <span>© 2026 Универмаг «Россия»</span>
          <a class="made-by" href="https://serenity.agency/" target="_blank" rel="noreferrer">
            <img src="${root}assets/serenity-logo.svg" alt="" width="18" height="18">
            <span>Сделано в Serenity</span>
          </a>
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
})();
