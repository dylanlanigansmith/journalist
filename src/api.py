from openai import OpenAI
import time
from colorama import Fore, Back, Style
client = None


oai_response_format={
    "type": "json_schema",
    "json_schema": {
      "name": "web_action",
      "strict": True,
      "schema": {
        "type": "object",
        "required": [
          "goal",
          "reasoning",
          "text_to_click"
        ],
        "properties": {
          "goal": {
            "type": "string"
          },
          "reasoning": {
            "type": "string"
          },
          "text_to_click": {
            "type": "string"
          }
        },
        "additionalProperties": False
      }
    }
  }


default_messages = [
   {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a web-browsing agent that accomplishes tasks. You are provided an image of a website, with the current url and a user requested action you must perform by finding the best text to click on the webpage. The result of clicking on the 'text_to_click' you choose will be the next message. Justify your reasoning and think step by step before choosing the action. If the next user request is the same url, your action before likely failed, attempt it again differently. If you detect previous failed attempts please make it known in the reasoning. If you feel that the answer to the original request is found, reply with your reasoning why, and the text_to_click should be set to 'found' \n "
        }
      ]
    }
]

messages = default_messages

def make_request():
    start_time = time.time()
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=1,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format=oai_response_format
    )
    if len(response.choices) == 0:
        raise IndexError("OpenAI Response has 0 choices")
    end_time = time.time()

    # Calculate the time taken
    elapsed_time = end_time - start_time
    print(Fore.YELLOW, end="")
    print(f"         >got response from OpenAI in {elapsed_time:.4f} seconds")
    print(Style.RESET_ALL, end="")
    return response.choices[0].message.content


#with openai schema json output this can be removed from prompt!!!
"""
        "text": "You are a web-browsing agent that accomplishes tasks. You are provided an image of a website, with the current url and a user requested action you must perform by finding the best text to click on the webpage. The result of clicking on the 'text_to_click' you choose will be the next message. Justify your reasoning and think step by step before choosing the action. Respond in only JSON, for example: {\"goal\" : \"play game\", \"The page has a button to play the game, and a button to exit it, we want to click the play button. I see no other elements that may conflict\", \"text_to_click\" : \"PLAY GAME\" }.  If the next user request is the same url, your action before likely failed, attempt it again differently. If you detect previous failed attempts please make it known in the reasoning. If you feel that the answer to the original request is found, reply with your reasoning why, and the text_to_click should be set to 'found' \n "
        }
"""