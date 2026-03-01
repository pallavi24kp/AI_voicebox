from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import json

MODEL_PATH = "models/final_model"

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

with open("models/label_mapping.json", "r") as f:
    label_mapping = json.load(f)

id2label = {int(v): k for k, v in label_mapping.items()}

def predict_intent(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    confidence, predicted_class = torch.max(probs, dim=1)

    return {
        "intent": id2label[predicted_class.item()],
        "confidence": round(confidence.item(), 3)
    }