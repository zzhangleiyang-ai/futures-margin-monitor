import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const [, , urlArg, screenshotArg, retriesArg, delayArg] = process.argv;

if (!urlArg) {
  console.error("Usage: node .github/scripts/check-site.mjs <url> [screenshot] [retries] [delayMs]");
  process.exit(1);
}

const screenshotPath = screenshotArg || path.join(".artifacts", "site-check.png");
const maxAttempts = Math.max(1, Number.parseInt(retriesArg || "1", 10));
const delayMs = Math.max(1000, Number.parseInt(delayArg || "5000", 10));

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function ensureParent(filePath) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
}

function shouldIgnoreConsole(text) {
  return /favicon\.ico/i.test(text);
}

async function runCheck(targetUrl) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
  const consoleErrors = [];
  const pageErrors = [];

  page.on("console", message => {
    if (message.type() === "error" && !shouldIgnoreConsole(message.text())) {
      consoleErrors.push(message.text());
    }
  });
  page.on("pageerror", error => pageErrors.push(error.message));

  try {
    await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2500);

    const summary = await page.evaluate(() => {
      const tableRows = document.querySelectorAll("tbody tr").length;
      const cards = document.querySelectorAll("[data-code]").length;
      const title = document.title || "";
      const statusText =
        document.getElementById("statusText")?.textContent?.trim() ||
        document.getElementById("selfCheckStatus")?.textContent?.trim() ||
        "";
      const totalCount =
        document.getElementById("totalCount")?.textContent?.trim() ||
        document.querySelectorAll("[data-code]").length.toString();
      const bodyText = (document.body?.innerText || "").replace(/\s+/g, " ").trim();
      return {
        title,
        tableRows,
        cards,
        statusText,
        totalCount,
        bodyText,
      };
    });

    await ensureParent(screenshotPath);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const visibleItems = Math.max(summary.tableRows, summary.cards);
    if (!summary.title) {
      throw new Error("page title is empty");
    }
    if (visibleItems < 20) {
      throw new Error(`too few visible items: ${visibleItems}`);
    }
    if (/加载失败|数据不可用|failed to fetch|404/i.test(summary.bodyText)) {
      throw new Error("page body indicates a loading failure");
    }
    if (/异常/i.test(summary.statusText)) {
      throw new Error(`status text indicates errors: ${summary.statusText}`);
    }
    if (consoleErrors.length) {
      throw new Error(`console errors: ${consoleErrors.join(" | ")}`);
    }
    if (pageErrors.length) {
      throw new Error(`page errors: ${pageErrors.join(" | ")}`);
    }

    console.log(JSON.stringify({ ok: true, url: targetUrl, visibleItems, ...summary }, null, 2));
  } finally {
    await browser.close();
  }
}

let lastError;
for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
  try {
    await runCheck(urlArg);
    process.exit(0);
  } catch (error) {
    lastError = error;
    console.error(`SITE CHECK attempt ${attempt}/${maxAttempts} failed: ${error.message}`);
    if (attempt < maxAttempts) {
      await sleep(delayMs);
    }
  }
}

console.error(`SITE CHECK FAILED: ${lastError?.message || "unknown error"}`);
process.exit(1);
