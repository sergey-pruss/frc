#!/usr/bin/env node
/**
 * Upload refreshed SEO / competitor PDFs to the shared Drive SEO folder.
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

const REPORTS = [
  {
    local: "export/seo-strategy-report.pdf",
    driveName: "seo-strategy-report.pdf",
  },
  {
    local: "export/competitor-analysis-report.pdf",
    driveName: "competitor-analysis-report.pdf",
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

async function listFolder(drive) {
  const res = await drive.files.list({
    q: `'${FOLDER_ID}' in parents and trashed=false`,
    fields: "files(id,name,mimeType,modifiedTime)",
    pageSize: 100,
    supportsAllDrives: true,
    includeItemsFromAllDrives: true,
  });
  return res.data.files || [];
}

async function uploadOrUpdate(drive, file, localPath, driveName) {
  const media = {
    mimeType: "application/pdf",
    body: fs.createReadStream(localPath),
  };

  if (file) {
    await drive.files.update({
      fileId: file.id,
      media,
      supportsAllDrives: true,
    });
    console.log(`  ✓ updated ${driveName} (${file.id})`);
    return file.id;
  }

  const created = await drive.files.create({
    requestBody: {
      name: driveName,
      parents: [FOLDER_ID],
      mimeType: "application/pdf",
    },
    media,
    fields: "id,name",
    supportsAllDrives: true,
  });
  console.log(`  ✓ created ${driveName} (${created.data.id})`);
  return created.data.id;
}

async function main() {
  for (const { local } of REPORTS) {
    const p = path.join(ROOT, local);
    if (!fs.existsSync(p)) {
      console.error(`Missing ${p}. Run: npm run build:pdf`);
      process.exit(1);
    }
  }

  const oauth2 = auth();
  const drive = google.drive({ version: "v3", auth: oauth2 });
  const files = await listFolder(drive);

  console.log("Drive SEO folder PDFs:");
  for (const { local, driveName } of REPORTS) {
    const localPath = path.join(ROOT, local);
    const stat = fs.statSync(localPath);
    const file = files.find((f) => f.name === driveName);
    console.log(`\n→ ${driveName} (local ${stat.mtime.toISOString().slice(0, 16)})`);
    await uploadOrUpdate(drive, file, localPath, driveName);
  }

  console.log("\nDone.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
