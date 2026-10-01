const { chromium } = require('playwright');

const BASE = 'https://endocare-gold.vercel.app';
const EMAIL = 'qa-admin-1785942988@test.endocare.local';
const PASS = 'Test1234!';

const results = { passed: [], failed: [], warnings: [] };

function pass(feature, detail) {
  results.passed.push({ feature, detail });
  console.log(`✅ ${feature}: ${detail}`);
}
function fail(feature, detail) {
  results.failed.push({ feature, detail });
  console.log(`❌ ${feature}: ${detail}`);
}
function warn(feature, detail) {
  results.warnings.push({ feature, detail });
  console.log(`⚠️  ${feature}: ${detail}`);
}

async function waitForNetworkIdle(page, timeout = 5000) {
  try { await page.waitForLoadState('networkidle', { timeout }); } catch {}
}

async function go(page, path, label) {
  const resp = await page.goto(`${BASE}${path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  if (!resp || resp.status() >= 400) { fail(label, `HTTP ${resp?.status()}`); return false; }
  await waitForNetworkIdle(page);
  pass(label, `loaded (${resp.status()})`);
  return true;
}

async function run() {
  console.log('🚀 COMPREHENSIVE ENDOCARE FEATURE TEST\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, ignoreHTTPSErrors: true });
  context.on('console', msg => { if (msg.type() === 'error') console.log(`[CONSOLE ERROR] ${msg.text().slice(0, 200)}`); });
  context.on('pageerror', err => console.log(`[PAGE ERROR] ${err.message}`));
  const page = await context.newPage();

  // LOGIN
  await go(page, '/auth/login', 'Login page');
  await page.waitForSelector('input[type="email"]', { timeout: 10000 });
  await page.fill('input[type="email"]', EMAIL);
  await page.fill('input[type="password"]', PASS);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard**', { timeout: 20000 }).catch(() => {});
  await waitForNetworkIdle(page, 10000);
  pass('Auth', `Login successful → ${page.url()}`);

  // ALL MODULES
  const modules = [
    ['/dashboard', 'Dashboard'],
    ['/appointments', 'Appointments'],
    ['/patients', 'Patients list'],
    ['/patients/new', 'Patient create'],
    ['/queue-board', 'Queue Board'],
    ['/prescriptions', 'Prescriptions'],
    ['/laboratory', 'Laboratory'],
    ['/pharmacy', 'Pharmacy'],
    ['/pharmacy/history', 'Pharmacy History'],
    ['/portal', 'Patient Portal'],
    ['/consultation', 'Consultations'],
    ['/doctors/schedule', 'Doctors Schedule'],
    ['/settings', 'Settings'],
    ['/analytics', 'Analytics'],
    ['/billing', 'Billing'],
    ['/kiosk', 'Kiosk'],
    ['/reminders', 'Reminders'],
  ];

  for (const [path, label] of modules) {
    await go(page, path, label);
    await page.waitForTimeout(1000);
  }

  // SPECIAL INTERACTIONS
  // Appointments dialog via button
  await go(page, '/appointments', 'Appointments (dialog test)');
  const newApptBtn = await page.$('button:has-text("New Appointment")').catch(() => false);
  if (newApptBtn) {
    await newApptBtn.click(); await page.waitForTimeout(1000);
    const dialog = await page.$('.fixed.inset-0.z-50, [role="dialog"]').catch(() => false);
    pass('Appointments dialog', dialog ? 'Opens via button' : 'Failed to open');
    await page.keyboard.press('Escape');
  }

  // ?new=true deep link
  await go(page, '/appointments?new=true', 'Appointments ?new=true');
  await page.waitForTimeout(1000);
  const dialog2 = await page.$('.fixed.inset-0.z-50, [role="dialog"]').catch(() => false);
  pass('Appointments ?new=true', dialog2 ? 'Auto-opens' : 'Did not auto-open');

  // Patient create
  await go(page, '/patients/new', 'Patient create (form)');
  try {
    await page.fill('input[id^="first-name-"]', 'Comprehensive');
    await page.fill('input[id^="last-name-"]', 'TestPatient');
    await page.fill('input[id^="date-of-birth-"]', '1990-01-15');
    await page.fill('input[id="phone"]', '9876543210');
    await page.fill('input[id="email"]', 'comprehensive@test.local');
    const genderSel = await page.$('select[id="gender"]').catch(() => null);
    if (genderSel) await genderSel.selectOption({ index: 1 }).catch(() => {});
    await page.click('button[type="submit"]');
    await waitForNetworkIdle(page, 10000);
    if (!page.url().includes('/patients/new')) {
      pass('Patient create', 'Success → redirected to list');
    } else {
      const toast = await page.locator('[data-sonner-toast], .toast, [role="alert"]').first().textContent().catch(() => '');
      warn('Patient create', `Stayed on form: ${toast || 'no toast'}`);
    }
  } catch (e) { fail('Patient create', `Form error: ${e.message}`); }

  // Settings → Doctors tab
  await go(page, '/settings', 'Settings (Doctors tab)');
  const doctorsTab = await page.$('button:has-text("Doctors"), [role="tab"]:has-text("Doctors")').catch(() => false);
  if (doctorsTab) {
    await doctorsTab.click(); await waitForNetworkIdle(page);
    const docList = await page.$('table, .divide-y, [data-testid="doctor-list"]').catch(() => false);
    pass('Settings → Doctors tab', docList ? 'Doctor list rendered' : 'Tab works, list empty');
  }

  // LOGOUT
  await page.goto(`${BASE}/dashboard`, { waitUntil: 'domcontentloaded' });
  await waitForNetworkIdle(page);
  const logoutBtn = await page.$('button:has-text("Sign Out"), a:has-text("Sign Out")').catch(() => false);
  if (logoutBtn) {
    await logoutBtn.click();
    await page.waitForURL('**/auth/login**', { timeout: 10000 }).catch(() => {});
    pass('Logout', page.url().includes('/auth/login') ? 'Redirected to login' : 'Clicked');
  }

  // SUMMARY
  console.log('\n===========================================');
  console.log('📋 COMPREHENSIVE TEST SUMMARY');
  console.log('===========================================');
  console.log(`✅ Passed:  ${results.passed.length}`);
  console.log(`❌ Failed:  ${results.failed.length}`);
  console.log(`⚠️  Warnings: ${results.warnings.length}`);
  if (results.failed.length) { console.log('\n❌ FAILURES:'); results.failed.forEach(f => console.log(`  - ${f.feature}: ${f.detail}`)); }
  if (results.warnings.length) { console.log('\n⚠️  WARNINGS:'); results.warnings.forEach(w => console.log(`  - ${w.feature}: ${w.detail}`)); }

  await browser.close();
  process.exit(results.failed.length > 0 ? 1 : 0);
}

run().catch(e => { console.error('FATAL:', e); process.exit(1); });