import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import pygame.gfxdraw
import sys
import math
import argparse
import time

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
        return 0.0 if t < 0.5 else 1.0
    else:
        return t

# Key state tracking for speed adjustment
speed_step = 1  # 1 cHz per step
min_speed = 1   # 0.01 Hz
max_speed = 100  # 1 Hz
speed_adjust_active = False
speed_adjust_last = 0
speed_adjust_delay = 0.15  # seconds between increments

# Key state tracking for size adjustment
size_step = 1  # pixels per step
min_size = 1
max_size = min(width, height)  # never allow the circle to be larger than the window
size_adjust_active = False
size_adjust_last = 0
size_adjust_delay = 0.15  # seconds between increments

# Key state tracking for angle adjustment
angle_step = 1  # degrees per step
angle_adjust_active = False
angle_adjust_last = 0
angle_adjust_delay = 0.15  # seconds between increments

# Key state tracking for motion type adjustment
motion_types = ['sine', 'triangle', 'square']
motion_step = 1  # index step
motion_adjust_active = False
motion_adjust_last = 0
motion_adjust_delay = 0.15  # seconds between increments

# Key state tracking for axes adjustment
axes_options = [0, 1, 2]
axes_step = 1
axes_adjust_active = False
axes_adjust_last = 0
axes_adjust_delay = 0.15  # seconds between increments

# Key state tracking for theme adjustment
THEME_NAMES = list(THEMES.keys())
theme_step = 1
theme_adjust_active = False
theme_adjust_last = 0
theme_adjust_delay = 0.15  # seconds between increments

# Key state tracking for fps cap adjustment
fps_step = 10
min_fps = 30
max_fps = 1000
fps_adjust_active = False
fps_adjust_last = 0
fps_adjust_delay = 0.15  # seconds between increments

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
            elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                speed_adjust_active = True
            elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                size_adjust_active = True
            elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                angle_adjust_active = True
            elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                motion_adjust_active = True
            elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                axes_adjust_active = True
            elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                theme_adjust_active = True
            elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                fps_adjust_active = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                speed_adjust_active = False
            if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                size_adjust_active = False
            if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                angle_adjust_active = False
            if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                motion_adjust_active = False
            if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                axes_adjust_active = False
            if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                theme_adjust_active = False
            if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                fps_adjust_active = False

    # Handle speed adjustment if 3 is held
    if speed_adjust_active:
        now = time.time()
        if now - speed_adjust_last > speed_adjust_delay:
            keys = pygame.key.get_pressed()
            # Save old period and elapsed before changing speed
            old_speed = args.speed
            old_period = 100.0 / old_speed if old_speed > 0 else 1.0
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - start_time) / 1000.0
            t_phase = (elapsed / old_period) % 1.0
            if keys[pygame.K_RIGHT]:
                args.speed = min(args.speed + speed_step, max_speed)
                speed_adjust_last = now
            elif keys[pygame.K_LEFT]:
                args.speed = max(args.speed - speed_step, min_speed)
                speed_adjust_last = now
            # After changing speed, adjust start_time to preserve phase
            new_period = 100.0 / args.speed if args.speed > 0 else 1.0
            # new_elapsed = t_phase * new_period
            # So, start_time = current_time - new_elapsed * 1000
            new_elapsed = t_phase * new_period
            start_time = current_time - int(new_elapsed * 1000)

    # Handle size adjustment if 2 is held
    if size_adjust_active:
        now = time.time()
        if now - size_adjust_last > size_adjust_delay:
            keys = pygame.key.get_pressed()
            old_size = args.size
            if keys[pygame.K_RIGHT]:
                args.size = min(args.size + size_step, max_size)
                size_adjust_last = now
            elif keys[pygame.K_LEFT]:
                args.size = max(args.size - size_step, min_size)
                size_adjust_last = now
            if args.size != old_size:
                radius = args.size // 2
                # Recompute t_min, t_max to keep edge at window edge
                t_min, t_max = get_axis_limits()

    # Handle angle adjustment if 1 is held
    if angle_adjust_active:
        now = time.time()
        if now - angle_adjust_last > angle_adjust_delay:
            keys = pygame.key.get_pressed()
            old_angle = args.angle
            if keys[pygame.K_RIGHT]:
                args.angle = args.angle + angle_step
                angle_adjust_last = now
            elif keys[pygame.K_LEFT]:
                args.angle = args.angle - angle_step
                angle_adjust_last = now
            # Normalize angle to [0, 360)
            args.angle = args.angle % 360
            if args.angle != old_angle:
                angle_rad = math.radians(args.angle)
                axis1_dx = math.cos(angle_rad)
                axis1_dy = -math.sin(angle_rad)
                axis2_dx = -axis1_dy
                axis2_dy = axis1_dx
                t_min, t_max = get_axis_limits()

    # Handle motion type adjustment if 4 is held
    if motion_adjust_active:
        now = time.time()
        if now - motion_adjust_last > motion_adjust_delay:
            keys = pygame.key.get_pressed()
            current_index = motion_types.index(args.motion)
            if keys[pygame.K_RIGHT]:
                new_index = (current_index + motion_step) % len(motion_types)
                args.motion = motion_types[new_index]
                motion_adjust_last = now
                # Reset to start position when motion type changes
                start_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT]:
                new_index = (current_index - motion_step) % len(motion_types)
                args.motion = motion_types[new_index]
                motion_adjust_last = now
                # Reset to start position when motion type changes
                start_time = pygame.time.get_ticks()

    # Handle axes amount adjustment if 6 is held
    if axes_adjust_active:
        now = time.time()
        if now - axes_adjust_last > axes_adjust_delay:
            keys = pygame.key.get_pressed()
            current_index = axes_options.index(args.axes)
            if keys[pygame.K_RIGHT]:
                new_index = (current_index + axes_step) % len(axes_options)
                args.axes = axes_options[new_index]
                axes_adjust_last = now
            elif keys[pygame.K_LEFT]:
                new_index = (current_index - axes_step) % len(axes_options)
                args.axes = axes_options[new_index]
                axes_adjust_last = now

    # Handle theme adjustment if 5 is held
    if theme_adjust_active:
        now = time.time()
        if now - theme_adjust_last > theme_adjust_delay:
            keys = pygame.key.get_pressed()
            current_index = THEME_NAMES.index(args.theme)
            if keys[pygame.K_RIGHT]:
                new_index = (current_index + theme_step) % len(THEME_NAMES)
                args.theme = THEME_NAMES[new_index]
                # Update theme colors live
                theme = THEMES[args.theme]
                BACKGROUND_COLOR = theme['BACKGROUND_COLOR']
                CIRCLE_COLOR = theme['CIRCLE_COLOR']
                AXIS_COLOR = theme['AXIS_COLOR']
                TEXT_COLOR = theme['TEXT_COLOR']
                theme_adjust_last = now
            elif keys[pygame.K_LEFT]:
                new_index = (current_index - theme_step) % len(THEME_NAMES)
                args.theme = THEME_NAMES[new_index]
                # Update theme colors live
                theme = THEMES[args.theme]
                BACKGROUND_COLOR = theme['BACKGROUND_COLOR']
                CIRCLE_COLOR = theme['CIRCLE_COLOR']
                AXIS_COLOR = theme['AXIS_COLOR']
                TEXT_COLOR = theme['TEXT_COLOR']
                theme_adjust_last = now

    # Handle fps cap adjustment if 7 is held
    if fps_adjust_active:
        now = time.time()
        if now - fps_adjust_last > fps_adjust_delay:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                fps_cap = min(fps_cap + fps_step, max_fps)
                fps_adjust_last = now
            elif keys[pygame.K_LEFT]:
                fps_cap = max(fps_cap - fps_step, min_fps)
                fps_adjust_last = now

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
            f"Angle: {int(round(args.angle % 180))}°",
            f"Size: {args.size} px",
            f"Speed: {args.speed} cHz",
            f"Motion: {args.motion}",
            f"Theme: {args.theme}",
            f"Axes: {args.axes}",
            f"FPS: {fps_cap} / {fps}",
        ]
        for i, line in enumerate(dev_lines):
            surf = font.render(line, True, TEXT_COLOR)
            screen.blit(surf, (10, 10 + i*28))
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps_cap)
