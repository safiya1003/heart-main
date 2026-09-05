"""
Heart Disease Prediction Pipeline
==================================
A clean, modular Machine Learning script to:
1. Load and clean heart disease data (`heart.csv`).
2. Preprocess data (impute physiologically invalid zeros, encode categoricals, standardize features).
3. Train ML models (KNN, Random Forest, etc.).
4. Evaluate accuracy, F1-score, confusion matrix, and classification report.
5. Save artifacts (`KNN_heart.pkl` / `RF_heart.pkl`, `scaler.pkl`, `columns.pkl`) for production / Streamlit (`app.py`).
6. Predict heart disease risk on new raw patient data.

Author: Antigravity AI
"""

import os
import argparse
from typing import Tuple, Dict, Any, List

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)


def load_data(filepath: str) -> pd.DataFrame:
    """Load dataset from a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded dataframe.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")
    df = pd.read_csv(filepath)
    print(f"[INFO] Loaded dataset successfully from '{filepath}'. Shape: {df.shape}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean physiologically invalid zero values in clinical measurements.

    In the Heart Disease dataset, Cholesterol and RestingBP contain invalid 0 values.
    We impute them with the mean of non-zero entries.

    Args:
        df: Input dataframe.

    Returns:
        pd.DataFrame: Cleaned dataframe.
    """
    df_clean = df.copy()

    # Impute Cholesterol = 0 with mean of valid Cholesterol
    valid_chol_mean = df_clean.loc[df_clean["Cholesterol"] > 0, "Cholesterol"].mean()
    zero_chol_count = (df_clean["Cholesterol"] == 0).sum()
    if zero_chol_count > 0:
        df_clean["Cholesterol"] = df_clean["Cholesterol"].replace(0, valid_chol_mean).round(2)
        print(f"[INFO] Imputed {zero_chol_count} zero values in 'Cholesterol' with mean ({valid_chol_mean:.2f})")

    # Impute RestingBP = 0 with mean of valid RestingBP
    valid_bp_mean = df_clean.loc[df_clean["RestingBP"] > 0, "RestingBP"].mean()
    zero_bp_count = (df_clean["RestingBP"] == 0).sum()
    if zero_bp_count > 0:
        df_clean["RestingBP"] = df_clean["RestingBP"].replace(0, valid_bp_mean).round(2)
        print(f"[INFO] Imputed {zero_bp_count} zero values in 'RestingBP' with mean ({valid_bp_mean:.2f})")

    return df_clean


def preprocess_data(
    df: pd.DataFrame,
    target_col: str = "HeartDisease",
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler, List[str]]:
    """Preprocess dataset: one-hot encode categorical features, split, and standardize.

    Args:
        df: Input dataframe.
        target_col: Name of the target variable column.
        test_size: Proportion of test data.
        random_state: Random seed for reproducibility.

    Returns:
        Tuple containing:
            - X_train_scaled (np.ndarray): Standardized training features.
            - X_test_scaled (np.ndarray): Standardized testing features.
            - y_train (pd.Series): Training labels.
            - y_test (pd.Series): Testing labels.
            - scaler (StandardScaler): Fitted StandardScaler object.
            - feature_names (List[str]): List of column names used in model.
    """
    df_clean = clean_data(df)

    # One-hot encode categoricals matching the notebook and app.py expectations (drop_first=True)
    df_encoded = pd.get_dummies(df_clean, drop_first=True)

    # Separate features and target
    X = df_encoded.drop(target_col, axis=1)
    y = df_encoded[target_col]
    feature_names = X.columns.tolist()

    print(f"[INFO] Total features after encoding: {len(feature_names)}")

    # Stratified train/test split to preserve target class ratio
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"[INFO] Train size: {X_train.shape[0]} samples, Test size: {X_test.shape[0]} samples")

    # Fit scaler strictly on training set to prevent data leakage
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names


def train_model(
    X_train: np.ndarray,
    y_train: pd.Series,
    model_type: str = "knn",
    **kwargs: Any,
) -> Any:
    """Train a machine learning classification model.

    Args:
        X_train: Standardized training feature matrix.
        y_train: Training labels.
        model_type: 'knn' or 'random_forest' / 'rf'.
        **kwargs: Additional hyperparameters passed to model constructor.

    Returns:
        Trained model instance.
    """
    model_type = model_type.lower()

    if model_type == "knn":
        n_neighbors = kwargs.get("n_neighbors", 7)
        weights = kwargs.get("weights", "distance")
        metric = kwargs.get("metric", "manhattan")
        model = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, metric=metric)
        print(f"[INFO] Training KNN (n_neighbors={n_neighbors}, weights='{weights}', metric='{metric}')...")

    elif model_type in ("random_forest", "rf"):
        n_estimators = kwargs.get("n_estimators", 150)
        max_depth = kwargs.get("max_depth", 6)
        random_state = kwargs.get("random_state", 42)
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
        )
        print(f"[INFO] Training Random Forest (n_estimators={n_estimators}, max_depth={max_depth})...")

    else:
        raise ValueError(f"Unsupported model type '{model_type}'. Choose 'knn' or 'rf'.")

    model.fit(X_train, y_train)
    print(f"[INFO] {model.__class__.__name__} training complete.")
    return model


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: pd.Series,
    model_name: str = "Model",
) -> Dict[str, float]:
    """Evaluate trained model and display comprehensive classification metrics.

    Args:
        model: Trained classifier.
        X_test: Standardized test features.
        y_test: Ground truth test labels.
        model_name: Display label for the model.

    Returns:
        Dict[str, float]: Dictionary containing key performance metrics.
    """
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    roc_auc = None
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 60)
    print(f"             EVALUATION REPORT: {model_name.upper()}")
    print("=" * 60)
    print(f"  Accuracy:  {acc:.4f} ({acc * 100:.2f}%)")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    if roc_auc is not None:
        print(f"  ROC-AUC:   {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  [TN={cm[0, 0]:3d}  FP={cm[0, 1]:3d}]")
    print(f"  [FN={cm[1, 0]:3d}  TP={cm[1, 1]:3d}]")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Disease (0)", "Disease (1)"]))
    print("=" * 60)

    metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
    }
    if roc_auc is not None:
        metrics["roc_auc"] = roc_auc
    return metrics


def save_artifacts(
    model: Any,
    scaler: StandardScaler,
    feature_names: List[str],
    model_path: str = "KNN_heart.pkl",
    scaler_path: str = "scaler.pkl",
    columns_path: str = "columns.pkl",
) -> None:
    """Save trained model, scaler, and expected feature column list.

    Args:
        model: Trained scikit-learn classifier.
        scaler: Fitted StandardScaler instance.
        feature_names: List of encoded feature column names.
        model_path: Filepath for serialized model.
        scaler_path: Filepath for serialized scaler.
        columns_path: Filepath for serialized column list.
    """
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(feature_names, columns_path)

    print(f"[INFO] Artifacts successfully saved:")
    print(f"       - Model:   {model_path}")
    print(f"       - Scaler:  {scaler_path}")
    print(f"       - Columns: {columns_path}")


def load_artifacts(
    model_path: str = "KNN_heart.pkl",
    scaler_path: str = "scaler.pkl",
    columns_path: str = "columns.pkl",
) -> Tuple[Any, StandardScaler, List[str]]:
    """Load serialized model, scaler, and expected feature columns.

    Args:
        model_path: Path to serialized model file.
        scaler_path: Path to serialized scaler file.
        columns_path: Path to serialized columns file.

    Returns:
        Tuple containing loaded (model, scaler, expected_columns).
    """
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    expected_columns = joblib.load(columns_path)
    return model, scaler, expected_columns


def predict_patient_risk(
    patient_data: Dict[str, Any],
    model: Any,
    scaler: StandardScaler,
    expected_columns: List[str],
) -> Dict[str, Any]:
    """Make a heart disease prediction for a single patient dictionary.

    Handles raw categorical and numerical fields identically to app.py.

    Args:
        patient_data: Dictionary containing patient clinical attributes:
            Age (int), Sex ('M'/'F'), ChestPainType ('ATA'/'NAP'/'ASY'/'TA'),
            RestingBP (int), Cholesterol (int), FastingBS (0/1),
            RestingECG ('Normal'/'ST'/'LVH'), MaxHR (int),
            ExerciseAngina ('Y'/'N'), Oldpeak (float), ST_Slope ('Up'/'Flat'/'Down').
        model: Loaded model object.
        scaler: Loaded StandardScaler.
        expected_columns: List of feature names model was trained on.

    Returns:
        Dict with 'prediction' (0 or 1), 'label' ('Low Risk' / 'High Risk'),
        and 'probability' (float between 0 and 1 if available).
    """
    # Build one-hot dictionary representation
    raw_input = {
        "Age": patient_data["Age"],
        "RestingBP": patient_data["RestingBP"],
        "Cholesterol": patient_data["Cholesterol"],
        "FastingBS": patient_data["FastingBS"],
        "MaxHR": patient_data["MaxHR"],
        "Oldpeak": patient_data["Oldpeak"],
        f"Sex_{patient_data['Sex']}": 1,
        f"ChestPainType_{patient_data['ChestPainType']}": 1,
        f"RestingECG_{patient_data['RestingECG']}": 1,
        f"ExerciseAngina_{patient_data['ExerciseAngina']}": 1,
        f"ST_Slope_{patient_data['ST_Slope']}": 1,
    }

    input_df = pd.DataFrame([raw_input])

    # Ensure all expected columns exist and are ordered correctly
    for col in expected_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[expected_columns]

    # Standardize features
    scaled_input = scaler.transform(input_df)

    # Predict
    pred = int(model.predict(scaled_input)[0])
    proba = None
    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(scaled_input)[0][1])

    result = {
        "prediction": pred,
        "label": "High Risk of Heart Disease" if pred == 1 else "Low Risk of Heart Disease",
        "probability": proba,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Heart Disease ML Training & Prediction Pipeline")
    parser.add_argument("--data", type=str, default="heart.csv", help="Path to heart.csv dataset")
    parser.add_argument("--model", type=str, default="both", choices=["knn", "rf", "both"], help="Model type: 'knn', 'rf', or 'both'")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set fraction (default: 0.2)")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("      HEART DISEASE PREDICTION PIPELINE INITIATING")
    print("=" * 60)

    # 1. Load Data
    df = load_data(args.data)

    # 2. Preprocess Data & Feature Scaling
    X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = preprocess_data(
        df, test_size=args.test_size, random_state=42
    )

    models_to_train = ["knn", "rf"] if args.model == "both" else [args.model]
    trained_models = {}
    metrics_summary = {}

    # 3. Train & Evaluate Models
    for m_type in models_to_train:
        m = train_model(X_train_scaled, y_train, model_type=m_type)
        m_name = "KNN" if m_type == "knn" else "Random Forest"
        metrics = evaluate_model(m, X_test_scaled, y_test, model_name=m_name)
        trained_models[m_type] = m
        metrics_summary[m_name] = metrics

    # Print Comparison Summary if multiple models were evaluated
    if len(metrics_summary) > 1:
        print("\n" + "=" * 60)
        print("                  MODEL COMPARISON SUMMARY")
        print("=" * 60)
        print(f"{'Model':<18} | {'Accuracy':<10} | {'F1 Score':<10} | {'ROC-AUC':<10}")
        print("-" * 60)
        for name, met in metrics_summary.items():
            auc_str = f"{met.get('roc_auc', 0.0):.4f}" if "roc_auc" in met else "N/A"
            print(f"{name:<18} | {met['accuracy']*100:.2f}%     | {met['f1_score']:.4f}     | {auc_str}")
        print("=" * 60 + "\n")

    # 4. Save Artifacts
    # Save KNN model for backward compatibility with app.py
    if "knn" in trained_models:
        save_artifacts(
            model=trained_models["knn"],
            scaler=scaler,
            feature_names=feature_names,
            model_path="KNN_heart.pkl",
            scaler_path="scaler.pkl",
            columns_path="columns.pkl",
        )

    # Save Random Forest model if trained
    if "rf" in trained_models:
        joblib.dump(trained_models["rf"], "RF_heart.pkl")
        print("[INFO] Saved Random Forest model to: RF_heart.pkl")

    # 5. Sample Prediction Verification
    print("\n" + "=" * 60)
    print("             SAMPLE PATIENT PREDICTION VERIFICATION")
    print("=" * 60)
    sample_patient = {
        "Age": 54,
        "Sex": "M",
        "ChestPainType": "ASY",
        "RestingBP": 140,
        "Cholesterol": 239,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 160,
        "ExerciseAngina": "N",
        "Oldpeak": 1.2,
        "ST_Slope": "Flat",
    }
    print("Sample Clinical Inputs:")
    for k, v in sample_patient.items():
        print(f"  {k:16s}: {v}")

    eval_model = trained_models.get("rf", trained_models.get("knn"))
    model_name_used = "Random Forest" if "rf" in trained_models else "KNN"
    res = predict_patient_risk(sample_patient, eval_model, scaler, feature_names)

    print(f"\nInference Result ({model_name_used}):")
    print(f"  Risk Status: {res['label']}")
    if res["probability"] is not None:
        print(f"  Probability: {res['probability'] * 100:.1f}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
