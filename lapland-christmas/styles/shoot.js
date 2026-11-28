const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto('file://' + path.join(__dirname, 'styles.html'));
  for (const s of process.argv.slice(2)) { await p.evaluate(s => window.draw(s), s); await p.screenshot({ path: path.join(__dirname, `style_${s}.png`) }); console.log(s); }
  await b.close();
})();
