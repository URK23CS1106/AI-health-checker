import joblib
import os
import numpy as np

# Global variables to cache the model & data
_model = None
_vectorizer = None
_disease_info = None

def load_artifacts():
    global _model, _vectorizer, _disease_info
    base_path = os.path.dirname(os.path.abspath(__file__))
    if _model is None:
        _model = joblib.load(os.path.join(base_path, 'model.joblib'))
    if _vectorizer is None:
        _vectorizer = joblib.load(os.path.join(base_path, 'vectorizer.joblib'))
    if _disease_info is None:
        _disease_info = joblib.load(os.path.join(base_path, 'disease_info.joblib'))

def predict_disease(symptoms_text: str, top_k: int = 3):
    load_artifacts()
    
    # Preprocess and vectorize
    X = _vectorizer.transform([symptoms_text.lower()])
    
    # Predict probabilities
    probs = _model.predict_proba(X)[0]
    classes = _model.classes_
    
    # Get top K indices
    top_indices = np.argsort(probs)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        disease = classes[idx]
        probability = float(probs[idx])
        if probability > 0.05:  # Only include if prob is decent
            info = _disease_info.get(disease, {})
            results.append({
                "disease": disease,
                "probability": probability,
                "description": info.get("Description", ""),
                "precautions": info.get("Precautions", ""),
                "medications": info.get("Medications", ""),
                "doctor_recommendation": info.get("Doctor_Recommendation", "")
            })
    
    return results

if __name__ == "__main__":
    # Test
    res = predict_disease("fever, cough, and a runny nose")
    print("Test predictions:", res)
