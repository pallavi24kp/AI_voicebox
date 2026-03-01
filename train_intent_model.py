import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

# Load dataset
df = pd.read_csv("data/intent_dataset.csv")

# Encode labels
label2id = {label: idx for idx, label in enumerate(df["intent"].unique())}
id2label = {idx: label for label, idx in label2id.items()}
df["label"] = df["intent"].map(label2id)

# Train-test split
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

# Load tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

# Tokenize
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True)

# Convert to HuggingFace Dataset
train_dataset = Dataset.from_dict({
    "input_ids": train_encodings["input_ids"],
    "attention_mask": train_encodings["attention_mask"],
    "labels": list(train_labels)
})

test_dataset = Dataset.from_dict({
    "input_ids": test_encodings["input_ids"],
    "attention_mask": test_encodings["attention_mask"],
    "labels": list(test_labels)
})

# Load model
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label2id)
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./models",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_steps=10,
    save_strategy="epoch"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Train
trainer.train()

# Evaluate
predictions = trainer.predict(test_dataset)
preds = torch.argmax(torch.tensor(predictions.predictions), dim=1)

print("\nClassification Report:\n")
print(classification_report(test_labels, preds, target_names=label2id.keys()))

# Confusion Matrix
cm = confusion_matrix(test_labels, preds)
plt.figure(figsize=(10,8))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=label2id.keys(), yticklabels=label2id.keys())
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.savefig("evaluation/confusion_matrix.png")
plt.close()

print("\nModel training complete. Confusion matrix saved in evaluation folder.")


import json

with open("models/label_mapping.json", "w") as f:
    json.dump(label2id, f)

trainer.save_model("models/final_model")
tokenizer.save_pretrained("models/final_model")
print("Model and label mapping saved successfully.")