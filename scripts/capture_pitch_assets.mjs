/**
 * Round 10 pitch assets. Does not change app code.
 * Writes 1920x1080 PNGs and full-autoplay MP4 backups.
 */
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, "../web/package.json"));
const { chromium } = require("@playwright/test");

const BASE = process.env.ESO_BASE || "http://127.0.0.1:8000";
const ART = "/opt/cursor/artifacts";
const MEDIA = path.resolve("docs/media");
const VIDEO_TMP = "/tmp/eso-videos";
const VIEW = { width: 1920, height: 1080 };
const SETTLE = 700;

fs.mkdirSync(ART, { recursive: true });
fs.mkdirSync(MEDIA, { recursive: true });

function shot(name) {
  return {
    art: path.join(ART, `${name}.png`),
    media: path.join(MEDIA, `${name}.png`),
  };
}

async function snap(page, name) {
  await page.waitForTimeout(SETTLE);
  const dest = shot(name);
  await page.screenshot({ path: dest.art, fullPage: false });
  fs.copyFileSync(dest.art, dest.media);
  console.log("shot", name);
}

async function gotoApp(page) {
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForSelector('[data-testid="start-present"]', { timeout: 20000 });
}

async function presentAt(page, steps) {
  await page.getByTestId("start-present").click();
  await page.getByTestId("present-bar").waitFor();
  const toggle = page.getByTestId("present-toggle");
  const label = (await toggle.innerText()).toLowerCase();
  if (/pauz|pause/.test(label)) await toggle.click();
  for (let i = 0; i < steps; i += 1) {
    const next = page.getByTestId("present-next");
    if (await next.isEnabled()) await next.click();
    else break;
    await page.waitForTimeout(280);
  }
}

async function captureStills(browser) {
  const page = await browser.newPage({ viewport: VIEW, deviceScaleFactor: 1 });
  await gotoApp(page);

  await presentAt(page, 0);
  await snap(page, "01_split_customer_desk");

  await page.getByTestId("present-next").click();
  await snap(page, "02_desk_queue");

  await page.getByTestId("present-next").click();
  await snap(page, "03_queue_after_paleisti_visas");

  await page.getByTestId("present-next").click();
  await snap(page, "03b_engineer_inbox");

  await page.getByTestId("present-next").click();
  await snap(page, "04_hero_canvas_inspector");

  await page.getByTestId("present-next").click();
  await snap(page, "05_abc_comparison");

  await page.getByTestId("present-next").click();
  await snap(page, "06_capacity");

  await page.getByTestId("present-exit").click();
  await page.locator('[data-node="check_voltage_drop"]').click();
  await snap(page, "07_voltage_profile");

  const pack = await page.request.get(BASE + "/api/present").then((r) => r.json());
  const heroId = pack.hero.id;
  await page.request.post(BASE + `/api/runs/${heroId}/resume`, { data: { decision: "approve" } });
  await page.goto(`${BASE}/api/runs/${heroId}/ts.html`, { waitUntil: "networkidle" });
  await page.locator('[data-page="1"]').waitFor({ timeout: 15000 });
  await snap(page, "08_ts_page_1");
  const page2 = page.locator('[data-page="2"]');
  if (await page2.count()) await page2.first().scrollIntoViewIfNeeded();
  await snap(page, "09_ts_page_2");

  await gotoApp(page);
  await presentAt(page, 8);
  await snap(page, "10_fail_reinforcement_brief");

  await page.getByTestId("present-next").click();
  await snap(page, "11_gallery_taxonomy");

  await page.getByTestId("present-exit").click();
  await gotoApp(page);
  await presentAt(page, 6);
  await page.getByTestId("present-exit").click();
  await page.locator('[data-node="check_capacity"]').click();
  await page.getByTestId("whatif-kw").evaluate((el) => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    setter.call(el, "100");
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  });
  await page.getByTestId("whatif-run").click();
  await page.getByTestId("escalate-dock").waitFor({ timeout: 20000 });
  await snap(page, "12_whatif_100kw");

  await gotoApp(page);
  await presentAt(page, 11);
  await snap(page, "13_agento_sekimas");

  await gotoApp(page);
  await presentAt(page, 12);
  await snap(page, "14_integracijos");

  await gotoApp(page);
  await presentAt(page, 13);
  await snap(page, "15_analitika");

  await page.goto(`${BASE}/api/onepager.html`, { waitUntil: "networkidle" });
  await snap(page, "16_onepager");

  await page.close();
}

async function recordAutoplay(browser, lang, rawWebm) {
  fs.mkdirSync(path.dirname(rawWebm), { recursive: true });
  const context = await browser.newContext({
    viewport: VIEW,
    deviceScaleFactor: 1,
    recordVideo: { dir: path.dirname(rawWebm), size: VIEW },
  });
  const page = await context.newPage();
  await gotoApp(page);
  await page.getByTestId("start-present").click();
  await page.getByTestId("present-bar").waitFor();
  if (lang === "en") {
    await page.getByTestId("present-en").click();
    await page.waitForTimeout(400);
    const playing = await page.getByTestId("present-toggle").innerText();
    if (/paleisti|play/i.test(playing)) await page.getByTestId("present-toggle").click();
  }
  await page.getByTestId("present-restart").waitFor({ timeout: 340000 });
  await page.waitForTimeout(32000);
  await page.close();
  const video = page.video();
  const tmp = await video.path();
  await context.close();
  fs.renameSync(tmp, rawWebm);
  console.log("recorded", lang, rawWebm, fs.statSync(rawWebm).size);
}

function toMp4(webm, mp4) {
  const r = spawnSync(
    "ffmpeg",
    [
      "-y",
      "-i",
      webm,
      "-vf",
      "scale=1920:1080:flags=lanczos,fps=30",
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-crf",
      "23",
      "-preset",
      "medium",
      "-movflags",
      "+faststart",
      "-an",
      mp4,
    ],
    { stdio: "inherit" },
  );
  if (r.status !== 0) throw new Error("ffmpeg failed for " + mp4);
}

async function maybeCommitCopy(mp4, destName) {
  const st = fs.statSync(mp4);
  const mb = st.size / (1024 * 1024);
  console.log("mp4", destName, mb.toFixed(1), "MB");
  if (mb <= 26) {
    const dest = path.join(MEDIA, destName);
    fs.copyFileSync(mp4, dest);
    console.log("copied under docs/media", dest);
    return dest;
  }
  console.log("over 25 MB — artifact only", mp4);
  return null;
}

const mode = process.argv[2] || "all";
const browser = await chromium.launch({ headless: true });
try {
  if (mode === "all" || mode === "stills") {
    console.log("stills…");
    await captureStills(browser);
  }
  if (mode === "all" || mode === "videos") {
    for (const lang of ["lt", "en"]) {
      const raw = path.join(VIDEO_TMP, `present_autoplay_${lang}.webm`);
      const mp4 = path.join(ART, `present_autoplay_${lang}_1920x1080.mp4`);
      console.log("autoplay", lang);
      await recordAutoplay(browser, lang, raw);
      toMp4(raw, mp4);
      await maybeCommitCopy(mp4, `present_autoplay_${lang}_1920x1080.mp4`);
    }
  }
} finally {
  await browser.close();
}
console.log("done");
