(function () {
  "use strict";

  const STORAGE_KEY = "frc-gate-v1";
  const PASS_HASH = "c6c2307ac025abfed680cb646bc38ca3c3d6e02662a0f2faa143dcff22268a49";
  const GATE_URL = "/gate/";
  const DEFAULT_NEXT = "/seo/";

  const script = document.currentScript;
  const isLoginPage = script?.hasAttribute("data-gate-login");

  function authed() {
    try {
      return sessionStorage.getItem(STORAGE_KEY) === PASS_HASH;
    } catch {
      return false;
    }
  }

  function grant() {
    try {
      sessionStorage.setItem(STORAGE_KEY, PASS_HASH);
    } catch {
      /* private mode */
    }
  }

  async function hashPassword(value) {
    const bytes = new TextEncoder().encode(value);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
  }

  function safeNext(raw) {
    if (!raw || !raw.startsWith("/") || raw.startsWith("//") || raw.startsWith(GATE_URL)) {
      return DEFAULT_NEXT;
    }
    return raw;
  }

  function redirectAfterLogin() {
    const next = safeNext(new URLSearchParams(location.search).get("next") || "");
    location.replace(next);
  }

  if (!isLoginPage) {
    if (!authed()) {
      const returnTo = location.pathname + location.search + location.hash;
      const suffix =
        returnTo && returnTo !== "/" && returnTo !== "/index.html"
          ? `?next=${encodeURIComponent(returnTo)}`
          : "";
      location.replace(GATE_URL + suffix);
      return;
    }

    if (location.pathname === "/" || location.pathname === "/index.html") {
      location.replace(DEFAULT_NEXT);
    }
    return;
  }

  document.documentElement.classList.add("gate-pending");

  async function tryLogin(password) {
    const hash = await hashPassword(password);
    if (hash !== PASS_HASH) return false;
    grant();
    return true;
  }

  function initLogin() {
    if (authed()) {
      redirectAfterLogin();
      return;
    }

    document.documentElement.classList.replace("gate-pending", "gate-ready");

    const form = document.getElementById("gate-form");
    const input = document.getElementById("gate-password");
    const wrap = document.querySelector(".gate-input-wrap");
    const hint = document.getElementById("gate-hint");
    if (!form || !input) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      hint.textContent = "";
      wrap?.classList.remove("is-error");

      const ok = await tryLogin(input.value);
      if (ok) {
        redirectAfterLogin();
        return;
      }

      wrap?.classList.add("is-error");
      hint.textContent = "Неверный пароль";
      input.select();
    });

    input.focus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLogin);
  } else {
    initLogin();
  }
})();
