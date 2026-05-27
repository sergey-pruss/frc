(function () {
  "use strict";

  const AUTH_KEY = "frc-gate-v1";
  const PASS_HASH = "c6c2307ac025abfed680cb646bc38ca3c3d6e02662a0f2faa143dcff22268a49";
  const GATE_URL = "/gate/";
  const DEFAULT_NEXT = "/seo/";
  const COOKIE_MAX_AGE = 31536000;

  const script = document.currentScript;
  const isLoginPage = script?.hasAttribute("data-gate-login");

  function readCookie(name) {
    for (const part of document.cookie.split(";")) {
      const chunk = part.trim();
      if (!chunk) continue;
      const eq = chunk.indexOf("=");
      if (eq === -1) continue;
      if (chunk.slice(0, eq) === name) {
        return decodeURIComponent(chunk.slice(eq + 1));
      }
    }
    return "";
  }

  function authed() {
    try {
      if (localStorage.getItem(AUTH_KEY) === PASS_HASH) return true;
    } catch {
      /* private mode */
    }
    return readCookie(AUTH_KEY) === PASS_HASH;
  }

  function grant() {
    try {
      localStorage.setItem(AUTH_KEY, PASS_HASH);
    } catch {
      /* private mode */
    }
    const secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${AUTH_KEY}=${PASS_HASH}; Path=/; Max-Age=${COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
  }

  function safeNext(raw) {
    if (
      !raw ||
      raw === "/" ||
      raw === "/index.html" ||
      !raw.startsWith("/") ||
      raw.startsWith("//") ||
      raw.startsWith(GATE_URL)
    ) {
      return DEFAULT_NEXT;
    }
    return raw;
  }

  async function hashPassword(value) {
    const bytes = new TextEncoder().encode(value);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
  }

  function redirectAfterLogin() {
    const next = safeNext(new URLSearchParams(location.search).get("next") || "");
    location.replace(next);
  }

  if (!isLoginPage) {
    if (location.pathname.startsWith("/gate")) return;

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

  if (authed()) {
    redirectAfterLogin();
    return;
  }

  async function tryLogin(password) {
    const hash = await hashPassword(password);
    if (hash !== PASS_HASH) return false;
    grant();
    return true;
  }

  function initLogin() {
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
