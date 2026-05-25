#!/usr/bin/env node
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const OUT = resolve(ROOT, "assets/generated/competitors");

const competitors = [
  { url: "https://kremlin-symbol.ru", file: "kremlin-symbol-home.png" },
  { url: "https://www.yarussia.com", file: "yarussia-home.png" },
  { url: "https://putin-team.ru", file: "putin-team-home.png" },
  { url: "https://victorydayshop.ru", file: "victorydayshop-home.png" },
  { url: "https://myhomeland.ru", file: "myhomeland-home.png" },
  { url: "https://russian-t-shirts.shop", file: "russian-tshirts-home.png" },
  { url: "https://greatrussianstyle.ru", file: "velikoross-home.png" },
  { url: "https://lutchshop.ru", file: "lutchshop-home.png" },
  { url: "https://shop.atributika.ru/katalog/russia/", file: "atributika-home.png" },
  { url: "https://gloryseason.ru", file: "gloryseason-home.png" },
  { url: "https://www.vsemayki.ru", file: "vsemayki-catalog.png" },
  { url: "https://printbar.ru", file: "printbar-home.png" },
  { url: "https://printio.ru", file: "printio-home.png" },
  { url: "https://v2.bosco.ru", file: "bosco-home.png" },
  { url: "https://shop.fc-zenit.ru", file: "zenit-home.png" },
  { url: "https://shop.tretyakovgallery.ru", file: "tretyakov-home.png" },
  { url: "https://www.hermitageshop.ru", file: "hermitage-home.png" },
  { url: "https://shop.shm.ru", file: "shm-home.png" },
  { url: "https://theartsmuseum.store", file: "pushkin-home.png" },
  { url: "https://rus-vit.ru", file: "rus-vit-home.png" },
];

const browser = await puppeteer.launch({
  headless: true,
  args: ["--no-sandbox", "--disable-setuid-sandbox"],
});

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function dismissPopups(page) {
  const selectors = [
    '[class*="cookie"] button',
    '[class*="Cookie"] button',
    '[id*="cookie"] button',
    '[class*="consent"] button',
    '[class*="popup"] [class*="close"]',
    '[class*="modal"] [class*="close"]',
    'button[class*="accept"]',
    'button[class*="agree"]',
    '.cookie-banner button',
    '.cookies button',
  ];
  for (const sel of selectors) {
    try {
      const btn = await page.$(sel);
      if (btn) {
        await btn.click();
        await sleep(500);
      }
    } catch {}
  }
}

let done = 0;
const total = competitors.length;

for (const { url, file } of competitors) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

  try {
    await page.goto(url, { waitUntil: "networkidle2", timeout: 30000 });
    await sleep(2000);
    await dismissPopups(page);
    await sleep(500);

    const outPath = resolve(OUT, file);
    await page.screenshot({ path: outPath, type: "png" });
    done++;
    console.log(`[${done}/${total}] ✓ ${file} <- ${url}`);
  } catch (err) {
    done++;
    console.log(`[${done}/${total}] ✗ ${file} <- ${url} (${err.message})`);
  }

  await page.close();
}

await browser.close();
console.log(`\nDone: ${done}/${total} screenshots captured.`);
