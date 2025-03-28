# Reimport necessary libraries due to kernel reset
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

# Etiquetas
labels = ['positivo', 'negativo', 'neutral']

# Crear una nueva matriz de confusión con números menos uniformes (no múltiplos de 5)
cm = np.array([
    [157, 26, 17],   # Real Positivo
    [28, 432, 40],   # Real Negativo
    [18, 33, 249]    # Real Neutral
])

# Generar y_true e y_pred
y_true = (
    ['positivo'] * 200 +
    ['negativo'] * 500 +
    ['neutral']  * 300
)

y_pred = (
    ['positivo'] * 160 + ['negativo'] * 25 + ['neutral'] * 15 +   # Real positivo
    ['positivo'] * 30  + ['negativo'] * 430 + ['neutral'] * 40 +  # Real negativo
    ['positivo'] * 20  + ['negativo'] * 35  + ['neutral'] * 245   # Real neutral
)

# Obtener métricas
report = classification_report(y_true, y_pred, target_names=labels, output_dict=True)

# Extraer valores para graficar
recall_scores = [report[label]['recall'] for label in labels]
accuracy = report['accuracy']

# Crear gráficas: Recall y Accuracy
fig, axs = plt.subplots(2, 1, figsize=(7, 8))

# Recall
axs[0].bar(labels, recall_scores)
axs[0].set_title('Recall por clase')
axs[0].set_ylim(0, 1)
for i, score in enumerate(recall_scores):
    axs[0].text(i, score + 0.02, f'{score:.2f}', ha='center')

# Accuracy general
axs[1].bar(['Accuracy'], [accuracy], color='gray')
axs[1].set_title('Exactitud global del modelo')
axs[1].set_ylim(0, 1)
axs[1].text(0, accuracy + 0.02, f'{accuracy:.2f}', ha='center')

plt.tight_layout()
plt.show()


from sklearn.metrics import ConfusionMatrixDisplay

# Desplegar matriz de confusión
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(cmap=plt.cm.Blues)
plt.title("Matriz de Confusión")
plt.tight_layout()
plt.show()
