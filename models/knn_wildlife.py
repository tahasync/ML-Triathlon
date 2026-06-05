import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'datasets')
RESULTS = os.path.join(BASE, 'results')

EFFECT_MAP = {
    'None': 0,
    'Other': 1,
    'Precautionary Landing': 2,
    'Aborted Take-off': 3,
    'Engine Shut Down': 4
}

def load_and_preprocess():
    df = pd.read_csv(os.path.join(DATA, 'wildlife_strikes.csv'))
    print(f"Loaded {len(df)} wildlife strike records")

    df['effect'] = df['effect'].fillna('None').map(EFFECT_MAP)
    df = df.dropna(subset=['effect'])

    species_counts = df['species'].value_counts()
    rare = species_counts[species_counts < 50].index
    df['species_clean'] = df['species'].fillna('UNKNOWN').replace(rare, 'OTHER')

    for col in ['phase_of_flt', 'time_of_day', 'sky']:
        df[col] = df[col].fillna('Unknown')

    for col in ['height', 'speed', 'ac_mass', 'num_engs']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].median())

    encoders = {}
    for col in ['phase_of_flt', 'time_of_day', 'sky', 'species_clean']:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = ['height', 'speed', 'ac_mass', 'num_engs',
                    'phase_of_flt_enc', 'time_of_day_enc', 'sky_enc', 'species_clean_enc']

    print(f"\nNaN check per feature column:")
    for col in feature_cols:
        nan_count = df[col].isna().sum()
        if nan_count > 0:
            print(f"  WARNING: {col} has {nan_count} NaN values")

    X = df[feature_cols].values.astype(np.float64)
    y = df['effect'].values.astype(np.int64)

    print(f"\nFeatures: {feature_cols}")
    print(f"Effect distribution:\n{df['effect'].map({v:k for k,v in EFFECT_MAP.items()}).value_counts().sort_index()}")
    print(f"X shape: {X.shape}, y shape: {y.shape}")

    return X, y, df, feature_cols

def find_best_k(X_train, y_train, X_test, y_test, max_k=30):
    train_acc = []
    test_acc = []
    K_range = range(1, max_k + 1)

    for k in K_range:
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, y_train)
        train_acc.append(knn.score(X_train, y_train))
        test_acc.append(knn.score(X_test, y_test))

    best_k = K_range[np.argmax(test_acc)]
    best_score = max(test_acc)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(K_range, train_acc, 'b-', label='Training Accuracy')
    ax.plot(K_range, test_acc, 'r-', label='Test Accuracy')
    ax.axvline(best_k, color='g', linestyle='--', alpha=0.7, label=f'Best k={best_k}')
    ax.set_title('KNN: Accuracy vs Number of Neighbors')
    ax.set_xlabel('k (Number of Neighbors)')
    ax.set_ylabel('Accuracy')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'wildlife_knn_accuracy.png'), dpi=100)
    plt.close()
    print(f"[Saved] wildlife_knn_accuracy.png")

    return best_k, best_score

def evaluate_model(knn, X_test, y_test, effect_names):
    y_pred = knn.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n=== KNN Classification Report ===")
    print(f"Test Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=effect_names))

    short_names = ['None', 'Other', 'Prec.\nLanding', 'Abort\nTake-off', 'Engine\nShut Down']
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=short_names)
    fig, ax = plt.subplots(figsize=(8, 7))
    disp.plot(ax=ax, cmap='Blues', values_format='d', xticks_rotation=0)
    ax.set_title('Confusion Matrix - Wildlife Strike Risk Level')
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'wildlife_confusion_matrix.png'), dpi=120)
    plt.close()
    print(f"[Saved] wildlife_confusion_matrix.png")

    return acc

def main():
    os.makedirs(RESULTS, exist_ok=True)
    X, y, df, feature_cols = load_and_preprocess()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    best_k, best_score = find_best_k(X_train, y_train, X_test, y_test, max_k=30)
    print(f"\nBest k = {best_k} with test accuracy = {best_score:.4f}")

    knn = KNeighborsClassifier(n_neighbors=best_k)
    knn.fit(X_train, y_train)

    cv_scores = cross_val_score(knn, X_scaled, y, cv=5)
    print(f"5-Fold CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    effect_names = ['None', 'Other', 'Precautionary Landing', 'Aborted Take-off', 'Engine Shut Down']
    evaluate_model(knn, X_test, y_test, effect_names)

    print("\nDone! KNN model trained and evaluated.")

if __name__ == '__main__':
    main()
