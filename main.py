from sklearn import svm, datasets
from iris_classifier import IrisClassifier
import pandas as pd
import numpy as np

if __name__ == "__main__":
    iris = datasets.load_iris()

    X, y = iris.data, iris.target

    clf = svm.SVC()
    clf.fit(X, y)

    iris_classifier_service = IrisClassifier()

    iris_classifier_service.pack('model', clf)

    saved_path = iris_classifier_service.save()
    print(saved_path)
