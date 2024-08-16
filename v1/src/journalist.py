from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image, ImageDraw, ImageFont
import pyautogui
import time
import cv2
import numpy as np
from io import BytesIO
from openai import OpenAI
import api
import base64
import re
import sys
from colorama import Fore, Back, Style

from cfg import *

config = Config()
driver = webdriver.Chrome()

DEFAULT_PAGE_LOAD_TIME = 3
DEFAULT_GRID_SIZE = 100

DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"




def img_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # or format="JPEG" for JPEG images
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str



def get_page_image(url, save = False):
    start_time = time.time()
    
    if(url != driver.current_url):
        driver.get(url)
        print("         >loaded ", url)
    # Wait for the page to load
    
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    #time.sleep(DEFAULT_PAGE_LOAD_TIME)


    # Capture screenshot
    print("        ")
    screenshot = driver.get_screenshot_as_png()

   
    elapsed_time = time.time() - start_time
    print(Fore.YELLOW, end="")
    print(f"         >loaded page and captured screenshot in {elapsed_time:.4f} s")
    print(Style.RESET_ALL, end="")
    image = Image.open(BytesIO(screenshot))
    if save:  print("         >Saving screenshots...")
    if save: image.save('screenshot.png')

   # image_with_grid = overlay_grid(image)
    # Save the screenshot with the grid overlay
    #if save: image_with_grid.save('screenshot_with_grid.png')
    return img_to_base64(image)



def escape_xpath_string(s):
    return s.replace("'", "\\'").replace('"', '\\"')


def click_text(text):
    print(f"         click_text({text}): ", end = "")
    try:
        # we know page is fully loaded by now
        element = driver.find_element(By.XPATH, f"//*[contains(text(), '{escape_xpath_string(text)}')]")
        
        
        if element:
            print(f"found '{element.tag_name}' element w/ text '{element.text}'")
            #element.click()
            driver.execute_script("arguments[0].click();", element)
            print("             >clicked successfully.")
        else:
            print("         >Element not found.")
        
    except Exception as e:
           print(f"click_text: An error occurred: {e}")
    

def page_action(url, action):
    start_time = time.time()
   
    # Calculate the time taken
   
    
    img64 = get_page_image(url)
    elapsed_time = time.time() - start_time
    print(Fore.YELLOW, end="")
    print(f"         >got page b64 img in {elapsed_time:.4f} s")
    print(Style.RESET_ALL, end="")
    api.messages.append({
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": { "url" : f"data:image/png;base64,{img64}" }
          
        },
        {
          "type": "text",
          "text": f"current url: {url} requested action: {action}"
        }
      ]
    })
    print("         >making request")
    response_str = api.make_request()

    api.messages.append({
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": response_str
        }
      ]
    })

    response = json.loads(response_str)
    ttc = response["text_to_click"]
    if ttc == "found" or ttc == "Found":
        print(Fore.GREEN, "\n==== Answer Found ====")
        print("\n\n", response["reasoning"])
        print(Style.RESET_ALL, end="")
        return "found"


    print(f"\n{Fore.CYAN}goal:{Style.RESET_ALL} ", response["goal"])
    print(f"{Fore.CYAN}text_to_click:{Style.RESET_ALL} '{ttc}'")
    print(f"{Fore.CYAN}reasoning:{Style.RESET_ALL} '{response['reasoning']}'  \n")
    print(Style.RESET_ALL, end="")
    click_text(ttc)
   
     
    #
    
    time.sleep(0.3)
    if driver.current_url == url:
        print('         >note: did not change url with action')
    return driver.current_url

def main(start_url = "https://www.oshawa.ca/en/index.aspx", action = "When does street parking ban start"):
    assert(config.ok())
    api.client = OpenAI(api_key=config["openapi_key"])
    print("starting journalist...")

    print(f"using url '{start_url}', figure out '{action}' ")

    
    url = start_url
    start_time = time.time()

    while(url != "found"):
        url = page_action(url, action)
       # input("enter to continue")

    end_time = time.time()

    # Calculate the time taken
    elapsed_time = end_time - start_time
    print(Fore.YELLOW, end="")
    print(f"Answer found in: {elapsed_time:.4f} seconds")
    print(Style.RESET_ALL, end="")

    time.sleep(0.5)
    #input("==press enter to quit==")
    driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python journalist.py <url> \"<search_text>\"")
        sys.exit(1)
    
    url = sys.argv[1]
    search_text = sys.argv[2]
    main(url, search_text)