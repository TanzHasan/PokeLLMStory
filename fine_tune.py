import openai

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
       return infile.read()

def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

import os
openai.api_key = os.environ["OPENAI_API_KEY"]

with open("finetune.json", "rb") as file:
    response = openai.File.create(
        file = file,
        purpose = 'fine-tune'
    )
file_id = response['id']
print(f"file uploaded successfully with id: {file_id}")