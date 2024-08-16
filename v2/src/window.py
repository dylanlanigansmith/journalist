import objc
from Cocoa import NSApplication, NSScreen, NSRect
from AppKit import NSStatusBar, NSStatusItem

def menu_bar_height():
    # Get the main screen
    screen = NSScreen.mainScreen()
    if not screen:
        raise RuntimeError("No main screen found")

    # Get the screen frame and visible frame
    screen_frame = screen.frame()
    visible_frame = screen.visibleFrame()

    # Calculate the height of the menu bar
    menu_bar_height = screen_frame.size.height - visible_frame.size.height

    return menu_bar_height

if __name__ == "__main__":
    height = menu_bar_height()
    print(f"Menu bar height: {height} points")
