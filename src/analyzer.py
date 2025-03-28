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
import subprocess
from nltk.sentiment import SentimentIntensityAnalyzer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class SentimentAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análisis de Sentimiento de Tweets (Nitter + VADER)")
        self.setGeometry(100, 100, 1200, 700)

        self.tweet_sentiments = []
        self.sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.main_layout.addWidget(QLabel("<h2>Análisis de sentimiento en tweets de Nitter</h2>"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Término de búsqueda (ej. trump)")
        self.main_layout.addWidget(self.search_input)

        self.depth_input = QLineEdit()
        self.depth_input.setPlaceholderText("Profundidad de búsqueda (ej. 1 a 5)")
        self.main_layout.addWidget(self.depth_input)

        self.search_button = QPushButton("Buscar y Analizar")
        self.search_button.clicked.connect(self.run_scraper_and_analyze)
        self.main_layout.addWidget(self.search_button)

        self.canvas = MplCanvas(self, width=5, height=3, dpi=100)
        self.main_layout.addWidget(self.canvas)

        self.splitter = QSplitter(Qt.Horizontal)
        self.positive_text = QTextEdit()
        self.neutral_text = QTextEdit()
        self.negative_text = QTextEdit()
        for widget in [self.positive_text, self.neutral_text, self.negative_text]:
            widget.setReadOnly(True)

        self.splitter.addWidget(self.positive_text)
        self.splitter.addWidget(self.neutral_text)
        self.splitter.addWidget(self.negative_text)
        self.splitter.setSizes([400, 400, 400])
        self.main_layout.addWidget(self.splitter)

    def run_scraper_and_analyze(self):
        term = self.search_input.text().strip()
        depth_str = self.depth_input.text().strip()

        if not term:
            QMessageBox.warning(self, "Error", "Por favor ingresa un término de búsqueda.")
            return

        try:
            depth = int(depth_str)
            if depth <= 0:
                raise ValueError
        except:
            depth = 1  # Valor por defecto seguro

        self.search_button.setEnabled(False)
        self.search_button.setText("Buscando tweets...")

        try:
            subprocess.run(["node", "scraper.js", term, str(depth)], check=True)

            with open('tweets.json', 'r', encoding='utf-8') as f:
                tweets = json.load(f)

            self.tweet_sentiments = []
            self.sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

            for tweet in tweets:
                scores = sia.polarity_scores(tweet)
                compound = scores['compound']
                if compound > 0.05:
                    sentiment = 'positive'
                elif compound < -0.05:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                self.sentiment_counts[sentiment] += 1
                self.tweet_sentiments.append((tweet, sentiment, compound))

            self.display_results()

        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", "Error al ejecutar el scraper de Nitter.")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "No se encontró el archivo tweets.json.")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))
        finally:
            self.search_button.setEnabled(True)
            self.search_button.setText("Buscar y Analizar")

    def display_results(self):
        all_positive = sorted([ts for ts in self.tweet_sentiments if ts[1] == 'positive'], key=lambda x: x[2], reverse=True)
        all_negative = sorted([ts for ts in self.tweet_sentiments if ts[1] == 'negative'], key=lambda x: x[2])
        all_neutral  = sorted([ts for ts in self.tweet_sentiments if ts[1] == 'neutral'],  key=lambda x: abs(x[2]))

        self.canvas.axes.clear()
        self.canvas.axes.bar(
            ['Positivos', 'Neutrales', 'Negativos'],
            [self.sentiment_counts['positive'], self.sentiment_counts['neutral'], self.sentiment_counts['negative']],
            color=['green', 'gray', 'red']
        )
        self.canvas.axes.set_title("Distribución de Sentimientos")
        self.canvas.draw()

        self.positive_text.setHtml("<h3 style='color:green'>Tweets Positivos</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_positive
        ))
        self.neutral_text.setHtml("<h3 style='color:gray'>Tweets Neutrales</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_neutral
        ) or "<p>No se encontraron tweets neutrales.</p>")
        self.negative_text.setHtml("<h3 style='color:red'>Tweets Negativos</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_negative
        ))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SentimentAnalysisApp()
    window.show()
    sys.exit(app.exec_())
