from selenium import webdriver
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

from cfg import *

config = Config()
driver = webdriver.Chrome()

DEFAULT_PAGE_LOAD_TIME = 3
DEFAULT_GRID_SIZE = 100

DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

def cell_to_img(x, y, grid_size = DEFAULT_GRID_SIZE): 
    """ """
    panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')  #width of chrome addr bar and shit
   
    center_x = x * grid_size + grid_size / 2
    center_y = y * grid_size + grid_size / 2
    return center_x, center_y + panel_height


def img_to_base64(image):
    """Convert a Pillow image to a base64-encoded string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # or format="JPEG" for JPEG images
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str


def overlay_grid(image, grid_size=DEFAULT_GRID_SIZE, line_color=(0, 255, 255), text_color=(255, 0, 0, 128), line_width=2, click_coords = None):
    """Overlay a transparent labeled coordinate grid onto an image."""
    width, height = image.size
    draw = ImageDraw.Draw(image, 'RGBA')

    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=line_color, width=line_width)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=line_color, width=line_width)


    font = ImageFont.truetype(DEFAULT_FONT_PATH, 14)
    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            cell_x = x // grid_size
            cell_y = y // grid_size
            text = f"{cell_x}/{cell_y}"
            
            # Get the size of the text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Calculate the position to center the text
            text_x = x + (grid_size - text_width) / 2
            text_y = y + (grid_size - text_height) / 2
            draw.text((text_x, text_y), text, fill=text_color, font=font)

    if click_coords:
        dot_radius = 10
        dot_color = (255, 0, 0, 235) 
        x, y = click_coords
        draw.ellipse([(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)], fill=dot_color)
    return image


def get_page_image(url, save = True):
    if(url != driver.current_url):
        driver.get(url)
    print("Loaded ", url)
    # Wait for the page to load
    time.sleep(DEFAULT_PAGE_LOAD_TIME)
    
    # Capture screenshot
    print("Captured Screenshot")
    screenshot = driver.get_screenshot_as_png()
    image = Image.open(BytesIO(screenshot))
    if save:  print("Saving screenshots...")
    if save: image.save('screenshot.png')

    image_with_grid = overlay_grid(image)
    # Save the screenshot with the grid overlay
    if save: image_with_grid.save('screenshot_with_grid.png')
    return img_to_base64(image_with_grid)

def parse_click_command(command):
    # Regular expression pattern to match 'click' or any other similar prefix followed by two numbers
    pattern = r'\b\w*\((\d+)\s*,\s*(\d+)\)'
    
    # Search for the pattern in the command string
    match = re.search(pattern, command)
    
    if match:
        # Extract numbers and convert them to integers
        x = int(match.group(1))
        y = int(match.group(2))
        return x, y
    else:
        raise ValueError("Invalid format. Expected format: command(x, y)")


def page_action(url, action):
    img64 = get_page_image(url)
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
    print("making request")
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
    print("Goal: ", response["goal"])
    print("Reasoning: ", response["reasoning"])
    print("Action: ", response["action"])
    cell_x, cell_y = parse_click_command(response["action"])
   
    x,y = cell_to_img(cell_x + 1, cell_y)
   #
    

    pyautogui.moveTo(x, y)
    # Print coordinates (for debugging)
    print(f"Clicking at coordinates: ({x}, {y}) in:")
  
    time.sleep(1)
 
    # Simulate mouse click
    pyautogui.click(x, y)

    
    time.sleep(1)
    if driver.current_url == url:
        print('did not change url with action')
    return driver.current_url

def main():
    assert(config.ok())
    api.client = OpenAI(api_key=config["openapi_key"])
    print("starting journalist")
#    visit_page("https://www.pitchfork.com")
    start_url = "https://www.oshawa.ca/en/index.aspx"
    url = start_url
    while(url == start_url or True):
        url = page_action(url, "What day is garbage day")
       # input("enter to continue")

    page_action(url, "Click Author Name")



    input("enter to quit")
    time.sleep(0.5)
    driver.quit()


if __name__ == "__main__":
    main()