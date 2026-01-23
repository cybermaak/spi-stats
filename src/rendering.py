"""
Shared rendering functions for stats display.
This module contains all rendering logic used by both the main stats.py 
and test scripts.
"""
from PIL import Image, ImageDraw, ImageFont

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


def load_fonts(title_font_size, stats_font_size):
    """Load fonts for rendering"""
    try:
        title_font = ImageFont.truetype(MAIN_FONT, title_font_size)
        stats_font = ImageFont.truetype(MAIN_FONT, stats_font_size)
        icon_font = ImageFont.truetype(MAIN_FONT, stats_font_size)
    except OSError:
        title_font = ImageFont.load_default()
        stats_font = ImageFont.load_default()
        icon_font = ImageFont.load_default()
    return title_font, stats_font, icon_font


def render_stats_direct(width, height, title_text, stats_data, title_font,
                        stats_font, icon_font, stats_font_size,
                        title_font_size):
    """Direct PIL rendering for text mode"""
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    y_offset = 10
    row_height = int(stats_font_size * 1.8)
    icon_x = 10
    value_x = 40
    title_spacing = int(title_font_size * 1.5)

    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset),
              title_text,
              fill=COLOR_MAP['white'],
              font=title_font)

    current_y = y_offset + title_spacing

    for stat_data in stats_data:
        draw.text((icon_x, current_y),
                  stat_data['icon'],
                  fill=COLOR_MAP[stat_data['icon_color']],
                  font=icon_font)
        draw.text((value_x, current_y),
                  stat_data['value'],
                  fill=COLOR_MAP[stat_data['value_color']],
                  font=stats_font)
        current_y += row_height

    return image


def render_stats_visual(width, height, title_text, stats_data, title_font,
                        stats_font, icon_font, stats_font_size,
                        title_font_size):
    """Visual rendering with progress bars"""
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    y_offset = 10
    row_height = int(stats_font_size * 1.8)
    icon_x = 10
    bar_start_x = 40
    bar_width = width - bar_start_x - 10
    bar_height = int(stats_font_size * 1.2)
    title_spacing = int(title_font_size * 1.5)

    bar_font_size = int(stats_font_size * 0.7)
    try:
        bar_font = ImageFont.truetype(MAIN_FONT, bar_font_size)
    except OSError:
        bar_font = ImageFont.load_default()

    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset),
              title_text,
              fill=COLOR_MAP['white'],
              font=title_font)

    current_y = y_offset + title_spacing

    for stat_data in stats_data:
        draw.text((icon_x, current_y),
                  stat_data['icon'],
                  fill=COLOR_MAP[stat_data['icon_color']],
                  font=icon_font)

        if stat_data['has_bar']:
            fill_width = int((bar_width * stat_data['percentage']) / 100)
            bar_y = current_y + int((stats_font_size - bar_height) / 2)

            draw.rectangle([
                bar_start_x, bar_y, bar_start_x + bar_width, bar_y + bar_height
            ],
                           fill=(40, 40, 40),
                           outline=(80, 80, 80))

            if fill_width > 0:
                draw.rectangle([
                    bar_start_x, bar_y, bar_start_x + fill_width,
                    bar_y + bar_height
                ],
                               fill=COLOR_MAP[stat_data['bar_color']])

            label_text = stat_data['label']
            label_bbox = draw.textbbox((0, 0), label_text, font=bar_font)
            label_width = label_bbox[2] - label_bbox[0]
            label_height = label_bbox[3] - label_bbox[1]

            if label_width < (bar_width - 10):
                text_x = bar_start_x + (bar_width - label_width) // 2
                text_y = bar_y + (bar_height -
                                  label_height) // 2 - label_bbox[1]
                text_color = (0, 0, 0)
                stroke_color = COLOR_MAP[stat_data['bar_color']]
                draw.text((text_x, text_y),
                          label_text,
                          fill=text_color,
                          font=bar_font,
                          stroke_width=1,
                          stroke_fill=stroke_color)
            else:
                text_x = bar_start_x + bar_width + 5
                text_y = current_y
                draw.text((text_x, text_y),
                          label_text,
                          fill=COLOR_MAP['white'],
                          font=bar_font)
        else:
            draw.text((bar_start_x, current_y),
                      stat_data['label'],
                      fill=COLOR_MAP[stat_data['bar_color']],
                      font=stats_font)

        current_y += row_height

    return image


def render_stats_grid(width, height, title_text, stats_data, title_font,
                      stats_font, icon_font, stats_font_size, title_font_size):
    """Grid layout rendering with 2xn arrangement"""
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    y_offset = 10
    x_margin = 10
    grid_spacing = 8
    title_spacing = int(title_font_size * 1.2)

    grid_font_size = int(stats_font_size * 0.65)
    try:
        grid_font = ImageFont.truetype(MAIN_FONT, grid_font_size)
    except OSError:
        grid_font = ImageFont.load_default()

    cell_width = (width - 2 * x_margin - grid_spacing) // 2
    cell_height = int(stats_font_size * 1.5)
    bar_height = int(stats_font_size * 0.9)

    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset),
              title_text,
              fill=COLOR_MAP['white'],
              font=title_font)

    current_y = y_offset + title_spacing

    ip_data = None
    grid_stats = []
    for stat_data in stats_data:
        if not stat_data['has_bar']:
            ip_data = stat_data
        else:
            grid_stats.append(stat_data)

    if ip_data:
        draw.text((x_margin, current_y),
                  ip_data['icon'],
                  fill=COLOR_MAP[ip_data['icon_color']],
                  font=icon_font)
        draw.text((x_margin + 30, current_y),
                  ip_data['label'],
                  fill=COLOR_MAP[ip_data['bar_color']],
                  font=stats_font)
        current_y += int(stats_font_size * 1.6)

    for i in range(0, len(grid_stats), 2):
        row_y = current_y

        if i < len(grid_stats):
            stat_data = grid_stats[i]
            cell_x = x_margin
            _draw_grid_cell(draw, stat_data, cell_x, row_y, cell_width,
                            cell_height, bar_height, grid_font, icon_font,
                            stats_font_size)

        if i + 1 < len(grid_stats):
            stat_data = grid_stats[i + 1]
            cell_x = x_margin + cell_width + grid_spacing
            _draw_grid_cell(draw, stat_data, cell_x, row_y, cell_width,
                            cell_height, bar_height, grid_font, icon_font,
                            stats_font_size)

        current_y += cell_height + grid_spacing

    return image


def _draw_grid_cell(draw, stat_data, x, y, cell_width, cell_height, bar_height,
                    grid_font, icon_font, stats_font_size):
    """Draw a single grid cell with icon, bar, and label"""
    icon_size = int(stats_font_size * 1.2)
    bar_y = y
    bar_x = x + icon_size + 2
    bar_width = cell_width - 4 - icon_size

    icon_bbox = draw.textbbox((0, 0), stat_data['icon'], font=icon_font)
    icon_x = x 
    draw.text((icon_x, y),
              stat_data['icon'],
              fill=COLOR_MAP[stat_data['icon_color']],
              font=icon_font)

    fill_width = int((bar_width * stat_data['percentage']) / 100)

    draw.rectangle([bar_x + 2, bar_y, bar_x + 2 + bar_width, bar_y + bar_height],
                   fill=(40, 40, 40),
                   outline=(80, 80, 80))

    if fill_width > 0:
        draw.rectangle([bar_x + 2, bar_y, bar_x + 2 + fill_width, bar_y + bar_height],
                       fill=COLOR_MAP[stat_data['bar_color']])

    label_text = stat_data['label']
    label_bbox = draw.textbbox((0, 0), label_text, font=grid_font)
    label_width = label_bbox[2] - label_bbox[0]
    label_height = label_bbox[3] - label_bbox[1]

    if label_width < (bar_width - 6):
        text_x = bar_x + 2 + (bar_width - label_width) // 2
        text_y = bar_y + (bar_height - label_height) // 2 - label_bbox[1]
        text_color = (0, 0, 0)
        stroke_color = COLOR_MAP[stat_data['bar_color']]
        draw.text((text_x, text_y),
                  label_text,
                  fill=text_color,
                  font=grid_font,
                  stroke_width=1,
                  stroke_fill=stroke_color)

    else:
        text_x = bar_x + (cell_width - label_width) // 2
        text_y = bar_y + bar_height + 2
        draw.text((text_x, text_y),
                  label_text,
                  fill=COLOR_MAP['white'],
                  font=grid_font)
