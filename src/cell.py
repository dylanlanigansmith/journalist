"""

def cell_to_img(x, y, grid_size = DEFAULT_GRID_SIZE): 
    """ """
    panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')  #width of chrome addr bar and shit
   
    center_x = x * grid_size + grid_size / 2
    center_y = y * grid_size + grid_size / 2
    return center_x, center_y + panel_height

def overlay_grid(image, grid_size=DEFAULT_GRID_SIZE, line_color=(0, 255, 255), text_color=(255, 0, 0, 128), line_width=2, click_coords = None):
  
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

    """