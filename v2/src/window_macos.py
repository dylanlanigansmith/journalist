#for macos, to fix coords for screen <-> chromedriver window translation


import objc
from Cocoa import NSApplication, NSScreen, NSRect
from AppKit import NSStatusBar, NSStatusItem
import subprocess

def activate_chrome():
    apple_script = '''
    tell application "Google Chrome"
        activate
    end tell
    '''
    subprocess.run(['osascript', '-e', apple_script])



def menu_bar_height():

    screen = NSScreen.mainScreen()
    if not screen:
        raise RuntimeError("No main screen found")


    screen_frame = screen.frame()
    visible_frame = screen.visibleFrame()


    menu_bar_height = screen_frame.size.height - visible_frame.size.height

    return menu_bar_height

if __name__ == "__main__":
    height = menu_bar_height()
    print(f"Menu bar height: {height} points")
    
    
