import pandas as pd
from typing import Dict, Any
from .preprocessing import clean_text
from .model_loader import get_model_and_metadata

def predict_low_star(review_text: str) -> Dict[str, Any]:
    """
    Given a review text, cleans it and predicts whether it is a low-star review (1-2 stars).
    Returns a dictionary with the prediction, confidence, and status.
    """
    if not review_text or not review_text.strip():
        return {"error": "Empty review text provided.", "is_low_star": None}
        
    model, metadata = get_model_and_metadata()
    if model is None:
        return {"error": "Model artifact not found. Please run the ML notebook.", "is_low_star": None}
        
    cleaned = clean_text(review_text)
    if len(cleaned) < 5:
        return {"error": "Text too short to predict reliably.", "is_low_star": None}
        
    try:
        pred = model.predict([cleaned])[0]
        prob = model.predict_proba([cleaned])[0]
        
        # Binary prediction interpretation
        is_low_star = bool(pred == 1)
        confidence = float(prob[1] if is_low_star else prob[0])
        
        return {
            "is_low_star": is_low_star,
            "confidence": confidence,
            "explanation": f"The model is {confidence*100:.1f}% confident this is a {'LOW-STAR (1-2)' if is_low_star else 'NOT LOW-STAR (3-5)'} review.",
            "error": None
        }
    except Exception as e:
        return {"error": f"Inference failed: {str(e)}", "is_low_star": None}
