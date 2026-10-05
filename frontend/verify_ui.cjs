const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  const consoleLogs = [];
  page.on('console', msg => consoleLogs.push(msg.text()));
  page.on('pageerror', err => consoleLogs.push('PAGE ERROR: ' + err.message));
  
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);
  
  // Submit query
  await page.click('text=Safe route Bharati');
  console.log('Query submitted, waiting for response...');
  
  // Wait for response (max 60s)
  await page.waitForTimeout(45000);
  
  // Capture browser console output
  console.log('\n=== BROWSER CONSOLE ===');
  consoleLogs.forEach(l => console.log(l));
  
  // Check route layer via page.evaluate
  const routeCheck = await page.evaluate(() => {
    const map = window.__AURORA_MAP__;
    if (!map) return { error: 'Map instance not exposed on window' };
    
    const layers = map.getStyle().layers.map(l => l.id);
    const sources = Object.keys(map.getStyle().sources);
    
    const routeLayers = layers.filter(l => l.includes('route'));
    const routeSources = sources.filter(s => s.includes('route'));
    
    let featuresOnRoute = [];
    try {
      featuresOnRoute = map.queryRenderedFeatures({ layers: routeLayers });
    } catch (e) {
      featuresOnRoute = ['ERROR: ' + e.message];
    }
    const deckgl = document.getElementById('deckgl-overlay');
    const deckglCanvas = document.querySelector('.deckgl-overlay canvas');
    
    return {
      allLayers: layers,
      allSources: sources,
      routeLayers,
      routeSources,
      renderedFeaturesCount: featuresOnRoute.length,
      mapBounds: map.getBounds().toArray(),
      mapLoaded: map.loaded(),
      hasDeckGL: !!deckglCanvas || !!document.querySelector('.deckgl-overlay') || !!document.querySelector('canvas[id^="deckgl"]'),
    };
  });
  
  console.log('\n=== MAP STATE ===');
  console.log(JSON.stringify(routeCheck, null, 2));
  
  const evidenceCheck = await page.evaluate(() => {
    const root = document.querySelector('[data-testid="evidence-panel"]');
    return {
      exists: !!root,
      textContent: root?.innerText || 'NO ROOT ELEMENT',
      innerHTML: root?.innerHTML?.slice(0, 500) || 'EMPTY',
    };
  });
  console.log('\n=== EVIDENCE PANEL ===');
  console.log(JSON.stringify(evidenceCheck, null, 2));
  
  const visualCheck = await page.evaluate(() => {
    const whySelectedItems = document.querySelectorAll('[data-testid="why-selected-item"]');
    
    return {
      whySelectedCount: whySelectedItems.length,
      whyRejectedExists: !!document.querySelector('[data-testid="why-rejected"]'),
      routeButtonCount: document.querySelectorAll('[data-testid="route-button"]').length,
    };
  });
  console.log('\n=== VISUAL CHECK ===');
  console.log(JSON.stringify(visualCheck, null, 2));

  // Take screenshot
  await page.screenshot({ path: 'verify_screenshot.png', fullPage: false });
  const finalCheck = await page.evaluate(() => {
    return {
      routeButtons: document.querySelectorAll('[data-testid="route-button"]').length,
      whySelectedItems: document.querySelectorAll('[data-testid="why-selected-item"]').length,
      whyRejectedItems: document.querySelectorAll('[data-testid="why-rejected-item"]').length,
      paretoPoints: document.querySelectorAll('[data-testid="pareto-point"]').length,
    };
  });
  
  await browser.close();

  const PASS = 
    finalCheck.routeButtons >= 3 &&
    finalCheck.whySelectedItems >= 3 &&
    finalCheck.whyRejectedItems >= 2 &&
    finalCheck.paretoPoints >= 3;

  console.log('Final check:', JSON.stringify(finalCheck, null, 2));
  console.log('\n=== VERIFICATION RESULT ===');
  if (PASS) {
    console.log('✅ PASS: All final criteria met');
    process.exit(0);
  } else {
    console.log('❌ FAIL: One or more final criteria failed.');
    process.exit(1);
  }
})();
