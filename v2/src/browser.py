from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys, ActionChains
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import time
import pyautogui
options = webdriver.ChromeOptions()
options.add_argument("window-size=1200x600")

driver = webdriver.Chrome()


def click(element):
    driver.execute_script("arguments[0].click();", element)

TIMEOUT=10

def img_to_base64(image, format="PNG"):
    buffered = BytesIO()
    image.save(buffered, format=format)  # format="JPEG" etc.
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def get(url):
    if(url != driver.current_url):
        driver.get(url)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    return driver.current_url == url

def screenshot():
    screenshot = driver.get_screenshot_as_png()
    return Image.open(BytesIO(screenshot))

def screenshot_base64():
    screenshot = BytesIO(driver.get_screenshot_as_png())
    img_str = base64.b64encode(screenshot.getvalue()).decode('utf-8')
    return img_str

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


#def test(url):
#    element = driver.find_element(By.XPATH, f"//*[contains(text(), '{escape_xpath_string("test")}')]")
#    return element
"""
    # XPath query to search for the text in multiple attributes
    elements = driver.find_elements(By.XPATH, 
        f"//input[contains(@placeholder, '{find}') or contains(@value, '{find}') or contains(@name, '{find}')]"
    )

    
"""

def scroll():
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(0.2)

def tester(url):
    # Define the text you are looking for
    find = 'What are you looking for?'

  # XPath query to search for the text in multiple attributes
    elements = driver.find_elements(By.XPATH, 
        f"//input[contains(@placeholder, '{find}') or contains(@value, '{find}') or contains(@name, '{find}')]"
    )
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{escape_xpath_string(find)}')]")

    
    click_text(find)
    for element in elements:
        if element.tag_name != 'input': continue
        did_something = False
        #dsadssoagppspd python
        if element:
            print(element.get_attribute('outerHTML'))
            print(f"newfind: found '{element.tag_name}' element w/ text '{element.text}'")
            if element.is_displayed() and element.is_enabled() and len(element.tag_name) and len(element.text):  click(element)
            click(element)
           # element.clear()
            print('clok')
            time.sleep(1)
            ActionChains(driver)\
                .send_keys( "parks")\
                .send_keys(Keys.ENTER)
            
            pyautogui.write('parks')
            pyautogui.press('enter')

            print("sentit?")
            if driver.current_url != url:
                return driver.current_url
            #if(element.parent)
            #click(element.parent)
            print("nope.. maybe?")
    

def test_send_keys_to_designated_element(driver):
    driver.get('https://selenium.dev/selenium/web/single_text_input.html')
    driver.find_element(By.TAG_NAME, "body").click()

    text_input = driver.find_element(By.ID, "textInput")
    ActionChains(driver)\
        .send_keys_to_element(text_input, "abc")\
        .perform()

    assert driver.find_element(By.ID, "textInput").get_attribute('value') == "abc"  



def search_thing(find, text, enter):
    print(f"         searchthing({find}, {text}, {enter}): ", end = "")
    try:
        # we know page is fully loaded by now
        element = driver.find_element(By.XPATH, f"//*[contains(text(), '{escape_xpath_string(find)}')]")
        
        search_bar = None
        if element:
            print(f"found '{element.tag_name}' element w/ text '{element.text}'")
            #element.click()
            driver.execute_script("arguments[0].click();", element)
            print("             >clicked successfully.")
            search_bar = driver.find_element(By.XPATH, f"//input[contains(text(), '{find}')]")  # Adjust XPath as needed

            if search_bar:
                # Clear the search bar if it has any default text
                search_bar.clear()
                
                # Input the search text
                search_bar.send_keys(text)
                
                # Submit the search by pressing Enter
                search_bar.send_keys(Keys.RETURN)
                
                print("Search submitted successfully.")
            else:
                print("Search bar element not found.")
        else:
            print("         >Element not found.")
        
    except Exception as e:
           print(f"searchthing: An error occurred: {e}")