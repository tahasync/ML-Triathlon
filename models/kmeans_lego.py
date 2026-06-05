import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'datasets')
RESULTS = os.path.join(BASE, 'results')

def load_data():
    sets = pd.read_csv(os.path.join(DATA, 'lego_sets.csv'))
    themes = pd.read_csv(os.path.join(DATA, 'lego_themes.csv'))
    themes.rename(columns={'id': 'theme_id'}, inplace=True)
    df = sets.merge(themes[['theme_id', 'name']], on='theme_id', how='left')
    df.rename(columns={'name_x': 'set_name', 'name_y': 'theme_name'}, inplace=True)
    df = df[(df['year'] >= 1950) & (df['num_parts'] > 0)].copy()
    return df

def elbow_method(X_scaled, max_k=12):
    inertias = []
    sil_scores = []
    K_range = range(2, max_k + 1)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X_scaled, labels))
    return K_range, inertias, sil_scores

def plot_elbow(K_range, inertias, sil_scores):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(K_range, inertias, 'bo-')
    axes[0].set_title('Elbow Method (Inertia)')
    axes[0].set_xlabel('Number of Clusters (k)')
    axes[0].set_ylabel('Inertia')

    axes[1].plot(K_range, sil_scores, 'ro-')
    axes[1].set_title('Silhouette Score vs k')
    axes[1].set_xlabel('Number of Clusters (k)')
    axes[1].set_ylabel('Silhouette Score')

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'lego_elbow.png'), dpi=100)
    plt.close()
    print(f"[Saved] lego_elbow.png")

def run_kmeans(X_scaled, df, k=4):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['cluster'] = km.fit_predict(X_scaled)

    print(f"\n=== K-Means (k={k}) on LEGO Data ===")
    print(f"Silhouette Score: {silhouette_score(X_scaled, df['cluster']):.4f}")

    print("\nCluster Centers (scaled):")
    centers_df = pd.DataFrame(km.cluster_centers_, columns=['year', 'num_parts'])
    print(centers_df.to_string(index=True))

    print("\nCluster Sizes:")
    print(df['cluster'].value_counts().sort_index())

    print("\nSample sets per cluster:")
    for c in sorted(df['cluster'].unique()):
        top = df[df['cluster'] == c].nsmallest(5, 'num_parts')
        print(f"\n  Cluster {c} (n={len(df[df['cluster']==c])}):")
        for _, row in top.iterrows():
            print(f"    {row['set_name']} ({row['year']}, {row['num_parts']} parts, theme: {row['theme_name']})")

    return df, km

def plot_clusters(X_scaled, df):
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df_pca = pd.DataFrame({'PC1': X_pca[:, 0], 'PC2': X_pca[:, 1], 'cluster': df['cluster']})

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for c in sorted(df['cluster'].unique()):
        mask = df_pca['cluster'] == c
        axes[0].scatter(df_pca.loc[mask, 'PC1'], df_pca.loc[mask, 'PC2'],
                        label=f'Cluster {c}', alpha=0.5, s=5)
    axes[0].set_title('LEGO Set Clusters (PCA)')
    axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} var)')
    axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} var)')
    axes[0].legend(markerscale=5)

    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(df['cluster'].unique())))
    for i, c in enumerate(sorted(df['cluster'].unique())):
        mask = df['cluster'] == c
        axes[1].scatter(df.loc[mask, 'year'], df.loc[mask, 'num_parts'],
                        label=f'Cluster {c}', color=colors[i], alpha=0.4, s=5)
    axes[1].set_title('LEGO Sets: Year vs Num Parts by Cluster')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Number of Parts')
    axes[1].legend(markerscale=5)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS, 'lego_clusters.png'), dpi=100)
    plt.close()
    print(f"[Saved] lego_clusters.png")
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_}")

def main():
    os.makedirs(RESULTS, exist_ok=True)
    df = load_data()
    print(f"Loaded {len(df)} LEGO sets")

    X = df[['year', 'num_parts']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    K_range, inertias, sil_scores = elbow_method(X_scaled, max_k=10)
    plot_elbow(K_range, inertias, sil_scores)

    best_k = K_range[np.argmax(sil_scores)]
    print(f"\nOptimal k = {best_k} (highest silhouette score)")

    df, km = run_kmeans(X_scaled, df, k=best_k)
    plot_clusters(X_scaled, df)

    print("\nDone! Results plotted and saved.")

if __name__ == '__main__':
    main()
