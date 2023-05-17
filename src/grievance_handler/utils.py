from boto3.s3.transfer import TransferConfig
import difflib
import boto3
from tenacity import retry, stop_after_attempt, wait_random_exponential
from datetime import datetime
from datetime import timezone

from src.grievance_handler.constants import (
    Super_Class,
    Intent,
    Sentiment,
    Base_Prompt,
    Sub_Class_Dictionary,
)


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def download_from_s3(bucket_name: str, remote_dir_name: str, model_path: str):
    GB = 1024**3
    config = TransferConfig(multipart_threshold=10 * GB)
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)
    PATH = os.getcwd()
    tc_model_path = os.path.join(PATH, model_path)
    for obj in bucket.objects.filter(Prefix=remote_dir_name):
        download_path = tc_model_path + "/" + obj.key
        bucket.download_file(obj.key, download_path, Config=config)


def get_model_response(prompt, tokenizer, model):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs)
    model_response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return model_response


def grievance_classifier(
    datetime_value, user_name, platform_name, user_message, db, model, tokenizer
):
    class_pred_dict = {
        "Super_Class": "",
        "Intent": "",
        "Sentiment": "",
        "Sub_Class": "",
    }
    cursor = db.cursor()
    try:
        formatted_datetime = datetime.fromisoformat(datetime_value[:-1]).astimezone(
            timezone.utc
        )
        formatted_datetime = formatted_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_datetime_obj = datetime.strptime(
            formatted_datetime, "%Y-%m-%d %H:%M:%S"
        )
        identifier_key = (
            str(formatted_datetime_obj) + "_" + user_name + "_" + platform_name
        )
        class_list = [Super_Class, Intent, Sentiment]
        for class_name in class_list:
            prompt = (
                Base_Prompt
                + user_message
                + "\n"
                + str(class_name)
                + "\nResponse Format - class"
            )
            class_pred = get_model_response(prompt, tokenizer, model)
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
            + "\nResponse Format - class"
        )
        # sub_class_pred = get_model_response(sub_class_prompt)[0]
        sub_class_pred = get_model_response(sub_class_prompt, tokenizer, model)
        subclass_pred_corrected = difflib.get_close_matches(
            sub_class_pred, sub_class_list
        )
        if subclass_pred_corrected:
            subclass_pred_corrected = subclass_pred_corrected[0]
        else:
            subclass_pred_corrected = "Others"
        class_pred_dict["Sub_Class"] = subclass_pred_corrected
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
