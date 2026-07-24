# ML-Triathlon — Three Algorithm Notebooks

Three Jupyter notebooks implementing K-Means clustering, K-Nearest Neighbors, and Multinomial Naive Bayes on three real-world datasets (LEGO, FAA Wildlife Strikes, UFO Sightings) — all executed with verified outputs.

## What it does

Three independent notebooks, each applying a different scikit-learn algorithm to a matching problem type:
- **K-Means** on LEGO sets (19,812 sets, features: year, num_parts) with PCA visualization and silhouette analysis
- **KNN** on FAA wildlife strike records (19,302 records, 8 features, 5-class classification) with cross-validation
- **Multinomial Naive Bayes + TF-IDF** on UFO sighting reports (30,000 sampled, 5,000 unigrams & bigrams, 10 shape categories)

## Tech stack

Python, scikit-learn (KMeans, KNeighborsClassifier, MultinomialNB, TfidfVectorizer), pandas, numpy, matplotlib, NLTK (stopwords)

## Verified results

### K-Means Clustering — LEGO Database
| Metric | Value |
|--------|-------|
| Optimal k | 4 |
| Silhouette Score | **0.5202** |
| Clusters | Modern small sets (12,104), Large collector (201), Vintage classics (5,677), Mid-size modern (1,830) |

### K-Nearest Neighbors — Aviation Wildlife Strikes
| Metric | Value |
|--------|-------|
| Best k | 8 |
| Test Accuracy | **89.77%** |
| 5-Fold CV Accuracy | **89.54% ± 0.12%** |

### Naive Bayes — UFO Sightings Reports
| Metric | Value |
|--------|-------|
| Test Accuracy | **46.10%** (baseline 24.3%) |
| Best classes | Triangle (F1=0.61), Fireball (F1=0.57), Light (F1=0.56) |

## Setup

```bash
pip install numpy pandas scikit-learn matplotlib nltk seaborn nbformat
jupyter notebook K-Means_LEGO.ipynb
```

All datasets are included in the `datasets/` folder.

## Status

**Complete — all notebooks executed with verified outputs.** The notebooks previously had no cell outputs (`execution_count: null`). They've been replaced with fully executed versions from Google Colab, confirming the reported metrics. Hardcoded file paths in the notebooks may need updating to run on a different machine.