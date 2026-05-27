#!/usr/bin/env node
/**
 * Create or update «Отчет по обратной связи менеджеров 2» in Drive SEO folder.
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
const REPORT_TITLE = "Отчет по обратной связи менеджеров 2 (итерация 26–27.05)";
const SHEET_TITLE = "ОС по пунктам";
const CSV_PATH = path.join(ROOT, "data/export/manager-feedback-report-2.csv");

const TOKEN_PATH = path.join(os.homedir(), ".config/gdrive-upload-token.json");
const CREDS_PATH = path.join(os.homedir(), ".config/gdrive-credentials.json");

const HEADER_GREEN = { red: 0.851, green: 0.918, blue: 0.827 };
const BAND_LIGHT = { red: 0.949, green: 0.949, blue: 0.949 };
const BAND_WHITE = { red: 1, green: 1, blue: 1 };

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

async function ensureSpreadsheet(drive, sheets) {
  const files = await listFolder(drive);
  let file = files.find(
    (f) =>
      f.mimeType === "application/vnd.google-apps.spreadsheet" &&
      /обратной связи менеджеров 2/i.test(f.name),
  );

  if (!file) {
    const created = await drive.files.create({
      requestBody: {
        name: REPORT_TITLE,
        parents: [FOLDER_ID],
        mimeType: "application/vnd.google-apps.spreadsheet",
      },
      fields: "id,name,webViewLink",
      supportsAllDrives: true,
    });
    file = created.data;
    console.log(`Created: ${file.name}`);
  } else {
    console.log(`Found: ${file.name} (${file.id})`);
  }

  const spreadsheetId = file.id;
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const first = meta.data.sheets?.[0];
  if (first && first.properties?.title !== SHEET_TITLE) {
    await sheets.spreadsheets.batchUpdate({
      spreadsheetId,
      requestBody: {
        requests: [
          {
            updateSheetProperties: {
              properties: {
                sheetId: first.properties.sheetId,
                title: SHEET_TITLE,
              },
              fields: "title",
            },
          },
        ],
      },
    });
  }

  return { spreadsheetId, webViewLink: file.webViewLink };
}

async function getSheetId(sheets, spreadsheetId, title) {
  const meta = await sheets.spreadsheets.get({ spreadsheetId });
  const sheet = meta.data.sheets?.find((s) => s.properties?.title === title);
  if (!sheet) throw new Error(`Sheet not found: ${title}`);
  return { sheetId: sheet.properties.sheetId, meta: sheet };
}

async function writeTab(sheets, spreadsheetId, tabTitle, values) {
  const esc = tabTitle.replace(/'/g, "''");
  await sheets.spreadsheets.values.clear({
    spreadsheetId,
    range: `'${esc}'!A:ZZ`,
  });
  await sheets.spreadsheets.values.update({
    spreadsheetId,
    range: `'${esc}'!A1`,
    valueInputOption: "USER_ENTERED",
    requestBody: { values },
  });
}

async function formatFeedbackTab(sheets, spreadsheetId, tabTitle, values) {
  const rowCount = values.length;
  const colCount = values[0]?.length || 4;
  const { sheetId, meta } = await getSheetId(sheets, spreadsheetId, tabTitle);
  const requests = [];

  for (const band of meta.bandedRanges || []) {
    if (band.range?.sheetId === sheetId) {
      requests.push({ deleteBanding: { bandedRangeId: band.bandedRangeId } });
    }
  }

  // Сброс фильтра перед повторной установкой
  requests.push({ clearBasicFilter: { sheetId } });

  requests.push({
    updateSheetProperties: {
      properties: { sheetId, gridProperties: { frozenRowCount: 1 } },
      fields: "gridProperties.frozenRowCount",
    },
  });

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
          wrapStrategy: "WRAP",
        },
      },
      fields:
        "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
    },
  });

  if (rowCount > 1) {
    requests.push({
      repeatCell: {
        range: {
          sheetId,
          startRowIndex: 1,
          endRowIndex: rowCount,
          startColumnIndex: 0,
          endColumnIndex: colCount,
        },
        cell: {
          userEnteredFormat: {
            wrapStrategy: "WRAP",
            verticalAlignment: "TOP",
          },
        },
        fields: "userEnteredFormat(wrapStrategy,verticalAlignment)",
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

  // Шире колонки «Что сделали» и «Осталось»
  const wideCols = [2, 3];
  for (const col of wideCols) {
    if (col < colCount) {
      requests.push({
        updateDimensionProperties: {
          range: {
            sheetId,
            dimension: "COLUMNS",
            startIndex: col,
            endIndex: col + 1,
          },
          properties: { pixelSize: 420 },
          fields: "pixelSize",
        },
      });
    }
  }
  if (colCount > 0) {
    requests.push({
      updateDimensionProperties: {
        range: {
          sheetId,
          dimension: "COLUMNS",
          startIndex: 0,
          endIndex: 1,
        },
        properties: { pixelSize: 140 },
        fields: "pixelSize",
      },
    });
  }
  if (colCount > 1) {
    requests.push({
      updateDimensionProperties: {
        range: {
          sheetId,
          dimension: "COLUMNS",
          startIndex: 1,
          endIndex: 2,
        },
        properties: { pixelSize: 280 },
        fields: "pixelSize",
      },
    });
  }

  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests },
  });
}

async function main() {
  if (!fs.existsSync(CSV_PATH)) {
    console.error(`Missing ${CSV_PATH}`);
    process.exit(1);
  }

  const values = parseCsv(fs.readFileSync(CSV_PATH, "utf8"));
  const oauth2 = auth();
  const drive = google.drive({ version: "v3", auth: oauth2 });
  const sheets = google.sheets({ version: "v4", auth: oauth2 });

  const { spreadsheetId, webViewLink } = await ensureSpreadsheet(drive, sheets);
  await writeTab(sheets, spreadsheetId, SHEET_TITLE, values);
  await formatFeedbackTab(sheets, spreadsheetId, SHEET_TITLE, values);

  const files = await listFolder(drive);
  const file = files.find((f) => f.id === spreadsheetId);
  if (file && file.name !== REPORT_TITLE) {
    await drive.files.update({
      fileId: spreadsheetId,
      requestBody: { name: REPORT_TITLE },
      supportsAllDrives: true,
    });
  }

  const url =
    webViewLink ||
    `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`;
  console.log(`\n✓ ${SHEET_TITLE}: ${values.length - 1} строк`);
  console.log(url);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
