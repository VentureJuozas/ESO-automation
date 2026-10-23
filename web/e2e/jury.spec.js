import { expect, test } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test("ESO helper single-case flow, step panels, approve, TS PDF", async ({ page, request }) => {
  await page.goto("/");
  await expect(page.getByTestId("app-title")).toHaveText("ESO helper");
  await expect(page).toHaveTitle("ESO helper");
  await page.getByTestId("nav-flow").click();
  await expect(page.getByTestId("sidebar")).toContainText("Application");
  await expect(page.getByTestId("sidebar")).toContainText("Connection point");
  await expect(page.getByTestId("sidebar")).toContainText("Analysis");
  await expect(page.getByTestId("sidebar")).toContainText("Solution");
  await expect(page.getByTestId("sidebar")).toContainText("Issue");
  await expect(page.getByTestId("request-bar")).toContainText("Requested power");
  await expect(page.getByTestId("request-bar")).toContainText("11 kW, 3-phase");
  await expect(page.getByTestId("request-bar")).toContainText("Coordinates");
  await expect(page.getByTestId("request-bar")).toContainText("pole 200/3");
  await expect(page.getByTestId("request-bar")).toContainText("New pole-mounted cabinet");
  await expect(page.getByTestId("request-bar")).not.toContainText("·");
  await expect(page.locator("body")).not.toContainText("Paleisti visas");
  await expect(page.locator("body")).not.toContainText("Atstatyti demo");
  await expect(page.locator("body")).not.toContainText("n8n");
  await expect(page.locator("body")).not.toContainText("DEMONSTRACINIS");
  await expect(page.locator("body")).not.toContainText("What-if");

  await page.getByTestId("run-flow").click();
  await expect(page.getByTestId("approval-dock")).toBeVisible({ timeout: 40000 });

  await page.getByTestId("step-check_capacity").click();
  await expect(page.getByTestId("step-panel")).toBeVisible();
  await expect(page.getByTestId("data-source")).toContainText("Power BI");
  await expect(page.getByTestId("requirements")).toContainText("80 %");
  await expect(page.getByTestId("calculation")).toBeVisible();
  await expect(page.getByTestId("load-loss")).toBeVisible();
  await expect(page.getByTestId("load-loss")).toContainText("Feeder current");
  await expect(page.getByTestId("load-loss")).toContainText("P_feeder");
  await expect(page.getByTestId("line-loading")).toContainText("Pass");
  await expect(page.getByTestId("load-loss")).not.toContainText("160.9");
  await expect(page.getByTestId("load-loss")).not.toContainText("85.4");
  await expect(page.getByTestId("loss-segments")).toBeVisible();
  await expect(page.getByTestId("result-block")).toContainText("Pass");

  await page.getByTestId("step-check_voltage_drop").click();
  await expect(page.getByTestId("data-source")).toContainText("line-load");
  await expect(page.getByTestId("requirements")).toContainText("207 V");
  await expect(page.getByTestId("load-loss")).toBeVisible();
  await expect(page.getByTestId("step-panel")).toContainText("224.0 V");
  await expect(page.getByTestId("line-loading")).toContainText("Pass");
  await expect(page.getByTestId("step-result")).toHaveText("Pass");

  await page.getByTestId("step-select_solution").click();
  await expect(page.getByTestId("calculation")).toContainText("selected");
  await expect(page.getByTestId("load-loss")).toContainText("Load and loss");

  await page.getByTestId("nav-trace").click();
  await expect(page.getByTestId("trace-panel")).toBeVisible();
  await expect(page.getByTestId("trace-stats")).toContainText("LLM");
  await expect(page.getByTestId("trace-stats")).toContainText("Python");
  await expect(page.getByTestId("trace-stats")).toContainText("Human");
  await expect(page.getByTestId("trace-legend")).toContainText("Python");
  await expect(page.getByTestId("trace-step-parse_request")).toBeVisible();

  await page.getByTestId("approve").click();
  await expect(page.getByTestId("open-ts")).toBeVisible({ timeout: 20000 });
  const href = await page.getByTestId("open-ts").getAttribute("href");
  const html = await request.get(href);
  expect(html.ok()).toBeTruthy();
  const text = await html.text();
  expect(text).toContain("PRIJUNGIMO SĄLYGOS");
  expect(text).toContain("Nauja leistina naudoti galia");
  expect(text).toContain("data:image/jpeg;base64,");
  expect(text).not.toContain("DEMONSTRACINIS");
  for (const glyph of "ąčęėįšųūž") expect(text).toContain(glyph);
  const pdf = await request.get(href.replace("/ts.html", "/ts.pdf"));
  expect(pdf.ok()).toBeTruthy();
  const body = await pdf.body();
  expect(body.subarray(0, 4).toString()).toBe("%PDF");
  expect(body.includes(Buffer.from("DejaVu"))).toBeTruthy();
});

test("sidebar groups collapse and select steps", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("nav-flow").click();
  const checks = page.getByTestId("group-checks");
  await expect(checks.getByTestId("step-check_capacity")).toBeVisible();
  await checks.getByRole("button", { name: /Analysis/ }).click();
  await expect(checks.getByTestId("step-check_capacity")).toHaveCount(0);
  await checks.getByRole("button", { name: /Analysis/ }).click();
  await page.getByTestId("step-check_voltage_drop").click();
  await expect(page.getByTestId("step-panel")).toContainText("Voltage");
  await expect(page.getByTestId("data-source")).toBeVisible();
  await expect(page.getByTestId("requirements")).toBeVisible();
});
