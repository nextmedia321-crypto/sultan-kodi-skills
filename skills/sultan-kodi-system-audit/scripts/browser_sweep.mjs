#!/usr/bin/env node
// Automatic browser sweep with Playwright. Crawls same-origin pages, clicks every visible button,
// records console errors, page errors, failed requests, dead buttons, plus perf numbers and optional axe-core.
// Usage: node browser_sweep.mjs <url> [--out .audit/sweep] [--max-pages 15] [--mobile] [--allow-destructive]
//                               [--save baseline.json] [--compare baseline.json]
// Needs: npm i playwright (or a global install). axe-core is used only if resolvable (npm i axe-core).
import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const require = createRequire(process.cwd() + '/');
const argv = process.argv.slice(2); const url = argv.find(a => /^https?:/.test(a));
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
if (!url) { console.log('usage: node browser_sweep.mjs <url> [--out dir] [--max-pages N] [--mobile] [--allow-destructive] [--save f] [--compare f]'); process.exit(2); }
let pw; try { pw = require('playwright'); } catch { try { pw = require('/usr/lib/node_modules/playwright'); } catch { console.log('Playwright is not installed: run npm i playwright && npx playwright install chromium. Record the sweep as not checkable until then.'); process.exit(3); } }
let axeSrc = null; try { axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8'); } catch {}
const out = opt('--out', '.audit/sweep'); fs.mkdirSync(out, { recursive: true });
const maxPages = +opt('--max-pages', 15); const origin = new URL(url).origin;
const DESTRUCTIVE = /delete|remove|destroy|cancel (?:subscription|account)|pay|purchase|buy|checkout|logout|log out|sign out|מחק|הסר|תשלום|רכוש|התנתק/i;
const allowD = argv.includes('--allow-destructive');
const browser = await pw.chromium.launch(); const issues = []; const pages = []; const seen = new Set(); const queue = [url];
const ctx = await browser.newContext(argv.includes('--mobile') ? { viewport: { width: 390, height: 844 }, isMobile: true } : { viewport: { width: 1366, height: 800 } });
const add = (type, where, detail) => issues.push({ type, where, detail: String(detail).slice(0, 300) });
while (queue.length && pages.length < maxPages) {
  const u = queue.shift(); if (seen.has(u)) continue; seen.add(u);
  const page = await ctx.newPage(); const rec = { url: u };
  page.on('console', m => { if (m.type() === 'error') add('console error', u, m.text()); });
  page.on('pageerror', e => add('uncaught exception', u, e.message));
  page.on('requestfailed', r => add('failed request', u, `${r.method()} ${r.url()} ${r.failure()?.errorText}`));
  page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(origin)) add('http ' + r.status(), u, `${r.request().method()} ${r.url()}`); });
  try {
    const t0 = Date.now(); const resp = await page.goto(u, { waitUntil: 'networkidle', timeout: 30000 });
    rec.status = resp?.status(); rec.loadMs = Date.now() - t0;
    rec.perf = await page.evaluate(() => { const n = performance.getEntriesByType('navigation')[0]; const lcp = performance.getEntriesByType('largest-contentful-paint').pop(); const res = performance.getEntriesByType('resource'); return { domContentLoaded: Math.round(n?.domContentLoadedEventEnd || 0), lcp: Math.round(lcp?.startTime || 0), requests: res.length, kb: Math.round(res.reduce((s, r) => s + (r.transferSize || 0), 0) / 1024) }; });
    if (resp && resp.status() >= 400) add('page error status', u, resp.status());
    const links = await page.$$eval('a[href]', as => as.map(a => a.href)); for (const l of links) { try { const x = new URL(l); x.hash = ''; if (x.origin === origin && !seen.has(x.href) && !queue.includes(x.href) && !/\.(pdf|zip|png|jpg|svg)$/i.test(x.pathname)) queue.push(x.href); } catch {} }
    const noName = await page.$$eval('img:not([alt]), button:not([aria-label]):empty, input:not([type=hidden]):not([aria-label]):not([id])', e => e.length); if (noName) add('accessibility (basic)', u, `${noName} images/buttons/inputs without accessible name`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2); if (overflow) add('horizontal overflow', u, 'page is wider than the viewport');
    if (axeSrc) { await page.evaluate(axeSrc); const r = await page.evaluate(async () => (await axe.run()).violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length }))); rec.axe = r; for (const v of r) if (['serious', 'critical'].includes(v.impact)) add('axe ' + v.impact, u, `${v.id} x${v.n}`); }
    const btns = await page.$$('button:visible, [role=button]:visible, input[type=submit]:visible'); rec.buttons = btns.length; let clicked = 0;
    for (let i = 0; i < Math.min(btns.length, 40); i++) {
      const b = (await page.$$('button:visible, [role=button]:visible, input[type=submit]:visible'))[i]; if (!b) continue;
      const label = ((await b.innerText().catch(() => '')) || (await b.getAttribute('aria-label')) || (await b.getAttribute('value')) || '').trim().slice(0, 40);
      if (!allowD && DESTRUCTIVE.test(label)) { rec.skipped = (rec.skipped || []).concat(label); continue; }
      if (await b.isDisabled().catch(() => false)) continue;
      const before = await page.evaluate(() => document.body.innerHTML.length + '|' + location.href); let reqs = 0; const cnt = () => reqs++; page.on('request', cnt);
      await b.click({ timeout: 3000, trial: false }).catch(e => add('click failed', u, `"${label}" ${e.message.split('\n')[0]}`)); await page.waitForTimeout(400); page.off('request', cnt); clicked++;
      const after = await page.evaluate(() => document.body.innerHTML.length + '|' + location.href);
      if (before === after && reqs === 0) add('dead button?', u, `"${label}" produced no DOM change, navigation or request (verify manually: may be intentional)`);
      if (page.url() !== u) { await page.goto(u, { waitUntil: 'networkidle' }).catch(() => {}); }
    }
    rec.clicked = clicked;
    await page.screenshot({ path: path.join(out, 'p' + pages.length + '.png') });
  } catch (e) { add('page failed to load', u, e.message.split('\n')[0]); }
  pages.push(rec); await page.close();
}
await browser.close();
const result = { url, when: new Date().toISOString(), pages, issues };
fs.writeFileSync(path.join(out, 'sweep.json'), JSON.stringify(result, null, 1));
console.log(`# Browser sweep of ${url}\npages visited: ${pages.length}, buttons clicked: ${pages.reduce((s, p) => s + (p.clicked || 0), 0)}, issues: ${issues.length}`);
for (const p of pages) console.log(`  ${p.url}  status ${p.status} load ${p.loadMs}ms lcp ${p.perf?.lcp}ms ${p.perf?.kb}KB ${p.perf?.requests} req` + (p.skipped ? `  skipped destructive: ${p.skipped.join(', ')}` : ''));
const g = {}; for (const i of issues) (g[i.type] ||= []).push(i); for (const [t, l] of Object.entries(g)) { console.log(`\n[${t}] ${l.length}`); for (const i of l.slice(0, 6)) console.log(`   ${i.where}  ${i.detail}`); }
if (opt('--save')) { fs.writeFileSync(opt('--save'), JSON.stringify(pages.map(p => ({ url: p.url, loadMs: p.loadMs, ...p.perf })), null, 1)); console.log('\nbaseline saved to', opt('--save')); }
if (opt('--compare') && fs.existsSync(opt('--compare'))) {
  const base = JSON.parse(fs.readFileSync(opt('--compare'))); console.log('\n# Compared with baseline (worse by >20% and >100ms is flagged)');
  for (const p of pages) { const b = base.find(x => x.url === p.url); if (!b) continue; for (const k of ['loadMs', 'lcp']) { const now = k === 'loadMs' ? p.loadMs : p.perf?.[k]; if (now > b[k] * 1.2 && now - b[k] > 100) console.log(`   REGRESSION ${p.url} ${k}: ${b[k]} -> ${now}`); } const nk = p.perf?.kb; if (nk > b.kb * 1.2 && nk - b.kb > 50) console.log(`   REGRESSION ${p.url} transfer: ${b.kb}KB -> ${nk}KB`); }
}
process.exit(issues.some(i => !/dead button/.test(i.type)) ? 1 : 0);
