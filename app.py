#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import typing as t

import html
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# Parse a .env file and then load all the variables found as environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----
# OpenAI API Key, get yours here: https://platform.openai.com/api-keys
# -----
openai_api_key: t.Optional[str] = os.getenv("API_KEY")


# -----
# Support Functions
# -----


def regex_to_english_prompt() -> str:
    return """
You are an application that converts regular expressions (regex) into corresponding English language patterns. 
Your task is to interpret the given regular expression and provide an English language description that accurately captures its pattern.
Please provide an English language description or explanation of the pattern represented by the given regular expression.

Examples:
1. Regular expression: r'^apple\d{1,3}\b'
   Corresponding English description: "Match any word starting with 'apple' followed by a number from 1 to 3."


Given below is the regular expression entered by the user:
{prompt}
"""


def english_to_regex_prompt() -> str:
    return """
You are an application that converts English language patterns into corresponding regular expressions (regex). 
You must aims to facilitate users in translating their natural language search queries, input validations, or other pattern-based requirements into regex format efficiently.
Your task is to generate a regular expression that matches the pattern described in the user's input. 
Ensure that the regex accurately captures the specified pattern and is presented in a clear and concise format.
Please provide the regex that corresponds to the given English language pattern.

Given below is the prompt entered by the user:

{prompt}

"""


# -----
# Program
# -----
client: OpenAI = OpenAI(api_key=openai_api_key)


def ai(
    prompt: str,
    model: t.Literal["gpt-4-0125-preview", "gpt-3.5-turbo-0125"] = "gpt-3.5-turbo-0125",
) -> t.Optional[str]:
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": (prompt),
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"AI completion failed: {e}")
        return None


def english_to_regex(prompt: str, model: str) -> str:
    try:
        subbed = english_to_regex_prompt().format(prompt=html.escape(prompt))
        fixed: t.Optional[str] = ai(prompt=subbed, model=model)
        if fixed is None:
            return "Error occurred during AI completion."
        return fixed

    except Exception as e:
        logging.error(f"Custom Approach failed: {e}")
        return "An error occurred."


def regex_to_english(prompt: str, model: str) -> str:
    try:
        subbed = regex_to_english_prompt().format(prompt=html.escape(prompt))
        fixed: t.Optional[str] = ai(prompt=subbed, model=model)
        if fixed is None:
            return "Error occurred during AI completion."
        return fixed

    except Exception as e:
        logging.error(f"Custom Approach failed: {e}")
        return "An error occurred."


def main(prompt: str, option: str, model: str) -> t.Optional[str]:
    if option == "English to Regex":
        return english_to_regex(prompt=prompt, model=model)
    elif option == "Regex to English":
        return regex_to_english(prompt=prompt, model=model)
    else:
        return "Error choosing `option`"


iface: gr.Interface = gr.Interface(
    fn=main,
    inputs=[
        "text",
        gr.Radio(["English to Regex", "Regex to English"], label="Choose Action"),
        gr.Radio(["gpt-3.5-turbo-0125", "gpt-4-0125-preview"], label="Select Model"),
    ],
    outputs="text",
    title="Regex Gen",
    description="Generate regex from English and also get explanations of regex with examples using OpenAI's API",
    # examples=[[""]],
    # allow_flagging=True,
    flagging_dir="flagged",
    api_name="translate",
)
iface.launch()
