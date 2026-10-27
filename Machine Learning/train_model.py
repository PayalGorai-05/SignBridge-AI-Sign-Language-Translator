
# ============================================================
#              SIGNBRIDGE - MODEL TRAINING
#           AI SIGN LANGUAGE RECOGNITION SYSTEM
#
# MODELS:
# Decision Tree | Random Forest | KNN | SVM | XGBoost
#
# EVALUATION:
# 1. Testing Accuracy (All Models)
# 2. Precision (All Models)
# 3. Recall (All Models)
# 4. F1-Score (All Models)
# 5. Training Accuracy (Random Forest Only)
# 6. Classification Report
# 7. Confusion Matrix
#
# OUTPUTS:
# gesture_model.pkl
# model_accuracy_comparison.png
# all_model_metrics_comparison.png
# confusion_matrix.png
# model_evaluation_metrics.csv
# ============================================================

import os
import sys
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

# ================= FILE PATHS =================

DATA_FILE = "my_gesture_dataset.csv"
MODEL_FILE = "gesture_model.pkl"

ACCURACY_GRAPH = "model_accuracy_comparison.png"
METRICS_GRAPH = "all_model_metrics_comparison.png"
CONFUSION_GRAPH = "confusion_matrix.png"
METRICS_CSV = "model_evaluation_metrics.csv"

FEATURES = [
    "flex0", "flex1", "flex2", "flex3", "flex4",
    "ax", "ay", "az", "gx", "gy", "gz"
]


def main():

    print("\n" + "=" * 70)
    print("       SIGNBRIDGE - AI SIGN LANGUAGE RECOGNITION")
    print("                  MODEL TRAINING")
    print("=" * 70)

    # ========================================================
    # STEP 1: LOAD DATASET
    # ========================================================

    if not os.path.exists(DATA_FILE):
        print("\nERROR: Dataset not found:", DATA_FILE)
        print("Keep the dataset in the same folder.")
        sys.exit(1)

    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.strip()

    required = FEATURES + ["gesture"]

    missing = [
        column for column in required
        if column not in df.columns
    ]

    if missing:
        print("\nMissing required columns:", missing)
        sys.exit(1)

    df = df[required].copy()

    df["gesture"] = (
        df["gesture"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    for column in FEATURES:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    df.dropna(subset=required, inplace=True)
    df = df[df["gesture"] != ""]

    if df.empty:
        print("\nERROR: Dataset is empty.")
        sys.exit(1)

    counts = df["gesture"].value_counts()

    if (counts < 2).any():
        print("\nEach gesture needs at least 2 samples.")
        print(counts[counts < 2])
        sys.exit(1)

    print("\nDataset loaded successfully!")
    print("Total samples :", len(df))
    print("Gesture classes:", df["gesture"].nunique())

    print("\nSamples per gesture:")
    print(counts.to_string())

    # ========================================================
    # STEP 2: FEATURES AND LABELS
    # ========================================================

    X = df[FEATURES]
    y = df["gesture"].astype(str)

    # ========================================================
    # STEP 3: TRAIN-TEST SPLIT
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples :", len(X_test))

    # ========================================================
    # STEP 4: DEFINE MODELS
    # ========================================================

    models = {

        "Decision Tree": DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced"
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        ),

        "KNN": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=5)
        ),

        "SVM": make_pipeline(
            StandardScaler(),
            SVC(
                kernel="rbf",
                probability=True,
                random_state=42,
                class_weight="balanced"
            )
        )
    }

    # ========================================================
    # STEP 5: OPTIONAL XGBOOST
    # ========================================================

    encoder = None
    y_train_encoded = None

    try:
        from xgboost import XGBClassifier

        encoder = LabelEncoder()
        y_train_encoded = encoder.fit_transform(y_train)

        models["XGBoost"] = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1
        )

        print("\nXGBoost available.")

    except ImportError:
        print("\nXGBoost not installed.")
        print("Continuing with four models.")

    # ========================================================
    # STEP 6: TRAIN AND EVALUATE ALL MODELS
    # ========================================================

    results = {}
    trained_models = {}
    all_predictions = {}

    rf_training_accuracy = None

    print("\n" + "=" * 70)
    print("                    MODEL EVALUATION")
    print("=" * 70)

    for name, model in models.items():

        print(f"\nTraining {name}...")

        # -------- MODEL TRAINING --------

        if name == "XGBoost":

            model.fit(X_train, y_train_encoded)

            encoded_predictions = (
                model.predict(X_test).astype(int)
            )

            predictions = encoder.inverse_transform(
                encoded_predictions
            )

        else:

            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

        # -------- TESTING ACCURACY --------

        accuracy = accuracy_score(
            y_test,
            predictions
        ) * 100

        # -------- PRECISION --------

        precision = precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        ) * 100

        # -------- RECALL --------

        recall = recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        ) * 100

        # -------- F1-SCORE --------

        f1 = f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        ) * 100

        # -------- SAVE RESULTS --------

        results[name] = {
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1-Score": f1
        }

        trained_models[name] = model
        all_predictions[name] = predictions

        # -------- PRINT METRICS --------

        print(f"Testing Accuracy : {accuracy:.2f}%")
        print(f"Precision        : {precision:.2f}%")
        print(f"Recall           : {recall:.2f}%")
        print(f"F1-Score         : {f1:.2f}%")

        # ====================================================
        # RANDOM FOREST TRAINING ACCURACY ONLY
        # ====================================================

        if name == "Random Forest":

            train_predictions = model.predict(X_train)

            rf_training_accuracy = accuracy_score(
                y_train,
                train_predictions
            ) * 100

            gap = rf_training_accuracy - accuracy

            print(
                f"Training Accuracy: "
                f"{rf_training_accuracy:.2f}%"
            )

            print(
                f"Train-Test Gap   : "
                f"{gap:.2f} percentage points"
            )

    # ========================================================
    # STEP 7: MODEL EVALUATION COMPARISON TABLE
    # ========================================================

    results_df = pd.DataFrame.from_dict(
        results,
        orient="index"
    )

    print("\n" + "=" * 70)
    print("              ALL MODEL EVALUATION METRICS")
    print("=" * 70)

    print(
        results_df.to_string(
            float_format=lambda x: f"{x:.2f}%"
        )
    )

    # Save numerical evaluation results to CSV
    results_df.to_csv(
        METRICS_CSV,
        index_label="Model",
        float_format="%.4f"
    )

    # ========================================================
    # STEP 8: SELECT BEST MODEL
    # ========================================================

    best_name = max(
        results,
        key=lambda name: results[name]["Accuracy"]
    )

    best_model = trained_models[best_name]
    best_predictions = all_predictions[best_name]

    print("\n" + "=" * 70)
    print("                       BEST MODEL")
    print("=" * 70)

    print("Model:", best_name)

    print(
        f"Testing Accuracy: "
        f"{results[best_name]['Accuracy']:.2f}%"
    )

    print(
        f"Precision       : "
        f"{results[best_name]['Precision']:.2f}%"
    )

    print(
        f"Recall          : "
        f"{results[best_name]['Recall']:.2f}%"
    )

    print(
        f"F1-Score        : "
        f"{results[best_name]['F1-Score']:.2f}%"
    )

    print("\nRandom Forest Performance:")

    print(
        f"Training Accuracy: "
        f"{rf_training_accuracy:.2f}%"
    )

    print(
        f"Testing Accuracy : "
        f"{results['Random Forest']['Accuracy']:.2f}%"
    )

    # ========================================================
    # STEP 9: SAVE BEST MODEL
    # ========================================================

    if best_name == "XGBoost":
        class_names = list(encoder.classes_)
    else:
        class_names = sorted(y.unique())

    best_bundle = {

        "model": best_model,
        "model_name": best_name,
        "features": FEATURES,
        "class_names": class_names,

        "label_to_id": {
            label: index
            for index, label in enumerate(class_names)
        },

        "id_to_label": {
            index: label
            for index, label in enumerate(class_names)
        }
    }

    joblib.dump(best_bundle, MODEL_FILE)

    print("\nBest model saved:")
    print(os.path.abspath(MODEL_FILE))

    # ========================================================
    # STEP 10: CLASSIFICATION REPORT
    # ========================================================

    print("\n" + "=" * 70)
    print("              BEST MODEL CLASSIFICATION REPORT")
    print("=" * 70)

    print(
        classification_report(
            y_test,
            best_predictions,
            labels=class_names,
            zero_division=0
        )
    )

    # ========================================================
    # STEP 11: CONFUSION MATRIX
    # ========================================================

    cm = confusion_matrix(
        y_test,
        best_predictions,
        labels=class_names
    )

    cm_df = pd.DataFrame(
        cm,
        index=class_names,
        columns=class_names
    )

    print("\n" + "=" * 70)
    print("                     CONFUSION MATRIX")
    print("=" * 70)

    print("\nRows    = Actual Gestures")
    print("Columns = Predicted Gestures\n")

    print(cm_df.to_string())

    # -------- CONFUSION MATRIX GRAPH --------

    fig_cm, ax_cm = plt.subplots(
        figsize=(11, 9)
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names
    )

    display.plot(
        ax=ax_cm,
        cmap="Blues",
        values_format="d",
        xticks_rotation=45,
        colorbar=True
    )

    ax_cm.set_title(
        f"SignBridge - {best_name}\nConfusion Matrix",
        fontsize=15,
        fontweight="bold",
        pad=15
    )

    ax_cm.set_xlabel("Predicted Gesture")
    ax_cm.set_ylabel("Actual Gesture")

    fig_cm.tight_layout()

    fig_cm.savefig(
        CONFUSION_GRAPH,
        dpi=300,
        bbox_inches="tight"
    )

    print("\nConfusion matrix saved:")
    print(os.path.abspath(CONFUSION_GRAPH))

    # ========================================================
    # STEP 12: ACCURACY COMPARISON GRAPH
    # ========================================================

    names = list(results.keys())

    scores = [
        results[name]["Accuracy"]
        for name in names
    ]

    fig_acc, ax_acc = plt.subplots(
        figsize=(12, 6)
    )

    bars = ax_acc.bar(
        names,
        scores,
        color="#4472C4",
        width=0.55
    )

    # Highlight best model
    best_index = names.index(best_name)
    bars[best_index].set_color("#2E8B57")

    ax_acc.set_title(
        "SignBridge - Model Accuracy Comparison",
        fontsize=16,
        fontweight="bold",
        pad=18
    )

    ax_acc.set_xlabel(
        "Machine Learning Models",
        fontsize=12
    )

    ax_acc.set_ylabel(
        "Testing Accuracy (%)",
        fontsize=12
    )

    ax_acc.set_ylim(0, 110)

    ax_acc.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    ax_acc.set_axisbelow(True)

    # Add exact percentage above each bar
    for bar, score in zip(bars, scores):

        ax_acc.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            f"{score:.2f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold"
        )

    fig_acc.tight_layout()

    fig_acc.savefig(
        ACCURACY_GRAPH,
        dpi=300,
        bbox_inches="tight"
    )

    print("\nAccuracy graph saved:")
    print(os.path.abspath(ACCURACY_GRAPH))

    # ========================================================
    # STEP 13: ALL MODEL METRICS IN ONE GROUPED BAR GRAPH
    # ========================================================

    print("\nGenerating combined model evaluation graph...")

    metric_names = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1-Score"
    ]

    # Each row represents one model
    metrics_df = results_df[metric_names]

    model_names = metrics_df.index.tolist()

    x = np.arange(len(model_names))

    # Width of each metric bar
    width = 0.19

    colors = [
        "#4472C4",  # Accuracy - Blue
        "#ED7D31",  # Precision - Orange
        "#70AD47",  # Recall - Green
        "#8064A2"   # F1-Score - Purple
    ]

    fig_metrics, ax_metrics = plt.subplots(
        figsize=(17, 9)
    )

    # Four bars for every model
    for i, metric in enumerate(metric_names):

        values = metrics_df[metric].values

        offset = (i - 1.5) * width

        bars = ax_metrics.bar(
            x + offset,
            values,
            width=width,
            label=metric,
            color=colors[i],
            edgecolor="white",
            linewidth=0.6
        )

        # ============================================
        # LABEL EVERY BAR WITH EXACT PERCENTAGE
        # ============================================

        ax_metrics.bar_label(
            bars,
            labels=[
                f"{value:.2f}%"
                for value in values
            ],
            padding=4,
            fontsize=9,
            fontweight="bold",
            rotation=90
        )

    # -------- GRAPH TITLE --------

    ax_metrics.set_title(
        "SignBridge - Machine Learning Model Evaluation\n"
        "Accuracy | Precision | Recall | F1-Score",
        fontsize=17,
        fontweight="bold",
        pad=25
    )

    # -------- AXES --------

    ax_metrics.set_xlabel(
        "Machine Learning Models",
        fontsize=13,
        fontweight="bold",
        labelpad=12
    )

    ax_metrics.set_ylabel(
        "Evaluation Metrics (%)",
        fontsize=13,
        fontweight="bold",
        labelpad=12
    )

    ax_metrics.set_xticks(x)

    ax_metrics.set_xticklabels(
        model_names,
        fontsize=11,
        fontweight="medium"
    )

    # Keep room for percentage labels
    ax_metrics.set_ylim(0, 115)

    ax_metrics.set_yticks(
        np.arange(0, 101, 10)
    )

    ax_metrics.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    ax_metrics.set_axisbelow(True)

    # -------- LEGEND --------

    ax_metrics.legend(
        title="Evaluation Metrics",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=4,
        fontsize=11,
        frameon=False
    )

    # -------- GRAPH STYLE --------

    ax_metrics.spines["top"].set_visible(False)
    ax_metrics.spines["right"].set_visible(False)

    fig_metrics.tight_layout()

    # -------- SAVE GRAPH --------

    fig_metrics.savefig(
        METRICS_GRAPH,
        dpi=300,
        bbox_inches="tight"
    )

    print("\nCombined evaluation metrics graph saved:")
    print(os.path.abspath(METRICS_GRAPH))

    # ========================================================
    # STEP 14: TRAINING COMPLETED
    # ========================================================

    print("\n" + "=" * 70)
    print("                    TRAINING COMPLETED")
    print("=" * 70)

    print("\nGenerated files:")

    print("1. gesture_model.pkl")
    print("2. model_accuracy_comparison.png")
    print("3. all_model_metrics_comparison.png")
    print("4. confusion_matrix.png")
    print("5. model_evaluation_metrics.csv")

    print("\nOpening graphs...")

    try:
        plt.show()
    except Exception as error:
        print("\nCould not display graphs:", error)
        print("Open saved PNG files directly.")

    print("\nTo start live recognition:")
    print("py predict_live.py")


if __name__ == "__main__":
    main()
