import sys
from src.textsummarizer.exception import TextSummarizerException
from src.textsummarizer.logging import logger
from src.textsummarizer.pipeline.dataingestionpipeline import DataIngestionTrainingPipeline
from src.textsummarizer.pipeline.datatransformationpipeline import DataTransformationTrainigPipeline
from src.textsummarizer.pipeline.modeltrainerpipeline import ModelTrainerTrainingPipeline
from src.textsummarizer.pipeline.modelevaluationpipeline import ModelEvaluationTrainingPipeline


STAGE_NAME="Data Ingestion Stage"

try:
    logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
    obj = DataIngestionTrainingPipeline()
    obj.initiate_data_ingestion()
    logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
    raise TextSummarizerException(e, sys)

STAGE_NAME="Data Transformation Stage"

try:
    logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
    obj = DataTransformationTrainigPipeline()
    obj.initiate_data_transformation()
    logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
    raise TextSummarizerException(e, sys)


STAGE_NAME="Model Trainer stage"

try:
    logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
    model_trainer_pipeline=ModelTrainerTrainingPipeline()
    model_trainer_pipeline.initiate_model_trainer()
    logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
    logger.exception(e)
    raise TextSummarizerException(e, sys)

STAGE_NAME = "Model Evaluation stage"
try: 
   logger.info(f"*******************")
   logger.info(f"----------------------- Stage : {STAGE_NAME} Started -----------------------")
   model_evaluation = ModelEvaluationTrainingPipeline()
   model_evaluation.initiate_model_evaluation()
   logger.info(f"----------------------- Stage : {STAGE_NAME} Completed -----------------------")
except Exception as e:
        logger.exception(e)
        raise TextSummarizerException(e, sys)