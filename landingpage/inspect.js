import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('http://localhost:5173');
  
  // Wait for React to render
  await page.waitForSelector('footer#cta');
  
  const metrics = await page.evaluate(() => {
    const footer = document.querySelector('footer#cta');
    const section = footer.querySelector('section');
    const canvasDiv = section.querySelector('div.absolute');
    const containerDiv = section.querySelector('div.container');
    const canvas = section.querySelector('canvas');
    
    return {
      footerWidth: footer.clientWidth,
      sectionWidth: section.clientWidth,
      canvasDivWidth: canvasDiv.clientWidth,
      containerDivWidth: containerDiv.clientWidth,
      canvasWidth: canvas ? canvas.clientWidth : null,
      canvasDivClasses: canvasDiv.className
    };
  });
  
  console.log(JSON.stringify(metrics, null, 2));
  await browser.close();
})();
