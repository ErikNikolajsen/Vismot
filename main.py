import pygame
import sys
import math
import argparse
import pygame.gfxdraw

# Argument parsing
parser = argparse.ArgumentParser(description='Eye Scan Therapy: Track a moving circle with your eyes.')
parser.add_argument('--speed', type=float, default=300, help='Oscillation speed in pixels per second (default: 300)')
parser.add_argument('--size', type=int, default=60, help='Diameter of the circle in pixels (default: 60)')
parser.add_argument('--angle', type=float, default=0, help='Angle of the oscillation axis in degrees (default: 0)')
parser.add_argument('--motion', type=str, default='sin', choices=['sin', 'triangle', 'square'], help='Oscillation type (sin, triangle, square)')
parser.add_argument('--theme', type=str, default='ocean', choices=['ocean', 'forest', 'desert', 'night', 'rose'], help='Color theme for the display (default: ocean)')
args = parser.parse_args()

# Color themes for minimal eyestrain
THEMES = {
    'ocean': {
        'BG_COLOR': (18, 24, 38),
        'CIRCLE_COLOR': (180, 210, 255),
        'AXIS_COLOR': (120, 170, 220),
        'TEXT_COLOR': (120, 170, 220),
    },
    'forest': {
        'BG_COLOR': (22, 32, 24),
        'CIRCLE_COLOR': (170, 210, 160),
        'AXIS_COLOR': (100, 160, 120),
        'TEXT_COLOR': (100, 160, 120),
    },
    'desert': {
        'BG_COLOR': (38, 32, 18),
        'CIRCLE_COLOR': (230, 210, 160),
        'AXIS_COLOR': (180, 160, 100),
        'TEXT_COLOR': (180, 160, 100),
    },
    'night': {
        'BG_COLOR': (12, 14, 18),
        'CIRCLE_COLOR': (180, 180, 200),
        'AXIS_COLOR': (80, 100, 140),
        'TEXT_COLOR': (80, 100, 140),
    },
    'rose': {
        'BG_COLOR': (32, 24, 28),
        'CIRCLE_COLOR': (255, 200, 210),
        'AXIS_COLOR': (200, 120, 140),
        'TEXT_COLOR': (200, 120, 140),
    },
}

# Select theme
theme = THEMES[args.theme]
BG_COLOR = theme['BG_COLOR']
CIRCLE_COLOR = theme['CIRCLE_COLOR']
AXIS_COLOR = theme['AXIS_COLOR']
TEXT_COLOR = theme['TEXT_COLOR']

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Eye Scan Therapy')
clock = pygame.time.Clock()
fps_cap = 60
pygame.mouse.set_visible(False)


# Window and geometry
width, height = screen.get_size()
center = (width // 2, height // 2)
radius = args.size // 2
angle_rad = math.radians(args.angle)

# Axis vector (unit vector)
axis_dx = math.cos(angle_rad)
axis_dy = math.sin(angle_rad)

# Perpendicular axis
perp_dx = -axis_dy
perp_dy = axis_dx

# Compute movement limits (so edge of circle never goes beyond window)
def get_axis_limits():
    t_pos = []
    t_neg = []
    # For each window edge, solve for t where the circle's edge touches the window edge
    # x = center[0] + axis_dx * t, y = center[1] + axis_dy * t
    # For left/right edges:
    if axis_dx != 0:
        for x_edge in [radius, width - radius]:
            t = (x_edge - center[0]) / axis_dx
            y = center[1] + axis_dy * t
            if radius <= y <= height - radius:
                if t > 0:
                    t_pos.append(t)
                else:
                    t_neg.append(t)
    # For top/bottom edges:
    if axis_dy != 0:
        for y_edge in [radius, height - radius]:
            t = (y_edge - center[1]) / axis_dy
            x = center[0] + axis_dx * t
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
    if motion_type == 'sin':
        return (math.sin(2 * math.pi * t - math.pi/2) + 1) / 2
    elif motion_type == 'triangle':
        # Normalized triangle wave in [0,1]
        return 1 - abs(2 * t - 1)
    elif motion_type == 'square':
        return 1.0 if t < 0.5 else 0.0
    else:
        return t

# Developer mode toggle
show_dev = False
font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 24)

# Main loop
start_time = pygame.time.get_ticks() / 1000.0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_F1:
                show_dev = not show_dev
    now = pygame.time.get_ticks() / 1000.0
    elapsed = now - start_time
    axis_length = t_max - t_min
    period = 2 * axis_length / args.speed if args.speed > 0 else 1
    t = (elapsed / period) % 1.0
    pos_factor = osc_func(t, args.motion)
    pos = t_min + pos_factor * (t_max - t_min)
    cx = int(center[0] + axis_dx * pos)
    cy = int(center[1] + axis_dy * pos)
    screen.fill(BG_COLOR)
    axis_len = max(width, height)
    ax1 = (int(center[0] - axis_dx * axis_len), int(center[1] - axis_dy * axis_len))
    ax2 = (int(center[0] + axis_dx * axis_len), int(center[1] + axis_dy * axis_len))
    perp1 = (int(center[0] - perp_dx * axis_len), int(center[1] - perp_dy * axis_len))
    perp2 = (int(center[0] + perp_dx * axis_len), int(center[1] + perp_dy * axis_len))
    pygame.draw.aaline(screen, AXIS_COLOR, ax1, ax2, 1)
    pygame.draw.aaline(screen, AXIS_COLOR, perp1, perp2, 1)
    pygame.gfxdraw.aacircle(screen, cx, cy, radius, CIRCLE_COLOR)
    pygame.gfxdraw.filled_circle(screen, cx, cy, radius, CIRCLE_COLOR)
    # Developer mode info
    if show_dev:
        fps = int(clock.get_fps())
        dev_lines = [
            f"Angle: {args.angle}°",
            f"Size: {args.size} px",
            f"Speed: {args.speed} px/s",
            f"Motion: {args.motion}",
            f"Theme: {args.theme}",
            f"FPS: {fps_cap} / {fps}",
        ]
        for i, line in enumerate(dev_lines):
            surf = font.render(line, True, TEXT_COLOR)
            screen.blit(surf, (10, 10 + i*28))
    pygame.display.flip()
    clock.tick(fps_cap)

pygame.quit()
sys.exit()
