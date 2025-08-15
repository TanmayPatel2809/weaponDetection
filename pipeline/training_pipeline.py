from src.data_ingestion import DataIngestion
from src.model_training import ModelTraining
from utils.common_functions import read_yaml
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import CONFIG_PATH
import sys
import os
import shutil

logger = get_logger(__name__)

def run_pipeline():
	"""Run data ingestion then model training and evaluation."""
	try:
		logger.info("Starting training pipeline")

		config = read_yaml(CONFIG_PATH)
		logger.info("Config loaded")

		data_ingestion = DataIngestion(config)
		data_ingestion.run()
		logger.info("Data ingestion completed")

		model_trainer = ModelTraining()
		model_trainer.train()
		model_trainer.evaluate()
		logger.info("Model training and evaluation completed")

		try:
			runs_dir = os.path.join(os.getcwd(), "runs")
			if os.path.isdir(runs_dir):
				shutil.rmtree(runs_dir)
				logger.info(f"Removed runs directory: {runs_dir}")
			else:
				logger.debug(f"No runs directory to remove at {runs_dir}")

			yolo_file = os.path.join(os.getcwd(), "yolo11n.pt")
			if os.path.isfile(yolo_file):
				os.remove(yolo_file)
				logger.info(f"Removed file: {yolo_file}")
			else:
				logger.debug(f"No yolo11n.pt file to remove at {yolo_file}")
		except Exception as cleanup_err:
			logger.warning(f"Cleanup failed: {cleanup_err}")

	except Exception as e:
		logger.exception("Training pipeline failed")
		raise CustomException(str(e)) from e


if __name__ == "__main__":
	try:
		run_pipeline()
	except Exception as e:
		logger.error("Exiting due to pipeline failure")
		sys.exit(1)