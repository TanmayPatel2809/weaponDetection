import os

######################## DATA INGESTION ########################

RAW_DIR = os.path.join("artifacts", "raw")
ZIP_FILE_DIR = RAW_DIR
CONFIG_PATH = "config/config.yaml"

######################## MODEL TRAINING ########################

MODEL_PATH = os.path.join("artifacts", "models","model.pt")
DATA_CONFIG = os.path.join("artifacts", "raw", "data.yaml")

TRAIN_DIR = os.path.join(RAW_DIR, "train")
TRAIN_IMG_DIR = os.path.join(TRAIN_DIR, "images")
TRAIN_LABEL_DIR = os.path.join(TRAIN_DIR, "labels")

VAL_DIR = os.path.join(RAW_DIR, "valid")
VAL_IMG_DIR = os.path.join(VAL_DIR, "images")
VAL_LABEL_DIR = os.path.join(VAL_DIR, "labels")

TEST_DIR = os.path.join(RAW_DIR, "test")
TEST_IMG_DIR = os.path.join(TEST_DIR, "images")
TEST_LABEL_DIR = os.path.join(TEST_DIR, "labels")

UPLOAD_DIR = "uploads"
DETECT_DIR = "runs/detect"