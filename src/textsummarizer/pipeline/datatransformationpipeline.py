import sys
from src.textsummarizer.logging import logger
from src.textsummarizer.exception import TextSummarizerException
from src.textsummarizer.config.configuration import ConfigurationManager
from src.textsummarizer.components.datatransformation import DataTransformation

class DataTransformationTrainigPipeline:
    def __init__(self) -> None:
        pass

    def initiate_data_transformation(self):
        try:
            config = ConfigurationManager()
            data_transformation_config = config.get_data_transformation_config()
            data_transformation = DataTransformation(config= data_transformation_config)
            data_transformation.convert()
        except Exception as e:
            raise TextSummarizerException(e, sys)