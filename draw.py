#!/usr/bin/env python

from PIL import Image, ImageDraw
import math
import numpy as np
import random


image_width = image_height = 800
#image_width = 2880
#image_height = 1800
scale = 9

lowres_image_width = image_width * scale
lowres_image_height = image_height * scale

DEFAULT_ELEM_PER_CELL = 1
DEFAULT_CELL_SIZE = 50
DEFAULT_CELL_BUFFER = 0.15


def make_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return (red, green, blue)


def draw_triangles(draw):
    """
    Draws the triangle foreground pattern.

    :param draw: the Draw object
    :type draw: ImageDraw.Draw
    """
    draw_in_grid(draw, draw_triangle)


def draw_triangle(draw, center_x, center_y, theta=0):
    """
    Draw a triangle at a given point.

    :param draw: the Draw object
    :type draw: ImageDraw.Draw
    :param center_x: the x coordinate of the triangle's center
    :type center_x: int
    :param center_y: the y coordinate of the triangle's center
    :type center_y: int
    """
    def rotate(coords, theta):
        x, y = coords
        x1 = x * math.cos(theta) - y * math.sin(theta)
        y1 = y * math.cos(theta) + x * math.sin(theta)
        return (x1, y1)

    def translate(coords, x, y):
        return (coords[0] + x, coords[1] + y)

    def offset(coords):
        x_off = 10
        y_off = 15
        return (coords[0] + x_off, coords[1] + y_off)

    color = make_random_color()

    # Make it an equilateral triangle
    base = 200
    height = math.sqrt(3) / 2 * base
    points = [
        (base / 2, height / 2),
        (0, -height / 2),
        (-base / 2, height / 2)
    ]
    points = [translate(rotate(x, theta), center_x, center_y) for x in points]
    shadow_points = points
    shadow_points = [offset(x) for x in points]

    draw.polygon(shadow_points, fill=(45, 112, 255))
    draw.polygon(points, fill=(247, 123, 233))


def draw_pills(draw):
    """
    Draws the "pills" background pattern.

    :param draw: the Draw object
    :type draw: ImageDraw.Draw
    """
    draw_in_grid(draw, draw_pill, 1, 35, cell_buffer=0.3)


def draw_pill(draw, x, y, theta):
    pill_length = 70
    pill_radius = pill_length / 2
    circle_distance = pill_length - pill_radius
    center = (x, y)
    fill1 = (255, 255, 255)
    fill2 = (61, 181, 44)

    angle = math.radians(random.randint(0, 360))
    offset = (circle_distance * math.cos(angle), circle_distance * math.sin(angle))

    # calculate circle centers
    start_coords = np.subtract(center, offset)
    end_coords = np.add(center, offset)

    # calculate rectangle endpoints
    dv = np.subtract(end_coords, start_coords)
    len_dv = np.sqrt(np.dot(dv, dv))
    unit_dv = np.divide(dv, len_dv)
    perp_dv_1 = np.multiply((unit_dv[1], unit_dv[0]), (pill_radius, -pill_radius))
    perp_dv_2 = np.multiply((unit_dv[1], unit_dv[0]), (-pill_radius, pill_radius))

    start_rect_coords = [
        tuple(start_coords + perp_dv_1),
        tuple(start_coords + perp_dv_2),
        tuple(center + perp_dv_2),
        tuple(center + perp_dv_1)
    ]
    end_rect_coords = [
        tuple(center + perp_dv_1),
        tuple(center + perp_dv_2),
        tuple(end_coords + perp_dv_2),
        tuple(end_coords + perp_dv_1)
    ]

    # draw circles and joining rectangles
    draw_circle(draw, start_coords, pill_radius, fill1)
    draw.polygon(start_rect_coords, fill=fill1)

    draw_circle(draw, end_coords, pill_radius, fill2)
    draw.polygon(end_rect_coords, fill=fill2)


def draw_circle(draw, center, radius, fill=None):
    """
    Draw a circle at a given point.

    :param draw: the Draw object
    :type draw: ImageDraw.Draw
    :param center: the coordinates of the circle's center
    :type center: (int, int)
    :param radius: the radius of the circle
    :type radius: int
    :param fill: the fill color to use; otherwise fill will be random
    :type fill: (num, num, num) or None
    """
    center_x, center_y = center
    circle_coords = (center_x - radius, center_y - radius, center_x + radius, center_y + radius)
    color = fill if fill else make_random_color()
    draw.ellipse(circle_coords, fill=color)


def draw_in_grid(draw, func, elements_per_cell=DEFAULT_ELEM_PER_CELL, cell_size=DEFAULT_CELL_SIZE,
                 show_grid=False, cell_buffer=DEFAULT_CELL_BUFFER):
    """
    Draw an element separated into cells on a grid.

    :param func: the draw function to call
    :type func: (int, int, float) -> None
    """
    num_rows = math.ceil(image_height / cell_size)
    num_cols = math.ceil(image_width / cell_size)
    for i in range(num_cols):
        min_x = int(lowres_image_width / num_cols * (i + cell_buffer))
        max_x = int(lowres_image_width / num_cols * (i + 1 - cell_buffer))
        for j in range(num_rows):
            min_y = int(lowres_image_height / num_rows * (j + cell_buffer))
            max_y = int(lowres_image_height / num_rows * (j + 1 - cell_buffer))
            if show_grid:
                draw.rectangle([(min_x, min_y), (max_x, max_y)], outline=(255, 255, 255))
            for k in range(elements_per_cell):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                theta = math.radians(random.randint(0, 360))
                func(draw, x, y, theta)


def draw_pattern(draw):
    """
    Draws the main pattern.

    :param draw: the Draw object
    :type draw: ImageDraw.Draw
    """
    tmp_img = Image.new('RGBA', (lowres_image_width, lowres_image_height), (0, 0, 0, 0))
    tmp_draw = ImageDraw.Draw(tmp_img)

    draw_pills(tmp_draw)
    draw_triangles(tmp_draw)

    return tmp_img


def main(argv=None):
    out_file = 'out.png'
    
    im = Image.new('RGBA', (lowres_image_width, lowres_image_height), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    
    # Draw the background
    image_bounds = (0, 0, lowres_image_width, lowres_image_height)
    #lbg = (255, 255, 243)
    bg = (255, 244, 153)
    dr.rectangle(image_bounds, fill=bg)

    pattern = draw_pattern(dr)
    im = Image.alpha_composite(im, pattern)

    im = im.resize((image_width, image_height), Image.ANTIALIAS)
    im.save(out_file, 'PNG')


if __name__ == '__main__':
    main()
