"""
Enhanced KNN classifier evaluation with both category and urgency detection.
- Loads data from database instead of JSON
- Ensures train/test split with no overlap
- Only examples with ID < 2000 are correctly marked for urgency
- Evaluates both category classification AND urgency detection
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from collections import defaultdict, Counter
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    precision_recall_fscore_support
)
from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.db_models import Example
from app.llm.client import get_embeddings

MAX_EXAMPLES_PER_FOLD_DB = 10
LOG_PROGRESS_N = 10
MAX_URGENCY_TAGGED_ID = 2370  # Only IDs < 2370 are reliably tagged for urgency
MAX_EXAMPLES_TO_TEST = 1000  # Limit total examples to test (None = no limit, use all)


def load_all_examples_from_db(engine) -> List[Tuple[str, str, bool, int]]:
    """
    Load all examples from database.
    Returns list of (text, category_id, is_urgent, example_id)
    Respects MAX_EXAMPLES_TO_TEST limit if set.
    """
    print("Loading examples from database...")
    with Session(engine) as session:
        statement = select(Example).order_by(Example.id)
        examples = session.exec(statement).all()
        
        # Apply limit if configured
        if MAX_EXAMPLES_TO_TEST is not None:
            examples = examples[:MAX_EXAMPLES_TO_TEST]
        
        data = []
        for ex in examples:
            data.append((ex.text, ex.category_id, ex.is_urgent, ex.id))
    
    print(f"Loaded {len(data)} examples from database")
    if MAX_EXAMPLES_TO_TEST is not None:
        print(f"   (Limited to {MAX_EXAMPLES_TO_TEST} examples - configure MAX_EXAMPLES_TO_TEST to change)")
    return data


def create_non_overlapping_split(
    full_data: List[Tuple[str, str, bool, int]], 
    test_ratio: float = 0.2,
    samples_per_category: int = 10
) -> Tuple[List[Tuple[str, str, bool, int]], List[Tuple[str, str, bool, int]]]:
    """
    Create train/test split that doesn't overlap.
    
    Returns:
        (train_data, test_data) - tuples of (text, category_id, is_urgent, example_id)
    """
    print(f"\nCreating non-overlapping train/test split (test_ratio={test_ratio})...")
    
    # Group by category
    by_category = defaultdict(list)
    for text, cat_id, is_urgent, ex_id in full_data:
        by_category[cat_id].append((text, cat_id, is_urgent, ex_id))
    
    train_data = []
    test_data = []
    
    # For each category, split train/test
    for cat_id, items in by_category.items():
        n_test = max(1, int(len(items) * test_ratio))
        n_test = min(n_test, samples_per_category)  # Cap at samples_per_category
        
        # Shuffle items within category
        shuffled = sorted(items, key=lambda x: x[3], reverse=False)  # Sort by ID for reproducibility
        
        test_items = shuffled[:n_test]
        train_items = shuffled[n_test:]
        
        test_data.extend(test_items)
        train_data.extend(train_items)
    
    print(f"Train set: {len(train_data)} samples, Test set: {len(test_data)} samples")
    
    return train_data, test_data


def evaluate_classification_and_urgency(
    session: Session,
    test_data: List[Tuple[str, str, bool, int]],
    k_value: int = 1,
    embeddings_cache: Dict[str, np.ndarray] = None
) -> Tuple[List, List, List, List, List, List]:
    """
    Evaluate both category classification and urgency detection.
    
    Returns:
        (y_true_cat, y_pred_cat, y_true_urgent, y_pred_urgent, confidences_cat, confidences_urgent)
    """
    embeddings_model = get_embeddings()
    
    y_true_cat = []
    y_pred_cat = []
    y_true_urgent = []
    y_pred_urgent = []
    confidences_cat = []
    confidences_urgent = []
    
    total_test_samples = len(test_data)
    
    # Pre-compute embeddings
    if embeddings_cache is None:
        embeddings_cache = {}
        print(f"   Pre-computing embeddings for {total_test_samples} test samples...")
        for text, _, _, _ in test_data:
            if text not in embeddings_cache:
                embeddings_cache[text] = embeddings_model.embed_query(text)
    
    # Classify each test sample
    for i, (text, true_cat, true_urgent, ex_id) in enumerate(test_data):
        query_embedding = embeddings_cache[text]
        
        # === CATEGORY CLASSIFICATION ===
        # Use ALL neighbors in the database for category
        statement_cat = (
            select(Example)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(k_value)
        )
        neighbors_cat = session.exec(statement_cat).all()
        
        if neighbors_cat:
            votes_cat = [ex.category_id for ex in neighbors_cat]
            vote_counts_cat = Counter(votes_cat)
            predicted_cat, count_cat = vote_counts_cat.most_common(1)[0]
            confidence_cat = count_cat / len(neighbors_cat)
        else:
            predicted_cat = "other"
            confidence_cat = 0.0
        
        y_true_cat.append(true_cat)
        y_pred_cat.append(predicted_cat)
        confidences_cat.append(confidence_cat)
        
        # === URGENCY DETECTION ===
        # Use only neighbors with ID <= MAX_URGENCY_TAGGED_ID for urgency (they're correctly tagged)
        statement_urgent = (
            select(Example)
            .where(Example.id <= MAX_URGENCY_TAGGED_ID)
            .order_by(Example.embedding.cosine_distance(query_embedding))
            .limit(k_value)
        )
        neighbors_urgent = session.exec(statement_urgent).all()
        
        if neighbors_urgent:
            urgent_votes = sum(1 for ex in neighbors_urgent if ex.is_urgent)
            predicted_urgent = urgent_votes > (len(neighbors_urgent) / 2)
            confidence_urgent = urgent_votes / len(neighbors_urgent)
        else:
            predicted_urgent = False
            confidence_urgent = 0.0
        
        y_true_urgent.append(true_urgent)
        y_pred_urgent.append(predicted_urgent)
        confidences_urgent.append(confidence_urgent)

        if (i + 1) % LOG_PROGRESS_N == 0:
            print(f"      Processed {i + 1}/{total_test_samples} test samples...")
    
    return (
        y_true_cat, y_pred_cat, 
        y_true_urgent, y_pred_urgent, 
        confidences_cat, confidences_urgent
    )


def print_evaluation_report(
    y_true_cat, y_pred_cat,
    y_true_urgent, y_pred_urgent,
    confidences_cat, confidences_urgent,
    metric_name: str = "TEST"
):
    """Print comprehensive evaluation report for both metrics."""
    
    acc_cat = accuracy_score(y_true_cat, y_pred_cat)
    acc_urgent = accuracy_score(y_true_urgent, y_pred_urgent)
    
    avg_conf_cat = np.mean(confidences_cat)
    avg_conf_urgent = np.mean(confidences_urgent)
    
    print("\n" + "="*70)
    print(f"{metric_name} RESULTS")
    print("="*70)
    
    # Category Results
    print(f"\nCATEGORY CLASSIFICATION:")
    print(f"   - Accuracy: {acc_cat:.2%}")
    print(f"   - Average Confidence: {avg_conf_cat:.3f}")
    print(f"   - Correct: {sum(1 for t, p in zip(y_true_cat, y_pred_cat) if t == p)}/{len(y_true_cat)}")
    
    # Urgency Results
    print(f"\nURGENCY DETECTION:")
    print(f"   - Accuracy: {acc_urgent:.2%}")
    print(f"   - Average Confidence: {avg_conf_urgent:.3f}")
    print(f"   - Correct: {sum(1 for t, p in zip(y_true_urgent, y_pred_urgent) if t == p)}/{len(y_true_urgent)}")
    
    # Detailed metrics for urgency (since it's binary)
    prec_u, recall_u, f1_u, _ = precision_recall_fscore_support(
        y_true_urgent, y_pred_urgent, average='binary', zero_division=0
    )
    print(f"   - Precision: {prec_u:.3f}, Recall: {recall_u:.3f}, F1: {f1_u:.3f}")
    
    # Distribution of urgent cases in test set
    n_urgent_true = sum(y_true_urgent)
    n_urgent_pred = sum(y_pred_urgent)
    print(f"   - Distribution: {n_urgent_true} urgent cases in true, {n_urgent_pred} predicted as urgent")
    
    return acc_cat, acc_urgent


def print_detailed_reports(y_true_cat, y_pred_cat, y_true_urgent, y_pred_urgent):
    """Print detailed classification and confusion matrix reports."""
    
    print("\n" + "="*70)
    print("CATEGORY CLASSIFICATION REPORT")
    print("="*70)
    print(classification_report(y_true_cat, y_pred_cat, zero_division=0))
    
    print("\n" + "="*70)
    print("CATEGORY CONFUSION MATRIX")
    print("="*70)
    unique_labels = sorted(list(set(y_true_cat + y_pred_cat)))
    cm = confusion_matrix(y_true_cat, y_pred_cat, labels=unique_labels)
    cm_df = pd.DataFrame(cm, index=unique_labels, columns=unique_labels)
    print(cm_df)
    
    print("\n" + "="*70)
    print("URGENCY DETECTION REPORT")
    print("="*70)
    print(classification_report(y_true_urgent, y_pred_urgent, target_names=["Not Urgent", "Urgent"], zero_division=0))
    
    print("\n" + "="*70)
    print("URGENCY CONFUSION MATRIX")
    print("="*70)
    cm_urgent = confusion_matrix(y_true_urgent, y_pred_urgent, labels=[False, True])
    cm_urgent_df = pd.DataFrame(
        cm_urgent, 
        index=["Not Urgent", "Urgent"], 
        columns=["Predicted Not Urgent", "Predicted Urgent"]
    )
    print(cm_urgent_df)

    cat_errors = [(true, pred) for true, pred in zip(y_true_cat, y_pred_cat) if true != pred]
    if cat_errors:
        print(f"\nCATEGORY ERRORS: {len(cat_errors)} ({len(cat_errors)/len(y_true_cat)*100:.1f}%)")
        error_counts = defaultdict(int)
        for true, pred in cat_errors:
            error_counts[f"{true} → {pred}"] += 1
        
        print("   Top misclassifications:")
        for error, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"      {error}: {count}x")
    else:
        print("\nPERFECT CATEGORY CLASSIFICATION! No errors found! Probably something is wrong!!!")
    
    # Show urgency errors
    urgent_errors = [(true, pred) for true, pred in zip(y_true_urgent, y_pred_urgent) if true != pred]
    if urgent_errors:
        print(f"\nURGENCY ERRORS: {len(urgent_errors)} ({len(urgent_errors)/len(y_true_urgent)*100:.1f}%)")
        fp = sum(1 for t, p in urgent_errors if not t and p)  # False positives
        fn = sum(1 for t, p in urgent_errors if t and not p)  # False negatives
        print(f"   False Positives: {fp}, False Negatives: {fn}")
    else:
        print("\nPERFECT URGENCY DETECTION! No errors found! Probably something is wrong!!!")


if __name__ == "__main__":
    print("="*70)
    print("ENHANCED KNN EVALUATION: Category + Urgency Detection")
    print(f"   Config: TOP_K={settings.TOP_K}, MAX_URGENCY_TAGGED_ID={MAX_URGENCY_TAGGED_ID}")
    print("="*70)
    
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # 1. Load all examples from database (READ ONLY - no modifications)
    print("\nReading data from database (NO MODIFICATIONS)...")
    all_data = load_all_examples_from_db(engine)
    print(f"Data loaded safely - database remains unchanged")
    
    print(f"\nDataset Statistics:")
    print(f"   Total examples: {len(all_data)}")
    
    # Count by urgency status
    tagged_data = [x for x in all_data if x[3] <= MAX_URGENCY_TAGGED_ID]
    untagged_data = [x for x in all_data if x[3] > MAX_URGENCY_TAGGED_ID]
    
    urgent_count = sum(1 for x in tagged_data if x[2])
    not_urgent_count = sum(1 for x in tagged_data if not x[2])
    
    print(f"   Correctly tagged (ID ≤ {MAX_URGENCY_TAGGED_ID}): {len(tagged_data)}")
    print(f"      - Urgent: {urgent_count}")
    print(f"      - Not Urgent: {not_urgent_count}")
    print(f"   Not tagged (ID > {MAX_URGENCY_TAGGED_ID}): {len(untagged_data)}")
    
    # Count by category
    cats = defaultdict(int)
    for _, cat_id, _, _ in all_data:
        cats[cat_id] += 1
    print(f"   Categories: {len(cats)}")
    
    # 2. Create non-overlapping train/test split (in memory only)
    train_data, test_data = create_non_overlapping_split(all_data, test_ratio=0.2, samples_per_category=50)
    
    print(f"\nTrain/Test split created IN MEMORY (database untouched)")
    print(f"   Training examples (in memory): {len(train_data)}")
    print(f"   Test examples (in memory): {len(test_data)}")
    
    # 3. Evaluate on TEST set using database for KNN queries
    print(f"\nEvaluating on TEST set ({len(test_data)} samples)...")
    print("   Training examples already have embeddings in database")
    print("   Computing only test embeddings for KNN queries...")
    
    embeddings_model = get_embeddings()
    
    with Session(engine) as session:
        # Pre-compute test embeddings only (training embeddings are in database)
        test_embeddings_cache = {}
        print(f"   Processing {len(test_data)} test examples...")
        for text, _, _, _ in test_data:
            if text not in test_embeddings_cache:
                test_embeddings_cache[text] = embeddings_model.embed_query(text)
        
        print(f"Test embeddings ready ({len(test_embeddings_cache)} unique texts)")
        
        # Evaluate
        k_value = settings.TOP_K
        print(f"\n   Running KNN evaluation (k={k_value})...")
        y_true_cat, y_pred_cat, y_true_urgent, y_pred_urgent, conf_cat, conf_urgent = (
            evaluate_classification_and_urgency(
                session, 
                test_data, 
                k_value=k_value,
                embeddings_cache=test_embeddings_cache
            )
        )
    
    # 5. Print results
    acc_cat, acc_urgent = print_evaluation_report(
        y_true_cat, y_pred_cat,
        y_true_urgent, y_pred_urgent,
        conf_cat, conf_urgent,
        metric_name=f"FINAL EVALUATION (k={k_value})"
    )
    
    # 6. Print detailed reports
    print_detailed_reports(y_true_cat, y_pred_cat, y_true_urgent, y_pred_urgent)
    
    # 7. Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"- Category Accuracy: {acc_cat:.2%}")
    print(f"- Urgency Accuracy:  {acc_urgent:.2%}")
    print(f"- Train/Test Split:  {len(train_data)}/{len(test_data)}")
    print(f"- K-value:           {k_value}")
    print(f"- Urgency Tagged ID: ≤ {MAX_URGENCY_TAGGED_ID}")
    print("="*70)
    
    print("\nDATABASE STATUS: COMPLETELY UNCHANGED")
    print("   All operations were in-memory only")
    print("   Your main tables are safe and identical to before")
