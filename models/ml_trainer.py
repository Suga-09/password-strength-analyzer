"""
Machine Learning trainer for password strength classification.
Run this once to generate the trained model file.
"""
import random
import string
import hashlib
import math
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class MLTrainer:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'length', 'lowercase_count', 'uppercase_count',
            'digit_count', 'special_count', 'entropy'
        ]

    # ---------- FEATURE EXTRACTION ----------
    def extract_features(self, password):
        length = len(password)
        lower = sum(1 for c in password if c.islower())
        upper = sum(1 for c in password if c.isupper())
        digits = sum(1 for c in password if c.isdigit())
        special = sum(1 for c in password if c in string.punctuation)

        # Shannon entropy
        charset_size = 0
        if lower > 0:
            charset_size += 26
        if upper > 0:
            charset_size += 26
        if digits > 0:
            charset_size += 10
        if special > 0:
            charset_size += 32
        entropy = length * math.log2(charset_size) if charset_size > 0 else 0

        return [length, lower, upper, digits, special, round(entropy, 2)]

    # ---------- SYNTHETIC DATA GENERATION ----------
    def generate_weak(self, n):
        patterns = ['password', '123456', 'qwerty', 'admin', 'welcome',
                    'letmein', 'hello', 'abc123', 'iloveyou', 'monkey']
        samples = []
        for _ in range(n):
            base = random.choice(patterns)
            if random.random() < 0.5:
                base += str(random.randint(0, 99))
            samples.append(base)
        return samples

    def generate_medium(self, n):
        samples = []
        words = ['dragon', 'tiger', 'sunshine', 'master', 'summer',
                 'winter', 'purple', 'silver', 'shadow', 'phoenix']
        for _ in range(n):
            word = random.choice(words)
            word = word.capitalize() + str(random.randint(100, 9999))
            samples.append(word)
        return samples

    def generate_strong(self, n):
        samples = []
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        for _ in range(n):
            length = random.randint(14, 24)
            samples.append(''.join(random.choice(alphabet)
                           for _ in range(length)))
        return samples

    def build_dataset(self, n_per_class=1000):
        weak = self.generate_weak(n_per_class)
        medium = self.generate_medium(n_per_class)
        strong = self.generate_strong(n_per_class)

        data = []
        for pwd in weak:
            data.append(self.extract_features(pwd) + [0])
        for pwd in medium:
            data.append(self.extract_features(pwd) + [1])
        for pwd in strong:
            data.append(self.extract_features(pwd) + [2])

        df = pd.DataFrame(data, columns=self.feature_names + ['label'])
        return df

    # ---------- TRAINING ----------
    def train(self, n_per_class=1000):
        print("📊 Generating synthetic dataset...")
        df = self.build_dataset(n_per_class)

        X = df[self.feature_names]
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print("🧠 Training RandomForestClassifier...")
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\n✅ Training complete!")
        print(f"🎯 Accuracy: {acc * 100:.2f}%")
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred,
              target_names=['Weak', 'Medium', 'Strong']))
        print(f"\n📊 Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        # Feature importance
        print(f"\n🔍 Feature Importance:")
        for name, imp in zip(self.feature_names, self.model.feature_importances_):
            print(f"   {name:20s}: {imp:.4f}")

        # Save model
        joblib.dump(self.model, 'models/password_model.pkl')
        print(f"\n💾 Model saved to models/password_model.pkl")
        return self.model

    def predict(self, password):
        if self.model is None:
            self.model = joblib.load('models/password_model.pkl')
        features = [self.extract_features(password)]
        prediction = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        labels = ['weak', 'medium', 'strong']
        return {
            'label': labels[prediction],
            'confidence': round(float(max(proba)) * 100, 2),
            'probabilities': {
                'weak': round(float(proba[0]) * 100, 2),
                'medium': round(float(proba[1]) * 100, 2),
                'strong': round(float(proba[2]) * 100, 2)
            }
        }


if __name__ == '__main__':
    trainer = MLTrainer()
    trainer.train(n_per_class=1000)
