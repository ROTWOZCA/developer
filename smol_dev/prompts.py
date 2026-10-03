import asyncio
import re
import time
import os
from typing import List, Optional, Callable, Any

from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import logging

logger = logging.getLogger(__name__)

# إعداد عميل Groq
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SMOL_DEV_SYSTEM_PROMPT = """
You are a top tier AI developer who is trying to write a program that will generate code for the user based on their intent.
Do not leave any todos, fully implement every feature requested.

When writing code, add comments to explain what you intend to do and why it aligns with the program plan and specific instructions from the original prompt.
"""


def specify_file_paths(prompt: str, plan: str, model: str = 'llama3-70b-8192'):
    completion = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": f"""{SMOL_DEV_SYSTEM_PROMPT}
      Given the prompt and the plan, return a JSON list of strings corresponding to the new files that will be generated.
      Output only the JSON array, no other text.
                  """,
            },
            {
                "role": "user",
                "content": f""" I want a: {prompt} """,
            },
            {
                "role": "user",
                "content": f""" The plan we have agreed on is: {plan} """,
            },
        ],
    )
    # استخراج الملفات من الرد
    content = completion.choices[0].message.content
    # محاولة استخراج JSON
    import json
    try:
        # البحث عن مصفوفة JSON
        match = re.search(r'\[.*?\]', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception:
        return []


def plan(prompt: str, stream_handler: Optional[Callable[[bytes], None]] = None, model: str = 'llama3-70b-8192', extra_messages: List[Any] = []):
    completion = client.chat.completions.create(
        model=model,
        temperature=0.7,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": f"""{SMOL_DEV_SYSTEM_PROMPT}

    In response to the user's prompt, write a plan using GitHub Markdown syntax. Begin with a YAML description of the new files that will be created.
  In this plan, please name and briefly describe the structure of code that will be generated, including, for each file we are generating, what variables they export, data schemas, id names of every DOM elements that javascript functions will use, message names, and function names.
                Respond only with plans following the above schema.
                  """,
            },
            {
                "role": "user",
                "content": f""" the app prompt is: {prompt} """,
            },
            *extra_messages,
        ],
    )

    collected_messages = []
    for chunk in completion:
        chunk_message_dict = chunk.choices[0]
        chunk_message = chunk_message_dict.delta
        if chunk_message_dict.finish_reason is None:
            collected_messages.append(chunk_message)
            if stream_handler:
                try:
                    if chunk_message.content:
                        stream_handler(chunk_message.content.encode("utf-8"))
                except Exception as err:
                    logger.info(f"\nstream_handler error: {err}")
                    logger.info(chunk_message)
    full_reply_content = "".join([m.content or "" for m in collected_messages])
    return full_reply_content


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
async def generate_code(prompt: str, plan: str, current_file: str, stream_handler: Optional[Callable[Any, Any]] = None,
                        model: str = 'llama3-70b-8192') -> str:
    first = True
    chunk_count = 0
    start_time = time.time()
    completion = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": f"""{SMOL_DEV_SYSTEM_PROMPT}

  In response to the user's prompt,
  Please name and briefly describe the structure of the app we will generate, including, for each file we are generating, what variables they export, data schemas, id names of every DOM elements that javascript functions will use, message names, and function names.

  We have broken up the program into per-file generation.
  Now your job is to generate only the code for the file: {current_file}

  only write valid code for the given filepath and file type, and return only the code.
  do not add any other explanation, only return valid code for that file type.
                  """,
            },
            {
                "role": "user",
                "content": f""" the plan we have agreed on is: {plan} """,
            },
            {
                "role": "user",
                "content": f""" the app prompt is: {prompt} """,
            },
            {
                "role": "user",
                "content": f"""
    Make sure to have consistent filenames if you reference other files we are also generating.

    Remember that you must obey 3 things:
       - you are generating code for the file {current_file}
       - do not stray from the names of the files and the plan we have decided on
       - MOST IMPORTANT OF ALL - every line of code you generate must be valid code. Do not include code fences in your response, for example

    Bad response (because it contains the code fence):
    ```javascript
    console.log("hello world")
