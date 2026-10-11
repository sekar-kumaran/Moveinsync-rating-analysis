# MoveInSync ML Model Details

## 1. Objective
The goal of this Machine Learning model is to perform **automated severity triage** on raw review text from Google Play Store. Specifically, the model predicts whether a given text corresponds to a **low-star experience (1 or 2 stars)** vs. 3–5 stars. 

*Note on Domain Scope:* The model is trained and evaluated exclusively on public Play Store reviews for `com.moveinsync.ets`. It has not been validated on internal enterprise support tickets, HR complaints, or other operational communication channels. Furthermore, it identifies correlational textual symptoms rather than confirmed internal root causes.

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
- **Training Set:** 80% of the deduplicated text dataset (6,392 reviews), stratified by class label.
- **Leakage Prevention:** Identical review texts (2,115 duplicate normalized-text occurrences beyond the first copy) are removed prior to the Train/Test split so that no exact text spans both partitions.
- **Test Set:** 20% held-out reviews (1,599 reviews), strictly isolated to ensure unbiased evaluation.

## 4. Evaluation Metrics (Held-Out Test Set)
- **ROC-AUC Score:** 0.909 (strong discriminative ability on Play Store review text)
- **F1-Macro Score:** 0.843 (substantially outperforms the majority-class baseline F1 of 0.335)
- **F1 (Low-Star Class):** 0.850 (Precision: 0.823, Recall: 0.879)
- **Calibration Status:** Model outputs are raw sigmoid scores from logistic regression and are **not calibrated probabilities**. They represent relative ranking scores rather than verified statistical confidence.

## 5. Feature Importance (Coefficients)
Because we used Logistic Regression, the model is highly interpretable. By inspecting the coefficients assigned to each TF-IDF feature:

**Top Predictors for Low-Star (Negative Signal):**
- "worst", "pathetic", "useless", "gps", "otp", "crash", "late", "driver"
- These words strongly push the prediction towards a 1 or 2 star classification.

**Top Predictors for High-Star (Positive Signal):**
- "good", "nice", "awesome", "best", "excellent", "easy", "smooth"
- These words strongly push the prediction towards a 3, 4, or 5 star classification.

## 6. Implementation & Live Inference
The model is serialized using `joblib` into `models/low_star_classifier.pkl` alongside its evaluation metadata in `models/model_metadata.json` and `data/processed/metrics.json`.

In the Streamlit Dashboard (`pages/4_ML_Model.py`), this `.pkl` file is loaded into a live inference engine. Users can test review text, and the dashboard runs the identical preprocessing and inference pipeline to output a severity signal and a model score gauge (with an explicit disclaimer that scores are not calibrated probabilities).
