from ocrmac import ocrmac
from PIL import Image, ImageDraw, ImageFont
import browser
import pyautogui
import time
from colorama import Fore, Style
from profiler import Profiler

import window_macos as window

from thefuzz import fuzz, process

# should port this to tesseract for others !!
#
##
def win_offset(): #browser panel height is slow!!!
    return browser.panel_height() + window.menu_bar_height()

def coords_pil_to_screen(x, y): 
    return x, y + win_offset()

def coords_screen_to_pil(x, y): 
    return x, y - win_offset()


def draw_dot(draw, x, y, dot_color = "red", dot_radius = 5):
    draw.ellipse([(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)], fill=dot_color)

def draw_dot_s(draw, cx, cy, dot_color = "red", dot_radius = 5):
    x, y = coords_screen_to_pil(cx, cy)
    draw.ellipse([(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)], fill=dot_color)

def word_bbox(bbox, text, find):
    x1, y1, x2, y2 = bbox

    #use the position of the substr (our keyword) in the larger text to guess where in the bounding box to click (vs the middle)
    text_width = x2 - x1
    text_height = y2 - y1

    find_start = text.find(find)
    if find_start == -1:
        print(f"        word_bbox: to find:'{find}' not found at all")
        return bbox

    find_end = find_start + len(find)
    find_length = len(text)

    find_x = x1 + (text_width * (find_start / find_length))
    find_width = text_width * (len(find) / find_length)

    return (find_x, y1, find_x + find_width, y2)

def bbox_middle(bbox):
    x1, y1, x2, y2 = bbox
    return x1 + (x2 - x1) / 2.0, y1 + (y2 - y1) / 2.0


def find_matching_text2(ocr_result, find):
    print(f"\nfind_matching_text2({len(ocr_result)} results, '{find}')")
    best = None
    word_list = [t[0] for t in ocr_result]

    out = process.extractOne(find, word_list, scorer=fuzz.ratio)   
    if out is None:
        print("no matches from extractOne found from list: ", word_list)
        return None
    found, ratio = out

    print(f"process  '{found}' {ratio} vs '{find}'")
    
    best = next((t for t in ocr_result if t[0] == found), None)

    if best is not None:
        print(f"best match to '{find}' is '{best[0]}' w/ ratio {ratio}")
    else: 
        print(f"couldn't find {found} in {ocr_result}.. wtf!")
    return best


def find_matching_text(ocr_result, find, dbg = False):
    print(f"\nfind_matching_text({len(ocr_result)} results, '{find}')")
    best = None
    best_ratio = 0.0
    for result in ocr_result:
        text = result[0]
        if text and (text == find or find in text): #automatic best
            print("    found direct match without fuzz")
            return result
        pr =  fuzz.partial_ratio(text,find)
        ratio = fuzz.ratio(find, text)

        RATIO_THRESHOLD=25

        if ratio <= RATIO_THRESHOLD and pr <= RATIO_THRESHOLD: print(f"{Fore.YELLOW}")
        PARTIAL_THRESHOLD = 90 #MIGHT BE WRONG
        if pr >= PARTIAL_THRESHOLD: 
            ratio = pr
            print(f"    using partial ratio {pr} (>{PARTIAL_THRESHOLD})")
        if dbg: print(f"    Ratio '{find}' vs '{text}' = {ratio}  [pr{pr}]")
        if ratio > best_ratio:
            best = result
            best_ratio = ratio
       
    print(type(best))
    if best is not None:
        print(f"best match to '{find}' is '{best[0]}' w/ ratio {best_ratio}")
        words = str(find).split()
        close_enough=False
        for word in words:
            if word in best[0]: close_enough = True
            print(f"{word} in '{best[0]}'?")
                    
    else: 
        print("no matches found, sucks")
    return best




def click_element_ocr(img, text_to_click, save_result = True, save_all = True):
    oc = ocrmac.OCR(img)
    rec = oc.recognize(True) #coords in PIL/img fmt 


    print(f"{Fore.YELLOW}click_element_ocr(img, text={text_to_click}, save={save_result}) -> ", end=Style.RESET_ALL)

    #[('SDL Wiki', 0.5, (31.99999868000002, 46.00000010000002, 163.99999868000003, 72.00000009999998))] 
    #[('NAME', CONF, (x1, y1, x2, y2))] 
    find_time = Profiler("find_matching_text")
    found = find_matching_text(rec, text_to_click)
    print("find_matching_1 = ", found)
    find_time.end()
    #find_time2 = Profiler("find_matching_text2")
    #found = find_matching_text2(rec, text_to_click)
    #print("find_matching_2 = ", found)
    #find_time2.end()

    if found is not None: 
        #total text, confidence, bounding box
        text, conf, bbox = found
        x1, y1, x2, y2 = bbox

        #middle x,y
        mx, my = x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2
        
        print(f"{Fore.GREEN} FOUND {Fore.WHITE}'{text}' {Fore.GREEN} conf={conf:.3f} dim={ (x2 - x1):.2f}x{y2 - y1:.2f} {Style.RESET_ALL}")

        if len(text) > len(text_to_click):
            mx, my = bbox_middle( word_bbox(bbox, text, text_to_click) )
            
        
        cx, cy = coords_pil_to_screen(mx, my)
        print(f"move mouse {cx:.1f} {cy:.1f}")
        pyautogui.click(cx, cy)
        if not save_result:
            browser.holdup() # assume saving takes a smidge so dont wait if we are doing that 
            return text

        print("  saving ocr results")

        prof = Profiler("ocr_saving_dbg")
        i = img.copy()
        draw = ImageDraw.Draw(i)
        draw.rectangle((x1, y1, x2, y2), outline="blue")
        if len(text) > len(text_to_click):
            a1, b1, a2, b2 =  word_bbox(bbox, text, text_to_click)
            draw.rectangle((a1, b1, a2, b2), outline="yellow")

        print(f"bb {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f}")
        print(f"mid  {mx:.1f} {my:.1f}")
        draw_dot(draw, mx, my)
        draw_dot_s(draw, cx, cy, "green")
        i.save("ocr_found.png", format="PNG")
        if save_all:
            bb_img = oc.annotate_PIL()
            bb_img.save("ocr_bb.png", format="PNG")
        prof.end()
        
        return text
        

    print(f"{ Fore.RED} FAILED TO FIND ELEMENT WITH TEXT {text_to_click} {Style.RESET_ALL}")
    return ""


    

   
    
