Super_Class = [
    "PASS/Reserved Seat Issue",
    "Ticket Related Issue",
    "Vehicle Related Issue",
    "Crew Behaviors",
    "Route",
    "Facility Issue",
    "Website/App Related Issue",
    "Others",
]

Sub_Class_Dictionary = {
    "PASS/Reserved Seat Issue": [
        "Wrong Date/Day/Month in  Pass Issued",
        "Physically challenged pass/Reserved seat issue",
        "Student pass",
        "Gender Miss Punch",
        "Senior citizen pass issue/ Seat Issue/concession ticket",
        "Smart Card",
        "Tummoc/app based passes",
    ],
    "Ticket Related Issue": [
        "Re-Issued",
        "Ticket printing issue",
        "Ticket not issued",
        "Change Due",
        "Checking Issue",
        "Q R  code issue",
    ],
    "Vehicle Related Issue": [
        "Digital and Manual board Issue",
        "Vehicle Defect",
        "Break Down",
        "Emission OF Smoke",
        "Pathetic Seats",
        "Display Of  Advertisement",
        "Cleanliness Of vehicle",
        "A/C   Issue",
    ],
    "Crew Behaviors": [
        "Rash Driving",
        "Signal jump/violations",
        "Crew misbehavior",
        "Harassment",
        "Women issue",
        "Assault",
        "Mobile usage while driving",
        "Drink And Drive",
        "Accident",
    ],
    "Route": [
        "Irregular operation",
        "Partial Trip",
        "Route deviation",
        "Delay departure",
        "Stopping more than mins in  Bus stops",
        "Non stoppage of buses in scheduled bus stops",
        "Trip Miss",
    ],
    "Facility Issue": [
        "Baggage loss",
        "Shanthinagar TTMC",
        "Jayanagar TTMC",
        "Kengeri TTMC",
        "Banashankari TTMC",
        "Koramangala TTMC",
        "Yeshawanthapura TTMC",
        "Vijayanagar TTMC",
        "Domlur TTMC",
        "Whitefield TTMC",
        "Bannerghatta TTMC",
        "Kempegowda Bus Station TTMC",
        "Shivajinagar TTMC",
    ],
    "Website/App Related Issue": ["Website Related Complaints", "Mobile app related"],
}

Intent = ["Urgnet Actionable", "Appeal"]

Sentiment = ["Positive", "Negative", "Neutral"]

# Chat_Gpt_Model_Config = {
#     "model": "gpt-3.5-turbo",
#     "temperature": 0.7,
#     "top_p": 1,
#     "n": 1,
#     "stream": False,
#     "stop": None,
#     "presence_penalty": 0,
#     "frequency_penalty": 0,
#     "max_tokens": 32,
# }

Base_Prompt = "Given the text classify among the classes given in the list\n"

twitter_scrapper_scroller = 5

twitter_email_id = "dhirajdddaga@gmail.com"
twitter_login_id = "dhirajdddaga"
twitter_password = "Putin_lodu"
aws_rds_host = "dult-database.cndfa7fhtn3n.us-east-1.rds.amazonaws.com"
aws_rds_username = "admin"
aws_rds_password = "dult__2023"
aws_rds_db = "kTestDb"
