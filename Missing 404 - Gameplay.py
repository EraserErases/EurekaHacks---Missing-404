import pygame
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Light Ascent")

# Load images
try:
    original_tree = pygame.image.load("deadtree.jpeg.png")
    background = pygame.transform.scale(original_tree, (WIDTH, HEIGHT))
    image_right = pygame.image.load("Default_guy_final.gif")
    image_left = pygame.image.load("Default_guy_around.gif")
    dirt_texture = pygame.image.load("FRLcSi.png")
    cliff_image = pygame.image.load("cliff.png")  # Make sure to have this image
    cliff_image = pygame.transform.scale(cliff_image, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Could not load image: {e}")
    pygame.quit()
    sys.exit()

# Game settings
character_x = 100  # Initial X position (relative to screen)
character_y = HEIGHT - (HEIGHT // 8) - image_right.get_height()
scroll_x = 0  # Tracks horizontal scrolling
character_speed = 5
gravity = 0.8
jump_speed = -15
velocity_y = 0
facing_left = False
on_ground = True

# Airwall settings
AIRWALL_LEFT = 50  # Global left boundary (in world coordinates)
airwall_visible = True  # Toggle with 'v' key

# Task system
current_task = "Find Parents"
screens_moved = 0
TASK_CHANGE_THRESHOLD = 12  # Changed from 20 to 12
CLIFF_SCENE = 16  # Slide where cliff scene appears
font = pygame.font.SysFont('Arial', 24)

# Game state
in_cliff_scene = False
cliff_scene_timer = 0
CLIFF_SCENE_DURATION = 180  # 3 seconds at 60 FPS
cliff_character_y = HEIGHT - (HEIGHT // 8) - image_right.get_height() - 200  # 200 pixels higher
cliff_character_x = WIDTH//2 - image_right.get_width()//2 - 100  # 100 pixels back from center

# Lightened backgrounds (now 5% increments from 100% to 60%)
lightened_backgrounds = []
for darkness in range(100, 59, -5):  # Changed from -10 to -5
    light_surface = pygame.Surface((WIDTH, HEIGHT))
    subtract_value = 255 * (100 - darkness) // 100
    light_surface.fill((subtract_value, subtract_value, subtract_value))
    bg_copy = background.copy()
    bg_copy.blit(light_surface, (0, 0), special_flags=pygame.BLEND_SUB)
    lightened_backgrounds.append(bg_copy)

# Ground setup
dirt_height = HEIGHT // 8
texture_ratio = dirt_texture.get_width() / dirt_texture.get_height()
dirt_texture = pygame.transform.scale(dirt_texture, (int(dirt_height * texture_ratio), dirt_height))

clock = pygame.time.Clock()
running = True

def get_current_background():
    lightness_level = min(scroll_x // WIDTH, len(lightened_backgrounds)-1)
    return lightened_backgrounds[lightness_level]

def update_task():
    global current_task, screens_moved, in_cliff_scene, cliff_scene_timer
    screens_moved = scroll_x // WIDTH
    
    if screens_moved == CLIFF_SCENE and not in_cliff_scene:  # Changed to == for exact slide
        in_cliff_scene = True
        cliff_scene_timer = 0
    
    if screens_moved >= TASK_CHANGE_THRESHOLD:
        current_task = "RUN!"
    else:
        current_task = "Find Parents"

def draw_task_list():
    task_text = f"Task: {current_task}"
    text_color = (255, 0, 0) if current_task == "RUN!" else (255, 255, 255)
    text_surface = font.render(task_text, True, text_color)
    screen.blit(text_surface, (WIDTH - 200, 20))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and on_ground and not in_cliff_scene:
                velocity_y = jump_speed
                on_ground = False
            if event.key == pygame.K_r:  # Reset
                character_x, scroll_x = 100, 0
                character_y = HEIGHT - dirt_height - image_right.get_height()
                velocity_y = 0
                current_task = "Find Parents"
                screens_moved = 0
                in_cliff_scene = False
                cliff_scene_timer = 0
            if event.key == pygame.K_v:  # Toggle airwall visibility
                airwall_visible = not airwall_visible

    if not in_cliff_scene:
        # Movement and physics (unchanged)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            if (scroll_x + character_x - character_speed) >= AIRWALL_LEFT:
                character_x -= character_speed
                facing_left = True
            elif scroll_x > 0 and character_x <= 0:
                scroll_x = max(0, scroll_x - character_speed)
                character_x = WIDTH - character_speed

        if keys[pygame.K_d]:
            character_x += character_speed
            facing_left = False
            if character_x > WIDTH:
                character_x = 0
                scroll_x += WIDTH

        update_task()
        
        # Apply gravity
        velocity_y += gravity
        character_y += velocity_y

        # Ground collision
        if character_y >= HEIGHT - dirt_height - image_right.get_height():
            character_y = HEIGHT - dirt_height - image_right.get_height()
            velocity_y = 0
            on_ground = True
    else:
        # In cliff scene - freeze controls and show cliff
        cliff_scene_timer += 1
        if cliff_scene_timer >= CLIFF_SCENE_DURATION:
            in_cliff_scene = False
            # Move player past the cliff scene
            scroll_x = (CLIFF_SCENE + 1) * WIDTH
            character_x = 100
            # Reset character position after cliff scene
            character_y = HEIGHT - dirt_height - image_right.get_height()

    # Drawing
    if scroll_x // WIDTH == CLIFF_SCENE:  # Only remove grass on the cliff slide
        # Draw just the cliff background (no ground/dirt)
        screen.blit(cliff_image, (0, 0))
        if in_cliff_scene:
            # Draw character standing still, 200 pixels higher and 100 pixels back
            screen.blit(image_right, (cliff_character_x, cliff_character_y))
    else:
        current_bg = get_current_background()
        screen.blit(current_bg, (0, 0))
        
        # Draw dirt floor
        tile_width = dirt_texture.get_width()
        offset_x = scroll_x % tile_width
        for i in range(-1, (WIDTH // tile_width) + 2):
            screen.blit(dirt_texture, (i * tile_width - offset_x, HEIGHT - dirt_height))
        
        # Draw character
        current_image = image_left if facing_left else image_right
        screen.blit(current_image, (character_x, character_y))
        
        # Draw airwall
        if airwall_visible:
            airwall_screen_x = AIRWALL_LEFT - scroll_x
            if 0 <= airwall_screen_x <= WIDTH:
                pygame.draw.line(screen, (0, 100, 255), (airwall_screen_x, 0), (airwall_screen_x, HEIGHT), 2)
    
    # Draw task list
    draw_task_list()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


