/*  
Script que extrae tweets de Nitter (una alternativa a Twitter)
para un término de búsqueda dado. El script simula un scroll
para activar el lazy-loading de tweets y hace clic en el botón
"más tweets" para cargar más tweets. Los tweets extraídos se
almacenan en un archivo JSON.

Para ejecutar el script, instala las dependencias en el archivo doc/commands.txt

Posteriormente, los tweets se analizan en el archivo main.py.

Autor: Joshua Nathaniel Arrazola Elizondo
Fecha: 02/03/2025
*/

const puppeteer = require('puppeteer');
const fs = require('fs');

const searchTerm = process.argv[2] || 'trump';
const maxClicks = parseInt(process.argv[3]) || 1;

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
      "AppleWebKit/537.36 (KHTML, like Gecko) " +
      "Chrome/119.0.0.0 Safari/537.36"
    );

    const url = `https://nitter.net/search?f=tweets&q=${encodeURIComponent(searchTerm)}`;
    console.log(`Accediendo a: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    await new Promise(resolve => setTimeout(resolve, 10000));
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await new Promise(resolve => setTimeout(resolve, 5000));

    const accumulatedTweets = new Set();

    for (let i = 0; i < maxClicks; i++) {
      const newTweets = await page.evaluate(() => {
        const nodes = document.querySelectorAll('div.tweet-content.media-body');
        return Array.from(nodes).map(node => node.innerText.trim());
      });

      newTweets.forEach(tweet => accumulatedTweets.add(tweet));
      console.log(`Tweets acumulados tras iteración ${i + 1}: ${accumulatedTweets.size}`);

      const nextButton = await page.$('a[href*="cursor="]');
      if (!nextButton) {
        console.log("No se encontró el botón para cargar más tweets.");
        break;
      }

      await nextButton.click();
      console.log(`Clic número ${i + 1} realizado.`);

      let tweetCountBefore = newTweets.length;
      let tweetCountAfter = tweetCountBefore;
      let retries = 0;
      while (tweetCountAfter <= tweetCountBefore && retries < 10) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        tweetCountAfter = await page.evaluate(() => {
          return document.querySelectorAll('div.tweet-content.media-body').length;
        });
        retries++;
      }
    }

    const tweetsArray = Array.from(accumulatedTweets);
    fs.writeFileSync('tweets.json', JSON.stringify(tweetsArray, null, 2), 'utf-8');
    console.log(`Se extrajeron un total de ${tweetsArray.length} tweets.`);

    await new Promise(resolve => setTimeout(resolve, 3000));
    await browser.close();

  } catch (error) {
    console.error('Error:', error);
  }
})();