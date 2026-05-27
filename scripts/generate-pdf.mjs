#!/usr/bin/env node
/**
 * Render SEO strategy and competitor analysis PDFs from the live HTML pages
 * (seo/index.html, analysis/index.html), which include @media print styles.
 * Competitor analysis PDF omits #screenshots (see analysis/index.html @media print).
 */
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const reports = [
  {
    src: resolve(ROOT, "seo/index.html"),
    dst: resolve(ROOT, "export/seo-strategy-report.pdf"),
    name: "SEO Strategy",
  },
  {
    src: resolve(ROOT, "analysis/index.html"),
    dst: resolve(ROOT, "export/competitor-analysis-report.pdf"),
    name: "Competitor Analysis",
  },
];

const browser = await puppeteer.launch({ headless: true });

for (const { src, dst, name } of reports) {
  const page = await browser.newPage();
  await page.emulateMediaType("print");
  await page.goto(`file://${src}`, { waitUntil: "networkidle0", timeout: 120_000 });
  await page.pdf({
    path: dst,
    format: "A4",
    landscape: true,
    preferCSSPageSize: true,
    margin: { top: "10mm", bottom: "14mm", left: "10mm", right: "10mm" },
    printBackground: true,
    displayHeaderFooter: false,
  });
  await page.close();
  console.log(`pdf → ${dst} (${name})`);
}

await browser.close();
