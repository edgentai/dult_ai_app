import pymysql
import difflib
from datetime import datetime
from datetime import timezone
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from src.grievance_handler.constants import *
from src.grievance_handler.scrapper_twitter import get_tweets
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


openai.api_key = "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"
db = pymysql.connect(
    host=aws_rds_host, user=aws_rds_username, password=aws_rds_password, db=aws_rds_db
)
cursor = db.cursor()
class_list = [Super_Class, Intent, Sentiment]

# model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_model_response(prompt):
    message_list = [
        {
            "role": "system",
            "content": "You are a helpful assistant that classifies a text into provided classes",
        },
        {"role": "user", "content": prompt},
    ]
    solution = openai.ChatCompletion.create(
        model=Chat_Gpt_Model_Config["model"],
        messages=message_list,
        temperature=Chat_Gpt_Model_Config["temperature"],
        top_p=Chat_Gpt_Model_Config["temperature"],
        n=Chat_Gpt_Model_Config["n"],
        stream=Chat_Gpt_Model_Config["stream"],
        stop=Chat_Gpt_Model_Config["stop"],
        max_tokens=Chat_Gpt_Model_Config["max_tokens"],
        presence_penalty=Chat_Gpt_Model_Config["presence_penalty"],
        frequency_penalty=Chat_Gpt_Model_Config["frequency_penalty"],
    )
    chatgpt_response = solution["choices"][0]["message"]["content"]
    return chatgpt_response

# def get_model_response(prompt):
#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(**inputs)
#     model_response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
#     return model_response


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def grievance_classifier(datetime_value, user_name, platform_name, user_message):
    class_pred_dict = {
        "Super_Class": "",
        "Intent": "",
        "Sentiment": "",
        "Sub_Class": "",
    }
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
        for class_name in class_list:
            # prompt = (
            #     Base_Prompt
            #     + user_message
            #     + "\n"
            #     + str(class_name)
            #     + "\nResponse Format - Text:class"
            # )
            # class_pred = get_model_response(prompt)[0]
            # class_pred_corrected = difflib.get_close_matches(class_pred, class_name)
            # if class_pred_corrected:
            #     class_pred_corrected = class_pred_corrected[0]
            # else:
            #     class_pred_corrected = "Others"
            # class_pred_dict[namestr(class_name, globals())[0]] = class_pred_corrected
            prompt = (
                Base_Prompt
                + user_message
                + "\n"
                + str(class_name)
                + "\nResponse Format - class"
            )
            class_pred = get_model_response(prompt)
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
        sub_class_pred = get_model_response(sub_class_prompt)
        subclass_pred_corrected = difflib.get_close_matches(sub_class_pred, sub_class_list)
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


def start_grievance_worker():
    list_of_tweets = get_tweets()
    for data in list_of_tweets:
        datetime_value = data["datetime"]
        user_name = data["user_name"]
        platform_name = data["platform_name"]
        user_message = data["user_message"]
        grievance_classifier(datetime_value, user_name, platform_name, user_message)
