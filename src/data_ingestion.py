import os
import zipfile
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml
from config.paths_config import *

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"DataIngestion initialized with bucket: {self.bucket_name}, file: {self.file_name}")

    def download_and_extract_zip_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)

            zip_file_path = os.path.join(RAW_DIR, self.file_name)
            blob.download_to_filename(zip_file_path)

            logger.info(f"Zip file downloaded from GCP bucket {self.bucket_name} to {zip_file_path}")

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(RAW_DIR)
                logger.info(f"Extracted zip file to {RAW_DIR}")

            os.remove(zip_file_path) 
            logger.info(f"Removed zip file {zip_file_path} after extraction")
        except Exception as e:
            logger.error(f"Error downloading zip from GCP: {str(e)}")
            raise CustomException(f"Error downloading zip from GCP: {str(e)}")


    def run(self):
        try:
            logger.info("Starting data ingestion process.")
            self.download_and_extract_zip_from_gcp()
            logger.info("Data ingestion process completed successfully.")
        except Exception as e:
            logger.error("Error in data ingestion process.")
            raise CustomException("Error in data ingestion process")
        
        finally:
            logger.info("Data ingestion process finished.")
            
if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()