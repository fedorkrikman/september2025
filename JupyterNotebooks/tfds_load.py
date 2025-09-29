import os
print(os.environ.get("TFDS_DATA_DIR"))
import tensorflow_datasets as tfds
print("Resolved:", tfds.core.constants.DATA_DIR)
ds = tfds.load("cifar10", split="train[:1%]")