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
from colorama import Fore, Back, Style
from thefuzz import fuzz, process
#options = webdriver.ChromeOptions()
#options.add_argument("window-size=1200x600")

driver = webdriver.Chrome()
driver.set_window_position(0,0, windowHandle='current') #for consistent pyautogui clicks
TIMEOUT=10
SHORT_TIMEOUT=0.3

def error_message_tidy(error_message):
    error_message = str(error_message)
    index = error_message.find('(Session info:')
    if index != -1:
        return error_message[:index].strip()
    else:
        return error_message.strip()
def holdup(how_many = 1): #iowait 
    time.sleep(SHORT_TIMEOUT * how_many)

def get_ready(timeout = TIMEOUT):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def click(element):
    try:
        element.click()
    except (Exception) as e:
        print("         >An error occurred.")
        print(f"         {Back.YELLOW}browser.click_text: exception:{Style.RESET_ALL}{Fore.YELLOW}\n            {error_message_tidy(str(e))} {Style.RESET_ALL}") 
    driver.execute_script("arguments[0].click();", element)
    holdup()

def scroll():
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    holdup()

def panel_height(): #len of chrome header etc (offset for content)
    return driver.execute_script('return window.outerHeight - window.innerHeight;')

def url(): #Current Url 
    return driver.current_url

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



def find_matching_elements(elements, find):
    print(f"\nfind_matching_text2({len(elements)} results, '{find}')")
  
    word_list = [e.text for e in elements]
    print(word_list)
    best = next((e for e in elements if e.text == find), None)
    if best is not None:
        print(f"found {best.text} direct match early")
        return best
    

    out = process.extract(find, word_list, scorer=fuzz.ratio)   
    if out is None:
        print("no matches from extractOne found from list: ", word_list)
        return None
    
    found = find
    for opt in out:
        match, ratio = opt
        print(f"process  '{match}' {ratio} vs '{find}'")
    found = out[0][0]
    ratio= out[0][1]

   #this is broken bc we actually want it to only do direct matches first for all cats, etc
   #need a real big algorithm for this 
   #lmao use another gpt


    
    best = next((e for e in elements if e.text == found), None)

    if best is not None:
        print(f"best match to '{find}' is '{best.text}' w/ ratio {ratio}")
    else: 
        print(f"couldn't find {found} in {elements}.. wtf!")

    print("best=",best)
    return best

def click_text(text_to_click, dbg = False):
    print(f"         browser.click_text({text_to_click}): ", end = "")
    text = escape_xpath_string(text_to_click)
    try:

        priorities = [
            'a',         # first priority direct links, goal is navigation
            'button',    
            'span',
            'img',
            'select',
            'input',    
            'form',
            '*',         # last priority whatever we can get
        ]
        #might be faster to find * elements, then iterate that total list more, instead of running find_elements each time for worst case....
        #hm
        bests = []
        for tag in priorities:
            if dbg: print(f"{Back.WHITE}{Fore.RED} <{tag}> {Style.RESET_ALL}", end ="")
            elements = driver.find_elements(By.XPATH, f"//{tag}[contains(text(), '{text}')]")
            
            if len(elements):
                old_size = len(elements)
                for element in elements:
                    if not element.is_displayed():
                        elements.remove(element)
                print(f" old {old_size} new {len(elements)}")

                if not len(elements):
                    print("we empty")
                    continue


                if dbg: 
                    print(f"Found {len(elements)} '{tag}' element(s) with text '{text}':")
                    for element in elements:
                        print(f"  - Tag: {element.tag_name}, Text: '{element.text}'")

                # could do fuzzy here like in ocr if we want..
                best_element = find_matching_elements(elements, text)

                if best_element is None: continue #best_element =  elements[0]
                print(f"             >found <{tag}> {best_element.tag_name}, text: '{best_element.text} ")
                bests.append(best_element)
            else: print(f" elements = {type(elements)}")
        if len(bests):
            if dbg: print("bests = ", len(bests))
            best_texts=[b.text for b in bests ]
            if dbg: 
                for best in bests:
                    print(f"<{best.tag_name}> '{best.text}'")
            
            winner, final_ratio = process.extractOne(text, best_texts, scorer=fuzz.ratio, score_cutoff=20)
            #should check duplicates first
            final = next((e for e in elements if e.text == winner), None) #find element with best text
            assert(final is not None)
         
            #final = bests[0]
            
            print(f"best match to {Fore.GREEN}\"{winner}\"{Style.RESET_ALL}  !! to_find='{text}' is {Fore.GREEN}<{final.tag_name}> '{final.text}'{Style.RESET_ALL} w/ ratio {final_ratio}")
            click(final)
            print(f"             {Fore.GREEN}>clicked successfully.{Style.RESET_ALL}")
            return text    
             
               
          
 
        print("         >No prioritized elements found.")
        
    except (Exception) as e:
        print("         >An error occurred.")
        print(f"         {Back.YELLOW}browser.click_text: exception:{Style.RESET_ALL}{Fore.YELLOW}\n            {error_message_tidy(str(e))} {Style.RESET_ALL}")

    return ""


def click_text_old(text):
    print(f"         browser.click_text({text}): ", end = "")
    try:
        # we know page is fully loaded by now
        element = driver.find_element(By.XPATH, f"//*[contains(text(), '{escape_xpath_string(text)}')]")
        
        if element:
            print(f"found '{element.tag_name}' element w/ text '{element.text}'")
            #element.click()
            driver.execute_script("arguments[0].click();", element)
            print("             >clicked successfully.")
            return text
        else:
             print("not found") #never
    except Exception as e:
           print("not found")
           #print(f"click_text: An error occurred: {str(e)}")
           print(f"         {Back.YELLOW}browser.click_text: exception:{Style.RESET_ALL}{Fore.YELLOW}\n            {error_message_tidy(str(e))} {Style.RESET_ALL}")

    return ""

def test_send_keys_to_designated_element(driver):
    driver.get('https://selenium.dev/selenium/web/single_text_input.html')
    driver.find_element(By.TAG_NAME, "body").click()

    text_input = driver.find_element(By.ID, "textInput")
    ActionChains(driver)\
        .send_keys_to_element(text_input, "abc")\
        .perform()

    assert driver.find_element(By.ID, "textInput").get_attribute('value') == "abc"  

#TODO merge all versions of this code to use one function!
def find_best_elements_by_priority(text_to_find, priorities = ['a','button','span','input','form','*'], dbg = True):
    print(f"find_best_elements_by_priority({text_to_find}, {priorities}, {dbg})")
    text = escape_xpath_string(text_to_find)
    try:
        bests = []
        for tag in priorities:
            if dbg: print(f"        {Back.WHITE}{Fore.RED} <{tag}> {Style.RESET_ALL}", end ="")
            all_elements = driver.find_elements(By.XPATH, f"//{tag}[contains(text(), '{text}')]")
            
            if len(all_elements):
                elements = [elem for elem in all_elements if elem.is_displayed() and elem.is_enabled()]
                if dbg: print(f"removed nonvis/non enabled elements: prev size = {len(all_elements)} new size = {len(elements)}")

                if not len(elements):
                    print(f"no visible elements found skipping {tag}..")
                    continue


                if dbg: 
                    print(f"        Found {len(elements)} '{tag}' element(s) with text '{text}':")
                    for element in elements:
                        print(f"  - Tag: {element.tag_name}, Text: '{element.text}'")

                # fuzzy needs work and standardizing 
                best_element = find_matching_elements(elements, text)

                if best_element is None: continue #best_element =  elements[0]
                print(f"             >found <{tag}> {best_element.tag_name}, text: '{best_element.text} ")
                bests.append(best_element)
            else: print(f"no elements found for {tag} [elements = {type(all_elements)}]")
        if len(bests):
            if dbg: print("     bests = ", len(bests))
            best_texts=[b.text for b in bests ]
            if dbg: 
                for best in bests:
                    print(f"<{best.tag_name}> '{best.text}'")
            
            winner, final_ratio = process.extractOne(text, best_texts, scorer=fuzz.ratio, score_cutoff=20)
            #should check duplicates first
            final = next((e for e in elements if e.text == winner), None) #find element with best text
            assert(final is not None)
    
            print(f"best match to {Fore.GREEN}\"{winner}\"{Style.RESET_ALL}  !! to_find='{text}' is {Fore.GREEN}<{final.tag_name}> '{final.text}'{Style.RESET_ALL} w/ ratio {final_ratio}")
            assert(final in bests)
            bests.remove(final)
            bests.insert(0, final)
            assert(bests[0] == final)

            print(f"             {Fore.GREEN}>moved winner to front{Style.RESET_ALL}")
            return bests    
             
               
          
 
        print("         >No prioritized elements found.")
        
    except (Exception) as e:
        print("         >An error occurred.")
        print(f"         {Back.YELLOW}browser.find_best_elements_by_priority: exception:{Style.RESET_ALL}{Fore.YELLOW}\n            {error_message_tidy(str(e))} {Style.RESET_ALL}")

    return []


def enter_text(text_to_find, text_to_enter, press_enter = True, dbg = True):
    print(f"      {Back.CYAN}browser.enter_text({text_to_find}, {text_to_enter}, press={press_enter}):{Style.RESET_ALL} ", end = "")
    priorities = [
            'input',         # first priority direct links, goal is navigation
            'textarea',    
            'select',
            'form',
            '*',         # last priority whatever we can get
        ]
    text = escape_xpath_string(text_to_find)
    best_elements = find_best_elements_by_priority(text_to_find, priorities)    
    print("best elements = ", len(best_elements))
    if True:
        print("trying placeholder")
        places = driver.find_elements(By.XPATH, f'//*[@placeholder="{text}"]')
        print(len(places))

        for placeholder in places:
            best_elements.append(placeholder)
    print("best elements = ", len(best_elements))
    if True:
        print(f"{Fore.BLUE} TRYING INPUTS {Style.RESET_ALL}")
        inputs = driver.find_elements(By.CSS_SELECTOR, 
        'input[type="text"], input[type="password"], input[type="email"], input[type="tel"], input[type="url"], input[type="search"], textarea, [contenteditable="true"]')

        # Filter valid text inputs
        valid_inputs = [elem for elem in inputs if elem.is_displayed() and elem.is_enabled()]
        print(f"{len(valid_inputs)} valid inputs found")
        # Print information about valid inputs
        for elem in valid_inputs:
            tag_name = elem.tag_name
            attributes = {
                'name': elem.get_attribute('name'),
                'id': elem.get_attribute('id'),
                'placeholder': elem.get_attribute('placeholder'),
                'type': elem.get_attribute('type') if tag_name == 'input' else None,
                'contenteditable': elem.get_attribute('contenteditable') if tag_name == 'div' or tag_name == 'span' else None
            }
            print(f"Input found: {attributes}")
            element = elem #lazy
            val = element.get_attribute("value") if tag_name == 'input' else None
            if val is not None:
                if val == text:
                    print("found input with value matching")
                    best_elements.append(elem)
                    continue
            placeholder = elem.get_attribute('placeholder')
            if placeholder is not None:
                if placeholder == text or placeholder == text_to_find:
                    print("found input with placeholder matching")
                    best_elements.append(elem)
            typeat = elem.get_attribute('type') if tag_name == 'input' else None,
            if typeat is not None:
                if typeat == text.split(" ")[0].lower() or placeholder == text_to_find.split(" ")[0].lower():
                    print("found input with type matching")
                    best_elements.append(elem)

    

    if len(best_elements):
        for element in best_elements:
            print(f"Element Best  - Tag: {element.tag_name}, Text: '{element.text}'")
            try:
                click(element)
                print("clicked")
                if element.tag_name == 'input':
                    value = element.get_attribute("value")
                    if value is not None:
                        print("input tag value = ", element.get_attribute("value"))
                        if len(value):
                            element.clear()
                            print("CLEARED INPUT!")

                element.send_keys(text_to_enter)
                print("sent keys")
                if element.tag_name == 'input':
                    print("new input tag value = ", element.get_attribute("value"))
                    value = element.get_attribute("value")
                    
                    if element.get_attribute("value") != text_to_enter:
                        print("PAG")
                        pyautogui.write(text_to_enter)  

                if element.get_attribute("value") != text_to_enter: 
                    print("     >seems like we failed for this one")
                    continue  
                print("wrote elem")
                if press_enter: pyautogui.press('enter')
                break
            except (Exception) as e:
                print(f"Error {error_message_tidy(e)}")



#IGNORE OLD NOT USED 
def tester(url):
    # Define the text you are looking for
    find = 'What are you looking for?'
    assert(False)
  #search for the text in multiple attributes
    elements = driver.find_elements(By.XPATH, 
        f"//input[contains(@placeholder, '{find}') or contains(@value, '{find}') or contains(@name, '{find}')]"
    )
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{escape_xpath_string(find)}')]")
    #use priority thing above, but then run up parents for text fields...

    
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
    


"""
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
"""
