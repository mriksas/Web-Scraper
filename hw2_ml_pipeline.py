# hw2_fast.py — ускорённый грид-сёрч: 4 модели + Excel экспорт
# Быстро за счёт:
# - компактных сеток гиперпараметров
# - 3-fold CV
# - параллелизма по потокам (Windows-safe)

import os
from pathlib import Path
from datetime import datetime
from pprint import pprint

import numpy as np
import pandas as pd
import joblib

from warnings import filterwarnings
from sklearn.exceptions import ConvergenceWarning
filterwarnings("ignore", category=ConvergenceWarning)

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report, confusion_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ---------- утилиты ----------

def make_pipe(model):
    return Pipeline([
        ("scaler", "passthrough"),
        ("reduce", "passthrough"),
        ("model", model),
    ])

def build_grids_fast():
    """Минимальные сетки для скорости."""
    grids = []

    # Logistic Regression — быстрый и стабильный вариант
    grids.append({
        "name": "LogisticRegression",
        "estimator": make_pipe(LogisticRegression(random_state=RANDOM_STATE)),
        "param_grid": {
            "scaler": [StandardScaler()],                 # только стандартизация
            "reduce": ["passthrough"],                    # без PCA/SelectKBest
            "model__C": [1.0],                            # одно значение
            "model__solver": ["liblinear"],
            "model__penalty": ["l2"],
            "model__max_iter": [1000],
        },
    })

    # SVC — урезанная сетка
    grids.append({
        "name": "SVC",
        "estimator": make_pipe(SVC(probability=True, random_state=RANDOM_STATE)),
        "param_grid": {
            "scaler": [StandardScaler()],                 # SVM любит скейлинг
            "reduce": ["passthrough"],
            "model__kernel": ["linear", "rbf"],          # только 2 ядра
            "model__C": [1, 10],                          # 2 значения
            "model__gamma": ["scale"],                    # одно значение (для rbf)
        },
    })

    # Random Forest — компактно
    grids.append({
        "name": "RandomForest",
        "estimator": make_pipe(RandomForestClassifier(random_state=RANDOM_STATE)),
        "param_grid": {
            "scaler": ["passthrough"],
            "reduce": ["passthrough"],
            "model__n_estimators": [150],                 # одно значение
            "model__max_depth": [None, 10],               # 2 значения
            "model__max_features": ["sqrt"],              # быстро и обычно хорошо
            "model__min_samples_split": [2],
            "model__min_samples_leaf": [1],
        },
    })

    # KNN — небольшой перебор
    grids.append({
        "name": "KNN",
        "estimator": make_pipe(KNeighborsClassifier()),
        "param_grid": {
            "scaler": [StandardScaler()],                 # критично для KNN
            "reduce": ["passthrough"],
            "model__n_neighbors": [5, 11],                # 2 значения
            "model__weights": ["uniform", "distance"],    # 2 значения
            "model__p": [2],                              # Евклидово расстояние
        },
    })
    return grids

def export_excel(leaderboard, best_params_df, test_reports_df, cv_tables):
    out_dir = Path("results"); out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"hw2_results_fast_{ts}.xlsx"

    engine = None
    for eng in ("openpyxl", "xlsxwriter"):
        try:
            __import__(eng); engine = eng; break
        except Exception:
            continue

    with pd.ExcelWriter(path, engine=engine) as writer:
        leaderboard.to_excel(writer, sheet_name="leaderboard", index=False)
        best_params_df.to_excel(writer, sheet_name="best_params", index=False)
        test_reports_df.to_excel(writer, sheet_name="test_reports", index=False)
        for name, df in cv_tables.items():
            df.to_excel(writer, sheet_name=f"cv_{name}"[:31], index=False)
    print(f"\nExcel сохранён: {path.resolve()}")

# ---------- основной скрипт ----------

def main():
    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series(data.target, name="target")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )

    # Меньше фолдов — быстрее
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    grids = build_grids_fast()
    scoring = {"accuracy": "accuracy", "f1": "f1", "roc_auc": "roc_auc"}

    leaderboard_rows, best_params_rows, test_reports_rows = [], [], []
    best_models, cv_tables = {}, {}

    # Поточный параллелизм (Windows-safe)
    threads = min(8, os.cpu_count() or 2)
    with joblib.parallel_backend("threading", n_jobs=threads):
        for g in grids:
            print(f"\n=== Tuning {g['name']} ===")
            gs = GridSearchCV(
                estimator=g["estimator"],
                param_grid=g["param_grid"],
                scoring=scoring,
                refit="roc_auc",
                cv=cv,
                n_jobs=-1,         # все доступные потоки
                verbose=0,
                return_train_score=False,
            )
            gs.fit(X_train, y_train)

            best_models[g["name"]] = gs.best_estimator_
            params = gs.best_params_
            cv_best = gs.best_score_

            clf = gs.best_estimator_
            proba = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else clf.decision_function(X_test)
            y_pred = clf.predict(X_test)

            metrics = {
                "test_accuracy": accuracy_score(y_test, y_pred),
                "test_f1": f1_score(y_test, y_pred),
                "test_roc_auc": roc_auc_score(y_test, proba),
            }

            scaler_name = params["scaler"].__class__.__name__ if params["scaler"] != "passthrough" else "None"
            reduce_name = params["reduce"].__class__.__name__ if params["reduce"] != "passthrough" else "None"

            leaderboard_rows.append({
                "Model": g["name"],
                "BestScaler": scaler_name,
                "BestReducer": reduce_name,
                "CV_ROC_AUC": cv_best,
                "Test_ROC_AUC": metrics["test_roc_auc"],
                "Test_Accuracy": metrics["test_accuracy"],
                "Test_F1": metrics["test_f1"],
            })

            row = {"Model": g["name"], "Scaler": scaler_name, "Reducer": reduce_name}
            for k, v in params.items():
                if k not in ("scaler", "reduce"):
                    row[k] = v
            best_params_rows.append(row)

            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            for label, stats in report.items():
                if isinstance(stats, dict):
                    test_reports_rows.append({
                        "Model": g["name"],
                        "Label": label,
                        "precision": stats.get("precision", np.nan),
                        "recall": stats.get("recall", np.nan),
                        "f1-score": stats.get("f1-score", np.nan),
                        "support": stats.get("support", np.nan),
                    })

            cv_tables[g["name"]] = pd.DataFrame(gs.cv_results_)
            print("CV ROC-AUC (лучший):", round(cv_best, 4))
            print("Лучшие параметры:"); pprint(params)

    leaderboard = pd.DataFrame(leaderboard_rows).sort_values(by="Test_ROC_AUC", ascending=False)
    print("\n===== Leaderboard =====")
    print(leaderboard.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # Победитель — краткий вывод
    winner_name = leaderboard.iloc[0]["Model"]
    winner = best_models[winner_name]
    y_pred = winner.predict(X_test)
    print(f"\n===== Победитель: {winner_name} =====")
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("Pipeline победителя:")
    for step, obj in winner.named_steps.items():
        print(f"  - {step}: {obj}")

    export_excel(leaderboard, pd.DataFrame(best_params_rows), pd.DataFrame(test_reports_rows), cv_tables)

if __name__ == "__main__":
    main()
