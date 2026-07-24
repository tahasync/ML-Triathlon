# ML-Triathlon — Three Algorithm Notebooks

Three Jupyter notebooks implementing K-Means clustering, K-Nearest Neighbors, and Multinomial Naive Bayes on three real-world datasets (LEGO, FAA Wildlife Strikes, UFO Sightings).

## What it does

Three independent notebooks, each applying a different scikit-learn algorithm to a matching problem type:
- **K-Means** on LEGO sets (features: year, num_parts) with PCA visualization and silhouette analysis
- **KNN** on FAA wildlife strike records (8 features, 5-class classification) with cross-validation
- **Multinomial Naive Bayes + TF-IDF** on UFO sighting reports (5000 unigrams & bigrams, 10 shape categories)

## Tech stack

Python, scikit-learn (KMeans, KNeighborsClassifier, MultinomialNB, TfidfVectorizer), pandas, numpy, matplotlib, NLTK (stopwords)

## Status

**Incomplete — notebooks have never been executed.** All three notebooks contain syntactically complete code with proper ML workflows (train/test splits, scaling, TF-IDF vectorization, evaluation), but **none have been run** — every cell has `execution_count: null` and zero output cells. The results table in a previous version of this README (silhouette score 0.5202, KNN accuracy 89.77%, Naive Bayes accuracy 46.10%) and the PNG images in `results/` were generated externally and **cannot be verified** from the committed notebooks.

Datasets are included in the `datasets/` folder. To run the notebooks, update the hardcoded `BASE` path at the top of each notebook and execute cells sequentially:

```bash
pip install numpy pandas scikit-learn matplotlib nltk seaborn nbformat
jupyter notebook K-Means_LEGO.ipynb
```