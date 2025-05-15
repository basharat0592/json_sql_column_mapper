from sentence_transformers import SentenceTransformer, InputExample, losses, models
from torch.utils.data import DataLoader

# Disable W&B Logging
import os
os.environ["WANDB_DISABLED"] = "true"

# Load base model
model = SentenceTransformer('all-MiniLM-L6-v2')

#training data for triplet loss
train_data = [
    ("JoinDate", "signup_date", "first_name"),
    ("Email", "email_address", "last_name"),
    ("enabled", "is_active", "signup_date"),
    ("PhoneNumber", "contact_number", "email_address"),
    ("CustomerId", "customer_id", "email_address"),
    ("FirstName", "first_name", "signup_date"),
    ("RefCode", "referral_code", "is_active"),
]

# Prepare InputExample objects
train_examples = [
    InputExample(texts=[anchor, positive, negative])
    for anchor, positive, negative in train_data
]

# DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Triplet loss
train_loss = losses.TripletLoss(model=model)

# Fine-tune the model
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=10,
    show_progress_bar=True
)

import pickle
from google.colab import files

# Save as pickle file
with open('json_sql_mapper.pkl', 'wb') as f:
    pickle.dump(model, f)

# Download the pickle file
files.download('fine_tuned_model.pkl')

import pickle
from sentence_transformers import util

# Load fine-tuned model from .pkl
with open("json_sql_mapper.pkl", "rb") as f:
    model = pickle.load(f)

#model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode and compare
sim = util.cos_sim(
    model.encode("JoinDate", convert_to_tensor=True),
    model.encode("first_name", convert_to_tensor=True)
)
print(sim)