import matplotlib.pyplot as plt
import numpy as np


def plot_tfidf(data):

    sorted_data = data["tfidf_scores"].items()
    sorted_data = sorted(sorted_data, key=lambda x: x[-1])

    x = []
    y = []

    for key, value in sorted_data:
        x.append(key)
        y.append(value)

    y_pos = np.arange(len(x))

    plt.barh(y_pos, y, align="center", alpha=0.5)
    plt.yticks(y_pos, x)
    plt.ylabel("TF-IDF Score")
    plt.title("Terms")

    plt.show()
