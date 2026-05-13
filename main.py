import sys
from src.textsummarizer.exception import TextSummarizerException
from src.textsummarizer.logging import logger
from src.textsummarizer.pipeline.dataingestionpipeline import DataIngestionTrainingPipeline
from src.textsummarizer.pipeline.datatransformationpipeline import DataTransformationTrainigPipeline


STAGE_NAME="Data Ingestion"

try:
    logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
    obj = DataIngestionTrainingPipeline()
    obj.initiate_data_ingestion()
    logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
    raise TextSummarizerException(e, sys)

STAGE_NAME="Data Transformation"

try:
    logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
    obj = DataTransformationTrainigPipeline()
    obj.initiate_data_transformation()
    logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
    raise TextSummarizerException(e, sys)