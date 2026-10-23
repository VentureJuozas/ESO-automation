import { expect, test } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test("customer submit, desk approve, PDF download", async ({ page, request }) => {
  await page.goto("/");
  await page.getByTestId("nav-split").click();
  const name = `E2E namas ${Date.now()}`;
  await page.getByTestId("portal-object").fill(name);
  await page.getByTestId("portal-submit").click();
  await expect(page.getByTestId("portal-status")).toContainText("laukia inžinieriaus", { timeout: 20000 });
  await expect(page.getByTestId("portal-timeline")).toContainText("laukia duomenų");
  await expect(page.getByTestId("portal-sla")).toBeVisible();
  const card = page.locator(`[data-title="${name}"]`);
  await expect(card).toBeVisible({ timeout: 20000 });
  await card.getByRole("button", { name: "Patvirtinti" }).click();
  await expect(page.getByTestId("portal-status")).toContainText("išduota", { timeout: 20000 });
  const href = await page.getByTestId("portal-pdf").getAttribute("href");
  const pdf = await request.get(href);
  expect(pdf.ok()).toBeTruthy();
  const body = await pdf.body();
  expect(body.subarray(0, 4).toString()).toBe("%PDF");
  expect(body.includes(Buffer.from("DejaVu"))).toBeTruthy();
  expect(body.includes(Buffer.from("/Count 2"))).toBeTruthy();
  expect(body.includes(Buffer.from("GIS-ANNEX"))).toBeTruthy();
  expect(body.includes(Buffer.from("TS-PAGE-1"))).toBeTruthy();
  expect(body.includes(Buffer.from("26-E-DEMO"))).toBeTruthy();
  const htmlHref = href.replace(/\.pdf$/, ".html").replace("/ts.pdf", "/ts.html");
  const html = await request.get(htmlHref);
  expect(html.ok()).toBeTruthy();
  const text = await html.text();
  expect(text).toContain('data-page="1"');
  expect(text).toContain('data-page="2"');
  expect(text).toContain("Priedas A");
  expect(text).toContain("ąčęėįšųūž");
});

test("missing-data branch resumes then issues", async ({ page, request }) => {
  await page.goto("/");
  await page.getByTestId("nav-customer").click();
  const name = `E2E be koord ${Date.now()}`;
  await page.getByTestId("portal-object").fill(name);
  await page.getByTestId("portal-nocoord").check();
  await page.getByTestId("portal-submit").click();
  await expect(page.getByTestId("portal-status")).toContainText("laukia duomenų", { timeout: 20000 });
  await expect(page.getByTestId("portal-missing")).toContainText("neišsiųstas");
  await page.getByTestId("portal-answer").click();
  await expect(page.getByTestId("portal-status")).toContainText("laukia inžinieriaus", { timeout: 20000 });
  await page.getByTestId("nav-desk").click();
  const card = page.locator(`[data-title="${name}"]`);
  await expect(card).toBeVisible({ timeout: 20000 });
  await card.getByRole("button", { name: "Patvirtinti" }).click();
  await page.getByTestId("nav-customer").click();
  // tracker is in-memory on that portal instance; re-submit is a new form.
  // Use API to confirm issued after approve.
  const queue = await request.get("/api/queue").then((r) => r.json());
  const row = queue.cases.find((c) => c.title === name);
  expect(row).toBeTruthy();
  const snap = await request.get(`/api/runs/${row.run_id}`).then((r) => r.json());
  expect(snap.status).toBe("issued");
});

test("fail branch shows reinforcement brief", async ({ page, request }) => {
  await page.goto("/");
  await page.getByTestId("scenario-fail_capacity").click();
  await expect(page.getByTestId("run-flow")).toBeEnabled();
  await page.getByTestId("run-flow").click();
  await expect(page.getByTestId("escalate-dock")).toBeVisible({ timeout: 40000 });
  const href = await page.getByTestId("brief-link").getAttribute("href");
  const html = await request.get(href);
  expect(html.ok()).toBeTruthy();
  const text = await html.text();
  expect(text).toContain("630");
  expect(text).toContain("ąčęėįšųūž");
  const pdf = await request.get(href.replace(".html", ".pdf"));
  expect((await pdf.body()).subarray(0, 4).toString()).toBe("%PDF");
});

test("agent trace overlay lists LLM Python and human", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("scenario-hero").click();
  await page.getByTestId("run-flow").click();
  await expect(page.getByTestId("kind-overlay")).toBeVisible({ timeout: 20000 });
  await page.getByTestId("kind-overlay").click();
  await expect(page.getByTestId("trace-panel")).toBeVisible();
  await expect(page.getByTestId("trace-stats")).toContainText("LLM");
  await expect(page.getByTestId("trace-stats")).toContainText("žmogaus");
  await expect(page.getByTestId("trace-legend")).toContainText("Python");
  await expect(page.getByTestId("canvas-kind-legend")).toBeVisible();
  await expect(page.getByTestId("trace-step-parse_request")).toBeVisible({ timeout: 20000 });
});

test("what-if 11 to 100 kW flips to escalate", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("scenario-hero").click();
  await page.getByTestId("whatif-kw").fill("100");
  await page.getByTestId("whatif-run").click();
  await expect(page.getByTestId("escalate-dock")).toBeVisible({ timeout: 20000 });
});

test("presentation walks every beat in LT and EN", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("start-present").click();
  await expect(page.getByTestId("present-bar")).toBeVisible();
  await page.getByTestId("present-toggle").click();
  const pack = await page.request.get("/api/present").then((r) => r.json());
  const beats = pack.beats;
  for (let i = 0; i < beats.length; i += 1) {
    await expect(page.getByTestId("present-title")).toHaveText(beats[i].lt.title);
    await page.getByTestId("present-en").click();
    await expect(page.getByTestId("present-title")).toHaveText(beats[i].en.title);
    await page.getByTestId("present-lt").click();
    await expect(page.getByTestId("present-title")).toHaveText(beats[i].lt.title);
    if (i < beats.length - 1) {
      await page.getByTestId("present-next").click();
    }
  }
  await expect(page.getByTestId("present-restart")).toBeVisible();
  await page.getByTestId("present-restart").click();
  await expect(page.getByTestId("present-title")).toHaveText(beats[0].lt.title);
});
