
tools=[
    {
      "type": "function",
      "function": {
        "name": "click_element_with_text",
        "description": "Clicks the element with the corresponding text. If this fails, ensure you used the correct search text",
        "parameters": {
          "type": "object",
          "properties": {
            "why_finding_text_furthers_goal":{
              "type": "string",
              "description": "Your reasoning why the element this text should be clicked"
            },
            "text_to_click": {
              "type": "string",
              "description": "The matching text for the element to be clicked"
            }
          },
          "required": [
            "why_finding_text_furthers_goal",
            "text_to_click"
          ],
          "additionalProperties": False
        },
        "strict": True
      }
    },
    {
      "type": "function",
      "function": {
        "name": "scroll_down",
        "description": "The next user message will be the same text but with the image of the webpage scrolled down. Ensure you do not have to scroll via clicking buttons, or pressing 'Load' if this does not seem to reveal more.",
        "parameters": {
          "type": "object",
          "properties": {
            "why_scroll": {
              "type": "string",
              "description": "What you hope to reveal by scrolling instead of trying to click something" #model will improve its next response to scrolled view using this prior justification
            }
          },
          "required": [
            "why_scroll"
          ],
          "additionalProperties": False
        },
        "strict": True
      }
    }
]

"""
    {
      "type": "function",
      "function": {
        "name": "enter_text_into_element",
        "description": "Simulates typing the given text into the element requested to search for, can optionally press enter, which is recommended for search bars",
        "parameters": {
          "type": "object",
          "properties": {
            "why_finding_text_furthers_goal":{
              "type": "string",
              "description": "Your reasoning why the element this text should be clicked"
            }
            "text_to_find": {
              "type": "string",
              "description": "The matching text to find the input element"
            },
            "input_text": {
              "type": "string",
              "description": "The text to enter into the element once located, for example: a search keyword or username"
            },
            "press_enter": {
              "type": "boolean",
              "description": "Should an enter press/input submission be simulated after the input text?"
            }
          },
          "required": [
            "text_to_find",
            "input_text",
            "press_enter"
          ],
          "additionalProperties": False
        },
        "strict": True
      }
    }
    """
  

response_format={
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

messages_start=[
    {
      "role": "system",
      "content": [
        {
          "text": "You are a web-browsing agent that accomplishes tasks. You are provided an image of a website, with the current url and a user requested action you must perform by finding the best text to click on the webpage. The result of clicking on the 'text_to_click' you choose will be the next message. Justify your reasoning and think step by step before choosing the action. If the next user request is the same url, your action before likely failed, attempt it again differently. Never scroll more than twice in a row if the previous attempt did not lead you somewhere. Only Make ONE TOOL CALL Before Responding with an update on your 'goal','reasoning',and 'text_to_click'.   If you detect previous failed attempts please make it known in the reasoning. Interact with pages to reveal more content when needed. Quality is what we are after. When you have found the answer to the original prompt, signify this by returning your FINAL COMPLETE answer after your usual reply in the \"reasoning\" field, and set \"text_to_click\" to 'found'. Never reply with more than one json object\n ",
          "type": "text"
        }
      ]
    }
]


"""

from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "system",
      "content": [
        {
          "text": "You are a web-browsing agent that accomplishes tasks. You are provided an image of a website, with the current url and a user requested action you must perform by finding the best text to click on the webpage. The result of clicking on the 'text_to_click' you choose will be the next message. Justify your reasoning and think step by step before choosing the action. If the next user request is the same url, your action before likely failed, attempt it again differently.   If you detect previous failed attempts please make it known in the reasoning. Use your tools as many times as you need to reach the best answer you can find. In your final reply, address the user and directly answer as well. Quality is what we are after. \n ",
          "type": "text"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "base64:image etc"
            }
        },
        {
          "type": "text",
          "text": "https://www.oshawa.ca/en/index.aspx\n\nWhen does street parking ban start?"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": ""
        }
      ],
      "tool_calls": [
        {
          "id": "call_kaAfG3ZYD5cl280vnx66mbN1",
          "type": "function",
          "function": {
            "name": "enter_text_into_element",
            "arguments": "{\"text_to_find\":\"What are you looking for?\",\"input_text\":\"street parking ban\",\"press_enter\":True}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "content": [
        {
          "type": "text",
          "text": "response"
        }
      ],
      "tool_call_id": "call_kaAfG3ZYD5cl280vnx66mbN1"
    }
  ],
  temperature=1,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  tools=[],
  response_format={}
)

"""