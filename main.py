import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import pygame.gfxdraw
import sys
import math
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='Eye Scan Therapy')
parser.add_argument('--speed', type=float, default=25, help='Oscillation frequency in centihertz (default: 20)')
parser.add_argument('--size', type=int, default=60, help='Diameter of the circle in pixels (default: 60)')
parser.add_argument('--angle', type=float, default=0, help='Angle of the oscillation axis in degrees (default: 0)')
parser.add_argument('--motion', type=str, default='sine', choices=['sine', 'triangle', 'square'], help='Oscillation type (sine, triangle, square)')
parser.add_argument('--theme', type=str, default='ocean', choices=['ocean', 'forest', 'desert', 'night', 'rose'], help='Color theme for the display (default: ocean)')
parser.add_argument('--axes', type=int, default=2, choices=[0, 1, 2], help='How many axes to display: 0, 1, or 2 (default: 2)')
parser.add_argument('--fps', type=int, default=500, help='Frame rate cap (default: 500)')
args = parser.parse_args()

# Color themes for minimal eyestrain
THEMES = {
    'ocean': {
        'BACKGROUND_COLOR': (18, 24, 38),
        'CIRCLE_COLOR': (180, 210, 255),
        'AXIS_COLOR': (120, 170, 220),
        'TEXT_COLOR': (120, 170, 220),
    },
    'forest': {
        'BACKGROUND_COLOR': (22, 32, 24),
        'CIRCLE_COLOR': (170, 210, 160),
        'AXIS_COLOR': (100, 160, 120),
        'TEXT_COLOR': (100, 160, 120),
    },
    'desert': {
        'BACKGROUND_COLOR': (38, 32, 18),
        'CIRCLE_COLOR': (230, 210, 160),
        'AXIS_COLOR': (180, 160, 100),
        'TEXT_COLOR': (180, 160, 100),
    },
    'night': {
        'BACKGROUND_COLOR': (12, 14, 18),
        'CIRCLE_COLOR': (180, 180, 200),
        'AXIS_COLOR': (80, 100, 140),
        'TEXT_COLOR': (80, 100, 140),
    },
    'rose': {
        'BACKGROUND_COLOR': (32, 24, 28),
        'CIRCLE_COLOR': (255, 200, 210),
        'AXIS_COLOR': (200, 120, 140),
        'TEXT_COLOR': (200, 120, 140),
    },
}

# Select theme
theme = THEMES[args.theme]
BACKGROUND_COLOR = theme['BACKGROUND_COLOR']
CIRCLE_COLOR = theme['CIRCLE_COLOR']
AXIS_COLOR = theme['AXIS_COLOR']
TEXT_COLOR = theme['TEXT_COLOR']

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Eye Scan Therapy')
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
fps_cap = args.fps
font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 24)

# Window and geometry
width, height = screen.get_size()
center = (width // 2, height // 2)
radius = args.size // 2
angle_rad = math.radians(args.angle)

# Movement axis unit vector
axis1_dx = math.cos(angle_rad)
axis1_dy = math.sin(angle_rad)

# Perpendicular axis unit vector
axis2_dx = -axis1_dy
axis2_dy = axis1_dx

# Compute movement limits (so edge of circle never goes beyond window)
def get_axis_limits():
    t_pos = []
    t_neg = []
    # For each window edge, solve for t where the circle's edge touches the window edge
    # x = center[0] + axis1_dx * t, y = center[1] + axis1_dy * t
    # For left/right edges:
    if axis1_dx != 0:
        for x_edge in [radius, width - radius]:
            t = (x_edge - center[0]) / axis1_dx
            y = center[1] + axis1_dy * t
            if radius <= y <= height - radius:
                if t > 0:
                    t_pos.append(t)
                else:
                    t_neg.append(t)
    # For top/bottom edges:
    if axis1_dy != 0:
        for y_edge in [radius, height - radius]:
            t = (y_edge - center[1]) / axis1_dy
            x = center[0] + axis1_dx * t
            if radius <= x <= width - radius:
                if t > 0:
                    t_pos.append(t)
                else:
                    t_neg.append(t)
    # Choose the smallest positive and largest negative t
    t_min = max([t for t in t_neg if t < 0], default=-min(width, height))
    t_max = min([t for t in t_pos if t > 0], default=min(width, height))
    return t_min, t_max

t_min, t_max = get_axis_limits()

# Oscillation functions
def osc_func(t, motion_type):
    t = t % 1.0
    if motion_type == 'sine':
        return (math.sin(2 * math.pi * t - math.pi/2) + 1) / 2
    elif motion_type == 'triangle':
        return 1 - abs(2 * t - 1)
    elif motion_type == 'square':
        return 1.0 if t < 0.5 else 0.0
    else:
        return t

# Simulation loop
show_dev = False
start_time = pygame.time.get_ticks()
axis_len = max(width, height)
axis1_a = (int(center[0] - axis1_dx * axis_len), int(center[1] - axis1_dy * axis_len))
axis1_b = (int(center[0] + axis1_dx * axis_len), int(center[1] + axis1_dy * axis_len))
axis2_a = (int(center[0] - axis2_dx * axis_len), int(center[1] - axis2_dy * axis_len))
axis2_b = (int(center[0] + axis2_dx * axis_len), int(center[1] + axis2_dy * axis_len))

while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_F1:
                show_dev = not show_dev
    
    # Update state
    current_time = pygame.time.get_ticks()
    elapsed = (current_time - start_time) / 1000.0
    axis_length = t_max - t_min
    period = 100.0 / args.speed if args.speed > 0 else 1.0
    t = (elapsed / period) % 1.0
    pos_factor = osc_func(t, args.motion)
    pos = t_min + pos_factor * (t_max - t_min)
    cx = int(center[0] + axis1_dx * pos)
    cy = int(center[1] + axis1_dy * pos)

    # Rendering
    screen.fill(BACKGROUND_COLOR)
    axis_len = max(width, height)
    axis1_a = (int(center[0] - axis1_dx * axis_len), int(center[1] - axis1_dy * axis_len))
    axis1_b = (int(center[0] + axis1_dx * axis_len), int(center[1] + axis1_dy * axis_len))
    axis2_a = (int(center[0] - axis2_dx * axis_len), int(center[1] - axis2_dy * axis_len))
    axis2_b = (int(center[0] + axis2_dx * axis_len), int(center[1] + axis2_dy * axis_len))

    if args.axes == 1:
        pygame.draw.aaline(screen, AXIS_COLOR, axis1_a, axis1_b, 1)
    elif args.axes == 2:
        pygame.draw.aaline(screen, AXIS_COLOR, axis1_a, axis1_b, 1)
        pygame.draw.aaline(screen, AXIS_COLOR, axis2_a, axis2_b, 1)

    pygame.gfxdraw.aacircle(screen, cx, cy, radius, CIRCLE_COLOR)
    pygame.gfxdraw.filled_circle(screen, cx, cy, radius, CIRCLE_COLOR)

    if show_dev:
        fps = int(clock.get_fps())
        dev_lines = [
            f"Angle: {int(round(args.angle))}°",
            f"Size: {args.size} px",
            f"Speed: {args.speed} cHz",
            f"Motion: {args.motion}",
            f"Theme: {args.theme}",
            f"FPS: {fps_cap} / {fps}",
        ]
        for i, line in enumerate(dev_lines):
            surf = font.render(line, True, TEXT_COLOR)
            screen.blit(surf, (10, 10 + i*28))
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps_cap)
