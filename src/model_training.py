import os
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from config.model_params import MODEL_PARAMS
from ultralytics import YOLO
from ultralytics.utils.benchmarks import check_yolo
import shutil


logger = get_logger(__name__)

class ModelTraining:
    def __init__(self):
        self.train_imgs = os.listdir(TRAIN_IMG_DIR)
        self.train_labels = os.listdir(TRAIN_LABEL_DIR)

        self.val_imgs = os.listdir(VAL_IMG_DIR)
        self.val_labels = os.listdir(VAL_LABEL_DIR)

        self.test_imgs = os.listdir(TEST_IMG_DIR)
        self.test_labels = os.listdir(TEST_LABEL_DIR)

        check_yolo_result = check_yolo()
        logger.info(f"Specs: {check_yolo_result}")

        logger.info("ModelTraining initialized with training, validation, and test datasets.")

    def train(self):
        logger.info("Starting training process...")

        model = YOLO("yolo11n.pt")

        result = model.train(
            name= MODEL_PARAMS['name'],
            data=DATA_CONFIG,
            epochs=MODEL_PARAMS['epochs'],
            batch=MODEL_PARAMS['batch_size'],
            imgsz=MODEL_PARAMS['imgsz'],
            save=MODEL_PARAMS['save'],
            workers=MODEL_PARAMS['workers']

        )   
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        best_model_path = f"runs/detect/{MODEL_PARAMS['name']}/weights/best.pt"
        shutil.copy(best_model_path, os.path.join(MODEL_PATH))
        logger.info(f"Model trained and saved to {MODEL_PATH}")

    def evaluate(self):
        logger.info("Starting evaluation process...")

        model = YOLO(MODEL_PATH)

        result = model.val(data=DATA_CONFIG, split="test")

        logger.info(f"Evaluation results: {result}")


if __name__ == "__main__":
    model_training = ModelTraining()
    model_training.train()
    model_training.evaluate()