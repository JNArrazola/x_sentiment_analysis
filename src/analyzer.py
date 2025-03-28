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
    QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout
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
        self.setWindowTitle("📊 Análisis de Sentimiento de Tweets (Nitter + VADER)")
        self.setGeometry(100, 100, 1200, 700)

        self.light_theme = """
            QWidget { background-color: #f5f7fa; color: #1c1c1c; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel { font-size: 18px; font-weight: bold; color: #222; padding: 6px 0; }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1c1c1c;
                font-family: 'Consolas';
            }
            QPushButton {
                padding: 10px 15px;
                background-color: #0078d4;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005ea2; }
            QSplitter::handle { background-color: #d0d0d0; }
        """

        self.dark_theme = """
            QWidget { background-color: #1e1e1e; color: #eeeeee; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel { font-size: 18px; font-weight: bold; color: #ffffff; padding: 6px 0; }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #444;
                border-radius: 6px;
                background-color: #2c2c2c;
                color: #ffffff;
                font-family: 'Consolas';
            }
            QPushButton {
                padding: 10px 15px;
                background-color: #3a85ff;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1c6fd6; }
            QSplitter::handle { background-color: #444; }
        """

        self.setStyleSheet(self.dark_theme)
        self.dark_mode_enabled = True

        self.tweet_sentiments = []
        self.sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.main_layout.addWidget(QLabel("📈 <b>Análisis de Sentimiento en Tweets</b>"))

        input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Término de búsqueda")
        input_layout.addWidget(self.search_input)

        self.depth_input = QLineEdit()
        self.depth_input.setPlaceholderText("📄 Profundidad")
        input_layout.addWidget(self.depth_input)

        self.search_button = QPushButton("🔎 Buscar y Analizar")
        self.search_button.clicked.connect(self.run_scraper_and_analyze)
        input_layout.addWidget(self.search_button)

        self.toggle_theme_button = QPushButton("🌓 Cambiar Tema")
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        input_layout.addWidget(self.toggle_theme_button)

        self.main_layout.addLayout(input_layout)
        self.main_layout.addWidget(QLabel("<hr>"))

        self.canvas = MplCanvas(self, width=5, height=3, dpi=100)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addWidget(QLabel("<hr>"))

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
            depth = 1

        self.search_button.setEnabled(False)
        self.search_button.setText("Buscando...")

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
            self.search_button.setText("🔎 Buscar y Analizar")

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

        self.positive_text.setHtml("<h3 style='color:lime'>Tweets Positivos</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_positive
        ))
        self.neutral_text.setHtml("<h3 style='color:lightgray'>Tweets Neutrales</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_neutral
        ) or "<p>No se encontraron tweets neutrales.</p>")
        self.negative_text.setHtml("<h3 style='color:salmon'>Tweets Negativos</h3>" + "".join(
            f"<p><b>Score: {c:.2f}</b><br>{t}</p>" for t, s, c in all_negative
        ))

    def toggle_theme(self):
        if self.dark_mode_enabled:
            self.setStyleSheet(self.light_theme)
            self.dark_mode_enabled = False
        else:
            self.setStyleSheet(self.dark_theme)
            self.dark_mode_enabled = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SentimentAnalysisApp()
    window.show()
    sys.exit(app.exec_())
