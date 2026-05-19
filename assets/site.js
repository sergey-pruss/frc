(function () {
  const script = document.currentScript;
  const depth = Number(script?.dataset.depth || 0);
  const root = depth ? "../".repeat(depth) : "./";

  const headerMount = document.querySelector("[data-site-header]");
  const footerMount = document.querySelector("[data-site-footer]");

  const nav = [
    { href: `${root}catalog/`, label: "Каталог" },
    { href: `${root}catalog/new/`, label: "Новинки" },
    { href: `${root}collections/`, label: "Коллекции" },
    { href: `${root}gift-cards/`, label: "Подарки" },
    { href: `${root}blog/`, label: "Журнал" },
  ];

  if (headerMount) {
    headerMount.innerHTML = `
      <div class="prototype-ribbon">Прототип интернет-магазина · рыбные тексты и фото · <a href="${root}seo/">SEO-проектирование (ТЗ)</a></div>
      <header class="site-header">
        <div class="wrap header-inner">
          <a class="logo" href="${root}">
            <strong>Универмаг «Россия»</strong>
            <span>Национальный центр «Россия»</span>
          </a>
          <nav class="site-nav" aria-label="Основное меню">
            ${nav.map((item) => `<a href="${item.href}">${item.label}</a>`).join("")}
          </nav>
          <div class="header-actions">
            <a class="btn btn-ghost" href="${root}delivery/">Доставка</a>
            <button class="btn btn-primary" type="button" data-demo-cart>Корзина · 0</button>
          </div>
        </div>
      </header>`;
  }

  if (footerMount) {
    footerMount.innerHTML = `
      <footer class="site-footer">
        <div class="wrap footer-grid">
          <div class="footer-col">
            <strong style="font-family:'Cormorant Garamond',serif;font-size:28px;">Универмаг «Россия»</strong>
            <p style="margin:12px 0 0;max-width:34ch;opacity:.8;">Официальный интернет-магазин мерча и одежды. Тексты и цены — заглушки для согласования структуры.</p>
          </div>
          <div class="footer-col">
            <h4>Покупателям</h4>
            <ul>
              <li><a href="${root}catalog/">Каталог</a></li>
              <li><a href="${root}sizes/">Размеры</a></li>
              <li><a href="${root}delivery/">Доставка и оплата</a></li>
              <li><a href="${root}loyalty/">Лояльность</a></li>
              <li><a href="${root}contacts/">Контакты</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Коллекции</h4>
            <ul>
              <li><a href="${root}collections/russia-capsule/">Russia Capsule</a></li>
              <li><a href="${root}collections/mystery-box/">Mystery Box</a></li>
              <li><a href="${root}collections/zimnyaya-liniya/">Зимняя линейка</a></li>
              <li><a href="${root}gift-cards/">Подарочные карты</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Бизнес</h4>
            <ul>
              <li><a href="${root}corporate/">Корпоративным</a></li>
              <li><a href="${root}about/">О бренде</a></li>
              <li><a href="${root}seo/">SEO-проектирование</a></li>
            </ul>
          </div>
        </div>
        <div class="wrap footer-bottom">© 2026 Прототип. Не является публичной офертой.</div>
      </footer>`;
  }

  document.querySelectorAll("[data-demo-cart]").forEach((btn) => {
    btn.addEventListener("click", () => {
      alert("Прототип: корзина и оформление заказа будут в следующей итерации.");
    });
  });

  document.querySelectorAll(".size-grid button").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.parentElement.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
    });
  });
})();
