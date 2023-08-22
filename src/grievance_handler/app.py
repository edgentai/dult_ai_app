import pymysql
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from src.grievance_handler.utils import download_from_s3, grievance_classifier
from src.grievance_handler.scrapper_twitter import get_tweets
from src.grievance_handler.constants import (
    s3_bucket_name,
    remote_dir_name,
    model_path,
    aws_rds_db,
    aws_rds_host,
    aws_rds_password,
    aws_rds_username,
)

db = pymysql.connect(
    host=aws_rds_host, user=aws_rds_username, password=aws_rds_password, db=aws_rds_db
)


def start_grievance_worker():
    # download_from_s3(s3_bucket_name, remote_dir_name, model_path)
    # model_classifier_path = os.path.join(os.getcwd(), model_path, remote_dir_name)
    # model = AutoModelForSeq2SeqLM.from_pretrained(model_classifier_path)
    # tokenizer = AutoTokenizer.from_pretrained(model_classifier_path)
    list_of_tweets = get_tweets()

    for data in list_of_tweets:
        datetime_value = data["created_at"][:10]
        user_name = data["author_id"]
        platform_name = data.get("platform_name", "twitter")
        user_message = data["text"]
        grievance_classifier(
            datetime_value, user_name, platform_name, user_message, db
        )
