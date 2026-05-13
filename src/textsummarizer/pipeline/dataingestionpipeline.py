from src.textsummarizer.config.configuration import ConfigurationManager
from src.textsummarizer.components.dataingestion import DataIngestion
from src.textsummarizer.exception import TextSummarizerException
import sys

class DataIngestionTrainingPipeline:
    def __init__(self) -> None:
        pass

    def initiate_data_ingestion(self):
        try:
            config = ConfigurationManager()
            data_ingestion_config = config.get_data_ingestion_config()
            data_ingestion = DataIngestion(config= data_ingestion_config)
            data_ingestion.download_zip()
            data_ingestion.extract_zip()
        except Exception as e:
            raise TextSummarizerException(e, sys)