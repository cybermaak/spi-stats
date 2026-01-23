import time
import signal
import sys
import multiprocessing as mp
import traceback

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from humanize import naturalsize

from adafruit_rgb_display import st7789
from system_stats import SystemStats
from stat_row import StatRow
from display_config import (CS_PIN, DC_PIN, RESET_PIN, BAUDRATE, DISPLAY_CONFIG, TITLE_FONT_SIZE, STATS_FONT_SIZE, DISPLAY_MODE, DISPLAY_LAYOUT)

MAIN_FONT = "./fonts/FiraCodeNerdFont-Light.ttf"

# Color mapping for PIL
COLOR_MAP = {
    'white': (255, 255, 255),
    'lightblue': (173, 216, 230),
    'yellow': (255, 255, 0),
    'lightgreen': (144, 238, 144),
    'lightcyan': (224, 255, 255),
    'cyan': (0, 255, 255),
    'red': (255, 0, 0),
    'orange': (255, 165, 0),
    'black': (0, 0, 0)
}

# Load fonts once at startup
try:
    title_font = ImageFont.truetype(MAIN_FONT, TITLE_FONT_SIZE)
    stats_font = ImageFont.truetype(MAIN_FONT, STATS_FONT_SIZE)
    icon_font = ImageFont.truetype(MAIN_FONT, STATS_FONT_SIZE)
except OSError:
    # Fallback to default font if custom font fails
    title_font = ImageFont.load_default()
    stats_font = ImageFont.load_default()
    icon_font = ImageFont.load_default()

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display with configuration
disp = st7789.ST7789(
    spi,
    cs=CS_PIN,
    dc=DC_PIN,
    rst=RESET_PIN,
    baudrate=BAUDRATE,
    **DISPLAY_CONFIG
)

# in one instance the display backlight just turned off and won't turn on even with reboot
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def send_image_to_display(pil_image):
    """Send PIL Image directly to SPI display"""
    try:
        disp.image(pil_image)
        return True
    except Exception as e:
        print(f"Error sending image to display: {e}")
        image_size = pil_image.size
        # Print the width and height from the tuple
        print(f"3.Image size (width, height): {image_size}")
        traceback.print_exc()
        return False

def create_blank_image(width, height):
    """Create a blank black image"""
    return Image.new("RGB", (width, height), (0, 0, 0))


def render_stats_direct(width, height, title_text, stats_data):
    """Direct PIL rendering for optimal performance"""
    # Create black background
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    # Layout constants - now relative to font sizes
    y_offset = 10  # Top margin
    row_height = int(STATS_FONT_SIZE * 1.8)  # Row height = 1.8x stats font size for comfortable spacing
    icon_x = 10    # Icon X position
    value_x = 40   # Value text X position
    title_spacing = int(TITLE_FONT_SIZE * 1.5)  # Title spacing = 1.5x title font size for proportional gap

    # Draw title centered at top
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset), title_text, fill=COLOR_MAP['white'], font=title_font)

    # Start drawing stats rows - space after title is relative to title font size
    current_y = y_offset + title_spacing

    for stat_data in stats_data:
        # Draw icon (left aligned)
        draw.text((icon_x, current_y), stat_data['icon'],
                  fill=COLOR_MAP[stat_data['icon_color']], font=icon_font)

        # Draw value (right of icon)
        draw.text((value_x, current_y), stat_data['value'],
                  fill=COLOR_MAP[stat_data['value_color']], font=stats_font)

        current_y += row_height

    return image


def render_stats_visual(width, height, title_text, stats_data):
    """Visual rendering with progress bars"""
    # Create black background
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    # Layout constants - relative to font sizes
    y_offset = 10  # Top margin
    row_height = int(STATS_FONT_SIZE * 1.8)  # Row height for comfortable spacing
    icon_x = 10    # Icon X position
    bar_start_x = 40  # Bar start position (right of icon)
    bar_width = width - bar_start_x - 10  # Bar width (to right edge with margin)
    bar_height = int(STATS_FONT_SIZE * 1.2)  # Increased bar height for better text fit
    title_spacing = int(TITLE_FONT_SIZE * 1.5)  # Title spacing
    
    # Create smaller font for bar labels (70% of stats font size)
    bar_font_size = int(STATS_FONT_SIZE * 0.7)
    try:
        bar_font = ImageFont.truetype(MAIN_FONT, bar_font_size)
    except OSError:
        bar_font = ImageFont.load_default()

    # Draw title centered at top
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset), title_text, fill=COLOR_MAP['white'], font=title_font)

    # Start drawing stats rows
    current_y = y_offset + title_spacing

    for stat_data in stats_data:
        # Draw icon (left aligned)
        draw.text((icon_x, current_y), stat_data['icon'],
                  fill=COLOR_MAP[stat_data['icon_color']], font=icon_font)

        if stat_data['has_bar']:
            # Calculate bar fill width based on percentage
            fill_width = int((bar_width * stat_data['percentage']) / 100)
            
            # Bar vertical position (centered with row)
            bar_y = current_y + int((STATS_FONT_SIZE - bar_height) / 2)
            
            # Draw background bar (empty portion) - dark gray
            draw.rectangle(
                [bar_start_x, bar_y, bar_start_x + bar_width, bar_y + bar_height],
                fill=(40, 40, 40),
                outline=(80, 80, 80)
            )
            
            # Draw filled bar (progress portion)
            if fill_width > 0:
                draw.rectangle(
                    [bar_start_x, bar_y, bar_start_x + fill_width, bar_y + bar_height],
                    fill=COLOR_MAP[stat_data['bar_color']]
                )
            
            # Draw label text inside the bar
            label_text = stat_data['label']
            label_bbox = draw.textbbox((0, 0), label_text, font=bar_font)
            label_width = label_bbox[2] - label_bbox[0]
            label_height = label_bbox[3] - label_bbox[1]
            
            # Check if text fits inside bar, otherwise position outside
            if label_width < (bar_width - 10):  # 10px margin
                # Center text in bar area
                text_x = bar_start_x + (bar_width - label_width) // 2
                text_y = bar_y + (bar_height - label_height) // 2 - label_bbox[1]
                # Use black text for better contrast on colored bars
                draw.text((text_x, text_y), label_text,
                          fill=(0, 0, 0), font=bar_font)
            else:
                # Text doesn't fit, place to the right of bar
                text_x = bar_start_x + bar_width + 5
                text_y = current_y
                draw.text((text_x, text_y), label_text,
                          fill=COLOR_MAP['white'], font=bar_font)
        else:
            # For non-bar items (like IP address), just draw the label text
            draw.text((bar_start_x, current_y), stat_data['label'],
                      fill=COLOR_MAP[stat_data['bar_color']], font=stats_font)

        current_y += row_height

    return image


def render_stats_grid(width, height, title_text, stats_data):
    """Grid layout rendering with 2xn arrangement"""
    # Create black background
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    # Layout constants
    y_offset = 10  # Top margin
    x_margin = 10  # Side margin
    grid_spacing = 8  # Space between grid cells
    title_spacing = int(TITLE_FONT_SIZE * 1.2)  # Reduced title spacing for grid
    
    # Create smaller font for grid labels (65% of stats font size)
    grid_font_size = int(STATS_FONT_SIZE * 0.65)
    try:
        grid_font = ImageFont.truetype(MAIN_FONT, grid_font_size)
    except OSError:
        grid_font = ImageFont.load_default()
    
    # Grid cell dimensions (2 columns)
    cell_width = (width - 2 * x_margin - grid_spacing) // 2
    cell_height = int(STATS_FONT_SIZE * 2.5)  # Height per grid cell
    bar_height = int(STATS_FONT_SIZE * 0.9)  # Bar height in grid

    # Draw title centered at top
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset), title_text, fill=COLOR_MAP['white'], font=title_font)

    # Starting position for grid
    current_y = y_offset + title_spacing
    
    # Separate IP from other stats (IP spans full width as first row)
    ip_data = None
    grid_stats = []
    for stat_data in stats_data:
        if not stat_data['has_bar']:
            ip_data = stat_data
        else:
            grid_stats.append(stat_data)
    
    # Draw IP address spanning full width
    if ip_data:
        # Draw icon
        draw.text((x_margin, current_y), ip_data['icon'],
                  fill=COLOR_MAP[ip_data['icon_color']], font=icon_font)
        # Draw IP text
        draw.text((x_margin + 30, current_y), ip_data['label'],
                  fill=COLOR_MAP[ip_data['bar_color']], font=stats_font)
        current_y += int(STATS_FONT_SIZE * 1.6)
    
    # Draw remaining stats in 2-column grid
    for i in range(0, len(grid_stats), 2):
        # Calculate row position
        row_y = current_y
        
        # Draw left cell (first stat in pair)
        if i < len(grid_stats):
            stat_data = grid_stats[i]
            cell_x = x_margin
            draw_grid_cell(draw, stat_data, cell_x, row_y, cell_width, cell_height, bar_height, grid_font)
        
        # Draw right cell (second stat in pair)
        if i + 1 < len(grid_stats):
            stat_data = grid_stats[i + 1]
            cell_x = x_margin + cell_width + grid_spacing
            draw_grid_cell(draw, stat_data, cell_x, row_y, cell_width, cell_height, bar_height, grid_font)
        
        current_y += cell_height + grid_spacing

    return image


def draw_grid_cell(draw, stat_data, x, y, cell_width, cell_height, bar_height, grid_font):
    """Draw a single grid cell with icon, bar, and label"""
    icon_size = int(STATS_FONT_SIZE * 1.2)
    bar_y = y + icon_size + 2
    bar_width = cell_width - 4
    
    # Draw icon centered above bar
    icon_bbox = draw.textbbox((0, 0), stat_data['icon'], font=icon_font)
    icon_width = icon_bbox[2] - icon_bbox[0]
    icon_x = x + (cell_width - icon_width) // 2
    draw.text((icon_x, y), stat_data['icon'],
              fill=COLOR_MAP[stat_data['icon_color']], font=icon_font)
    
    # Calculate bar fill width based on percentage
    fill_width = int((bar_width * stat_data['percentage']) / 100)
    
    # Draw background bar
    draw.rectangle(
        [x + 2, bar_y, x + 2 + bar_width, bar_y + bar_height],
        fill=(40, 40, 40),
        outline=(80, 80, 80)
    )
    
    # Draw filled bar
    if fill_width > 0:
        draw.rectangle(
            [x + 2, bar_y, x + 2 + fill_width, bar_y + bar_height],
            fill=COLOR_MAP[stat_data['bar_color']]
        )
    
    # Draw label text inside the bar
    label_text = stat_data['label']
    label_bbox = draw.textbbox((0, 0), label_text, font=grid_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_height = label_bbox[3] - label_bbox[1]
    
    # Center text in bar
    if label_width < (bar_width - 6):
        text_x = x + 2 + (bar_width - label_width) // 2
        text_y = bar_y + (bar_height - label_height) // 2 - label_bbox[1]
        # Use black text for better contrast
        draw.text((text_x, text_y), label_text,
                  fill=(0, 0, 0), font=grid_font)
    else:
        # Text too wide, place below bar
        text_x = x + (cell_width - label_width) // 2
        text_y = bar_y + bar_height + 2
        draw.text((text_x, text_y), label_text,
                  fill=COLOR_MAP['white'], font=grid_font)


def shutdown_handler(_signum, _frame):
    print("shutdown_handler...")
    # Use display dimensions directly since width/height may not be in scope
    if disp.rotation % 180 == 90:
        h = disp.width
        w = disp.height
    else:
        w = disp.width
        h = disp.height
    blank_image_final = create_blank_image(w, h)
    send_image_to_display(blank_image_final)
    print("blank image sent...")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

ip_stat = StatRow(
    icon="\uf109",  # Network icon
    label="",
    color="lightblue",
    get_stat=SystemStats.get_ip_address,
    state_string=lambda stat: stat,
    is_warning=lambda stat: False,
    is_critical=lambda stat: False,
    get_percentage=None,  # IP address has no percentage
    visual_label=lambda stat: stat  # Same as text mode
)

cpu_stat = StatRow(
    icon="\uf4bc",  # CPU icon
    label="",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}%",
    is_warning=lambda stat: stat >= 70,
    is_critical=lambda stat: stat >= 90,
    get_percentage=lambda stat: stat,  # CPU returns percentage directly
    visual_label=lambda stat: f"{stat:.1f}%"
)

mem_stat = StatRow(
    icon="\uefc5",  # Memory icon
    label="",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory: f"{naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
    get_percentage=lambda memory: memory.percent,
    visual_label=lambda memory: f"{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)"
)

disk_stat = StatRow(
    icon="\uf472",  # Disk icon
    label="",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk: f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
    get_percentage=lambda disk: (disk.used / disk.total) * 100,
    visual_label=lambda disk: f"{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)"
)

temp_stat = StatRow(
    icon="\uf2c9",  # Temperature icon
    label="",
    color="cyan",
    get_stat=SystemStats.get_temperature_stats,
    state_string=lambda cpu_temp: f"{cpu_temp:.1f}°C",
    is_warning=lambda cpu_temp: cpu_temp >= 60,
    is_critical=lambda cpu_temp: cpu_temp >= 70,
    get_percentage=lambda cpu_temp: cpu_temp,  # Use temperature as percentage (0-100°C range)
    visual_label=lambda cpu_temp: f"{cpu_temp:.1f}°C"
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

title_text = "═ SYSTEM MONITOR ═"
stats = [ip_stat, cpu_stat, mem_stat, disk_stat, temp_stat]

print(f"Display initialized: {disp.width}x{disp.height}, rotation: {disp.rotation}")
print(f"Display mode: {DISPLAY_MODE}, Layout: {DISPLAY_LAYOUT}")
# Initialize display with blank screen
blank_image = create_blank_image(width, height)
send_image_to_display(blank_image)

try:
    while True:
        def update_stats():
            # Send image to display
            try:
                # Choose rendering mode based on configuration
                if DISPLAY_MODE == 'visual':
                    # Collect stats data for visual mode (with progress bars)
                    stats_data = [stat.get_visual_data() for stat in stats]
                    
                    # Choose layout: grid or rows
                    if DISPLAY_LAYOUT == 'grid':
                        pil_image = render_stats_grid(width, height, title_text, stats_data)
                    else:
                        pil_image = render_stats_visual(width, height, title_text, stats_data)
                else:
                    # Collect stats data for text mode (default)
                    stats_data = [stat.update_compose() for stat in stats]
                    # Render with text mode (rows layout only)
                    pil_image = render_stats_direct(width, height, title_text, stats_data)
                
                pil_image.save("screenshot.png")
                # Send directly to SPI display
                send_image_to_display(pil_image)

            except Exception as e:
                print(f"Error rendering or sending image to display: {e}")
                traceback.print_exc()
        # print("************Timestamp 1:", time.time())
        # Process forking used as safety measure for memory management
        # Can be removed if direct PIL rendering proves stable
        proc = mp.Process(target=update_stats)
        proc.start()
        proc.join()

        time.sleep(1)
except KeyboardInterrupt:
    shutdown_handler(0, 0)
