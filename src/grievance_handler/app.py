import boto3
from src.grievance_handler.constants import *
# from gsheet_util import sh, counter
# import pickle
from src.grievance_handler.scrapper_twitter import get_tweets
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# openai.api_key = "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"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Dult_Grievance_Classification")
class_list = [Super_Class, Intent, Sentiment]

model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")


# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
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
        for class_name in class_list:
            prompt = (
                Base_Prompt
                + user_message
                + "\n"
                + str(class_name)
                + "\nResponse Format - Text:class"
            )
            class_pred = get_model_response(prompt)[0]
            class_pred_dict[namestr(class_name, globals())[0]] = class_pred

        sub_class_list = Sub_Class_Dictionary[class_pred_dict["Super_Class"]]
        sub_class_prompt = (
            Base_Prompt
            + user_message
            + "\n"
            + str(sub_class_list)
            + "\nResponse Format - Text:class"
        )
        sub_class_pred = get_model_response(sub_class_prompt)
        class_pred_dict["Sub_Class"] = sub_class_pred
        print("prediction is:", class_pred_dict)
        identifier_key = str(datetime) + "_" + user_name + "_" + platform_name

        # sh.update_cell(counter, 1, identifier_key)
        # sh.update_cell(counter, 2, user_message)
        # for index, key in enumerate(class_pred_dict):
        #     sh.update_cell(counter, index + 3, class_pred_dict[key])

        table.put_item(
            Item={
                "identifier_key": identifier_key,
                "user_message": user_message,
                "classes": class_pred_dict,
            }
        )
    except Exception as e:
        print("Exception is:", e)


def start_grievance_worker():
    list_of_tweets = get_tweets()
    # print(len(list_of_tweets))
    # row_counter = counter
    for data in list_of_tweets:
        datetime = data["datetime"]
        user_name = data["user_name"]
        platform_name = data["platform_name"]
        user_message = data["user_message"]
        grievance_classifier(datetime, user_name, platform_name, user_message)
        # row_counter = row_counter + 1
    # counter_file = open("counter", "wb")
    # pickle.dump(row_counter, counter_file)
    # counter_file.close()
