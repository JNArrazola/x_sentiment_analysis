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

const searchTerm = 'planets';  // Terminom a buscar
const maxClicks = 5; // Profundidad de la búsqueda

(async () => {
  try {
    // Inicia el navegador (modo no headless para evitar detección)
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Configurar un User-Agent realista
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
      "AppleWebKit/537.36 (KHTML, like Gecko) " +
      "Chrome/119.0.0.0 Safari/537.36"
    );

    // Construir la URL usando el término de búsqueda
    const url = `https://nitter.net/search?f=tweets&q=${encodeURIComponent(searchTerm)}`;
    console.log(`Accediendo a: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

    // Espera inicial para que se cargue el contenido
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Simular un scroll para activar lazy-loading
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Objeto Set para acumular tweets sin duplicados
    const accumulatedTweets = new Set();

    for (let i = 0; i < maxClicks; i++) {
      // Extraer los tweets actuales de la página
      const newTweets = await page.evaluate(() => {
        const nodes = document.querySelectorAll('div.tweet-content.media-body');
        return Array.from(nodes).map(node => node.innerText.trim());
      });
      
      // Agregar cada tweet al conjunto acumulado
      newTweets.forEach(tweet => accumulatedTweets.add(tweet));
      console.log(`Tweets acumulados tras iteración ${i + 1}: ${accumulatedTweets.size}`);

      // Buscar el botón "más tweets" (que contiene "cursor=" en su href)
      const nextButton = await page.$('a[href*="cursor="]');
      if (!nextButton) {
        console.log("No se encontró el botón de cargar más tweets.");
        break;
      }

      // Hacer clic en el botón
      await nextButton.click();
      console.log(`Clic número ${i + 1} realizado.`);

      // Esperar a que se carguen nuevos tweets: 
      // Se espera hasta que el número de tweets en el DOM aumente
      let tweetCountBefore = newTweets.length;
      let tweetCountAfter = tweetCountBefore;
      let retries = 0;
      const maxRetries = 10;
      while (tweetCountAfter <= tweetCountBefore && retries < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        tweetCountAfter = await page.evaluate(() => {
          return document.querySelectorAll('div.tweet-content.media-body').length;
        });
        retries++;
      }
    }

    // Convertir el conjunto a un array y guardar en un archivo JSON
    const tweetsArray = Array.from(accumulatedTweets);
    fs.writeFileSync('tweets.json', JSON.stringify(tweetsArray, null, 2), 'utf-8');
    console.log(`Se extrajeron un total de ${tweetsArray.length} tweets.`);

    // await browser.close();
  } catch (error) {
    console.error('Error:', error);
  }
})();
