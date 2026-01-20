import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# ===============================GLOBAL VARIABLES==============================================
# Player & Enemy Settings
enemy_list = []
grid_size = 500
player_speed = 8
enemy_spead = .8  
bullet_speed = 10
camera_height = 150.0
camera_angle = 0.0
first_persion_camera_mode = False
player_position = [0, 0]
player_rotation_angle = 90.0
player_facing_angle = 90.0
# Player Health & Game State

player_health = 100  
game_score_conter = 0
game_over_flag = False
player_fall_angle = 0
cheat_mode_flag = False
cheat_camera_view = False

# Punch mechanics 
punch_active = False
punch_timer = 0
punch_max_duration = 15
punch_range = 40

#Jump Attack mechanics
jump_attack_active = False
jump_attack_timer = 0
jump_attack_y_timer = 0
jump_attack_max_duration = 25
jump_attack_horizontal_velocity = 0
jump_attack_direction_x = 0
jump_attack_direction_z = 0
jump_attack_angle = 35  
jump_attack_range = 60  
jump_attack_scored = False 

#WORLD SETTINGS
grid_floor_length = 5000 
zone_length = 1000 

#Jump physics
player_is_jumping = False
jump_timer = 0
jump_max_duration = 30
jump_height = 50
player_y_offset = 0
initial_jump_velocity = 2.5 
gravity = 0.15 

#SPINNING FLASH KICK
spin_kick_active = False
spin_kick_timer = 0
spin_kick_max_duration = 30
spin_radius = 120         
spin_force = 18           
spin_hit_registered = False

# ZONE SYSTEM
current_zone = 0 # 0 to 4
enemies_per_zone = 5      
enemies_spawned_in_zone = 0
enemies_killed_in_zone = 0
zone_cleared = False      

# LEVEL & BOSS
game_level = 1
enemy_counter = 0
boss_active = False
boss_bullets = []  
boss_bullet_speed = 8.0
boss_is_shooting = False
boss_shoot_timer = 0
boss_shoot_cooldown = 120 
boss_spawned_flag = False 
boss_hp = game_level * 100 + 100

# HUNTER BLADES
hunter_blades = []
hunter_blade_speed = 7.0

# HTI EFFECTS
hit_effects_list = []

#CHEAT MODE & BOMBS
cheat_active = False 
bomb_list = [] 
bomb_drop_speed = 15
bomb_trigger_distance = 300
explosion_radius_max = 40

#COLLECTIBLES
crate_list = [] 
item_list = [] 
debris_list = [] 
floating_text_list = [] 
crates_per_zone = 3

#TREES, CARS & PARTICLES (NEW ADDITION)
trees_list = []
cars_list = []
fire_particles = []
day_night_timer = 0
DAY_NIGHT_CYCLE_DURATION = 30 * 60  
is_daytime = True
snow_particles = []

#UI STATE
game_paused = False
show_restart_selection = False

# ===============================NEW OBSTACLE & PARTICLE FUNCTIONS==============================================
def initialize_obstacles():
    """Initialize trees and cars for the current level"""
    global trees_list, cars_list, zone_length, grid_size
    trees_list = []
    cars_list = []
    # Generate 8 trees per zone (40 total across 5 zones)
    for zone in range(5):
        zone_start = zone * zone_length if zone > 0 else -grid_size
        zone_end = (zone + 1) * zone_length
        color_variants = ['dark', 'dark', 'medium', 'medium', 'medium', 'light', 'light', 'light']
        tree_types = ['sphere', 'sphere', 'cone', 'cone', 'oval', 'oval', 'sphere', 'cone']
        for i in range(8):
            # Ensure trees don't spawn exactly on the main path (keeping z=0 relatively clear)
            x = random.randint(int(zone_start) + 100, int(zone_end) - 100)
            z_side = random.choice([
                random.randint(int(-grid_size) + 50, -100),
                random.randint(100, int(grid_size) - 50)
            ])
            tree_type = tree_types[i % len(tree_types)]
            color_variant = color_variants[i % len(color_variants)]
            trees_list.append({
                'x': x, 'z': z_side, 'type': tree_type, 
                'size': random.randint(40, 60), 'color': color_variant,
                'height': random.randint(60, 90)
            })
    # Generate 2 cars per zone (some on fire)
    for zone in range(5):
        zone_start = zone * zone_length if zone > 0 else -grid_size
        zone_end = (zone + 1) * zone_length
        for i in range(2):
            x = random.randint(int(zone_start) + 150, int(zone_end) - 150)
            z = random.randint(-200, 200)
            has_fire = random.choice([True, False])
            cars_list.append({'x': x, 'z': z, 'has_fire': has_fire})

def draw_tree(x, z, trunk_height=80, canopy_size=60, tree_type='sphere', color_variant='medium'):
    """Draw a detailed 3D tree"""
    # Tree base/roots
    glColor3f(0.25, 0.15, 0.10)
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 12, 10, 8, 10, 1)
    gluDeleteQuadric(quadric)
    glPopMatrix()
    # Main trunk
    glColor3f(0.35, 0.25, 0.15)
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 10, 8, trunk_height, 12, 1)
    gluDeleteQuadric(quadric)
    glPopMatrix()
    # Choose color based on variant
    if color_variant == 'dark':
        main_color = (0.08, 0.35, 0.08)
        shadow_color = (0.05, 0.25, 0.05)
    elif color_variant == 'light':
        main_color = (0.35, 0.75, 0.35)
        shadow_color = (0.25, 0.65, 0.25)
    else:  # medium
        main_color = (0.20, 0.55, 0.20)
        shadow_color = (0.15, 0.45, 0.15)
    # Draw canopy based on type
    if tree_type == 'sphere':
        glColor3f(*shadow_color)
        glPushMatrix()
        glTranslatef(x, trunk_height - 5, z)
        gluSphere(gluNewQuadric(), canopy_size * 0.9, 16, 16)
        glPopMatrix()
        glColor3f(*main_color)
        glPushMatrix()
        glTranslatef(x, trunk_height, z)
        gluSphere(gluNewQuadric(), canopy_size, 16, 16)
        glPopMatrix()
    elif tree_type == 'cone':
        glColor3f(*shadow_color)
        glPushMatrix()
        glTranslatef(x, trunk_height - 5, z)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), canopy_size * 1.1, 0, canopy_size * 1.6, 12, 1)
        glPopMatrix()
        glColor3f(*main_color)
        glPushMatrix()
        glTranslatef(x, trunk_height, z)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), canopy_size, 0, canopy_size * 1.5, 12, 1)
        glPopMatrix()
    elif tree_type == 'oval':
        glColor3f(*shadow_color)
        glPushMatrix()
        glTranslatef(x, trunk_height - 5, z)
        glScalef(1.1, 1.6, 1.1)
        gluSphere(gluNewQuadric(), canopy_size * 0.9, 16, 16)
        glPopMatrix()
        glColor3f(*main_color)
        glPushMatrix()
        glTranslatef(x, trunk_height, z)
        glScalef(1.0, 1.5, 1.0)
        gluSphere(gluNewQuadric(), canopy_size, 16, 16)
        glPopMatrix()

def draw_car_wreckage(x, z, has_fire=False):
    """Draw a demolished car obstacle with optional fire"""
    # Main body
    glColor3f(0.7, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(x, 15, z)
    glRotatef(-10, 0, 1, 0)
    glScalef(50, 15, 30)
    glutSolidCube(1)
    glPopMatrix()
    # Roof
    glColor3f(0.6, 0.25, 0.08)
    glPushMatrix()
    glTranslatef(x - 5, 22, z)
    glRotatef(-15, 0, 1, 0)
    glScalef(30, 5, 25)
    glutSolidCube(1)
    glPopMatrix()
    # Wheels
    wheel_positions = [(18, -14), (18, 14), (-18, -14), (-18, 14)]
    for wx, wz in wheel_positions:
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(x + wx, 8, z + wz)
        glRotatef(90, 0, 0, 1)
        gluCylinder(gluNewQuadric(), 6, 6, 4, 8, 1)
        glPopMatrix()

def draw_obstacles():
    """Draw all trees and cars"""
    for tree in trees_list:
        draw_tree(tree['x'], tree['z'], tree['height'], tree['size'], tree['type'], tree['color'])
    for car in cars_list:
        draw_car_wreckage(car['x'], car['z'], car.get('has_fire', False))

def check_obstacle_collision(x, z, radius=15):
    """Check if position collides with any obstacle"""
    # Check trees
    for tree in trees_list:
        dx = x - tree['x']
        dz = z - tree['z']
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < tree['size'] * 0.5 + radius: # Adjusted hitbox for trees
            return True
    # Check cars
    for car in cars_list:
        dx = x - car['x']
        dz = z - car['z']
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < 40 + radius:
            return True
    # Check crates (boxes)
    for crate in crate_list:
        dx = x - crate['pos'][0]
        dz = z - crate['pos'][1]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < 20 + radius:
            return True
    return False

def update_day_night_cycle():
    """Update day/night cycle timer"""
    global day_night_timer, is_daytime
    day_night_timer += 1
    if day_night_timer >= DAY_NIGHT_CYCLE_DURATION:
        day_night_timer = 0
        is_daytime = not is_daytime

def update_snow_particles():
    """Update snow particles during night time"""
    global snow_particles
    # Only generate snow at night
    if not is_daytime:
        if random.random() < 0.5:
            snow_particles.append({
                'x': player_position[0] + random.uniform(-500, 500),
                'y': random.uniform(100, 200),
                'z': player_position[1] + random.uniform(-400, 400),
                'vz': random.uniform(-1.5, -0.5),
                'vx': random.uniform(-0.3, 0.3),
                'size': random.uniform(2, 5),
                'life': 300
            })
    # Update existing snow particles
    for particle in snow_particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vz']
        particle['life'] -= 1
        if particle['y'] <= 2 or particle['life'] <= 0:
            snow_particles.remove(particle)

def draw_snow_particles():
    """Draw snow particles as white spheres"""
    glColor3f(1.0, 1.0, 1.0)
    for particle in snow_particles:
        glPushMatrix()
        glTranslatef(particle['x'], particle['y'], particle['z'])
        gluSphere(gluNewQuadric(), particle['size'], 6, 6)
        glPopMatrix()

def update_fire_particles():
    """Update fire particles for cars with fire"""
    global fire_particles
    # Add new fire particles
    for car in cars_list:
        if car.get('has_fire', False) and random.random() < 0.3:
            fire_particles.append({
                'x': car['x'] + random.uniform(-20, 20),
                'z': car['z'] + random.uniform(-10, 10),
                'y': 15 + random.uniform(0, 10),
                'vy': random.uniform(2, 4),
                'life': random.randint(20, 40),
                'size': random.uniform(3, 8),
                'r': 1.0, 'g': random.uniform(0.3, 0.7), 'b': 0.0
            })
    # Update existing particles
    for particle in fire_particles[:]:
        particle['y'] += particle['vy']
        particle['vy'] *= 0.95
        particle['life'] -= 1
        particle['size'] *= 0.97
        if particle['life'] <= 0:
            fire_particles.remove(particle)

def draw_fire_particles():
    """Draw fire particles"""
    for particle in fire_particles:
        glColor3f(particle['r'], particle['g'], particle['b'])
        glPushMatrix()
        glTranslatef(particle['x'], particle['y'], particle['z'])
        gluSphere(gluNewQuadric(), particle['size'], 6, 6)
        glPopMatrix()

# ==============================HIT EFFECTS FUNCTIONS===============================================
def spawn_hit_spark(x, y, z):
    """ Creates a new hit spark at the given location """
    # Timer = 10 frames of life
    hit_effects_list.append({'pos': [x, y, z], 'timer': 10}) 

def draw_hit_effects():
    """ Draws all active hit sparks and removes old ones """
    global hit_effects_list
    # Use a copy of the list to safely remove items while iterating
    for i in range(len(hit_effects_list) - 1, -1, -1):
        effect = hit_effects_list[i]
        # 1. Decrease Timer
        effect['timer'] -= 1
        if effect['timer'] <= 0:
            del hit_effects_list[i]
            continue
        # 2. Draw the Spark (A jagged yellow star)
        x, y, z = effect['pos']
        # Scale the size based on time (Explode outwards)
        # Starts small, gets big, then disappears
        scale = (12 - effect['timer']) * 0.8 
        glPushMatrix()
        glTranslatef(x, y, z)
        # Make the spark always face the camera (optional, but looks better)
        # glRotatef(-camera_angle, 0, 1, 0) 
        glScalef(scale, scale, scale)
        # Draw a jagged star shape
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 1.0, 0.0) # Bright Yellow
        # Center to Top Spike
        glVertex3f(0, 0, 0); glVertex3f(-2, 2, 0); glVertex3f(0, 8, 0)
        glVertex3f(0, 0, 0); glVertex3f(2, 2, 0);  glVertex3f(0, 8, 0)
        # Center to Bottom Spike
        glVertex3f(0, 0, 0); glVertex3f(-2, -2, 0); glVertex3f(0, -8, 0)
        glVertex3f(0, 0, 0); glVertex3f(2, -2, 0);  glVertex3f(0, -8, 0)
        # Center to Left Spike
        glVertex3f(0, 0, 0); glVertex3f(-2, 2, 0); glVertex3f(-8, 0, 0)
        glVertex3f(0, 0, 0); glVertex3f(-2, -2, 0); glVertex3f(-8, 0, 0)
        # Center to Right Spike
        glVertex3f(0, 0, 0); glVertex3f(2, 2, 0);  glVertex3f(8, 0, 0)
        glVertex3f(0, 0, 0); glVertex3f(2, -2, 0); glVertex3f(8, 0, 0)
        # Add a white core for extra brightness
        glColor3f(1.0, 1.0, 1.0)
        glVertex3f(0, 2, 0); glVertex3f(-2, -1, 0); glVertex3f(2, -1, 0)
        glEnd()
        glPopMatrix()

# ====================================SETUP & DRAWING FUNCTIONS=========================================
def camera_setup():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1.25, 1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_persion_camera_mode:
        if cheat_mode_flag and cheat_camera_view:
            gluLookAt(
                player_position[0] + 50, 80, player_position[1] + 50,
                player_position[0], 35, player_position[1],
                0, 1, 0
            )
        else:
            r = math.radians(player_facing_angle)
            gluLookAt(
                player_position[0] + 6.50 * math.sin(r), 50, player_position[1] + 6.50 * math.cos(r),
                player_position[0] + 6.50 * math.sin(r) + 80 * math.sin(r), 50, player_position[1] + 6.50 * math.cos(r) + 80 * math.cos(r),
                0, 1, 0
            )
    else:
        r = math.radians(camera_angle)
        px = player_position[0]
        pz = player_position[1]
        camX = px + 350 * math.sin(r)
        camZ = pz + 350 * math.cos(r)
        gluLookAt(camX, camera_height, camZ, px, 30, pz, 0, 1, 0)

def draw_cheat_bombs():
    for bomb in bomb_list:
        glPushMatrix()
        glTranslatef(bomb['pos'][0], bomb['pos'][1], bomb['pos'][2])
        if bomb['state'] == 'falling':
            glColor3f(1.0, 0.3, 0.0); glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 5, 0, 20, 10, 10); glutSolidSphere(5, 10, 10)       
        elif bomb['state'] == 'exploding':
            progress = bomb['timer'] / 20.0 
            if progress < 0.3: glColor3f(1.0, 1.0, 0.0) 
            elif progress < 0.7: glColor3f(1.0, 0.2, 0.0) 
            else: glColor3f(0.5, 0.5, 0.5) 
            glutSolidSphere(explosion_radius_max * progress, 16, 16)
        glPopMatrix()

def draw_collectibles_and_effects():
    # Draw Crates
    for crate in crate_list:
        glPushMatrix(); glTranslatef(crate['pos'][0], 15, crate['pos'][1])
        glColor3f(0.6, 0.4, 0.2); glutSolidCube(30); glColor3f(0.0, 0.0, 0.0); glutWireCube(30.2); glPopMatrix()
    # Draw Items (Health/Score)
    for item in item_list:
        glPushMatrix(); glTranslatef(item['pos'][0], 15, item['pos'][1]); glRotatef(time.time() * 100, 0, 1, 0)
        if item['type'] == 'health': glColor3f(0.0, 1.0, 0.0); glutSolidSphere(10, 16, 16)
        elif item['type'] == 'score': glColor3f(1.0, 0.8, 0.0); glScalef(1.0, 1.5, 1.0); glutSolidOctahedron()
        glPopMatrix()
    # Draw Debris
    for debris in debris_list:
        glPushMatrix(); glTranslatef(debris['x'], debris['y'], debris['z'])
        glColor3f(0.5, 0.3, 0.1); glutSolidCube(3); glPopMatrix()
    # Draw Floating Text
    for ft in floating_text_list:
        glColor3f(1, 1, 0); glRasterPos3f(ft['x'], ft['y'], ft['z'])
        for ch in ft['text']: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_bounddary_wall():
    wall_h = 50
    # Left Wall
    glColor3f(0,0,1)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size,0,-grid_size); glVertex3f(-grid_size,0,grid_size)
    glVertex3f(-grid_size,wall_h,grid_size); glVertex3f(-grid_size,wall_h,-grid_size)
    glEnd()
    # Back Wall
    glColor3f(1,1,0)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size, 0, grid_size); glVertex3f(grid_floor_length, 0, grid_size)
    glVertex3f(grid_floor_length, wall_h, grid_size); glVertex3f(-grid_size, wall_h, grid_size)
    glEnd()
    # Front Wall
    glColor3f(0,1,0)
    glBegin(GL_QUADS)
    glVertex3f(grid_floor_length, 0, -grid_size); glVertex3f(grid_floor_length, 0, grid_size)
    glVertex3f(grid_floor_length, wall_h, grid_size); glVertex3f(grid_floor_length, wall_h, -grid_size)
    glEnd()
    # Right Wall
    glColor3f(0,0.8,0.8)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size,0,-grid_size); glVertex3f(grid_floor_length,0,-grid_size)
    glVertex3f(grid_floor_length,wall_h,-grid_size); glVertex3f(-grid_size,wall_h,-grid_size)
    glEnd()

def draw_grid_floor():
    global grid_floor_length, grid_size, game_level
    tile_size = 30
    # Level-based color selection
    if game_level == 1: color_1, color_2 = (0.70, 0.75, 0.80), (0.60, 0.65, 0.70)
    elif game_level == 2: color_1, color_2 = (0.25, 0.40, 0.20), (0.35, 0.30, 0.20)
    elif game_level == 3: color_1, color_2 = (0.85, 0.75, 0.60), (0.80, 0.70, 0.55)
    elif game_level == 4: color_1, color_2 = (0.60, 0.60, 0.65), (0.50, 0.50, 0.55)
    else: color_1, color_2 = (1.0, 1.0, 1.0), (0.8, 0.7, 1.0)
    glBegin(GL_QUADS)
    for i in range(-grid_size, grid_floor_length, tile_size):
        for j in range(-grid_size, grid_size, tile_size):
            # Checkerboard color logic
            if (i // tile_size + j // tile_size) % 2 == 0:
                glColor3f(*color_1)
            else:
                glColor3f(*color_2)
            x_start = i
            x_end = min(i + tile_size, grid_floor_length)
            z_start = j
            z_end = min(j + tile_size, grid_size)
            floor_y = -0.1
            
            glVertex3f(x_start, floor_y, z_start)
            glVertex3f(x_end, floor_y, z_start)
            glVertex3f(x_end, floor_y, z_end)
            glVertex3f(x_start, floor_y, z_end)
    glEnd()

def draw_player():
    global player_y_offset
    glPushMatrix()
    glTranslatef(player_position[0], 25 + player_y_offset, player_position[1])
    glRotatef(player_facing_angle, 0, 1, 0)
    if jump_attack_active:
        lean_angle = 30 * (jump_attack_timer / jump_attack_max_duration)
        glRotatef(lean_angle, 1, 0, 0)
    if game_over_flag:
        glRotatef(player_fall_angle, 1, 0, 0)
    q = gluNewQuadric()
    # Body
    glColor3f(0.35, 0.48, 0.28)
    glPushMatrix(); glTranslatef(0, 8, 0); glScalef(2.3, 3.1, 1.5); glutSolidCube(10); glPopMatrix()
    # Head
    glColor3f(0, 0, 0)
    glPushMatrix(); glTranslatef(0, 26, 0); gluSphere(q, 7.5, 22, 22); glPopMatrix()
    # Left Arm
    glColor3f(0.98, 0.83, 0.72)
    glPushMatrix(); glTranslatef(-11.5, 13, 5); gluCylinder(q, 4.2, 4.2, 16, 12, 12); glPopMatrix()
    # Right Arm
    glColor3f(0.98, 0.83, 0.72)
    glPushMatrix(); glTranslatef(11.5, 13, 5)
    if punch_active and not jump_attack_active:
        punch_extension = (punch_timer / punch_max_duration) * 50
        glTranslatef(0, 0, punch_extension)
    gluCylinder(q, 4.2, 4.2, 16, 12, 12)
    glColor3f(1.0, 0.0, 0.0) # Boxing Glove
    glPushMatrix(); glTranslatef(0, 0, 16); gluCylinder(q, 3.8, 0, 6.5, 18, 18); glPopMatrix()
    glPopMatrix()
    # Legs
    for i in [-1, 1]: # -1 left, 1 right
        glPushMatrix()
        glTranslatef(i * 8.5, -3, 0)
        if spin_kick_active:
            spin_angle = (i * spin_kick_timer / spin_kick_max_duration) * 360
            glRotatef(spin_angle, 0, 1, 0); glRotatef(110, 1, 0, 0)
            glColor3f(1.0, 0.4, 0.0)
        elif jump_attack_active and i == 1:
            kick_extension = (jump_attack_timer / jump_attack_max_duration) * 35
            glRotatef(45 + kick_extension, 1, 0, 0); glTranslatef(0, 0, kick_extension * 0.5)
            glColor3f(1.0, 0.3, 0.0)
        else:
            glRotatef(90, 1, 0, 0); glColor3f(0, 0, 0.75)
        gluCylinder(q, 5.2, 5.2, 26, 12, 12)
        glPopMatrix()
    glPopMatrix()

# ENEMY DRAWING FUNCTIONS
def draw_enemy_punk(q, size):
    glColor3f(0.1, 0.2, 0.7) 
    for x in [-4, 4]:
        glPushMatrix(); glTranslatef(x, 0, 0); glRotatef(-90, 1, 0, 0); gluCylinder(q, 3, 3, 14, 8, 8); glPopMatrix()
    glColor3f(0.9, 0.8, 0.1) 
    glPushMatrix(); glTranslatef(0, 25, 0); glScalef(1.2, 1.5, 0.8); glutSolidCube(15); glPopMatrix()
    glColor3f(0.8, 0.6, 0.5) 
    glPushMatrix(); glTranslatef(0, 38, 0); gluSphere(q, 6, 16, 16); glPopMatrix()

def draw_enemy_hunter(q, size):
    glColor3f(0.2, 0.15, 0.1) 
    for x in [-5, 5]:
        glPushMatrix(); glTranslatef(x, 0, 0); glRotatef(-90, 1, 0, 0); gluCylinder(q, 4, 3, 12, 8, 8); glPopMatrix()
    glColor3f(0.1, 0.4, 0.1) 
    glPushMatrix(); glTranslatef(0, 22, 0); glScalef(1.5, 1.4, 1.0); glutSolidCube(15); glPopMatrix()
    glColor3f(0.8, 0.6, 0.5) 
    glPushMatrix(); glTranslatef(0, 35, 0); gluSphere(q, 6, 16, 16); glPopMatrix()

def draw_enemy_dino(q, size):
    glPushMatrix(); glTranslatef(0, 10, 0)
    glColor3f(0.2, 0.6, 0.2) 
    for x in [-5, 5]:
        glPushMatrix(); glTranslatef(x, -10, 5); glRotatef(90, 1, 0, 0); gluCylinder(q, 3, 2, 15, 8, 8); glPopMatrix()
    glColor3f(0.3, 0.8, 0.3) 
    glPushMatrix(); glScalef(1.0, 1.0, 2.0); gluSphere(q, 10, 16, 16); glPopMatrix()
    glColor3f(0.2, 0.6, 0.2)
    glPushMatrix(); glTranslatef(0, 0, -10); glRotatef(180, 0, 1, 0); gluCylinder(q, 8, 1, 25, 12, 12); glPopMatrix()
    glPopMatrix()

def draw_enemy_fat_guy(q, size):
    glColor3f(0.2, 0.3, 0.2) 
    for x in [-10, 10]:
        glPushMatrix(); glTranslatef(x, 0, 0); glRotatef(-90, 1, 0, 0); gluCylinder(q, 5, 5, 16, 10, 10); glPopMatrix()
    glColor3f(0.9, 0.9, 0.9) 
    glPushMatrix(); glTranslatef(0, 24, 0); glScalef(1.5, 1.3, 1.3); gluSphere(q, 13, 20, 20); glPopMatrix()
    glColor3f(0.8, 0.6, 0.5)
    glPushMatrix(); glTranslatef(0, 42, 0); glScalef(1.1, 1.0, 1.1); gluSphere(q, 7, 16, 16); glPopMatrix()

def draw_boss_vice(q):
    glColor3f(0.2, 0.2, 0.2) 
    glPushMatrix(); glTranslatef(0, 10, 0); glScalef(2.5, 4.0, 1.8); glutSolidCube(10); glPopMatrix()
    glColor3f(0.8, 0.6, 0.5)
    glPushMatrix(); glTranslatef(0, 35, 0); gluSphere(q, 8, 16, 16)
    glColor3f(0.1, 0.1, 0.1); glTranslatef(0, 5, 0); glRotatef(-90, 1, 0, 0); gluCylinder(q, 10, 7, 4, 16, 16); glPopMatrix()
    # Arm
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix(); glTranslatef(12, 25, 0)
    if boss_is_shooting: glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 4, 3, 15, 8, 8); glPopMatrix()

def draw_hunter_blades():
    global hunter_blades
    for b in hunter_blades:
        glPushMatrix()
        glTranslatef(b['pos'][0], 25, b['pos'][1])
        glRotatef(b['angle'], 0, 1, 0)
        glColor3f(1.0, 0.0, 0.0); glPushMatrix(); glTranslatef(-3, 0, 0); glScalef(6.0, 0.8, 1.5); glutSolidCube(1); glPopMatrix()
        glColor3f(0.8, 0.7, 0.2); glPushMatrix(); glScalef(1.0, 1.0, 4.0); glutSolidCube(1); glPopMatrix()
        glColor3f(0.9, 0.9, 0.9); glPushMatrix(); glTranslatef(4, 0, 0); glScalef(8.0, 0.2, 2.0); glutSolidCube(1); glPopMatrix()
        glPopMatrix()

def draw_bullets():
    glColor3f(1, 1, 0)
    q = gluNewQuadric()
    for b in boss_bullets:
        glPushMatrix(); glTranslatef(b['pos'][0], 25, b['pos'][1]); gluSphere(q, 3, 8, 8); glPopMatrix()
    draw_hunter_blades()

def draw_enemies():
    for e in enemy_list:
        glPushMatrix()
        glTranslatef(e['enemy_position'][0], e['enemy_position'][1], e['enemy_position'][2])
        dx = player_position[0] - e['enemy_position'][0]
        dz = player_position[1] - e['enemy_position'][2]
        angle = math.degrees(math.atan2(dx, dz))
        glRotatef(angle, 0, 1, 0)
        glScalef(e['enemy_size'], e['enemy_size'], e['enemy_size'])
        q = gluNewQuadric()
        t = e.get('type', 1)
        if t == 1: draw_enemy_punk(q, e['enemy_size'])
        elif t == 2: draw_enemy_hunter(q, e['enemy_size'])
        elif t == 3: draw_enemy_dino(q, e['enemy_size'])
        elif t == 4: draw_enemy_fat_guy(q, e['enemy_size'])
        elif t == 5: draw_boss_vice(q)  
        glPopMatrix()

# ====================================PLAYER ATTACK HITBOX DRAWING=========================================
def draw_jump_attack_hitbox():
    if jump_attack_active:
        glPushMatrix()
        glTranslatef(player_position[0], player_y_offset + 25, player_position[1])
        glRotatef(player_facing_angle, 0, 1, 0)
        progress = jump_attack_timer / jump_attack_max_duration
        glTranslatef(0, -10, 25 + progress * 35)
        glColor3f(1, 0.4, 0) 
        glPushMatrix(); glRotatef(90, 1, 0, 0); gluCylinder(gluNewQuadric(), 12, 8, 30, 16, 16); glPopMatrix()
        glPopMatrix()

def draw_punch_range():
    if punch_active and not jump_attack_active:
        glPushMatrix()
        glTranslatef(player_position[0], 25, player_position[1])
        glRotatef(player_facing_angle, 0, 1, 0)
        glTranslatef(0, 0, 20 + (punch_timer / punch_max_duration) * 20)
        glColor3f(1, 1 - (punch_timer / punch_max_duration) * 0.5, 0)
        gluSphere(gluNewQuadric(), 8 + (punch_timer / punch_max_duration) * 4, 16, 16)
        glPopMatrix()




# ====================================UI & TEXT DRAWING FUNCTIONS=========================================
def draw_ui_buttons():
    glDisable(GL_DEPTH_TEST) 
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    # 1. PLAY / PAUSE (940-980, 750-790)
    glColor3f(0, 1, 0) if game_paused else glColor3f(1, 0.8, 0)
    if game_paused: 
        glBegin(GL_TRIANGLES); glVertex2f(945, 750); glVertex2f(945, 790); glVertex2f(980, 770); glEnd()
    else: 
        glLineWidth(5); glBegin(GL_LINES); glVertex2f(950, 750); glVertex2f(950, 790); glVertex2f(970, 750); glVertex2f(970, 790); glEnd()
    # 2. RESTART BUTTON (940-980, 700-740)
    glColor3f(0, 0.8, 0.8); glBegin(GL_QUADS); glVertex2f(940, 700); glVertex2f(980, 700); glVertex2f(980, 740); glVertex2f(940, 740); glEnd()
    glColor3f(1, 1, 1); glLineWidth(2); glBegin(GL_LINE_STRIP)
    for i in range(270):
        rad = math.radians(i + 45)
        glVertex2f(960 + 10 * math.cos(rad), 720 + 10 * math.sin(rad))
    glEnd()
    glBegin(GL_TRIANGLES); glVertex2f(965, 725); glVertex2f(975, 725); glVertex2f(970, 735); glEnd()
    # 3. EXIT BUTTON (940-980, 650-690)
    glColor3f(1, 0, 0); glLineWidth(5)
    glBegin(GL_LINES); glVertex2f(945, 655); glVertex2f(975, 685); glVertex2f(945, 685); glVertex2f(975, 655); glEnd()
    # RESTART MENU OVERLAY
    if show_restart_selection:
        glColor4f(0, 0, 0, 0.9); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS); glVertex2f(250, 300); glVertex2f(750, 300); glVertex2f(750, 500); glVertex2f(250, 500); glEnd()
        glDisable(GL_BLEND)
        glColor3f(1, 1, 1); writing_text(350, 460, "YOU DIED / RESTART MENU")
        # Option 1: Restart Level
        glColor3f(0, 0.5, 1); glBegin(GL_QUADS); glVertex2f(300, 380); glVertex2f(490, 380); glVertex2f(490, 430); glVertex2f(300, 430); glEnd()
        glColor3f(1, 1, 1); writing_text(320, 400, f"Restart Level {game_level}")
        # Option 2: New Game
        glColor3f(1, 0.5, 0); glBegin(GL_QUADS); glVertex2f(510, 380); glVertex2f(700, 380); glVertex2f(700, 430); glVertex2f(510, 430); glEnd()
        glColor3f(1, 1, 1); writing_text(540, 400, "New Game")
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def writing_text(x, y, s, f=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(f, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_go_sign():
    if zone_cleared and int(time.time() * 2) % 2 == 0:
        glColor3f(0, 1, 0); writing_text(800, 600, "GO! >>>", GLUT_BITMAP_TIMES_ROMAN_24)





# ==================================== LOGIC & UPDATE FUNCTIONS=========================================
def spawn_floating_text(x, y, z, text):
    floating_text_list.append({'x': x, 'y': y, 'z': z, 'text': text, 'life': 50})

def spawn_debris(x, z):
    for _ in range(8):
        debris_list.append({'x': x, 'y': 15, 'z': z, 'vx': random.uniform(-1, 1), 'vy': random.uniform(1, 3), 'vz': random.uniform(-1, 1), 'life': 40})

def spawn_crates_for_zone():
    global crate_list, item_list, current_zone, zone_length
    crate_list.clear(); item_list.clear()
    zone_min_x = -grid_size if current_zone == 0 else current_zone * zone_length
    zone_max_x = (current_zone + 1) * zone_length
    start_x = zone_min_x + 100; end_x = zone_max_x - 100
    if start_x < end_x:
        for _ in range(crates_per_zone):
            crate_list.append({'pos': [random.uniform(start_x, end_x), random.uniform(-grid_size + 50, grid_size - 50)]})

def update_cheat_bombs():
    global game_score_conter, enemies_killed_in_zone
    if cheat_active:
        for e in enemy_list:
            if math.sqrt((player_position[0] - e['enemy_position'][0])**2 + (player_position[1] - e['enemy_position'][2])**2) < bomb_trigger_distance and not e.get('doomed', False):
                e['doomed'] = True 
                bomb_list.append({'pos': [e['enemy_position'][0], 150, e['enemy_position'][2]], 'state': 'falling', 'timer': 0})
    bombs_to_remove, enemies_to_kill_indices = [], []
    for b_idx, bomb in enumerate(bomb_list):
        if bomb['state'] == 'falling':
            bomb['pos'][1] -= bomb_drop_speed
            if bomb['pos'][1] <= 10:
                bomb['state'] = 'exploding'; bomb['timer'] = 0
                for e_idx, e in enumerate(enemy_list):
                    if math.sqrt((bomb['pos'][0] - e['enemy_position'][0])**2 + (bomb['pos'][2] - e['enemy_position'][2])**2) < 20: enemies_to_kill_indices.append(e_idx)
        elif bomb['state'] == 'exploding':
            bomb['timer'] += 1
            if bomb['timer'] > 20: bombs_to_remove.append(b_idx)
    for index in sorted(bombs_to_remove, reverse=True): del bomb_list[index]
    unique_kills = sorted(list(set(enemies_to_kill_indices)), reverse=True)
    for index in unique_kills:
        if index < len(enemy_list):
            spawn_floating_text(enemy_list[index]['enemy_position'][0], 50, enemy_list[index]['enemy_position'][2], "+KILL (CHEAT)")
            del enemy_list[index]; enemies_killed_in_zone += 1; game_score_conter += 1

def update_collectibles_and_visuals():
    global player_health, game_score_conter
    # Update Text
    for ft in floating_text_list: ft['y'] += 1; ft['life'] -= 1
    floating_text_list[:] = [ft for ft in floating_text_list if ft['life'] > 0]
    # Update Debris
    for db in debris_list: db['x'] += db['vx']; db['y'] += db['vy']; db['z'] += db['vz']; db['vy'] -= 0.3; db['life'] -= 1
    debris_list[:] = [db for db in debris_list if db['life'] > 0]
    # Check Crate Destruction
    is_attacking = punch_active or jump_attack_active or spin_kick_active
    crates_broken = []
    if is_attacking:
        for i, crate in enumerate(crate_list):
            dist = math.sqrt((player_position[0] - crate['pos'][0])**2 + (player_position[1] - crate['pos'][1])**2)
            if dist < 50: 
                crates_broken.append(i); spawn_debris(crate['pos'][0], crate['pos'][1])
                item_list.append({'pos': crate['pos'], 'type': random.choice(['health', 'score']), 'value': random.choice([50, 100, 200]), 'timer': 0})
    for i in sorted(crates_broken, reverse=True): del crate_list[i]
    # Check Item Collection
    items_collected = []
    for i, item in enumerate(item_list):
        if math.sqrt((player_position[0] - item['pos'][0])**2 + (player_position[1] - item['pos'][1])**2) < 50:
            items_collected.append(i)
            txt = "+20 HP" if item['type'] == 'health' else f"+{item['value']} PTS"
            spawn_floating_text(item['pos'][0], 40, item['pos'][1], txt)
            if item['type'] == 'health': player_health = min(100, player_health + 20)
            elif item['type'] == 'score': game_score_conter += item.get('value', 50)
    for i in sorted(items_collected, reverse=True): del item_list[i]

def update_boss_bullets():
    global boss_bullets, player_health, game_over_flag
    new_bullets = []
    for b in boss_bullets:
        b['pos'][0] += b['dir'][0] * boss_bullet_speed
        b['pos'][1] += b['dir'][1] * boss_bullet_speed 
        dist = math.sqrt((b['pos'][0] - player_position[0])**2 + (b['pos'][1] - player_position[1])**2)
        if dist < 15:
            player_health -= 15
            if player_health <= 0: game_over_flag = True
            continue 
        if abs(b['pos'][0] - player_position[0]) < 1000: new_bullets.append(b)
    boss_bullets = new_bullets

def update_hunter_blades():
    global hunter_blades, player_health, game_over_flag
    new_blades = []
    for b in hunter_blades:
        b['pos'][0] += b['vel'][0]
        b['pos'][1] += b['vel'][1]
        b['angle'] = (b['angle'] + 20) % 360
        dist = math.sqrt((b['pos'][0] - player_position[0])**2 + (b['pos'][1] - player_position[1])**2)
        if dist < 20: 
            player_health -= 10
            if player_health <= 0: game_over_flag = True
            continue 
        if abs(b['pos'][0] - player_position[0]) < 1200: new_blades.append(b)
    hunter_blades = new_blades

def spawn_boss():
    global enemy_list, current_zone, zone_length, grid_size, player_position, boss_spawned_flag, boss_hp
    zone_min_x = -grid_size if current_zone == 0 else current_zone * zone_length
    spawn_x = player_position[0] + 200
    enemy_list.append({
        "enemy_position": [spawn_x, 10, 0], "enemy_size": 1.5, "size_direction": 1,
        "type": 5, "state": "chasing", "charge_dir": 0 , "hp": boss_hp, "shoot_timer": 0
    })
    print("BOSS SPAWNED!")

def spawn_enemy(i=None, spawn_distance=500):
    global enemy_list, enemy_counter, enemies_spawned_in_zone, enemies_per_zone, current_zone, zone_length
    if current_zone == 0: zone_min_x = -grid_size
    else: zone_min_x = current_zone * zone_length
    zone_max_x = (current_zone + 1) * zone_length
    def get_valid_spawn_x(px, dist):
        proposed_x = px + random.uniform(-dist, dist)
        if proposed_x < zone_min_x + 10: proposed_x = zone_min_x + 10
        elif proposed_x > zone_max_x - 10: proposed_x = zone_max_x - 10
        return proposed_x
    new_enemy = {
        "enemy_position": [0, 10, 0], "enemy_size": 1.3, "size_direction": 1, 
        "type": random.choice([1, 2, 3, 4]), "state": "chasing", "charge_dir": 0,
        "shoot_timer": random.randint(50, 150)
    }
    if i is not None:
        if i < len(enemy_list):
            spawn_x = get_valid_spawn_x(player_position[0], spawn_distance)
            spawn_z = max(-grid_size + 10, min(player_position[1] + random.uniform(-spawn_distance, spawn_distance), grid_size - 10))
            new_enemy["enemy_position"] = [spawn_x, 10, spawn_z]
            enemy_list[i] = new_enemy
        return
    if enemies_spawned_in_zone < enemies_per_zone:
        enemy_counter += 1; enemies_spawned_in_zone += 1
        spawn_x = get_valid_spawn_x(player_position[0], spawn_distance)
        spawn_z = max(-grid_size + 10, min(player_position[1] + random.uniform(-spawn_distance, spawn_distance), grid_size - 10))
        new_enemy["enemy_position"] = [spawn_x, 10, spawn_z]
        enemy_list.append(new_enemy)

def reset_game(level=1, score=0):
    global player_position, player_rotation_angle, player_facing_angle, player_health, game_score_conter, game_over_flag, player_fall_angle, cheat_mode_flag, cheat_camera_view
    global punch_active, punch_timer, jump_attack_active, jump_attack_timer, player_is_jumping, jump_timer, player_y_offset
    global current_zone, enemies_spawned_in_zone, enemies_killed_in_zone, zone_cleared, game_level
    global boss_spawned_flag, enemies_per_zone, boss_hp, hunter_blades, bomb_list, crate_list, item_list
    global game_paused, show_restart_selection
    # NEW GLOBALS RESET
    global trees_list, cars_list, fire_particles, snow_particles, day_night_timer, is_daytime
    trees_list = []
    cars_list = []
    fire_particles = []
    snow_particles = []
    day_night_timer = 0
    is_daytime = True
    hunter_blades.clear(); bomb_list.clear(); crate_list.clear(); item_list.clear()
    player_rotation_angle = 90; player_facing_angle = 90
    game_score_conter = score
    player_position = [0, 0]
    enemy_list.clear()
    game_over_flag = False
    cheat_mode_flag = False; cheat_camera_view = False
    player_health = 100; player_fall_angle = 0
    punch_active = False; punch_timer = 0
    jump_attack_active = False; jump_attack_timer = 0
    player_is_jumping = False; jump_timer = 0; player_y_offset = 0
    current_zone = 0
    game_level = level 
    boss_spawned_flag = False            
    enemies_per_zone = 5                 
    boss_hp = game_level * 100 + 100     
    enemies_spawned_in_zone = 0
    enemies_killed_in_zone = 0
    zone_cleared = False
    game_paused = False
    show_restart_selection = False
    spawn_crates_for_zone()
    initialize_obstacles()
    while len(enemy_list) < 3 and enemies_spawned_in_zone < enemies_per_zone:
        spawn_enemy()

# ===================================INPUT HANDLING==========================================
def keyboard_input(k, x, y):
    global player_rotation_angle, player_facing_angle, cheat_mode_flag, cheat_camera_view, first_persion_camera_mode, player_is_jumping, jump_timer
    global current_zone, zone_cleared, grid_size, zone_length, enemies_killed_in_zone, enemy_list, game_score_conter, cheat_active
    if game_paused: return # Disable movement when paused
    if game_over_flag:
        if k.lower() == b'r': reset_game()
        return
    r = math.radians(player_rotation_angle)
    nx, nz = player_position[0], player_position[1]
    key = k.lower()
    if not jump_attack_active:
        if key == b'd':
            nx += player_speed * math.sin(r); nz += player_speed * math.cos(r)
            player_facing_angle = player_rotation_angle
            zone_limit_x = (current_zone + 1) * zone_length
            if not zone_cleared and nx > zone_limit_x - 50: nx = zone_limit_x - 50
        if key == b'a':
            nx -= player_speed * math.sin(r); nz -= player_speed * math.cos(r)
            player_facing_angle = (player_rotation_angle + 180) % 360
            min_limit = -grid_size if current_zone == 0 else current_zone * zone_length
            if nx < min_limit: nx = min_limit
        if key == b'w': nx += player_speed * math.cos(r); nz -= player_speed * math.sin(r)
        if key == b's': nx -= player_speed * math.cos(r); nz += player_speed * math.sin(r)
        if -grid_size < nx < grid_floor_length and -grid_size < nz < grid_size:
            # Only move if there is no collision with trees/cars
            if not check_obstacle_collision(nx, nz):
                player_position[0], player_position[1] = nx, nz
    if key == b'c':
            cheat_active = not cheat_active 
            if cheat_active:
                print("Cheat Active: Bombs Incoming!")
            else:
                print("Cheat Deactivated")
    if key == b'v':
        if cheat_mode_flag: cheat_camera_view = not cheat_camera_view
        else: cheat_camera_view = False
    if key == b'q': first_persion_camera_mode = not first_persion_camera_mode
    if key == b' ' and not player_is_jumping and not jump_attack_active:
        player_is_jumping = True; jump_timer = 0

def mouse_listner(b, s, x, y):
    global punch_active, punch_timer, jump_attack_active, jump_attack_timer, jump_attack_horizontal_velocity
    global jump_attack_direction_x, jump_attack_direction_z, jump_attack_y_timer, player_is_jumping
    global spin_kick_active, spin_kick_timer, spin_hit_registered
    global game_paused, show_restart_selection, game_over_flag, player_health, current_zone
    adj_y = 800 - y 
    if b == GLUT_LEFT_BUTTON and s == GLUT_DOWN:
        # 1. PLAY/PAUSE
        if 940 <= x <= 980 and 750 <= adj_y <= 790:
            game_paused = not game_paused
            return
        # 2. RESTART MENU
        if 940 <= x <= 980 and 700 <= adj_y <= 740:
            show_restart_selection = not show_restart_selection
            game_paused = True
            return
        # 3. EXIT
        if 940 <= x <= 980 and 650 <= adj_y <= 690:
            os._exit(0)
        if show_restart_selection:
            # Restart Level
            if 300 <= x <= 490 and 380 <= adj_y <= 430:
                player_health = 100; game_paused = False; show_restart_selection = False
            # New Game
            if 510 <= x <= 700 and 380 <= adj_y <= 430:
                reset_game()
            return
    # GAMEPLAY CLICKS
    if game_paused or game_over_flag: return
    if b == GLUT_LEFT_BUTTON and s == GLUT_DOWN:
        if player_is_jumping and not jump_attack_active:
            jump_attack_active, jump_attack_timer, jump_attack_y_timer = True, 0, 0
            r = math.radians(player_facing_angle)
            jump_attack_direction_x, jump_attack_direction_z, jump_attack_horizontal_velocity = math.sin(r), math.cos(r), 8.0
        if not player_is_jumping and not punch_active: punch_active, punch_timer = True, 0
    if b == GLUT_RIGHT_BUTTON and s == GLUT_DOWN:
        if player_is_jumping and not spin_kick_active: spin_kick_active, spin_kick_timer, spin_hit_registered = True, 0, False

def special_key_input(k, x, y):
    global camera_height, camera_angle
    if k == GLUT_KEY_LEFT: camera_angle -= 2
    if k == GLUT_KEY_RIGHT: camera_angle += 2
    if k == GLUT_KEY_UP: camera_height += 3
    if k == GLUT_KEY_DOWN:
        camera_height -= 3
        if camera_height < 50: camera_height = 50

# ====================================PHYSICS & ENEMY UPDATES=========================================
def update_jump():
    global player_is_jumping, jump_timer, player_y_offset
    if player_is_jumping and not jump_attack_active:
        jump_timer += 1
        t = jump_timer / jump_max_duration
        player_y_offset = jump_height * (4 * t * (1 - t))
        if jump_timer >= jump_max_duration:
            jump_timer, player_y_offset, player_is_jumping = 0, 0, False

def update_jump_attack():
    global jump_attack_active, jump_attack_timer, player_y_offset, player_is_jumping, player_position, jump_timer, current_zone, zone_cleared, zone_length
    if jump_attack_active:
        jump_attack_timer += 1
        nx = player_position[0] + jump_attack_horizontal_velocity * jump_attack_direction_x
        nz = player_position[1] + jump_attack_horizontal_velocity * jump_attack_direction_z
        zone_limit_x = (current_zone + 1) * zone_length
        if not zone_cleared and nx > zone_limit_x - 50: nx = zone_limit_x - 50
        if -grid_size < nx < grid_floor_length and -grid_size < nz < grid_size:
            if not check_obstacle_collision(nx, nz): # Prevent jumping INSIDE trees
                player_position[0], player_position[1] = nx, nz
        player_y_offset = initial_jump_velocity * jump_timer - 0.5 * gravity * jump_timer * jump_timer
        if player_y_offset < 0: player_y_offset = 0
        jump_timer += 1
        if jump_attack_timer >= jump_attack_max_duration or player_y_offset <= 0:
            jump_attack_active, jump_attack_timer, player_is_jumping, jump_timer, player_y_offset = False, 0, False, 0, 0

def update_punch():
    global punch_active, punch_timer
    if punch_active:
        punch_timer += 1
        if punch_timer >= punch_max_duration: punch_active, punch_timer = False, 0

def update_spin_kick():
    global spin_kick_active, spin_kick_timer, player_is_jumping, player_y_offset
    if not spin_kick_active: return
    spin_kick_timer += 1
    player_y_offset = 35
    if spin_kick_timer >= spin_kick_max_duration:
        spin_kick_active = False; spin_kick_timer = 0; player_is_jumping = False; player_y_offset = 0

def update_enemies():
    global current_zone, zone_length, grid_size, boss_is_shooting, boss_shoot_timer, boss_bullets, boss_shoot_cooldown
    global hunter_blades, hunter_blade_speed
    ATTACK_RANGE_X, ALIGNMENT_BUFFER, CHARGE_SPEED, CHARGE_TRIGGER_DIST = 50, 15, 6.0, 250
    zone_min_x = -grid_size if current_zone == 0 else current_zone * zone_length
    zone_max_x = (current_zone + 1) * zone_length
    for e in enemy_list:
        if 'state' not in e: e['state'] = 'chasing'
        if 'charge_dir' not in e: e['charge_dir'] = 0
        if 'shoot_timer' not in e: e['shoot_timer'] = random.randint(50, 150)
        dx = player_position[0] - e['enemy_position'][0]
        dz = player_position[1] - e['enemy_position'][2]
        dist = math.sqrt(dx*dx + dz*dz)
        if e.get('type') == 5: # Boss
            if boss_shoot_timer > 0:
                boss_shoot_timer -= 1
                boss_is_shooting = (boss_shoot_timer > (boss_shoot_cooldown - 20)) 
                if boss_shoot_timer == boss_shoot_cooldown - 10:
                    angle = math.atan2(dx, dz)
                    boss_bullets.append({'pos': [e['enemy_position'][0], e['enemy_position'][2]], 'dir': [math.sin(angle), math.cos(angle)]})
                continue 
            if dist > 150:
                e['enemy_position'][0] += (enemy_spead * 1.5) if dx > 0 else -(enemy_spead * 1.5)
                e['enemy_position'][2] += (enemy_spead * 1.5) if dz > 0 else -(enemy_spead * 1.5)
            e['enemy_position'][0] = max(zone_min_x, min(e['enemy_position'][0], zone_max_x))
            if random.random() < 0.01: boss_shoot_timer = boss_shoot_cooldown
            continue 
        if e.get('type') == 2: # Hunter
            e['shoot_timer'] -= 1
            if e['shoot_timer'] <= 0 and dist < 400:
                mag = math.sqrt(dx*dx + dz*dz)
                if mag != 0:
                    hunter_blades.append({'pos': [e['enemy_position'][0], e['enemy_position'][2]], 'vel': [(dx/mag)*hunter_blade_speed, (dz/mag)*hunter_blade_speed], 'angle': 0})
                e['shoot_timer'] = random.randint(120, 200)
        if e.get('type') == 4: # Fat Guy
            if e['state'] == 'charging':
                e['enemy_position'][0] += e['charge_dir'] * CHARGE_SPEED
                if (e['enemy_position'][0] < zone_min_x) or (e['enemy_position'][0] > zone_max_x):
                    e['enemy_position'][0] = max(zone_min_x, min(e['enemy_position'][0], zone_max_x)); e['state'] = 'chasing'
                continue 
            if abs(dz) <= ALIGNMENT_BUFFER and abs(dx) < CHARGE_TRIGGER_DIST:
                e['state'] = 'charging'; e['charge_dir'] = 1 if dx > 0 else -1; continue
        if abs(dz) <= ALIGNMENT_BUFFER and abs(dx) <= ATTACK_RANGE_X: e['state'] = 'attacking'
        elif abs(dz) > ALIGNMENT_BUFFER:
            e['enemy_position'][2] += enemy_spead if dz > 0 else -enemy_spead
            e['enemy_position'][2] = max(-grid_size + 10, min(e['enemy_position'][2], grid_size - 10))
        elif abs(dx) > ATTACK_RANGE_X:
            e['enemy_position'][0] += enemy_spead if dx > 0 else -enemy_spead
            e['enemy_position'][0] = max(zone_min_x, min(e['enemy_position'][0], zone_max_x))

# COLLISION HANDLERS
def handle_spin_kick_collisions():
    global enemy_list, game_score_conter, spin_hit_registered, player_health, enemies_killed_in_zone, boss_hp
    if not spin_kick_active: return
    hits = []
    for i, e in enumerate(enemy_list):
        dx, dz = e['enemy_position'][0] - player_position[0], e['enemy_position'][2] - player_position[1]
        if (dx * dx + dz * dz) <= (spin_radius * spin_radius):
            hits.append(i); angle = math.atan2(dx, dz)
            e['enemy_position'][0] += math.sin(angle) * spin_force; e['enemy_position'][2] += math.cos(angle) * spin_force
    if hits and not spin_hit_registered:
        spin_hit_registered = True
        enemies_to_delete = []
        for i in hits:
            if enemy_list[i].get('type') == 5:
                enemy_list[i]['hp'] -= 25; boss_hp = enemy_list[i]['hp']
                if enemy_list[i]['hp'] <= 0: enemies_to_delete.append(i)
            else: enemies_to_delete.append(i)
        for i in sorted(enemies_to_delete, reverse=True): del enemy_list[i]; enemies_killed_in_zone += 1
        player_health -= 25; game_score_conter += len(hits)

def handle_jump_attack_collisions():
    global game_score_conter, enemy_list, jump_attack_scored, enemies_killed_in_zone, boss_hp
    if not jump_attack_active or jump_attack_scored: return
    kill_indices = []
    r = math.radians(player_facing_angle)
    forward_dist = 25 + (jump_attack_timer / jump_attack_max_duration) * 35
    hb_x, hb_z, hb_y = player_position[0] + forward_dist * math.sin(r), player_position[1] + forward_dist * math.cos(r), player_y_offset + 25
    hit_registered = False
    for j, e in enumerate(enemy_list):
        ex, ey, ez = e['enemy_position'][0], e['enemy_position'][1], e['enemy_position'][2]
        er = 10 * e['enemy_size']
        if (hb_x+15 > ex-er and hb_x-15 < ex+er and hb_z+15 > ez-er and hb_z-15 < ez+er and hb_y+20 > ey-er and hb_y-20 < ey+er):
            hit_registered = True; game_score_conter += 1
            if e.get('type') == 5:
                e['hp'] -= 15; boss_hp = e['hp']
                if e['hp'] <= 0: kill_indices.append(j)
            else: kill_indices.append(j)
    if hit_registered: jump_attack_scored = True
    for j in sorted(kill_indices, reverse=True): del enemy_list[j]; enemies_killed_in_zone += 1

def handle_punch_enemy_collisions():
    global game_score_conter, enemy_list, enemies_killed_in_zone, boss_hp
    # 1. Timing Check
    if not punch_active or jump_attack_active or punch_timer < 5: 
        return
    kill_indices = []
    r = math.radians(player_facing_angle)
    dir_x = math.sin(r)
    dir_z = math.cos(r)
    effective_range = 75 
    for j, e in enumerate(enemy_list):
        ex = e['enemy_position'][0] - player_position[0]
        ez = e['enemy_position'][2] - player_position[1]
        dist = math.sqrt(ex*ex + ez*ez)
        if dist < effective_range:
            if dist > 0:
                norm_ex = ex / dist
                norm_ez = ez / dist
                dot_product = (dir_x * norm_ex) + (dir_z * norm_ez)
                if dot_product > 0.5:
                    spawn_hit_spark(e['enemy_position'][0], 40, e['enemy_position'][2])
                    game_score_conter += 1
                    if e.get('type') == 5:
                        e['hp'] -= 10
                        boss_hp = e['hp']
                        if e['hp'] <= 0: kill_indices.append(j)
                    else:
                        kill_indices.append(j)
    for j in sorted(kill_indices, reverse=True): 
        del enemy_list[j]
        enemies_killed_in_zone += 1

def handle_player_enemy_collisions():
    global player_health, game_over_flag, enemy_list
    if jump_attack_active or spin_kick_active: return
    hit_indices = []
    for j, e in enumerate(enemy_list):
        dist = math.sqrt((player_position[0]-e['enemy_position'][0])**2 + (player_position[1]-e['enemy_position'][2])**2)
        if dist < 20:
            player_health -= 20 if e.get('type') == 4 else 10
            hit_indices.append(j)
            if player_health <= 0: game_over_flag = True; break
    if not game_over_flag:
        for j in set(hit_indices):
            e = enemy_list[j]
            if e.get('type') == 5:
                dx, dz = e['enemy_position'][0] - player_position[0], e['enemy_position'][2] - player_position[1]
                mag = math.sqrt(dx*dx + dz*dz)
                if mag != 0: e['enemy_position'][0] += (dx/mag)*50; e['enemy_position'][2] += (dz/mag)*50
            else: spawn_enemy(j); enemy_list[j]['type'] = e.get('type', 1)

def cheat_mode_actions():
    if not cheat_mode_flag or game_over_flag: return
    global player_rotation_angle, player_facing_angle, punch_active, punch_timer
    player_rotation_angle = (player_rotation_angle + 2) % 360
    player_facing_angle = player_rotation_angle
    for e in enemy_list:
        dx, dz = e['enemy_position'][0]-player_position[0], e['enemy_position'][2]-player_position[1]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < punch_range * 1.5 and not punch_active:
            if random.random() < 0.15: punch_active, punch_timer = True, 0

def idle():
    global game_over_flag, player_fall_angle, enemies_killed_in_zone, enemies_spawned_in_zone, enemies_per_zone, zone_cleared, current_zone, game_level, zone_length, boss_spawned_flag, enemy_list, game_paused
    if game_paused: 
        glutPostRedisplay()
        return
    if game_over_flag:
        if player_fall_angle < 90: player_fall_angle += 1
        glutPostRedisplay()
        return
    update_day_night_cycle()
    update_snow_particles()
    update_fire_particles()
    update_cheat_bombs()
    update_collectibles_and_visuals()
    update_punch()
    update_jump_attack()
    update_enemies()
    handle_jump_attack_collisions() 
    handle_punch_enemy_collisions() 
    handle_player_enemy_collisions()
    cheat_mode_actions()
    update_jump()
    update_spin_kick()
    update_boss_bullets()
    update_hunter_blades()
    handle_spin_kick_collisions()
    if not zone_cleared and enemies_spawned_in_zone < enemies_per_zone and len(enemy_list) < 3: 
        spawn_enemy()
    if enemies_killed_in_zone >= enemies_per_zone: 
        zone_cleared = True
        if current_zone == 4: 
            if not boss_spawned_flag:
                spawn_boss()
                enemies_per_zone = 1
                enemies_spawned_in_zone = 1
                enemies_killed_in_zone = 0
                boss_spawned_flag = True
                zone_cleared = False
                return                        
            else:
                print(f"Level {game_level} Complete!")
                reset_game(level=game_level + 1, score=game_score_conter)
                return 
        else:
            if not zone_cleared: enemies_per_zone = 5
    zone_limit_x = (current_zone + 1) * zone_length
    if player_position[0] > zone_limit_x + 50:
        current_zone += 1
        enemies_spawned_in_zone = 0; enemies_killed_in_zone = 0; zone_cleared = False
        spawn_crates_for_zone()
        print(f"Entering Zone {current_zone + 1}")
    if player_health <= 0: game_over_flag = True
    glutPostRedisplay()

def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glEnable(GL_DEPTH_TEST); glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if is_daytime:
        glClearColor(0.5, 0.8, 0.9, 1.0) 
    else:
        glClearColor(0.05, 0.05, 0.1, 1.0) 
    camera_setup()
    draw_grid_floor()
    draw_bounddary_wall()
    draw_obstacles()
    draw_fire_particles()
    draw_snow_particles()
    draw_player()
    draw_enemies()
    draw_hit_effects()
    draw_punch_range()
    draw_jump_attack_hitbox()
    draw_bullets()
    draw_cheat_bombs()
    draw_collectibles_and_effects()
    if not game_over_flag:
        writing_text(10, 770, f"Player HP: {max(0, player_health)}")
        writing_text(10, 740, f"Boss HP: {boss_hp if boss_spawned_flag else 'N/A'}")
        writing_text(10, 710, f"Level: {game_level} | Score: {game_score_conter} | Zone: {current_zone + 1}")
        writing_text(10, 680, f"Enemies Left: {max(0, enemies_per_zone - enemies_killed_in_zone)}")
        draw_go_sign()
    else:
        writing_text(10, 770, f"Game is Over. Your Score is {game_score_conter}."); writing_text(10, 740, 'Press "R" to Restart')
    draw_ui_buttons()
    glutSwapBuffers()

def main():
    glutInit()
    reset_game()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Punch Combat - developed by azizul kabir jayed")
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_input)
    glutSpecialFunc(special_key_input)
    glutMouseFunc(mouse_listner)
    glutIdleFunc(idle)
    glutMainLoop()
if __name__ == "__main__": main()