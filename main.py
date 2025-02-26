from datasets import load_dataset
from groq import Groq
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set JSON key file path
json_key_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

# Groq API Client
client = Groq(
    api_key=os.environ.get('GROQ_API_KEY'),
)

# Load dataset
dataset = load_dataset("allenai/ai2_arc", "ARC-Challenge")

# Select first 20 questions from 'train' split
questions = dataset["train"]["question"][:3]
choices = dataset["train"]["choices"][:3]

# Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
client_gspread = gspread.authorize(credentials)

# Open spreadsheet and select worksheet
spreadsheet_name = "Gruppenarbeit Knowledge Management"
worksheet_name = "test2"
spreadsheet = client_gspread.open(spreadsheet_name)
worksheet = spreadsheet.worksheet(worksheet_name)

# Initialize response row index
row_index = 2
column_index = 2

for index, (question, choice) in enumerate(zip(questions, choices)):
    # Format choices with labels
    labeled_choices = ", ".join([f"{label}: {text}" for text, label in zip(choice["text"], choice["label"])])

    messages = [
        {"role": "user", "content": question},
        {"role": "user", "content": f"Choices: {labeled_choices}"},
        {"role": "user", "content": "Please respond with the label (A, B, C or D) of your answer. Only respond with the label and no further explanation nor any punctuation"}
    ]

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""

    print(f"Question {index+1}: {question}")
    print("Choices:", labeled_choices)
    print("Response:")
    print(response)
    print("\n")

    worksheet.update_cell(row_index, column_index, response)
    row_index += 1  # Move to the next row