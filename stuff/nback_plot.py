import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib.ticker import MaxNLocator
import numpy as np

# ... (other functions stay the same) ...
def load_and_prepare_data():
    brain_file = str(Path.home()) + '/.brainworkshop/data/stats.txt'
    brain_columns = ['time', 'dnb', 'percent', 'mode', 'back', 'ticks_per_trial', 'num_trials_total',
                     'manual', 'session_number', 'pos1', 'audio', 'color', 'visvis', 'audiovis', 'arithmetic',
                     'image', 'visaudio', 'audio2', 'pos2', 'pos3', 'pos4', 'vis1', 'vis2', 'vis3', 'vis4',
                     'tickstimesnumtimestrials', 'None']

    df = pd.read_csv(brain_file, names=brain_columns)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').sort_index()

    # Convert columns that should be numeric but are not
    for col in ['percent', 'back', 'ticks_per_trial', 'num_trials_total']:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 'coerce' will set invalid parsing to NaN

    df['score'] = df['back'] * 100 + df['percent']

    # Keep 'dnb' and numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    return df, numeric_columns

def find_optimal_clusters(data, max_k=10):
    # Check if the number of samples is too low
    if len(data) <= 2:
        return 1  # Not enough data to form clusters, return a default single cluster

    silhouette_scores = []
    max_k = min(max_k, len(data) - 1)  # Ensure max_k does not exceed n_samples - 1

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=10, n_init=10)
        kmeans.fit(data)
        score = silhouette_score(data, kmeans.labels_)
        silhouette_scores.append((k, score))

    # Find the optimal k using silhouette score
    optimal_k = sorted(silhouette_scores, key=lambda x: x[1], reverse=True)[0][0]
    return optimal_k

def cluster_dnb_levels(df):
    # Extract the feature for clustering (dnb levels encoded as integers)
    dnb_levels = df['dnb'].unique()
    dnb_encoded = pd.factorize(dnb_levels)[0].reshape(-1, 1)

    # Find the optimal number of clusters
    optimal_k = find_optimal_clusters(dnb_encoded)
    kmeans = KMeans(n_clusters=optimal_k, random_state=10)
    kmeans.fit(dnb_encoded)

    # Map the cluster labels to the original dnb levels
    cluster_labels = kmeans.labels_
    dnb_cluster_map = dict(zip(dnb_levels, cluster_labels))
    return dnb_cluster_map

def plot_enhanced(df, numeric_columns):
    fig, ax = plt.subplots(figsize=(15, 8))

    # Cluster dnb levels
    dnb_cluster_map = cluster_dnb_levels(df)
    df['cluster'] = df['dnb'].map(dnb_cluster_map)
    cluster_colors = plt.cm.tab10(np.linspace(0, 1, len(np.unique(df['cluster']))))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
    ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
    ax.set_facecolor('whitesmoke')

    for cluster, color in zip(np.unique(df['cluster']), cluster_colors):
        cluster_df = df[df['cluster'] == cluster]
        groups = cluster_df.groupby([cluster_df.index.date])

        daily_mean = groups[numeric_columns].mean()
        daily_std = groups[numeric_columns].std()

        ax.fill_between(daily_mean.index, daily_mean['score'] - daily_std['score'],
                        daily_mean['score'] + daily_std['score'], color=color, alpha=0.3)
        ax.scatter(daily_mean.index, daily_mean['score'], label=f'Cluster {cluster}', color=color, alpha=0.7)

    ax.xaxis.set_tick_params(rotation=45)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.set_xlabel('Date')
    ax.set_ylabel('Score')
    ax.set_title('Enhanced Brain Workshop N-back Performance with Clusters')
    ax.legend()

    plt.tight_layout()
    plt.show()


def main():
    df, numeric_columns = load_and_prepare_data()
    plot_enhanced(df, numeric_columns)

if __name__ == '__main__':
    main()
