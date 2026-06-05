import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score
import os
import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'datasets')
RESULTS = os.path.join(BASE, 'results')
STOPWORDS = set(stopwords.words('english'))

COLUMNS = ['datetime', 'city', 'state', 'country', 'shape', 'duration_seconds',
           'duration_hms', 'comments', 'date_posted', 'latitude', 'longitude']

def load_and_preprocess():
    df = pd.read_csv(os.path.join(DATA, 'nuforc_sightings.csv'),
                     names=COLUMNS, header=0, low_memory=False)
    print(f"Loaded {len(df)} UFO sighting records")

    df['comments'] = df['comments'].fillna('').astype(str)
    df['shape'] = df['shape'].fillna('unknown').str.lower().str.strip()

    # Filter to top 10 shapes for reasonable classification
    top_shapes = df['shape'].value_counts().head(10).index
    df = df[df['shape'].isin(top_shapes)].copy()
    print(f"Top 10 shapes: {list(top_shapes)}")
    print(f"Filtered to {len(df)} records with top 10 shapes")

    return df

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    return ' '.join(words)

def show_top_features(vectorizer, model, class_names, n=10):
    feature_names = vectorizer.get_feature_names_out()
    n_classes = min(len(class_names), 10)
    n_cols = 2
    n_rows = (n_classes + 1) // 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, n_rows * 3.5))
    axes = axes.flatten()

    for i in range(n_classes):
        log_probs = model.feature_log_prob_[i]
        top_idx = np.argsort(log_probs)[-n:]

        ax = axes[i]
        ax.barh(range(n), log_probs[top_idx])
        ax.set_yticks(range(n))
        ax.set_yticklabels([feature_names[j] for j in top_idx])
        ax.set_title(f'Top features for: {class_names[i]}')

    for j in range(n_classes, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'ufo_top_features.png'), dpi=100)
    plt.close()
    print(f"[Saved] ufo_top_features.png")

def evaluate_model(model, X_test, y_test, class_names):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n=== Naive Bayes Classification Report ===")
    print(f"Test Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=class_names))

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    fig, ax = plt.subplots(figsize=(12, 10))
    disp.plot(ax=ax, cmap='Blues', xticks_rotation=45, values_format='d')
    ax.set_title('Confusion Matrix - UFO Shape Prediction')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'ufo_confusion_matrix.png'), dpi=100)
    plt.close()
    print(f"[Saved] ufo_confusion_matrix.png")

    return acc

def main():
    os.makedirs(RESULTS, exist_ok=True)
    df = load_and_preprocess()

    df['clean_comments'] = df['comments'].apply(clean_text)
    df = df[df['clean_comments'].str.len() > 10].copy()
    print(f"After text cleaning filter: {len(df)} records")

    X = df['clean_comments']
    y = df['shape']

    # Use a subset if too large
    if len(df) > 30000:
        df_sample = df.sample(n=30000, random_state=42)
        X = df_sample['clean_comments']
        y = df_sample['shape']
        print(f"Sampled to 30,000 records for performance")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2),
                                  min_df=5, max_df=0.7, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")

    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)

    class_names = list(model.classes_)
    evaluate_model(model, X_test_vec, y_test, class_names)
    show_top_features(vectorizer, model, class_names, n=10)

    print("\nSample predictions:")
    sample_size = min(5, len(X_test))
    sample_idxs = np.random.choice(len(X_test), size=sample_size, replace=False)
    X_sample = X_test.iloc[sample_idxs]
    y_sample_true = y_test.iloc[sample_idxs]
    y_sample_pred = model.predict(vectorizer.transform(X_sample))
    for i, idx in enumerate(sample_idxs):
        print(f"  True: {y_sample_true.iloc[i]:>12} | Pred: {y_sample_pred[i]:>12} | Text: {X_sample.iloc[i][:80]}...")

    print("\nDone! Naive Bayes model trained and evaluated.")

if __name__ == '__main__':
    main()
