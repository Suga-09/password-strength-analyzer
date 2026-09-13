"""
Generate all report charts from the trained ML model.
Run: python generate_chart.py
"""
import os
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay,
                             precision_recall_fscore_support)

# Import your trainer
from models.ml_trainer import MLTrainer


def ensure_output_folder():
    os.makedirs('report_charts', exist_ok=True)


# ---------- Chart 1: Feature Importance ----------
def chart_feature_importance(model):
    features = ['length', 'lowercase_count', 'uppercase_count',
                'digit_count', 'special_count', 'entropy']
    importances = model.feature_importances_
    indices = np.argsort(importances)

    plt.figure(figsize=(10, 6))
    bars = plt.barh(
        [features[i] for i in indices],
        [importances[i] for i in indices],
        color='#667eea', edgecolor='#4c51bf'
    )
    for bar, v in zip(bars, [importances[i] for i in indices]):
        plt.text(v + 0.005, bar.get_y() + bar.get_height() / 2,
                 f'{v:.4f}', va='center')
    plt.xlabel('Importance Score')
    plt.title('Feature Importance for Password Strength Classification',
              fontweight='bold')
    plt.tight_layout()
    plt.savefig('report_charts/feature_importance.png', dpi=150)
    plt.close()
    print("💾 Saved: report_charts/feature_importance.png")


# ---------- Chart 2: Confusion Matrix ----------
def chart_confusion_matrix(model):
    trainer = MLTrainer()
    df = trainer.build_dataset(1000)
    features = trainer.feature_names
    X = df[features]
    y = df['label']
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(
        cm, display_labels=['Weak', 'Medium', 'Strong'])
    disp.plot(cmap='Blues', ax=plt.gca())
    plt.title('Confusion Matrix — RandomForest Classifier', fontweight='bold')
    plt.tight_layout()
    plt.savefig('report_charts/confusion_matrix.png', dpi=150)
    plt.close()
    print("💾 Saved: report_charts/confusion_matrix.png")


# ---------- Chart 3: Class Distribution ----------
def chart_class_distribution():
    trainer = MLTrainer()
    df = trainer.build_dataset(1000)
    counts = df['label'].value_counts().sort_index()

    plt.figure(figsize=(8, 5))
    bars = plt.bar(['Weak', 'Medium', 'Strong'], counts.values,
                   color=['#fc8181', '#f6ad55', '#68d391'])
    for bar, v in zip(bars, counts.values):
        plt.text(bar.get_x() + bar.get_width() / 2, v + 10,
                 str(v), ha='center', fontweight='bold')
    plt.ylabel('Count')
    plt.title('Synthetic Dataset Class Distribution', fontweight='bold')
    plt.tight_layout()
    plt.savefig('report_charts/class_distribution.png', dpi=150)
    plt.close()
    print("💾 Saved: report_charts/class_distribution.png")


# ---------- Chart 4: Precision / Recall / F1 ----------
def chart_precision_recall(model):
    trainer = MLTrainer()
    df = trainer.build_dataset(1000)
    X = df[trainer.feature_names]
    y = df['label']
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    y_pred = model.predict(X_test)
    p, r, f, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1, 2])

    classes = ['Weak', 'Medium', 'Strong']
    x = np.arange(len(classes))
    width = 0.25

    plt.figure(figsize=(9, 5))
    plt.bar(x - width, p, width, label='Precision', color='#667eea')
    plt.bar(x, r, width, label='Recall', color='#f6ad55')
    plt.bar(x + width, f, width, label='F1-Score', color='#68d391')
    plt.xticks(x, classes)
    plt.ylim(0, 1.1)
    plt.ylabel('Score')
    plt.title('Precision, Recall, and F1-Score by Class', fontweight='bold')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('report_charts/metrics_by_class.png', dpi=150)
    plt.close()
    print("💾 Saved: report_charts/metrics_by_class.png")


# ---------- Main ----------
if __name__ == '__main__':
    ensure_output_folder()

    model_path = 'models/password_model.pkl'
    if not os.path.exists(model_path):
        print("❌ Model not found. Run 'python models/ml_trainer.py' first.")
        exit(1)

    print("📊 Generating report charts...\n")
    model = joblib.load(model_path)

    chart_feature_importance(model)
    chart_confusion_matrix(model)
    chart_class_distribution()
    chart_precision_recall(model)

    print("\n✅ All charts saved in report_charts/")
