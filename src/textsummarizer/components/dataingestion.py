import urllib.request as request
import zipfile
from src.textsummarizer.logging import logger
from src.textsummarizer.entity.config_entity import DataIngestionConfig
import os

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    ## Downloading the Zip file
    def download_zip(self):
        if not os.path.exists(self.config.local_data_file):
            filename, header = request.urlretrieve(
                url= self.config.source_URL,
                filename= self.config.local_data_file
            )
            logger.info(f"{filename} Downloaded! with following info: \n{header}")
        else:
            logger.info(f"File already exists")
    
    ## Extracting the Zip file
    def extract_zip(self):
        """
        zip_file_path: str
        Extracts the zip file into the data directory
        Function returns None
        """

        unzip_path = self.config.unzip_dir
        os.makedirs(unzip_path, exist_ok=True)
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_file:
            zip_file.extractall(unzip_path)