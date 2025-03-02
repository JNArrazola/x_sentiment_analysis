"""  
Archivo principal de la aplicación de análisis de sentimiento de tweets.

Hace uso de la librería NLTK para realizar el análisis de sentimiento de los tweets
y de la librería PyQt5 para la interfaz gráfica.

El archivo tweets.json contiene una lista de tweets en formato JSON extraídos de Nitter (https://nitter.net/)
por el script "script.js".

Para ejecutar la aplicación, simplemente correr el script con Python 3:
    python main.py

El sia.polarity_scores(tweet) devuelve un diccionario con las siguientes llaves:
    - 'neg': puntaje de negatividad
    - 'neu': puntaje de neutralidad
    - 'pos': puntaje de positividad
    - 'compound': puntaje compuesto

El puntaje compuesto es un valor entre -1 y 1 que representa la polaridad del texto.
Un valor mayor a 0.05 es considerado positivo, menor a -0.05 es negativo y entre -0.05 y 0.05 es neutral.

El modelo de análisis de sentimiento VADER (Valence Aware Dictionary and sEntiment Reasoner) es un modelo
de análisis de sentimiento basado en reglas y léxico que está específicamente diseñado para analizar
sentimientos en redes sociales.

@author: Joshua Nathaniel Arrazola Elizondo
@date: 02/03/2025
"""


import sys
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QTextEdit
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Descargar el lexicón de VADER
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Cargar los tweets desde el archivo JSON
with open('tweets.json', 'r', encoding='utf-8') as f:
    tweets = json.load(f)

# Procesar tweets: aplicar análisis de sentimiento
tweet_sentiments = []
sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

for tweet in tweets:
    scores = sia.polarity_scores(tweet)
    compound = scores['compound']
    if compound > 0.05:
        sentiment = 'positive'
    elif compound < -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    sentiment_counts[sentiment] += 1
    tweet_sentiments.append((tweet, sentiment, compound))

# Filtrar y ordenar los tweets por categoría
all_positive = sorted([ts for ts in tweet_sentiments if ts[1]=='positive'], key=lambda x: x[2], reverse=True)
all_negative = sorted([ts for ts in tweet_sentiments if ts[1]=='negative'], key=lambda x: x[2])
all_neutral  = sorted([ts for ts in tweet_sentiments if ts[1]=='neutral'],  key=lambda x: abs(x[2]))

# Clase para embeber el gráfico de matplotlib en PyQt
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

# Clase principal de la interfaz
class SentimentAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análisis de Sentimiento de Tweets")
        self.setGeometry(100, 100, 1200, 700)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Crear el canvas de matplotlib y graficar la distribución de sentimientos
        self.canvas = MplCanvas(self, width=5, height=3, dpi=100)
        self.plot_bar_chart()
        main_layout.addWidget(self.canvas)
        
        # Usar un QSplitter para dividir en tres secciones: positivos, neutrales y negativos
        splitter = QSplitter(Qt.Horizontal)
        
        # Área de texto para los tweets positivos
        self.positive_text = QTextEdit()
        self.positive_text.setReadOnly(True)
        pos_text = "<h2>Tweets Positivos</h2>"
        for tweet, sentiment, compound in all_positive:
            pos_text += f"<p><b><font color='green'>Score: {compound:.2f}</font></b><br>{tweet}</p>"
        self.positive_text.setHtml(pos_text)
        
        # Área de texto para los tweets neutrales
        self.neutral_text = QTextEdit()
        self.neutral_text.setReadOnly(True)
        neu_text = "<h2>Tweets Neutrales</h2>"
        if all_neutral:
            for tweet, sentiment, compound in all_neutral:
                neu_text += f"<p><b><font color='gray'>Score: {compound:.2f}</font></b><br>{tweet}</p>"
        else:
            neu_text += "<p>No se encontraron tweets neutrales.</p>"
        self.neutral_text.setHtml(neu_text)
        
        # Área de texto para los tweets negativos
        self.negative_text = QTextEdit()
        self.negative_text.setReadOnly(True)
        neg_text = "<h2>Tweets Negativos</h2>"
        for tweet, sentiment, compound in all_negative:
            neg_text += f"<p><b><font color='red'>Score: {compound:.2f}</font></b><br>{tweet}</p>"
        self.negative_text.setHtml(neg_text)
        
        splitter.addWidget(self.positive_text)
        splitter.addWidget(self.neutral_text)
        splitter.addWidget(self.negative_text)
        splitter.setSizes([400, 400, 400])
        main_layout.addWidget(splitter)
    
    def plot_bar_chart(self):
        # Graficar la distribución de sentimientos
        categories = list(sentiment_counts.keys())
        counts = [sentiment_counts[cat] for cat in categories]
        self.canvas.axes.clear()
        self.canvas.axes.bar(categories, counts, color=['green', 'gray', 'red'])
        self.canvas.axes.set_title("Distribución de Sentimientos")
        self.canvas.axes.set_xlabel("Sentimiento")
        self.canvas.axes.set_ylabel("Cantidad de Tweets")
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SentimentAnalysisApp()
    window.show()
    sys.exit(app.exec_())
