import os

from dotenv import load_dotenv
from huggingface_hub import login

load_dotenv()

token = os.getenv("HF_TOKEN")


login(token=token)
from datasets import load_dataset

# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("lerobot/stanford_kuka_multimodal_dataset")

# Display comprehensive dataset information
print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

# Basic dataset info
print(f"Dataset type: {type(ds)}")
print(f"Dataset keys (splits): {list(ds.keys())}")
print(f"Number of splits: {len(ds)}")
# print number of rows in train split
print(
    f"Number of samples in 'train' split: {len(ds['train']) if 'train' in ds else 'N/A'}"
)
# print column names and types
print(f"Column names and types: {ds['train'].features if 'train' in ds else 'N/A'}")
