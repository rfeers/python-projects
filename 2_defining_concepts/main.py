import requests
import json
from transformers import pipeline

# Suppress Transformers library messages
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# API to get the definitions
url_api = "https://api.dictionaryapi.dev/api/v2/entries/en/"

# Define a function that calls an API to get the definition. 
def get_word_def(word:str): 
    try: 
        response = requests.get(url_api+word)

        data = response.json()
        meanings = data[0]["meanings"][0]["definitions"]

        meaning_list = []
        for meaning in meanings:
            meaning_list.append(meaning["definition"])
        
        combined_text = " ".join(meaning_list)

        return combined_text
    
    except:
        return "Error" 
    
# Define a function that summarizes the text if it is too long
def summarize_definition(input_text: str):
        # Generate the summary
        summary = summarizer(input_text, max_length=min(100, length), do_sample=False)
        return summary[0]['summary_text']

# Define a function that returns a definition given the user input
def get_definition(word: str):
     data = get_word_def(word)

     if data == "Error":
        return "We are sorry to say this... but this word does not exist! Please try another one."
     elif len(data) > 100: 
        return summarize_definition(word)
     else: 
         return data

# User input
word = input("Enter word: ")

# Printing the user input
print(get_definition(word))

