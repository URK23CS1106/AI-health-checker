import pandas as pd
import random
import os

# Core diseases with robust mock data
DISEASES = [
    {
        "Disease": "Common Cold",
        "Symptoms": ["runny nose", "sore throat", "cough", "mild fever", "sneezing", "congestion"],
        "Description": "A common viral infection of the nose and throat.",
        "Precautions": "Rest, drink plenty of fluids, wash hands often.",
        "Medications": "Paracetamol, Ibuprofen, Decongestants, Cough syrup.",
        "Doctor_Recommendation": "Consult if symptoms last more than a week or if you develop a high fever."
    },
    {
        "Disease": "Influenza (Flu)",
        "Symptoms": ["high fever", "chills", "muscle aches", "fatigue", "dry cough", "headache", "sweats"],
        "Description": "A viral infection that attacks your respiratory system.",
        "Precautions": "Strict bed rest, isolate yourself, stay hydrated.",
        "Medications": "Oseltamivir (if prescribed early), Paracetamol for fever.",
        "Doctor_Recommendation": "Consult a doctor immediately if you experience shortness of breath or persistent chest pain."
    },
    {
        "Disease": "COVID-19",
        "Symptoms": ["fever", "dry cough", "loss of taste", "loss of smell", "shortness of breath", "fatigue", "sore throat", "body aches"],
        "Description": "A highly contagious respiratory illness caused by the SARS-CoV-2 virus.",
        "Precautions": "Isolate, wear a mask, monitor oxygen levels.",
        "Medications": "Paracetamol, Vitamin C, Zinc, prescribed antivirals if severe.",
        "Doctor_Recommendation": "Seek immediate medical attention if oxygen drops below 94% or you have difficulty breathing."
    },
    {
        "Disease": "Migraine",
        "Symptoms": ["severe headache", "throbbing pain", "nausea", "sensitivity to light", "sensitivity to sound", "vomiting"],
        "Description": "A neurological condition that can cause multiple symptoms, frequently characterized by intense, debilitating headaches.",
        "Precautions": "Rest in a quiet and dark room, avoid known triggers like caffeine or stress.",
        "Medications": "Ibuprofen, Triptans (prescription), Aspirin.",
        "Doctor_Recommendation": "Consult a neurologist if migraines are frequent and severely disrupt daily life."
    },
    {
        "Disease": "Gastroenteritis (Stomach Flu)",
        "Symptoms": ["diarrhea", "vomiting", "stomach cramps", "nausea", "low-grade fever", "muscle aches"],
        "Description": "An intestinal infection marked by diarrhea, cramps, nausea, vomiting, and fever.",
        "Precautions": "Stay hydrated, eat bland foods, wash hands thoroughly.",
        "Medications": "Oral rehydration salts (ORS), Loperamide (if advised).",
        "Doctor_Recommendation": "Consult if you cannot keep liquids down for 24 hours, or if there is blood in stool."
    },
    {
        "Disease": "Allergic Rhinitis",
        "Symptoms": ["sneezing", "itchy eyes", "watery eyes", "runny nose", "itchy throat", "nasal congestion"],
        "Description": "An allergic response causing itchy, watery eyes, sneezing, and other similar symptoms.",
        "Precautions": "Avoid allergens (dust, pollen), keep indoors during high pollen seasons.",
        "Medications": "Antihistamines (Cetirizine, Loratadine), Nasal corticosteroids.",
        "Doctor_Recommendation": "Consult an allergist if symptoms are severe and unresponsive to over-the-counter medicine."
    },
    {
        "Disease": "Asthma",
        "Symptoms": ["shortness of breath", "chest tightness", "wheezing", "coughing episodes", "rapid breathing"],
        "Description": "A condition in which your airways narrow and swell and may produce extra mucus.",
        "Precautions": "Avoid triggers (smoke, strong odors), carry an inhaler always.",
        "Medications": "Bronchodilators (Albuterol inhaler), Inhaled corticosteroids.",
        "Doctor_Recommendation": "Immediate emergency care required for severe shortness of breath or if an inhaler doesn't help."
    },
    {
        "Disease": "Dengue Fever",
        "Symptoms": ["high fever", "severe headache", "pain behind eyes", "joint pain", "muscle pain", "rash", "fatigue"],
        "Description": "A mosquito-borne viral disease occurring in tropical and subtropical areas.",
        "Precautions": "Use mosquito nets, wear long sleeves, use repellents.",
        "Medications": "Paracetamol for fever. STRICTLY AVOID Aspirin or Ibuprofen.",
        "Doctor_Recommendation": "Hospitalization may be required; consult immediately if experiencing severe abdominal pain or bleeding."
    },
    {
        "Disease": "Food Poisoning",
        "Symptoms": ["nausea", "vomiting", "diarrhea", "abdominal cramps", "fever", "weakness"],
        "Description": "Illness caused by eating contaminated food.",
        "Precautions": "Rest, stay hydrated with sips of water or clear broths.",
        "Medications": "Oral rehydration salts, Bismuth subsalicylate.",
        "Doctor_Recommendation": "Consult a doctor if symptoms last more than a few days, or if you have a very high fever."
    },
    {
        "Disease": "Typhoid",
        "Symptoms": ["prolonged high fever", "weakness", "stomach pain", "headache", "loss of appetite", "rash"],
        "Description": "A bacterial infection that can lead to a high fever, diarrhea, and vomiting.",
        "Precautions": "Drink boiled or bottled water, avoid raw foods.",
        "Medications": "Antibiotics (prescription only), Paracetamol for fever.",
        "Doctor_Recommendation": "Requires immediate medical consultation for a proper antibiotic course."
    }
]

# Generate synthetic combinations to simulate varied user inputs
data = []
for _ in range(1500):
    disease_info = random.choice(DISEASES)
    # Pick a random subset of symptoms (between 2 and all symptoms)
    symptoms_subset = random.sample(disease_info["Symptoms"], k=random.randint(2, len(disease_info["Symptoms"])))
    
    # Shuffle and join them in different ways to simulate NLP inputs
    random.shuffle(symptoms_subset)
    symptoms_text = ", ".join(symptoms_subset)
    
    # Sometimes add "I have" or "feeling" for variation
    prefix_choices = ["", "I have ", "Feeling ", "Experiencing ", "Suffering from "]
    symptoms_str = random.choice(prefix_choices) + symptoms_text

    data.append({
        "Symptoms": symptoms_str.lower(),
        "Disease": disease_info["Disease"],
        "Description": disease_info["Description"],
        "Precautions": disease_info["Precautions"],
        "Medications": disease_info["Medications"],
        "Doctor_Recommendation": disease_info["Doctor_Recommendation"]
    })

df = pd.DataFrame(data)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(base_dir, 'data', 'symptom_dataset.csv')
df.to_csv(output_path, index=False)
print(f"Generated synthetic dataset with {len(df)} samples at {output_path}")
