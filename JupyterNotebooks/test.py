import sys, os, numpy as np, pandas as pd, matplotlib, seaborn as sns, PIL
import tensorflow as tf, tensorflow_datasets as tfds

###
matplotlib.rcParams['figure.figsize'] = [9, 6]
print("PY:", sys.executable)
print("TF:", tf.__version__, "| TFDS:", tfds.__version__)
print("DATA_DIR:", os.environ.get("TFDS_DATA_DIR"))