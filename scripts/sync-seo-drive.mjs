#!/usr/bin/env node
/**
 * Sync semantic CSV exports into Google Drive SEO folder spreadsheets.
 * ~/.config/gdrive-credentials.json + ~/.config/gdrive-upload-token.json
 */
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { google } from "googleapis";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const FOLDER_ID = "1lNe8YZ3axwHMfVJ-AgcH-pXWC5KJ4LWm";

const TOKEN_PATH = path.join(os.homedir(), ".config/gdrive-upload-token.json");
const CREDS_PATH = path.join(os.homedir(), ".config/gdrive-credentials.json");

const JOBS = [
  {
    match: "Семантическое ядро каталога",
    rename: "Семантическое ядро каталога (910 запросов)",
    tabs: [
      { title: "Полный спрос 100+", csv: "data/export/catalog-wordstat-full.csv" },
      { title: "Топ 5–10 на категорию", csv: "data/export/catalog-keywords-top10.csv" },
    ],
  },
  {
    match: "Кандидаты на статичные фильтры",
    rename: "Кандидаты на статичные фильтры (SEO whitelist)",
    tabs: [{ title: "Кандидаты", csv: "data/export/static-filter-candidates.csv" }],
  },
];

function auth() {
  const creds = JSON.parse(fs.readFileSync(CREDS_PATH, "utf8"));
  const token = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
  const oauth2 = new google.auth.OAuth2(
    creds.installed.client_id,
    creds.installed.client_secret,
  );
  oauth2.setCredentials(token);
  return oauth2;
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    const next = text[i + 1];
    if (inQuotes) {
      if (c === '"' && next === '"') {
        cell += '"';
        i++;
      } else if (c === '"') inQuotes = false;
      else cell += c;
      continue;
    }
    if (c === '"') {
      inQuotes = true;
      continue;
    }
    if (c === ",") {
      row.push(cell);
      cell = "";
      continue;
    }
    if (c === "\n" || (c === "\r" && next === "\n")) {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
      if (c === "\r") i++;
      continue;
    }
    if (c === "\r") continue;
    cell += c;
  }
  if (cell.length || row.length) {
    row.push(cell);
    rows.push(row);
  }
  return rows;
}

async function listFolder(drive) {
  const res = await drive.files.list({
    q: `'${FOLDER_ID}' in parents and trashed=false`,
    fields: "files(id,name,mimeType)",
    pageSize: 100,
    supportsAllDrives: true,
    includeItemsFromAllDrives: true,
  });
  return res.data.files || [];
}

async function getSheetId(sheets, spreadsheetId, title) {
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const sheet = meta.data.sheets?.find((s) => s.properties?.title === title);
  if (!sheet) throw new Error(`Sheet not found: ${title}`);
  return { sheetId: sheet.properties.sheetId, meta: sheet };
}

async function ensureSheetTab(sheets, spreadsheetId, title) {
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const existing = meta.data.sheets?.find((s) => s.properties?.title === title);
  if (existing) return existing.properties.sheetId;

  const res = await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [{ addSheet: { properties: { title } } }],
    },
  });
  return res.data.replies[0].addSheet.properties.sheetId;
}

const HEADER_GREEN = { red: 0.851, green: 0.918, blue: 0.827 };
const BAND_LIGHT = { red: 0.949, green: 0.949, blue: 0.949 };
const BAND_WHITE = { red: 1, green: 1, blue: 1 };
const CONTROVERSIAL_HIGH = { red: 0.96, green: 0.8, blue: 0.8 };
const CONTROVERSIAL_MED = { red: 1, green: 0.95, blue: 0.8 };

const HIGH_CONTROVERSIAL_REASONS = /Видеоигры|Авто-бренды|Спортклубы/;

function controversialBackground(reason) {
  return HIGH_CONTROVERSIAL_REASONS.test(reason || "") ? CONTROVERSIAL_HIGH : CONTROVERSIAL_MED;
}

async function formatTabLikeReference(sheets, spreadsheetId, tabTitle, values) {
  const rowCount = values.length;
  const colCount = values[0]?.length || 1;
  const headers = values[0] || [];
  const queryCol = headers.indexOf("Запрос");
  const showsCol = headers.indexOf("Показы/мес");
  const controversialCol = headers.indexOf("Спорный");
  const reasonCol = headers.indexOf("Причина");

  const { sheetId, meta } = await getSheetId(sheets, spreadsheetId, tabTitle);
  const requests = [];

  for (const band of meta.bandedRanges || []) {
    if (band.range?.sheetId === sheetId) {
      requests.push({ deleteBanding: { bandedRangeId: band.bandedRangeId } });
    }
  }

  requests.push({
    updateSheetProperties: {
      properties: {
        sheetId,
        gridProperties: { frozenRowCount: 1 },
      },
      fields: "gridProperties.frozenRowCount",
    },
  });

  if (rowCount > 1) {
    requests.push({
      addBanding: {
        bandedRange: {
          range: {
            sheetId,
            startRowIndex: 0,
            endRowIndex: rowCount,
            startColumnIndex: 0,
            endColumnIndex: colCount,
          },
          rowProperties: {
            headerColor: HEADER_GREEN,
            firstBandColor: BAND_WHITE,
            secondBandColor: BAND_LIGHT,
          },
        },
      },
    });
  }

  requests.push({
    repeatCell: {
      range: {
        sheetId,
        startRowIndex: 0,
        endRowIndex: 1,
        startColumnIndex: 0,
        endColumnIndex: colCount,
      },
      cell: {
        userEnteredFormat: {
          backgroundColor: HEADER_GREEN,
          textFormat: { bold: true },
          horizontalAlignment: "CENTER",
          verticalAlignment: "MIDDLE",
        },
      },
      fields: "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
    },
  });

  // Показы/мес — число с разделителем тысяч
  if (rowCount > 1 && showsCol >= 0) {
    requests.push({
      repeatCell: {
        range: {
          sheetId,
          startRowIndex: 1,
          endRowIndex: rowCount,
          startColumnIndex: showsCol,
          endColumnIndex: showsCol + 1,
        },
        cell: {
          userEnteredFormat: {
            numberFormat: { type: "NUMBER", pattern: "#,##0" },
            horizontalAlignment: "RIGHT",
          },
        },
        fields: "userEnteredFormat(numberFormat,horizontalAlignment)",
      },
    });
  }

  requests.push({
    setBasicFilter: {
      filter: {
        range: {
          sheetId,
          startRowIndex: 0,
          endRowIndex: rowCount,
          startColumnIndex: 0,
          endColumnIndex: colCount,
        },
      },
    },
  });

  requests.push({
    autoResizeDimensions: {
      dimensions: {
        sheetId,
        dimension: "COLUMNS",
        startIndex: 0,
        endIndex: colCount,
      },
    },
  });

  // Запрос — перенос длинных фраз
  if (rowCount > 1 && queryCol >= 0) {
    requests.push({
      repeatCell: {
        range: {
          sheetId,
          startRowIndex: 1,
          endRowIndex: rowCount,
          startColumnIndex: queryCol,
          endColumnIndex: queryCol + 1,
        },
        cell: {
          userEnteredFormat: { wrapStrategy: "WRAP" },
        },
        fields: "userEnteredFormat.wrapStrategy",
      },
    });
  }

  // Спорные запросы — подсветка строк по колонкам «Спорный» / «Причина»
  if (rowCount > 1 && controversialCol >= 0) {
    for (let rowIndex = 1; rowIndex < rowCount; rowIndex++) {
      const row = values[rowIndex] || [];
      if (row[controversialCol] !== "Да") continue;
      const reason = reasonCol >= 0 ? row[reasonCol] : "";
      requests.push({
        repeatCell: {
          range: {
            sheetId,
            startRowIndex: rowIndex,
            endRowIndex: rowIndex + 1,
            startColumnIndex: 0,
            endColumnIndex: colCount,
          },
          cell: {
            userEnteredFormat: {
              backgroundColor: controversialBackground(reason),
            },
          },
          fields: "userEnteredFormat.backgroundColor",
        },
      });
    }
  }

  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });
}

async function writeTab(sheets, spreadsheetId, tabTitle, values) {
  const range = `'${tabTitle.replace(/'/g, "''")}'!A:ZZ`;
  await sheets.spreadsheets.values.clear({ spreadsheetId, range });
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: `'${tabTitle.replace(/'/g, "''")}'!A1`,
    valueInputOption: "USER_ENTERED",
    requestBody: { values },
  });
}

async function syncSpreadsheet(drive, sheets, file, job) {
  const spreadsheetId = file.id;
  console.log(`\n→ ${file.name} (${spreadsheetId})`);

  for (const tab of job.tabs) {
    const csvPath = path.join(ROOT, tab.csv);
    if (!fs.existsSync(csvPath)) {
      console.error(`  Missing ${csvPath}`);
      process.exit(1);
    }
    const values = parseCsv(fs.readFileSync(csvPath, "utf8"));
    await ensureSheetTab(sheets, spreadsheetId, tab.title);
    await writeTab(sheets, spreadsheetId, tab.title, values);
    await formatTabLikeReference(sheets, spreadsheetId, tab.title, values);
    console.log(`  ✓ ${tab.title}: ${values.length - 1} rows (formatted)`);
  }

  if (job.rename) {
    const targetName = job.rename;
    if (file.name !== targetName) {
      await drive.files.update({
        fileId: spreadsheetId,
        requestBody: { name: targetName },
        supportsAllDrives: true,
      });
      console.log(`  Renamed → ${targetName}`);
    }
  }
}

async function main() {
  for (const job of JOBS) {
    for (const tab of job.tabs) {
      const p = path.join(ROOT, tab.csv);
      if (!fs.existsSync(p)) {
        console.error(`Missing ${p}. Run: npm run build:wordstat && python3 scripts/export-static-filters-csv.py`);
        process.exit(1);
      }
    }
  }

  const oauth2 = auth();
  const drive = google.drive({ version: "v3", auth: oauth2 });
  const sheets = google.sheets({ version: "v4", auth: oauth2 });

  const files = await listFolder(drive);
  console.log("SEO folder files:");
  for (const f of files) console.log(`  ${f.name}`);

  for (const job of JOBS) {
    const file = files.find(
      (f) =>
        f.name.includes(job.match) &&
        f.mimeType === "application/vnd.google-apps.spreadsheet",
    );
    if (!file) {
      console.warn(`\n⚠ Spreadsheet not found for: ${job.match}`);
      continue;
    }
    await syncSpreadsheet(drive, sheets, file, job);
  }

  console.log("\nDone.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
