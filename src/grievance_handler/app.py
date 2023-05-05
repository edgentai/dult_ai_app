import boto3
import difflib
from src.grievance_handler.constants import *
from src.grievance_handler.scrapper_twitter import get_tweets
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Dult_Grievance_Classification")
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
        for class_name in class_list:
            identifier_key = str(datetime) + "_" + user_name + "_" + platform_name
            prompt = (
                Base_Prompt
                + user_message
                + "\n"
                + str(class_name)
                + "\nResponse Format - Text:class"
            )
            class_pred = get_model_response(prompt)[0]
            class_pred_corrected= difflib.get_close_matches(class_pred, class_name)
            if class_pred_corrected:
                class_pred_corrected = class_pred_corrected[0]
            else:
                class_pred_corrected = "Others"
            class_pred_dict[namestr(class_name, globals())[0]] = class_pred_corrected

        sub_class_list = []
        if class_pred_dict["Super_Class"] != "Others":
            sub_class_list = Sub_Class_Dictionary[class_pred_dict["Super_Class"]]
        else:
            table.put_item(
                Item={
                     "identifier_key": identifier_key,
                     "datetime": datetime,
                     "user_message": user_message,
                     "Super_Class": class_pred_dict['Super_Class'],
                     "Intent":class_pred_dict['Intent'],
                     "Sentiment":class_pred_dict['Sentiment'],
                     "Sub_Class":class_pred_dict['Sub_Class']
                })
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
        

        # sh.update_cell(counter, 1, identifier_key)
        # sh.update_cell(counter, 2, user_message)
        # for index, key in enumerate(class_pred_dict):
        #     sh.update_cell(counter, index + 3, class_pred_dict[key])

        table.put_item(
                Item={
                     "identifier_key": identifier_key,
                     "datetime": datetime,
                     "user_message": user_message,
                     "Super_Class": class_pred_dict['Super_Class'],
                     "Intent":class_pred_dict['Intent'],
                     "Sentiment":class_pred_dict['Sentiment'],
                     "Sub_Class":class_pred_dict['Sub_Class']
        })
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



# list_of_tweets =[ {
#     "datetime" : "2023.05.01",
#     "user_name" : "shubham",
#     "platform_name" : "twitter",
#     "user_message" : "I have been charged more than the issued price for a route"
# }]