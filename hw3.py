# hw3_text_ml_ultra.py — Homework 3 (ультрабырзая версия)

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import Counter

from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

CATEGORIES = ["sci.space", "rec.sport.hockey", "talk.politics.mideast"]

# -------------------------------
# 1. Мини-датасет (по 30 текстов на класс)
# -------------------------------
def collect_dataset():
    data_all = fetch_20newsgroups(
        subset="train",
        categories=CATEGORIES,
        remove=("headers", "footers", "quotes"),
        shuffle=True,
        random_state=RANDOM_STATE
    )
    texts, labels = [], []
    for cls in np.unique(data_all.target):
        idx = np.where(data_all.target == cls)[0][:30]  # берём 30 документов
        for i in idx:
            texts.append(data_all.data[i])
            labels.append(data_all.target[i])
    target_names = data_all.target_names
    df = pd.DataFrame({"text": texts, "label_id": labels})
    df["label"] = df["label_id"].map(lambda i: target_names[i])
    return df, target_names

# -------------------------------
# 2. Классификация (без GridSearch)
# -------------------------------
def run_classification(df, target_names):
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label_id"], test_size=0.25, stratify=df["label_id"],
        random_state=RANDOM_STATE
    )

    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)

    classifiers = {
        "LogisticRegression": LogisticRegression(max_iter=500, solver="liblinear", random_state=RANDOM_STATE),
        "LinearSVC": LinearSVC(C=1.0, random_state=RANDOM_STATE),
        "MultinomialNB": MultinomialNB(alpha=1.0),
    }

    rows = []
    reports = []

    for name, clf in classifiers.items():
        pipe = Pipeline([
            ("tfidf", vectorizer),
            ("clf", clf),
        ])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro")

        rows.append({"Model": name, "Test_Accuracy": acc, "Test_F1_macro": f1})

        rep = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        for label, stats in rep.items():
            if isinstance(stats, dict):
                reports.append({
                    "Model": name, "Label": label,
                    "precision": stats.get("precision", np.nan),
                    "recall": stats.get("recall", np.nan),
                    "f1-score": stats.get("f1-score", np.nan),
                })

    return pd.DataFrame(rows), pd.DataFrame(reports)

# -------------------------------
# 3. Кластеризация (KMeans + Agglomerative)
# -------------------------------
def run_clustering(df):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    X = vectorizer.fit_transform(df["text"])
    true_labels = df["label_id"].values
    n_clusters = len(np.unique(true_labels))

    svd = TruncatedSVD(n_components=20, random_state=RANDOM_STATE)
    X_lsa = svd.fit_transform(X)

    rows = []
    # KMeans
    km = KMeans(n_clusters=n_clusters, n_init=5, random_state=RANDOM_STATE)
    pred_km = km.fit_predict(X_lsa)
    rows.append({
        "Algo": "KMeans", "ARI": adjusted_rand_score(true_labels, pred_km),
        "NMI": normalized_mutual_info_score(true_labels, pred_km)
    })
    # Agglomerative
    agg = AgglomerativeClustering(n_clusters=n_clusters)
    pred_agg = agg.fit_predict(X_lsa)
    rows.append({
        "Algo": "Agglomerative", "ARI": adjusted_rand_score(true_labels, pred_agg),
        "NMI": normalized_mutual_info_score(true_labels, pred_agg)
    })
    return pd.DataFrame(rows)

# -------------------------------
# 4. Экспорт
# -------------------------------
def export_all(df, clf_results, clf_reports, clustering_df):
    out_dir = Path("results"); out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = out_dir / f"hw3_ultra_results_{ts}.xlsx"
    csv_path = out_dir / f"hw3_ultra_dataset_{ts}.csv"

    df[["text", "label"]].to_csv(csv_path, index=False, encoding="utf-8")
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        clf_results.to_excel(writer, sheet_name="clf_results", index=False)
        clf_reports.to_excel(writer, sheet_name="clf_reports", index=False)
        clustering_df.to_excel(writer, sheet_name="clustering", index=False)

    print(f"\nSaved Excel: {excel_path.resolve()}")
    print(f"Saved CSV (для Orange): {csv_path.resolve()}")

# -------------------------------
# Main
# -------------------------------
def main():
    print("Collecting dataset...")
    df, target_names = collect_dataset()
    print("Classes:", Counter(df["label"]))

    print("\nClassification...")
    clf_results, clf_reports = run_classification(df, target_names)

    print("\nClustering...")
    clustering_df = run_clustering(df)

    print("\nExport...")
    export_all(df, clf_results, clf_reports, clustering_df)

    print("\nDone.")

if __name__ == "__main__":
    main()
