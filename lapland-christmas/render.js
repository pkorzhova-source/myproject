// Renders scene.html frame by frame and pipes frames into ffmpeg.
// Usage: node render.js            -> full video (frames.mp4)
//        node render.js preview 3 9 15 19.5  -> PNG stills at given seconds
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 20;
const mime = { '.html': 'text/html', '.js': 'text/javascript' };

(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => { console.log('[err]', e.message); process.exit(1); });
  await page.route('http://scene.local/**', r => {
    const f = path.join(__dirname, new URL(r.request().url()).pathname);
    r.fulfill({ body: fs.readFileSync(f), contentType: mime[path.extname(f)] || 'application/octet-stream' });
  });
  await page.goto('http://scene.local/scene.html');
  await page.waitForFunction(() => window.ready === true, null, { timeout: 300000 });
  const shot = async t => { await page.evaluate(t => window.render(t), t); return page.screenshot({ type: 'png' }); };

  if (process.argv[2] === 'preview') {
    for (const s of process.argv.slice(3)) {
      const t0 = Date.now(); const buf = await shot(+s);
      fs.writeFileSync(path.join(__dirname, `preview_${s}.png`), buf); console.log('t', s, Date.now() - t0, 'ms');
    }
  } else {
    const out = path.join(__dirname, 'frames.mp4');
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow', out], { stdio: ['pipe', 'ignore', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < FPS * DUR; i++) {
      const buf = await shot(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 30 === 0) console.log('frame', i, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log('done', out);
  }
  await browser.close();
})();
