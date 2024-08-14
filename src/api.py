from openai import OpenAI
import json

client = None

oai_tools=[
    {
      "type": "function",
      "function": {
        "name": "click_cell",
        "strict": True,
        "parameters": {
          "type": "object",
          "required": [
            "x",
            "y"
          ],
          "properties": {
            "x": {
              "type": "number",
              "description": "the X coordinate of the cell to click"
            },
            "y": {
              "type": "number",
              "description": "the Y coordinate of the cell to click"
            }
          },
          "additionalProperties": False
        },
        "description": "Click at the location of the cell coordinates given"
      }
    }
  ]
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
          "action"
        ],
        "properties": {
          "goal": {
            "type": "string"
          },
          "reasoning": {
            "type": "string"
          },
          "action": {
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
          "text": "You are a web-browsing agent that accomplishes tasks. You are provided an image of a website, with a grid of cells overlayed. As well, the current url and a user requested action you must perform is provided. Respond with your next action to satisfy/click on the request, for example: click(2,8) where 2,8 are the coordinates of the cell you want to click. The result of this action will be the next message.  Justify your reasoning and think step by step before choosing the cell. Respond in only JSON with the fields \"goal\", \"reasoning\" and \"action\", for example: \"goal\" : \"play game\", \"The page has a button to play the game, and a button to exit it, we want to click the play button. I see no other elements that may conflict\", \"action\" : \"click(2, 16)\".  Make sure you pick the cell that contains the majority of the element requested. If text matches, pick the cell with that text. Once you find a cell, search again to ensure it is the best match, vocalize this reasoning first. If the next user request is the same url, your action before likely failed, attempt it again. Do not repeat the same cell if your previous action likely failed. You get a million dollar reward for each cell you get right. If you detect previous failed attempts please make it known in the reasoning"
        }
      ]
    }
]

messages = default_messages

def make_request():
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.95,
    max_tokens=512,
    top_p=0.8,
    frequency_penalty=0,
    presence_penalty=0,
    tools=oai_tools,
    response_format=oai_response_format
    )
    if len(response.choices) == 0:
        raise IndexError("OpenAI Response has 0 choices")
    return response.choices[0].message.content