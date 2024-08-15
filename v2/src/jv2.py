#DLS 2024
#see LICENSE.txt in root dir
#
#   Journalist v.2
#
#
import time, sys, json
from config import *
from browser import *
from colorama import Style, Fore

from openai import OpenAI

import openaisdk as oai
import browser
config = Config()

messages = []
client = None

def call_ai(msgs, perf=True):
    time_start = time.time()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        tools=oai.tools,
        response_format=oai.response_format
    )
    if perf:
        elapsed_time = time.time() - time_start
        print(Fore.YELLOW, end="")
        print(f"         >response from OpenAI after {elapsed_time:.4f}s")
        print(Style.RESET_ALL, end="")
    return resp

def enter_text_into_element(args_str):
    args = json.loads(args_str)
    print(f"enter_text_into_elements({args})")
  #  args['text_to_find'], args['input_text'], args['press_enter']
    to_find = args['text_to_find']
    to_input = args['input_text']
    enter = args['press_enter']
    return browser.search_thing(to_find, to_input, enter)



def loop(url, user_prompt):
    browser.get(url)
    time.sleep(5)
    global messages
    browser.tester(url)
    input("huh")
    exit()
    messages.append({
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url" : f"data:image/png;base64,{browser.screenshot_base64()}" }
          
        },
        {
          "type": "text",
          "text": f"current url: <{url}> original user request: '{user_prompt}'"
        }
      ]
    })

    resp = call_ai( messages)
    print(resp)
    for choice in resp.choices:
        latest = choice.message
        print("message: ", latest)
        if latest.tool_calls or len(latest.tool_calls):
            for call in latest.tool_calls:
                assert(call.type == 'function')
                func = call.function

                args = call.function.arguments
                assert(len(args))
               
                if func.name == "enter_text_into_element":
                    enter_text_into_element(args)
                else:
                    print("unknown/unhandled function! ", call)



    return url


def main(url_base, user_prompt):
    print(f"journalist v2 @{url_base} -> '{user_prompt}' \n\n")
    time_start = time.time()
    elapsed_time = time.time() - time_start

    global messages
    global client

    client = OpenAI(api_key=config["openapi_key"])

    messages = oai.messages_start
 
   
    browser.test_send_keys_to_designated_element(driver)
    url = url_base
    while url != "":
        url = loop( url, user_prompt)
        input("enterrrrr")
    print(Fore.YELLOW, end="")
    print("exiting after {elapsed_time:.4f}s")
    print(Style.RESET_ALL, end="")

if __name__ == "__main__": 
    assert(config.ok())
    main(config["test_url"], config["test_prompt"])
