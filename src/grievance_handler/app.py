import boto3
import pymysql
import difflib
from datetime import datetime
from datetime import timezone
from src.grievance_handler.constants import *
from src.grievance_handler.scrapper_twitter import get_tweets
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

db = pymysql.connect(
    host=aws_rds_host, user=aws_rds_username, password=aws_rds_password, db=aws_rds_db
)
cursor = db.cursor()
class_list = [Super_Class, Intent, Sentiment]

model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")


def get_model_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs)
    model_response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return model_response


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def grievance_classifier(datetime, user_name, platform_name, user_message):
    class_pred_dict = {
        "Super_Class": "",
        "Intent": "",
        "Sentiment": "",
        "Sub_Class": "",
    }
    try:
        formatted_datetime = datetime.fromisoformat(datetime[:-1]).astimezone(
            timezone.utc
        )
        formatted_datetime = formatted_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_datetime_obj = datetime.strptime(
            formatted_datetime, "%Y-%m-%d %H:%M:%S"
        )
        identifier_key = (
            str(formatted_datetime_obj) + "_" + user_name + "_" + platform_name
        )
        for class_name in class_list:
            prompt = (
                Base_Prompt
                + user_message
                + "\n"
                + str(class_name)
                + "\nResponse Format - Text:class"
            )
            class_pred = get_model_response(prompt)[0]
            class_pred_corrected = difflib.get_close_matches(class_pred, class_name)
            if class_pred_corrected:
                class_pred_corrected = class_pred_corrected[0]
            else:
                class_pred_corrected = "Others"
            class_pred_dict[namestr(class_name, globals())[0]] = class_pred_corrected

        sub_class_list = []
        if class_pred_dict["Super_Class"] != "Others":
            sub_class_list = Sub_Class_Dictionary[class_pred_dict["Super_Class"]]
        else:
            sql = (
                """ insert into dult_grievance_classification(id,Date,Intent,Sentiment,Sub_Class,Super_Class,user_message) values('%s','%s', '%s', '%s','%s','%s','%s')"""
                % (
                    identifier_key,
                    formatted_datetime_obj,
                    class_pred_dict["Intent"],
                    class_pred_dict["Sentiment"],
                    class_pred_dict["Sub_Class"],
                    class_pred_dict["Super_Class"],
                    user_message,
                )
            )
            cursor.execute(sql)
            db.commit()
            return
        sub_class_prompt = (
            Base_Prompt
            + user_message
            + "\n"
            + str(sub_class_list)
            + "\nResponse Format - Text:class"
        )
        sub_class_pred = get_model_response(sub_class_prompt)[0]
        class_pred_dict["Sub_Class"] = sub_class_pred
        print("prediction is:", class_pred_dict)

        sql = (
            """ insert into dult_grievance_classification(id,Date,Intent,Sentiment,Sub_Class,Super_Class,user_message) values('%s','%s', '%s', '%s','%s','%s','%s')"""
            % (
                identifier_key,
                formatted_datetime_obj,
                class_pred_dict["Intent"],
                class_pred_dict["Sentiment"],
                class_pred_dict["Sub_Class"],
                class_pred_dict["Super_Class"],
                user_message,
            )
        )
        cursor.execute(sql)
        db.commit()

    except Exception as e:
        print("Exception is:", e)


def start_grievance_worker():
    list_of_tweets = get_tweets()
    for data in list_of_tweets:
        datetime = data["datetime"]
        user_name = data["user_name"]
        platform_name = data["platform_name"]
        user_message = data["user_message"]
        grievance_classifier(datetime, user_name, platform_name, user_message)
