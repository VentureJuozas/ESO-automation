/**
 * 1920x1080 product screenshots for ESO helper.
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, "../web/package.json"));
const { chromium } = require("@playwright/test");

const BASE = process.env.ESO_BASE || "http://127.0.0.1:8000";
const ART = "/opt/cursor/artifacts";
const MEDIA = path.resolve("docs/media");
const VIEW = { width: 1920, height: 1080 };

fs.mkdirSync(ART, { recursive: true });
fs.mkdirSync(MEDIA, { recursive: true });

async function snap(page, name) {
  await page.waitForTimeout(500);
  const art = path.join(ART, `${name}.png`);
  const media = path.join(MEDIA, `${name}.png`);
  await page.screenshot({ path: art, fullPage: false });
  fs.copyFileSync(art, media);
  console.log("shot", name);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: VIEW, deviceScaleFactor: 1 });
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.getByTestId("app-title").waitFor();
  await snap(page, "01_full_flow");
  await snap(page, "02_sidebar_dropdowns");

  await page.getByTestId("run-flow").click();
  await page.getByTestId("approval-dock").waitFor({ timeout: 40000 });

  await page.getByTestId("step-check_capacity").click();
  await page.getByTestId("load-loss").waitFor();
  await snap(page, "03_capacity_load_loss");

  await page.getByTestId("step-check_voltage_drop").click();
  await page.getByTestId("load-loss").waitFor();
  await snap(page, "04_voltage");

  await page.getByTestId("step-select_solution").click();
  await page.getByTestId("load-loss").waitFor();
  await snap(page, "05_solution");

  await snap(page, "06_approval");

  await page.getByTestId("nav-trace").click();
  await page.getByTestId("trace-panel").waitFor();
  await snap(page, "07_trace");

  await page.getByTestId("approve").click();
  await page.getByTestId("open-ts").waitFor({ timeout: 20000 });
  const href = await page.getByTestId("open-ts").getAttribute("href");
  await page.goto(BASE + href, { waitUntil: "networkidle" });
  await snap(page, "08_ts_page_1");
  const page2 = page.locator('[data-page="2"]');
  if (await page2.count()) {
    await page2.scrollIntoViewIfNeeded();
    await snap(page, "09_ts_page_2");
  }
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
