#DLS 2024
#see LICENSE.txt in root dir
#
#   Journalist v.2
#
#
import time, sys, json
from colorama import Style, Fore, Back


from config import *
import browser
import openaisdk as oai
import textwrap


from openai import OpenAI
import ocr 
import window_macos as window


config = Config()

messages = []
client = None

used_tokens = 0

PRICE_PER_M_TOK = 0.15
PRICE_PER_TOK = PRICE_PER_M_TOK / 1000000.0


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
    global used_tokens
    used_tokens += resp.usage.total_tokens

    if perf:
        elapsed_time = time.time() - time_start
        print(Fore.YELLOW, end="")
        print(f"         >response from OpenAI after {elapsed_time:.4f}s {resp.usage.total_tokens}/{used_tokens}")
        print(Style.RESET_ALL, end="")


    return resp

def remove_old_images(debug = True):
    print(f"{Back.RED} REMOVE OLD IMAGES {Style.RESET_ALL}")
    global messages
    removed = 0
    chars = 0
    for message in messages:
        #print(repr(chat_message))
       # message = chat_message.content
        if message['role'] != 'user': continue
        if message == messages[-1]: continue

        for content in message['content']:
            if content['type'] == 'text' and debug:
                print("     >looking at message: ", content['text'])
            if content['type'] != 'image_url': continue
            chars += len(content["image_url"]['url'])
            message['content'].remove(content)
            removed += 1
            if debug:
                print(Fore.RED + "     >removed image for message" + Style.RESET_ALL)

    print(f"{Back.RED} Removed {removed} images from history to save {chars} chars / ~{chars // 4} tok {Style.RESET_ALL}")

def create_function_result(result, call_id):
    global messages
    messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                        "tool_call_id" : call_id
                    })
    return result


#THIS WAS REMOVED FOR NOW
def enter_text_into_element(args_str):
    args = json.loads(args_str)
    print(f"DEPRECATED enter_text_into_elements({args})")
  #  args['text_to_find'], args['input_text'], args['press_enter']
    to_find = args['text_to_find']
    to_input = args['input_text']
    enter = args['press_enter']
    return browser.search_thing(to_find, to_input, enter)


#needs to use OCR and element 

def click_element_with_text_dom(text_to_click):
    print(f"click_element_with_text_dom({text_to_click})")
    return browser.click_text(text_to_click)


def click_element_with_text_ocr(text_to_click):
    print(f"click_element_with_text_ocr({text_to_click})")
    return ocr.click_element_ocr(browser.screenshot(), text_to_click, save_all=False)


def click_element_with_text(text_to_click):
    result = ""
    old_url = browser.url()

    result = click_element_with_text_dom(text_to_click)
    browser.holdup() #jic for testing
    if result != "": 
        if old_url == browser.url():
            print(f"{Back.MAGENTA}{Style.BRIGHT}URL DIDN'T CHANGE WE COULD HAVE TRIED TO SAVE IT HERE!{Style.RESET_ALL}")
    if not len(result) or result == "": #i dont trust python
        result = click_element_with_text_ocr(text_to_click)
        

    return result

def click_element_with_text_function(args_str, call_id):
    args = json.loads(args_str)
    print(f"click_element_with_text({args})")
    found = click_element_with_text(args['text_to_click'])
    status = "tried to click text, could not find a match to click"
    if len(found):
        status = "found a match and tried to click text, if the url didn't change then try something else, that text might not be clickable"

    result = { 'status' : status, "url" : browser.url() } 
    ret = create_function_result(result, call_id)
    return ret
"""    
    messages.append({
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url" : f"data:image/png;base64,{browser.screenshot_base64()}" }
          
        },
        {
          "type": "text",
          "text": f"this is the updated view after running the  click_element_with_text() function you used. '"
        }
      ]
    })
"""
    

def scroll_down(args_str, call_id):
    args = json.loads(args_str)
    print(f"scroll_down({args})")
    global messages
    browser.scroll()
  
    result = { 'status' : "the next message from user will be just the scrolled webpage you just requested."} # you can just respond with anything in order to continue the convo and get this next message."}
    ret = create_function_result(result, call_id)
    messages.append({
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url" : f"data:image/png;base64,{browser.screenshot_base64()}" }
          
        },
        {
          "type": "text",
          "text": f"this scrolled view from the scroll() function you used. '"
        }
      ]
    })

    return ret
    

def found_answer(reply, dbg = True):
    if dbg:
        print(f"found_answer(reply=<goal: '{reply['goal']}', text_to_click: '{reply['text_to_click']}'>)")

    answer = textwrap.indent(reply['reasoning'], '      ') # this doesnt work how i want :( 
    print(f"\n{Back.GREEN}==== Answer Found ===={Style.RESET_ALL}")
    print(f"\n\n{Fore.GREEN} {answer} {Style.RESET_ALL}")
    return ""

skip_user = False

def loop(url, user_prompt):
    global skip_user
    browser.get(url)
    browser.holdup()    
    global messages
    #click_element_with_text("History")
   # browser.holdup()
   # click_element_with_text_ocr(user_prompt)
   # click_element_with_text("Second Sino")
   # input('exit')
   # exit()

    if not skip_user: messages.append({
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
    skip_user = False
    resp = call_ai( messages)
    
    print(resp)
    for choice in resp.choices:
        latest = choice.message

        messages.append(latest.to_dict())
        jstr = json.dumps(latest.to_dict(), indent=4)

        print(Fore.CYAN + textwrap.indent(jstr,"   ") + Style.RESET_ALL)
       # print(f"{Fore.YELLOW} message:{Style.RESET_ALL} {latest} \n")
        if latest.tool_calls and len(latest.tool_calls):
            print(Fore.RED, "Tool Call" + Style.RESET_ALL)
            for call in latest.tool_calls:
                assert(call.type == 'function')
                func = call.function

                args = call.function.arguments
                assert(len(args))
                result = { "status" : "function failed try another thing", "url" : browser.url() }
                if func.name == "click_element_with_text":
                    result = click_element_with_text_function(args, call.id)
                elif func.name == "scroll_down":
                    result = scroll_down(args, call.id)
                else:
                    result['status'] = "The function requested does not exist!?"
                    print("unknown/unhandled function! ", call)
                    create_function_result(result, call.id)
                skip_user = True

            

        elif latest.content:
            print(Back.CYAN, "Content" + Style.RESET_ALL)
            #print(latest.content)
            reply = json.loads(latest.content)
            browser.holdup()
            print(Fore.CYAN + json.dumps(reply, indent=4) + Style.RESET_ALL)
            if 'text_to_click' not in reply or 'reasoning' not in reply or 'goal' not in reply:
                raise KeyError("API Content Does Not Match Expected JSON Schema")
            
            if reply['text_to_click']:
                if reply['text_to_click'] == 'found':
                    return found_answer(reply)
                click_element_with_text( reply['text_to_click'])
        

    #add response for resend

    
    return browser.url()

def log_token_usage():
    global used_tokens
    cost = used_tokens * PRICE_PER_TOK
    print(f"{Back.MAGENTA}API Usage:{Style.RESET_ALL} {Fore.MAGENTA} {used_tokens} TOK | ${cost:.3f} {Style.RESET_ALL}")


def main(url_base, user_prompt):
    print(f"journalist v2 @{url_base} -> '{user_prompt}' \n\n")
    time_start = time.time()
    elapsed_time = time.time() - time_start

    global messages
    global client
    
    client = OpenAI(api_key=config["openapi_key"])

    messages = oai.messages_start
    window.activate_chrome()
    #uncomment to test if selenium input works, 
    #   you can add pyautogui to same test to test that if needed
    #browser.test_send_keys_to_designated_element(driver)
    url = url_base
    its = 0
    last_prune=0
    PRUNE_AFTER = 1
    while url != "":
        print(f"\n{Back.BLUE}[{its}]{Style.RESET_ALL}")
        if (its - last_prune ) > PRUNE_AFTER:
            remove_old_images()
            last_prune = its
        
        url = loop( url, user_prompt)
        its += 1
        log_token_usage()

        #uncomment to ensure confirmation to avoid accidental API calls when testing
        #input(Fore.RED + "CONTINUE..." + Style.RESET_ALL)
        
    print(Fore.YELLOW, end="")
    print("exiting after {elapsed_time:.4f}s")
    print(Style.RESET_ALL, end="")
    browser.driver.close()
    return 0

if __name__ == "__main__": 
    assert(config.ok())
    err = 1
    if len(sys.argv) != 3:
        #no args, use defaults if we can
        if len(sys.argv) == 1 and len(config["test_url"]) and len(config["test_prompt"]):
            print("using test values from config")
            err = main(config["test_url"], config["test_prompt"])
        #missing arg or no defaults!
        else:  
            print("no test values in config!")
            print("Usage: python jv2.py <url> \"<search_text>\"")
    else: 
        url = sys.argv[1]
        search_text = sys.argv[2]       
        err = main(url, search_text)
    sys.exit(err)
   
