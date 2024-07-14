# -*- coding: utf-8 -*-
"""rating-predictor.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iYj6cSrqqKMsCGNSlorJvQGjapf0YWGK

## 1. Import Statements

---
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install transformers

import torch
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, BertModel, BertForSequenceClassification

device = 'cuda' if torch.cuda.is_available() else 'cpu'
device

"""## 2. Load the Data

---

The original code in this section is located in `bert-training.ipynb`. It is included here to make the `get_star_predictions()` function to work.
"""

from google.colab import drive
drive.mount('/content/drive')

github_url = '/content/reviews_v1_hiring_task.csv'
df = pd.read_csv(github_url)
df = df[['reviews.text', 'reviews.rating']]
df

train_dataset, test_dataset = train_test_split(df, test_size=0.2, random_state=1)
test_dataset = test_dataset.reset_index(drop=True)

"""## 3. Define the BERT Model

---

The original code in this section is located in `bert-training.ipynb`. It is included here to make the `get_star_predictions()` function to work. The output is suppressed to make the notebook easier to read.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# model = BertForSequenceClassification.from_pretrained(
#     "bert-base-uncased",
#     num_labels = len(df['reviews.rating'].unique()), # Number of unique labels for our multi-class classification problem.
#     output_attentions = False,
#     output_hidden_states = False,
# )
# model.to(device)

"""## 4. Load the Trained Model

---

Here, we load the `pytorch_model_2_epochs.bin` file, which contains the trained weights.
"""

# Load the trained model.
model.load_state_dict(torch.load('drive/My Drive/CAP 5610/pytorch_model_2_epochs.bin'))
model.eval()

"""## 5. Define the Reviews Dataset

---

The original code in this section is located in `star_prediction.ipyn`. It is included here to make the `get_star_predictions()` function to work.
"""

class ReviewsDataset(Dataset):
    def __init__(self, df, max_length=512):
        self.df = df
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.max_length = max_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # input=review, label=stars
        review = self.df.loc[idx, 'reviews.text']
        # labels are 0-indexed
        label = int(self.df.loc[idx, 'reviews.rating']) - 1

        encoded = self.tokenizer(
            review,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            return_attention_mask=True,  # Construct attention masks.
            truncation=True
        )

        input_ids = encoded['input_ids']
        attn_mask = encoded['attention_mask']

        return {
            'input_ids': torch.tensor(input_ids),
            'attn_mask': torch.tensor(attn_mask),
            'label': torch.tensor(label)
        }

"""## 6. Predict the Star Rating

---

The following code takes a string comment and returns a predicted star rating.
"""

def get_single_prediction(review, model):
  """
  Predict a star rating from a review comment.

  :comment: the string containing the review comment.
  :model: the model to be used for the prediction.
  """

  df = pd.DataFrame()
  df['reviews.text'] = [review]
  df['reviews.rating'] = ['0']

  dataset = ReviewsDataset(df)

  TEST_BATCH_SIZE = 1
  NUM_WORKERS = 1

  test_params = {'batch_size': TEST_BATCH_SIZE,
              'shuffle': True,
              'num_workers': NUM_WORKERS}

  data_loader = DataLoader(dataset, **test_params)

  total_examples = len(df)
  predictions = np.zeros([total_examples], dtype=object)

  for batch, data in enumerate(data_loader):

    input_ids = data['input_ids'].to(device)
    mask = data['attn_mask'].to(device)


    outputs = model(input_ids, mask)


    big_val, big_idx = torch.max(outputs[0].data, dim=1)
    star_predictions = (big_idx + 1).cpu().numpy()

  return star_predictions[0]

prediction = get_single_prediction("This is bad product!", model)

print(prediction)