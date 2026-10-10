# MoveInSync ML Model Details

## 1. Objective
The goal of this Machine Learning model is to perform **automated severity triage** on raw text feedback (such as app reviews, support tickets, or in-app feedback). Specifically, the model predicts whether a given text corresponds to a **low-star experience (1 or 2 stars)**, which allows the product and operations teams to automatically flag and escalate severe issues before they escalate.

## 2. Methodology & Pipeline

**Algorithm:** Logistic Regression with balanced class weights.
**Feature Engineering:** TF-IDF (Term Frequency-Inverse Document Frequency) Vectorization.

### Pipeline Steps:
1. **Text Preprocessing:** 
   - Converting to lowercase.
   - Removing URLs, punctuation, and non-alphabetic characters.
   - Stripping excess whitespace.
2. **Vectorization:** 
   - `TfidfVectorizer` extracting unigrams and bigrams (`ngram_range=(1, 2)`).
   - Constrained to the top 3,000 features (`max_features=3000`).
   - Discarding common English stopwords.
3. **Classification:**
   - `LogisticRegression` using `class_weight='balanced'` to account for any class imbalance between low-star and high-star reviews.

## 3. Data Splits
- **Training Set:** 80% of the dataset, stratified to maintain the class distribution.
- **Leakage Prevention:** Identical review texts (e.g., "Good", "Worst app") are dropped before the Train/Test split to ensure that no duplicate texts cross the training and testing boundaries, guaranteeing a clean evaluation.
- **Test Set:** 20% of the dataset, held out entirely during training to ensure unbiased evaluation metrics.

## 4. Evaluation Metrics (Test Set)
- **ROC-AUC Score:** ~0.908 (indicating excellent separability between the classes)
- **F1-Macro Score:** ~0.839 (a robust metric for imbalanced datasets, confirming the model handles both classes well)
- The model is well-calibrated, with confidence distributions heavily skewed toward 0.0 (high-star) and 1.0 (low-star) for actual matching labels.

## 5. Feature Importance (Coefficients)
Because we used Logistic Regression, the model is highly interpretable. By inspecting the coefficients assigned to each TF-IDF feature:

**Top Predictors for Low-Star (Negative Signal):**
- "worst", "pathetic", "useless", "gps", "otp", "crash", "late", "driver"
- These words strongly push the prediction towards a 1 or 2 star classification.

**Top Predictors for High-Star (Positive Signal):**
- "good", "nice", "awesome", "best", "excellent", "easy", "smooth"
- These words strongly push the prediction towards a 3, 4, or 5 star classification.

## 6. Implementation & Live Inference
The model is serialized using `joblib` into `models/low_star_classifier.pkl` alongside its metadata in `models/model_metadata.json`.

In the Streamlit Dashboard (`pages/4_ML_Model.py`), this `.pkl` file is loaded into a live inference engine. Users can paste in free-form text, and the dashboard runs the exact preprocessing and inference pipeline to return a confidence gauge showing the exact probability `P(Low-Star)`.
