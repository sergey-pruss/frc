#!/usr/bin/env node
/**
 * Watch for changes in report pages and rebuild PDFs.
 */
import { watch } from "chokidar";
import { execSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

let building = false;

function run(cmd, label) {
  console.log(`\n[watch] ${label}…`);
  try {
    execSync(cmd, { cwd: ROOT, stdio: "inherit" });
    console.log(`[watch] ${label} ✓`);
  } catch (e) {
    console.error(`[watch] ${label} FAILED (exit ${e.status})`);
  }
}

async function rebuild(trigger) {
  if (building) return;
  building = true;
  const ts = new Date().toLocaleTimeString("ru-RU");
  console.log(`\n═══ ${ts}  changed: ${trigger} ═══`);

  const siteSource = /scripts\/(content|generate-prototype)\.py/.test(trigger);
  const reportSource =
    /^(seo|analysis)\/index\.html$/.test(trigger) ||
    /^assets\//.test(trigger) ||
    /^data\/.*\.json$/.test(trigger);

  if (siteSource) {
    run("python3 scripts/generate-prototype.py", "generate site");
  }

  if (siteSource || reportSource) {
    run("node scripts/generate-pdf.mjs", "generate PDF");
  }

  building = false;
}

const watcher = watch(
  [
    "scripts/content.py",
    "scripts/generate-prototype.py",
    "seo/index.html",
    "analysis/index.html",
    "assets/**/*",
    "data/catalog-wordstat-full.json",
    "data/catalog-keywords-top10.json",
  ],
  {
    cwd: ROOT,
    ignoreInitial: true,
    awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
  },
);

watcher.on("change", (path) => rebuild(path));
watcher.on("add", (path) => rebuild(path));

console.log("[watch] Watching seo/, analysis/, assets/, data/…");
console.log("[watch] Press Ctrl+C to stop.\n");
