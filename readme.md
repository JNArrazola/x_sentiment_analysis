# X Sentiment Analysis

Este es un proyecto escolar desarrollado en **JavaScript** y **Python** que se centra en analizar opiniones en redes sociales, tomando como fuente principal tweets extraídos de Nitter (una alternativa ligera a Twitter).

## 📌 Descripción

**X Sentiment Analysis** tiene como objetivo recopilar tweets relacionados con un término de búsqueda específico, analizar el sentimiento que expresan y presentar los resultados de forma visual y amigable. La aplicación se divide en dos grandes bloques:

1. **Extracción de tweets**  
   Se utiliza un script en **JavaScript** (con Puppeteer) para navegar por Nitter, simular la interacción del usuario (scroll y clics en el botón "más tweets") y recopilar una cantidad considerable de tweets. Estos se guardan en un archivo JSON (`tweets.json`).

2. **Análisis de sentimientos**  
   Con **Python** se carga el archivo de tweets y se utiliza **VADER** (de la librería NLTK) para analizar cada tweet. VADER asigna un score compuesto que permite clasificar cada tweet en:
   - ✅ **Positivo** (score > 0.05)
   - ⚪ **Neutral** (score entre -0.05 y 0.05)
   - ❌ **Negativo** (score < -0.05)

   Finalmente, se muestra una interfaz gráfica desarrollada con **PyQt5** y **matplotlib**, que presenta:
   - 📊 Un **gráfico de barras** con la distribución de sentimientos.
   - 📑 Tres **secciones de texto** donde se listan todos los tweets por categoría (positivos, neutrales y negativos), resaltando su score con colores.

---

## 🔄 Flujo de la Aplicación

### **1️⃣ Extracción de Tweets (JavaScript)**

- Se define un **término de búsqueda** (ejemplo: `"Fortnite"`) mediante una variable.
- El script **navega a la URL de búsqueda** en Nitter, espera a que se cargue el contenido y simula scroll para activar la carga dinámica.
- Se realizan múltiples clics en el botón `"más tweets"` para acumular nuevos tweets.
- Los tweets recopilados **se guardan en un archivo** `tweets.json`.

### **2️⃣ Análisis de Sentimientos (Python)**

- Se carga el archivo `tweets.json`.
- Cada tweet **se analiza con [VADER](https://github.com/cjhutto/vaderSentiment/blob/master/README.rst)**, generando un **score compuesto** que lo clasifica en positivo, neutral o negativo.
- Se cuentan y ordenan los tweets por categoría.
- Se muestra una **interfaz gráfica interactiva** que incluye:
  - Un **gráfico de barras** con la distribución de sentimientos.
  - Tres **paneles de texto** donde se muestran todos los tweets, con su score resaltado en colores.

---
## 🧠 Modelo y Técnicas Utilizadas

✅ **Scraping de Tweets:** Se usa **Puppeteer** para navegar en Nitter y extraer los tweets sin necesidad de la API oficial de Twitter.  
✅ **Análisis de Sentimientos:** Se emplea **VADER** de NLTK, un modelo especializado en textos cortos y redes sociales.  
✅ **Interfaz Gráfica:** Se usa **PyQt5** para crear una UI interactiva y **matplotlib** para visualizar los resultados en gráficos.

---

## ⚙️ Cómo Ejecutar el Proyecto

### **📌 Requisitos**

- **Node.js** (para ejecutar el script de scraping)
- **Python 3.11+** (se recomienda esta versión para evitar incompatibilidades)
- **Librerías de Node.js:**
  ```bash
    npm install puppeteer
    ```
- **Librerías de Python:**
    ```bash
    pip install nltk matplotlib PyQt5
    ```

### Paso 1: Extracción de Tweets
1. **Editar** el archivo `src/scraper.js` y cambiar la variable `searchTerm` con el término que se desea buscar, así como también la variable `maxClicks` para definir la '*profundidad*' de la búsqueda.
2. **Ejecutar** el archivo `src/scraper.js`:
    ```bash
    node src/scraper.js
    ```

### Paso 2: Análisis de sentimientos
1. **(Opcional)** Crear un entorno virtual: 
    ```bash
    python -m venv env
    source env/bin/activate  # En Windows: `env\Scripts\activate`, en Linux: `source env/bin/activate`
    ```
2. **Instalar** las dependencias necesarias: 
    ```bash
    pip install -r doc/requirements.txt
    ```
3. **Ejecutar** el analizador de sentimientos `src/analyzer.py`:
    ```bash
    python3 src/analyzer.py
    ```