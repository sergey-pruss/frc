#!/usr/bin/env node
/**
 * Watch for changes in source files and rebuild:
 *  - scripts/content.py or scripts/generate-prototype.py → regenerate site + PDF
 *  - export/seo-report-print.html → regenerate PDF only
 *  - assets/** → copy is instant (static), but re-run PDF in case images changed
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
  const reportSource = /export\/seo-report-print\.html/.test(trigger);

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
    "export/seo-report-print.html",
  ],
  {
    cwd: ROOT,
    ignoreInitial: true,
    awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
  }
);

watcher.on("change", (path) => rebuild(path));
watcher.on("add", (path) => rebuild(path));

console.log("[watch] Watching for changes in scripts/ and export/…");
console.log("[watch] Press Ctrl+C to stop.\n");
