import pygame
import sys
import math
import random
import json
import os

# --- Game Setup & Constants ---
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube's Journey Home")
clock = pygame.time.Clock()

vec = pygame.math.Vector2
font = pygame.font.SysFont('Arial', 18, bold=True)
title_font = pygame.font.SysFont('Arial', 48, bold=True)
btn_font = pygame.font.SysFont('Arial', 24, bold=True)

env_colors = {
    "sky": (100, 180, 210), "dirt": (86, 52, 24), "grass": (54, 180, 44)
}

# --- Account & Save System ---
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

accounts_db = load_accounts()
current_user = None

# --- UI Classes ---
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = (60, 60, 70)
        self.hover_color = (100, 150, 255)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        current_color = self.hover_color if is_hovered else self.color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (30, 30, 35), self.rect.inflate(-6, -6), border_radius=6)
        
        text_surf = btn_font.render(self.text, True, current_color if is_hovered else (200, 200, 200))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class LevelButton(Button):
    def __init__(self, x, y, w, h, level_num):
        super().__init__(x, y, w, h, f"LEVEL {level_num}")
        self.level_num = level_num
        self.bg_surface = pygame.Surface((w, h))
        self.generate_texture(w, h)
        
    def generate_texture(self, w, h):
        # Base colors based on biome logic from load_level
        if self.level_num in [1, 2]: # Jungle
            self.bg_surface.fill((100, 180, 210)) # Sky
            pygame.draw.rect(self.bg_surface, (86, 52, 24), (0, h//2, w, h//2)) # Dirt
            pygame.draw.rect(self.bg_surface, (54, 180, 44), (0, h//2, w, 15)) # Grass
            # Add some leaves/trees
            pygame.draw.circle(self.bg_surface, (34, 139, 34), (w//4, h//2), 20)
            pygame.draw.circle(self.bg_surface, (34, 139, 34), (w*3//4, h//2 - 10), 25)
            
        elif self.level_num == 3: # Toxic
            self.bg_surface.fill((30, 50, 70))
            pygame.draw.rect(self.bg_surface, (60, 40, 20), (0, h//2 + 10, w, h//2))
            pygame.draw.rect(self.bg_surface, (100, 255, 50), (0, h - 20, w, 20)) # Sludge
            
        elif self.level_num in [4, 5]: # Caves
            self.bg_surface.fill((20, 20, 40) if self.level_num == 4 else (10, 10, 15))
            pygame.draw.rect(self.bg_surface, (40, 30, 30) if self.level_num == 4 else (70, 70, 75), (0, h//2 + 10, w, h//2))
            # Stalactites
            pygame.draw.polygon(self.bg_surface, (50, 50, 55), [(w//4, 0), (w//4+20, 0), (w//4+10, h//3)])
            pygame.draw.polygon(self.bg_surface, (50, 50, 55), [(w*3//4, 0), (w*3//4+15, 0), (w*3//4+7, h//4)])
            
        elif self.level_num == 6: # Spider Boss
            self.bg_surface.fill((5, 5, 10))
            pygame.draw.rect(self.bg_surface, (40, 40, 45), (0, h//2 - 10, w, h//2 + 10))
            # Web lines
            pygame.draw.line(self.bg_surface, (150, 150, 150), (0, 0), (w, h//2), 2)
            pygame.draw.line(self.bg_surface, (150, 150, 150), (w, 0), (0, h//2), 2)
            pygame.draw.circle(self.bg_surface, (130, 60, 160), (w//2, h//3), 15) # Mini boss body
            
        elif self.level_num in [7, 8]: # Sky Ruins
            self.bg_surface.fill((150, 200, 250) if self.level_num == 7 else (40, 80, 40))
            pygame.draw.rect(self.bg_surface, (200, 200, 220) if self.level_num == 7 else (60, 40, 20), (0, h - 30, w, 30))
            # Clouds
            pygame.draw.circle(self.bg_surface, (255, 255, 255), (w//3, h//4), 15)
            pygame.draw.circle(self.bg_surface, (255, 255, 255), (w//3 + 15, h//4 - 5), 20)
            pygame.draw.circle(self.bg_surface, (255, 255, 255), (w//3 + 30, h//4), 15)
            
        elif self.level_num == 9: # Volcano Final
            self.bg_surface.fill((50, 20, 20))
            pygame.draw.rect(self.bg_surface, (30, 10, 10), (0, h//2, w, h//2))
            pygame.draw.rect(self.bg_surface, (255, 100, 0), (0, h - 25, w, 25)) # Lava
            pygame.draw.circle(self.bg_surface, (255, 150, 0), (w//4, h - 25), 8) # Lava bubble

        elif self.level_num in [10, 11, 12]: # Zombie Graveyard
            self.bg_surface.fill((20, 30, 20))
            pygame.draw.rect(self.bg_surface, (40, 50, 40), (0, h - 20, w, 20))
            pygame.draw.rect(self.bg_surface, (100, 100, 100), (w//2 - 10, h - 35, 20, 20), border_radius=4)
            if self.level_num == 10:
                pygame.draw.circle(self.bg_surface, (255, 0, 0), (w//2, h//3), 6) # Mini boss eye

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Draw the custom background scaled to current draw size
        scaled_bg = pygame.transform.scale(self.bg_surface, (self.rect.width - 6, self.rect.height - 6))
        
        # Draw frame
        pygame.draw.rect(surface, (200, 200, 200) if is_hovered else (50, 50, 60), self.rect, border_radius=8)
        
        # Blit the custom background inside the frame
        surface.blit(scaled_bg, (self.rect.x + 3, self.rect.y + 3))
        
        # Darken if out of focus (not hovered)
        if not is_hovered:
            dark_overlay = pygame.Surface((self.rect.width - 6, self.rect.height - 6), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 100))
            surface.blit(dark_overlay, (self.rect.x + 3, self.rect.y + 3))
        
        # Draw text with shadow for readability
        text_surf = btn_font.render(self.text, True, (255, 255, 255))
        shadow_surf = btn_font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surf, text_rect)

class IconButton(Button):
    def __init__(self, x, y, w, h, icon_type):
        super().__init__(x, y, w, h, "")
        self.icon_type = icon_type

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        current_color = self.hover_color if is_hovered else self.color
        
        rad = self.rect.width // 2 if self.icon_type in ["resume", "quit"] else 8
        pygame.draw.rect(surface, current_color, self.rect, border_radius=rad)
        
        inner_color = (120, 120, 130) if self.icon_type == "hamburger" else (40, 40, 50)
        pygame.draw.rect(surface, inner_color, self.rect.inflate(-4, -4), border_radius=max(2, rad-2))
        
        cx, cy = self.rect.center
        if self.icon_type == "hamburger":
            pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy - 6), (cx + 10, cy - 6), 3)
            pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 3)
            pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy + 6), (cx + 10, cy + 6), 3)
        elif self.icon_type == "resume":
            pygame.draw.polygon(surface, (100, 255, 100), [(cx - 4, cy - 8), (cx - 4, cy + 8), (cx + 8, cy)])
        elif self.icon_type == "quit":
            pygame.draw.rect(surface, (255, 150, 150), (cx - 6, cy - 8, 12, 16), border_radius=2)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy), (cx + 10, cy), 2)
            pygame.draw.polygon(surface, (255, 255, 255), [(cx + 8, cy - 4), (cx + 8, cy + 4), (cx + 14, cy)])
        elif self.icon_type == "shop":
            pygame.draw.rect(surface, (200, 200, 200), (cx - 8, cy - 2, 16, 12))
            pygame.draw.polygon(surface, (150, 100, 100), [(cx - 10, cy - 2), (cx, cy - 10), (cx + 10, cy - 2)])
            pygame.draw.rect(surface, (100, 200, 255), (cx - 4, cy + 2, 8, 8))

class TextInput:
    def __init__(self, x, y, w, h, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.is_password = is_password
        self.active = False
        self.color_inactive = (60, 60, 70)
        self.color_active = (100, 150, 255)
        self.color = self.color_inactive

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass 
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 15 and event.unicode.isprintable(): 
                    self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (30, 30, 35), self.rect.inflate(-4, -4), border_radius=3)
        
        display_text = "*" * len(self.text) if self.is_password and self.text else self.text
        if not self.text and not self.active:
            text_surf = btn_font.render(self.placeholder, True, (150, 150, 150))
        else:
            text_surf = btn_font.render(display_text, True, (255, 255, 255))
            
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + self.rect.height // 2 - text_surf.get_height() // 2))

# --- Visual Effects Classes ---
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-5, 5), random.uniform(-6, 2)
        self.timer = random.randint(30, 60)
        self.color = color
        self.size = random.randint(3, 8)

    def update(self):
        self.vy += 0.3 
        self.x += self.vx
        self.y += self.vy
        self.timer -= 1

    def draw(self, surface):
        if self.timer > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

class CaveEntrance(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        rock_colors = [(70, 70, 75), (50, 50, 55), (30, 30, 35)]
        
        base_points = [(0, h), (w * 0.15, h * 0.5), (w * 0.3, h * 0.15), (w * 0.5, 0), 
                       (w * 0.7, h * 0.15), (w * 0.85, h * 0.5), (w, h)]
        pygame.draw.polygon(self.image, rock_colors[2], base_points)
        
        mid_points = [(w * 0.1, h), (w * 0.25, h * 0.55), (w * 0.4, h * 0.25), 
                      (w * 0.6, h * 0.25), (w * 0.75, h * 0.55), (w * 0.9, h)]
        pygame.draw.polygon(self.image, rock_colors[1], mid_points)
        
        for _ in range(4):
            rw, rh = random.randint(w//4, w//2), random.randint(h//4, h//2)
            rx, ry = random.randint(int(w*0.1), int(w*0.5)), random.randint(int(h*0.3), int(h*0.7))
            pygame.draw.polygon(self.image, random.choice(rock_colors), [(rx, ry + rh), (rx + rw//2, ry), (rx + rw, ry + rh)])
            
        pygame.draw.rect(self.image, (0, 0, 0), (w * 0.35, h * 0.6, w * 0.3, h * 0.4))
        pygame.draw.ellipse(self.image, (0, 0, 0), (w * 0.35, h * 0.4, w * 0.3, h * 0.4))
        
        for _ in range(6):
             pygame.draw.circle(self.image, rock_colors[0], (random.randint(int(w*0.05), int(w*0.95)), h - random.randint(0, 15)), random.randint(10, 25))

        self.rect = self.image.get_rect(midbottom=(x, y))

# --- Boss & Arena Mechanics ---
class WebTrap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 255, 200, 150), (15, 15), 15)
        pygame.draw.line(self.image, (255, 255, 255), (5, 15), (25, 15), 2)
        pygame.draw.line(self.image, (255, 255, 255), (15, 5), (15, 25), 2)
        pygame.draw.line(self.image, (255, 255, 255), (8, 8), (22, 22), 2)
        pygame.draw.line(self.image, (255, 255, 255), (8, 22), (22, 8), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = 4 
        self.spawn_time = pygame.time.get_ticks()

    def update(self, platforms):
        self.rect.y += self.vy
        if pygame.sprite.spritecollide(self, platforms, False):
            self.vy = 0
            
        if pygame.time.get_ticks() - self.spawn_time > 4000:
            self.kill()

class SpiderBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((120, 80), pygame.SRCALPHA)
        self.color = (130, 60, 160) 
        leg_color = (100, 50, 120)
        
        pygame.draw.lines(self.image, leg_color, False, [(60, 40), (20, 10), (0, 40)], 6)
        pygame.draw.lines(self.image, leg_color, False, [(60, 40), (30, 0), (10, 50)], 6)
        pygame.draw.lines(self.image, leg_color, False, [(60, 40), (100, 10), (120, 40)], 6)
        pygame.draw.lines(self.image, leg_color, False, [(60, 40), (90, 0), (110, 50)], 6)
        
        pygame.draw.ellipse(self.image, self.color, (20, 20, 80, 50)) 
        pygame.draw.ellipse(self.image, (50, 255, 50), (35, 30, 10, 30))
        pygame.draw.ellipse(self.image, (50, 255, 50), (55, 35, 10, 25))
        pygame.draw.ellipse(self.image, (50, 255, 50), (75, 30, 10, 30))
        pygame.draw.circle(self.image, (60, 30, 80), (60, 60), 20) 
        pygame.draw.circle(self.image, (255, 50, 50), (50, 65), 5)
        pygame.draw.circle(self.image, (255, 50, 50), (70, 65), 5)

        self.rect = self.image.get_rect(midtop=(x, y))
        self.vx = 4
        self.max_hp = 3
        self.hp = self.max_hp
        self.last_attack = pygame.time.get_ticks()
        self.is_dead = False
        self.i_frames = 0

    def update(self, hazards_group):
        if self.is_dead: return
        current_time = pygame.time.get_ticks()
        
        self.rect.x += self.vx
        if self.rect.right > WIDTH - 50 or self.rect.left < 50:
            self.vx *= -1
            
        if current_time - self.last_attack > 1800:
            self.last_attack = current_time
            hazards_group.add(WebTrap(self.rect.centerx, self.rect.bottom))

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.i_frames > 1000: 
            self.hp -= 1
            self.i_frames = current_time
            self.vx *= 1.5 
            if self.hp <= 0:
                self.is_dead = True
                self.kill()
                return True 
        return False

    def draw(self, surface):
        if self.is_dead: return
        if pygame.time.get_ticks() - self.i_frames < 200:
            flash_img = self.image.copy()
            flash_img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_img, self.rect)
        else:
            surface.blit(self.image, self.rect)
            
        hp_width = 80
        pygame.draw.rect(surface, (100, 100, 100), (self.rect.centerx - hp_width//2, self.rect.top - 20, hp_width, 10))
        pygame.draw.rect(surface, (50, 255, 50), (self.rect.centerx - hp_width//2, self.rect.top - 20, hp_width * (self.hp/self.max_hp), 10))

class Trampoline(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 60, 70), (0, h//2, w, h//2), border_radius=4)
        pygame.draw.ellipse(self.image, (100, 200, 255), (0, 0, w, h))
        pygame.draw.ellipse(self.image, (200, 255, 255), (w//4, h//4, w//2, h//2))
        self.rect = self.image.get_rect(topleft=(x, y))

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_dist=100):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (50, 100, 50), (10, 15, 20, 25), border_radius=4)
        pygame.draw.rect(self.image, (70, 150, 70), (5, 0, 30, 20), border_radius=6)
        pygame.draw.rect(self.image, (255, 50, 50), (10, 5, 6, 4))
        pygame.draw.rect(self.image, (255, 50, 50), (24, 5, 6, 4))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.start_x = x
        self.walk_dist = walk_dist
        self.vx = 1.5
        self.hp = 2
        self.is_dead = False
        self.i_frames = 0

    def update(self):
        if self.is_dead: return
        self.rect.x += self.vx
        if abs(self.rect.centerx - self.start_x) > self.walk_dist:
            self.vx *= -1

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.i_frames > 500:
            self.hp -= 1
            self.i_frames = current_time
            self.vx *= 1.2
            if self.hp <= 0:
                self.is_dead = True
                self.kill()
                return True
        return False

    def draw(self, surface):
        if self.is_dead: return
        if pygame.time.get_ticks() - self.i_frames < 200:
            flash_img = self.image.copy()
            flash_img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

class ZombieBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (40, 80, 40), (20, 20, 40, 60), border_radius=5)
        pygame.draw.rect(self.image, (60, 120, 60), (10, 0, 60, 40), border_radius=10)
        pygame.draw.rect(self.image, (255, 0, 0), (20, 10, 10, 10))
        pygame.draw.rect(self.image, (255, 0, 0), (50, 10, 10, 10))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.vx = 2
        self.max_hp = 5
        self.hp = self.max_hp
        self.last_attack = pygame.time.get_ticks()
        self.is_dead = False
        self.i_frames = 0

    def update(self, hazards_group):
        if self.is_dead: return
        self.rect.x += self.vx
        if self.rect.right > WIDTH - 50 or self.rect.left < 50:
            self.vx *= -1
            
    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.i_frames > 1000: 
            self.hp -= 1
            self.i_frames = current_time
            self.vx *= 1.2 
            if self.hp <= 0:
                self.is_dead = True
                self.kill()
                return True 
        return False

    def draw(self, surface):
        if self.is_dead: return
        if pygame.time.get_ticks() - self.i_frames < 200:
            flash_img = self.image.copy()
            flash_img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_img, self.rect)
        else:
            surface.blit(self.image, self.rect)
        hp_width = 80
        pygame.draw.rect(surface, (100, 100, 100), (self.rect.centerx - hp_width//2, self.rect.top - 20, hp_width, 10))
        pygame.draw.rect(surface, (50, 255, 50), (self.rect.centerx - hp_width//2, self.rect.top - 20, hp_width * (self.hp/self.max_hp), 10))

# --- Environment & Standard Classes ---
class Cloud:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(10, 100)
        self.speed, self.size = random.uniform(0.1, 0.3), random.randint(40, 80)
    def update(self):
        self.x += self.speed
        if self.x - self.size > WIDTH:
            self.x, self.y = -self.size, random.randint(10, 100)
    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), self.y), self.size // 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + self.size * 0.4), self.y - self.size * 0.2), self.size // 2)

class Tree:
    def __init__(self, x, y, is_bg=False):
        self.base_x, self.y = x, y
        self.is_bg = is_bg
        self.size = random.uniform(1.5, 2.5) if is_bg else random.uniform(3.0, 5.0)
        self.sway_speed, self.sway_offset = random.uniform(0.5, 1.2), random.uniform(0, math.pi * 2)
        w_shade = random.randint(30, 50) if is_bg else random.randint(50, 70)
        self.trunk_color = (w_shade, w_shade - 15, w_shade - 25)
        self.leaf_color = (15, random.randint(60, 100) if is_bg else random.randint(100, 140), 25)
        self.bark_strips = []
        if not is_bg:
            for _ in range(int(8 * self.size)):
                self.bark_strips.append((random.uniform(-12 * self.size, 12 * self.size), random.uniform(2, 6 * self.size), random.randint(-15, 15)))

    def draw(self, surface):
        sway = math.sin(pygame.time.get_ticks() / 1000.0 * self.sway_speed + self.sway_offset) * (12 * self.size)
        trunk_w, trunk_h = 30 * self.size, 200 * self.size
        pygame.draw.rect(surface, self.trunk_color, (self.base_x - trunk_w/2, self.y - trunk_h, trunk_w, trunk_h + 100))
        for offset_x, strip_w, shade_diff in self.bark_strips:
            strip_color = (max(0, min(255, self.trunk_color[0] + shade_diff)), max(0, min(255, self.trunk_color[1] + shade_diff)), max(0, min(255, self.trunk_color[2] + shade_diff)))
            pygame.draw.rect(surface, strip_color, (self.base_x + offset_x, self.y - trunk_h, strip_w, trunk_h + 100))
        leaves_x, leaves_y = self.base_x + sway, self.y - trunk_h + (40 * self.size)
        pygame.draw.circle(surface, self.leaf_color, (int(leaves_x), int(leaves_y)), int(80 * self.size))
        pygame.draw.circle(surface, self.leaf_color, (int(leaves_x - 40*self.size), int(leaves_y + 30*self.size)), int(60 * self.size))
        pygame.draw.circle(surface, self.leaf_color, (int(leaves_x + 40*self.size), int(leaves_y + 30*self.size)), int(60 * self.size))

class Vine(pygame.sprite.Sprite):
    def __init__(self, x, y, length):
        super().__init__()
        self.image = pygame.Surface((20, length), pygame.SRCALPHA)
        pygame.draw.line(self.image, (34, 139, 34), (10, 0), (10, length), 4)
        for i in range(10, length - 10, 25):
            pygame.draw.ellipse(self.image, (46, 184, 46), (0, i, 12, 12))
            pygame.draw.ellipse(self.image, (46, 184, 46), (8, i + 12, 12, 12))
        self.rect = self.image.get_rect(topleft=(x, y))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, env_colors["dirt"], (0, 0, w, h), border_radius=8)
        pygame.draw.rect(self.image, env_colors["grass"], (0, 0, w, 14), border_top_left_radius=8, border_top_right_radius=8)
        self.rect = self.image.get_rect(topleft=(x, y))

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((100, 255, 50, 200)) 
        self.rect = self.image.get_rect(topleft=(x, y))
    def update(self, *args): pass 

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.time_offset = random.uniform(0, 10)
    def draw(self, surface):
        pulse = abs(math.sin((pygame.time.get_ticks() / 1000.0) * 3)) * 50
        pygame.draw.ellipse(surface, (200, 100, 255, 150), self.rect) 
        pygame.draw.ellipse(surface, (255, 200, 255), self.rect.inflate(-10 + pulse/5, -10 + pulse/5))     

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, message):
        super().__init__()
        self.base_y, self.message = y, message
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 220, 255, 200), (15, 15), 15) 
        pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 6)       
        self.rect = self.image.get_rect(midbottom=(x, y))
    def update(self):
        self.rect.y = self.base_y + math.sin(pygame.time.get_ticks() / 1000.0 * 4) * 4
    def draw_tooltip(self, surface, player_pos):
        if math.hypot(player_pos.x - self.rect.centerx, player_pos.y - self.rect.centery) < 150:
            text = font.render(self.message, True, (255, 255, 255))
            text_rect = text.get_rect(midbottom=(self.rect.centerx, self.rect.top - 15))
            bg_rect = text_rect.inflate(16, 10)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, 180), bg_surf.get_rect(), border_radius=5)
            surface.blit(bg_surf, bg_rect.topleft)
            surface.blit(text, text_rect)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x):
        super().__init__()
        self.image = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 100, 0, 100), (0, 0, 40, 20)) 
        pygame.draw.ellipse(self.image, (255, 150, 0), (5, 5, 30, 10))
        pygame.draw.ellipse(self.image, (255, 255, 255), (10, 7, 20, 6))
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 7 * dir_x 
    def update(self):
        self.rect.x += self.vx
        if self.rect.right < -100 or self.rect.left > WIDTH + 100: self.kill()

class Cannon(pygame.sprite.Sprite):
    def __init__(self, x, y, dir_x, offset=0):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (60, 60, 65), (0, 0, 40, 30), border_radius=5)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dir_x, self.spawn_offset = dir_x, 45 if dir_x == 1 else -15
        self.last_shot = pygame.time.get_ticks() - offset 
    def update(self, projectiles_group):
        if pygame.time.get_ticks() - self.last_shot > 2000:
            self.last_shot = pygame.time.get_ticks()
            projectiles_group.add(Projectile(self.rect.x + self.spawn_offset, self.rect.centery, self.dir_x))

class Bat:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(50, 250)
        self.speed, self.offset = random.uniform(2.0, 4.0), random.uniform(0, math.pi * 2)
    def update(self):
        self.x -= self.speed
        if self.x < -50: self.x, self.y = WIDTH + 50, random.randint(50, 250)
    def draw(self, surface):
        flap_y = math.sin(pygame.time.get_ticks() / 100.0 + self.offset) * 5
        pygame.draw.ellipse(surface, (20, 20, 25), (self.x, self.y + flap_y, 30, 15)) 
        pygame.draw.polygon(surface, (20, 20, 25), [(self.x+5, self.y+flap_y), (self.x-10, self.y-10+flap_y), (self.x+5, self.y+5+flap_y)]) 
        pygame.draw.polygon(surface, (20, 20, 25), [(self.x+25, self.y+flap_y), (self.x+40, self.y-10+flap_y), (self.x+25, self.y+5+flap_y)]) 

class Stalactite:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), -random.randint(50, 150)
        self.width, self.height = random.randint(20, 40), random.randint(60, 120)
        self.color = (random.randint(40, 60), random.randint(40, 60), random.randint(45, 65))
        self.falling, self.vy = False, 0
    def update(self):
        if not self.falling and random.random() < 0.001: self.falling = True
        if self.falling:
            self.vy += 0.2
            self.y += self.vy
        if self.y > HEIGHT:
            self.y, self.x, self.falling, self.vy = -random.randint(50, 150), random.randint(0, WIDTH), False, 0
    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, [(self.x, self.y), (self.x + self.width, self.y), (self.x + self.width//2, self.y + self.height)])

class RockTumbler:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), -random.randint(10, 50)
        self.size, self.color = random.randint(5, 15), (random.randint(30, 50), random.randint(30, 50), random.randint(35, 55))
        self.vx, self.vy = random.uniform(-1, 1), random.uniform(1, 3)
    def update(self):
        self.vy += 0.1
        self.x += self.vx
        self.y += self.vy
        if self.y > HEIGHT + 20:
            self.y, self.x, self.vy = -random.randint(10, 50), random.randint(0, WIDTH), random.uniform(1, 3)
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# --- Player ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width, self.height = 40, 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.spawn_point = vec(50, HEIGHT - 100)
        self.pos = vec(self.spawn_point)
        self.vel, self.acc = vec(0, 0), vec(0, 0)
        self.ACCEL, self.FRICTION, self.GRAVITY = 0.8, -0.12, 0.5
        self.JUMP_POWER, self.CLIMB_SPEED = -11.5, 4
        self.look_dir = vec(0, 0)
        self.is_climbing = False
        self.state, self.death_timer, self.invincible_timer = 'alive', 0, 0
        self.color = "DEFAULT"
        self.particles = []
        
        self.has_dagger = False
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0

    def trigger_death(self):
        if self.state == 'alive':
            self.state, self.death_timer = 'dying', pygame.time.get_ticks()
            self.vel, self.acc = vec(0, 0), vec(0, 0)
            
            if self.color == "RAINBOW": base_c = (255, 100, 100)
            elif self.color == "BW_GRADIENT": base_c = (150, 150, 150)
            elif isinstance(self.color, tuple): base_c = self.color
            else: base_c = (20, 20, 25)
            
            for _ in range(40):
                self.particles.append(Particle(self.rect.centerx, self.rect.centery, random.choice([base_c, (255, 255, 255)])))

    def update(self, platforms, vines, hazards, projectiles, trampolines, boss):
        current_time = pygame.time.get_ticks()

        if self.state == 'dying':
            for p in self.particles[:]:
                p.update()
                if p.timer <= 0: self.particles.remove(p)
            if current_time - self.death_timer > 1500:
                self.state, self.pos, self.vel = 'alive', vec(self.spawn_point), vec(0, 0)
                self.invincible_timer = current_time 
                self.particles.clear()
            return 

        keys = pygame.key.get_pressed()
        input_dir, self.acc = vec(0, 0), vec(0, self.GRAVITY)
        
        ascend = keys[pygame.K_UP] or keys[pygame.K_w]
        descend = keys[pygame.K_DOWN] or keys[pygame.K_s]
        moving_horizontally = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        if self.has_dagger and keys[pygame.K_SPACE] and current_time - self.attack_cooldown > 500:
            self.is_attacking = True
            self.attack_timer = current_time
            self.attack_cooldown = current_time
            
        if self.is_attacking and current_time - self.attack_timer > 200:
            self.is_attacking = False
        
        if pygame.sprite.spritecollide(self, vines, False):
            if ascend and not moving_horizontally: self.is_climbing, self.vel.y = True, -self.CLIMB_SPEED
            elif descend: self.is_climbing, self.vel.y = True, self.CLIMB_SPEED
            elif self.is_climbing: self.vel.y = 1.2 
        else: self.is_climbing = False

        if self.is_climbing: self.acc.y = 0

        # X-AXIS
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.acc.x, input_dir.x = -self.ACCEL, -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.acc.x, input_dir.x = self.ACCEL, 1

        self.acc.x += self.vel.x * self.FRICTION
        self.vel.x += self.acc.x
        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.rect.centerx = self.pos.x 

        for hit in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel.x > 0: self.rect.right = hit.rect.left
            elif self.vel.x < 0: self.rect.left = hit.rect.right
            self.pos.x, self.vel.x = self.rect.centerx, 0

        if self.pos.x < self.width / 2: self.pos.x, self.vel.x = self.width / 2, self.vel.x * -0.5 
        elif self.pos.x > WIDTH - self.width / 2: self.pos.x, self.vel.x = WIDTH - self.width / 2, self.vel.x * -0.5 

        # Y-AXIS
        if keys[pygame.K_UP] or keys[pygame.K_w]: input_dir.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: input_dir.y = 1

        self.vel.y += self.acc.y
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.bottom = self.pos.y 

        for hit in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel.y > 0: self.rect.bottom, self.vel.y, self.is_climbing = hit.rect.top, 0, False
            elif self.vel.y < 0: self.rect.top, self.vel.y = hit.rect.bottom, 0
            self.pos.y = self.rect.bottom

        for hit in pygame.sprite.spritecollide(self, trampolines, False):
            if self.vel.y > 0 and self.rect.bottom <= hit.rect.centery + 15: 
                self.rect.bottom = hit.rect.top
                self.vel.y = self.JUMP_POWER * 2.0 # Extra boost for the boss!
                self.is_climbing = False
            self.pos.y = self.rect.bottom

        if boss and not boss.is_dead:
            if self.rect.colliderect(boss.rect):
                if self.vel.y > 0 and self.rect.bottom < boss.rect.centery:
                    boss_died = boss.take_damage()
                    self.vel.y = self.JUMP_POWER * 1.2 
                    if boss_died: 
                        portals.add(Portal(WIDTH//2, HEIGHT - 60)) 
                        if isinstance(boss, ZombieBoss):
                            self.has_dagger = True
                elif current_time - self.invincible_timer > 2000:
                    self.trigger_death() 

        for z in zombies:
            if not z.is_dead:
                if self.is_attacking:
                    attack_rect = pygame.Rect(self.rect.centerx, self.rect.y - 10, 40, 60)
                    if self.look_dir.x < 0: attack_rect.x -= 40
                    if attack_rect.colliderect(z.rect):
                        z.take_damage()
                if self.rect.colliderect(z.rect) and current_time - self.invincible_timer > 2000:
                    self.trigger_death()

        if self.pos.y > HEIGHT + 50: self.trigger_death()

        if current_time - self.invincible_timer > 2000:
            if pygame.sprite.spritecollide(self, hazards, False) or pygame.sprite.spritecollide(self, projectiles, False):
                self.trigger_death()

        self.look_dir = input_dir.normalize() if input_dir.length() > 0 else vec(0, 0)

    def jump(self, platforms, vines):
        if self.state != 'alive': return 
        self.rect.y += 1 
        on_ground = pygame.sprite.spritecollide(self, platforms, False)
        on_vine = pygame.sprite.spritecollide(self, vines, False)
        self.rect.y -= 1
        keys = pygame.key.get_pressed()
        moving_horizontally = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]
        if on_ground or (on_vine and moving_horizontally):
            self.vel.y, self.is_climbing = self.JUMP_POWER, False

    def draw(self, surface):
        if self.state == 'dying':
            for p in self.particles: p.draw(surface)
            return
        if pygame.time.get_ticks() - self.invincible_timer < 2000 and (pygame.time.get_ticks() // 150) % 2 == 0: return 

        if self.color == "RAINBOW":
            t = pygame.time.get_ticks() / 1000.0
            draw_c = (int(math.sin(t*3)*127+128), int(math.sin(t*3+2)*127+128), int(math.sin(t*3+4)*127+128))
        elif self.color == "BW_GRADIENT":
            t = pygame.time.get_ticks() / 1000.0
            v = int(math.sin(t*2)*127+128)
            draw_c = (v, v, v)
        elif isinstance(self.color, tuple):
            draw_c = self.color
        else:
            draw_c = (20, 20, 25)

        pygame.draw.rect(surface, draw_c, self.rect, border_radius=10)
        inner_c = (min(255, draw_c[0] + 60), min(255, draw_c[1] + 60), min(255, draw_c[2] + 65))
        pygame.draw.rect(surface, inner_c, (self.rect.x + 5, self.rect.y + 5, 10, 10), border_radius=5)
        
        c_x, c_y = self.rect.x + self.width / 2, self.rect.y + self.height / 2
        e_x, e_y = self.look_dir.x * 6, self.look_dir.y * 6
        pygame.draw.circle(surface, (255, 255, 255), (c_x + e_x, c_y + e_y), 14)
        pygame.draw.circle(surface, (0, 0, 0), (c_x + e_x * 1.8, c_y + e_y * 1.8), 6)

        if self.has_dagger:
            dagger_x = self.rect.right if self.look_dir.x >= 0 else self.rect.left
            if self.is_attacking:
                swipe_start = math.pi/4 if self.look_dir.x >= 0 else math.pi*0.75
                swipe_end = -math.pi/4 if self.look_dir.x >= 0 else math.pi*1.25
                arc_rect = pygame.Rect(self.rect.centerx - 30, self.rect.y - 10, 60, 60)
                if self.look_dir.x >= 0:
                    pygame.draw.arc(surface, (200, 200, 200), arc_rect, swipe_end, swipe_start, 4)
                else:
                    pygame.draw.arc(surface, (200, 200, 200), arc_rect, swipe_start, swipe_end, 4)
            else:
                pygame.draw.line(surface, (150, 150, 150), (dagger_x, c_y + 5), (dagger_x + (5 * self.look_dir.x), c_y + 15), 3)
                pygame.draw.line(surface, (100, 50, 20), (dagger_x, c_y + 5), (dagger_x - (2 * self.look_dir.x), c_y), 3)

# --- Level Manager ---
player = Player()
platforms, vines, hazards, trampolines, cannons, projectiles, npcs, portals, scenery, zombies = [pygame.sprite.Group() for _ in range(10)]
boss_entity = None

def load_level(level_num):
    global boss_entity
    for g in [platforms, vines, hazards, trampolines, cannons, projectiles, npcs, portals, scenery, zombies]: g.empty()
    boss_entity = None
    
    if level_num > 10:
        player.has_dagger = True
        
    if level_num == 1:
        env_colors.update({"sky": (100, 180, 210), "dirt": (86, 52, 24), "grass": (54, 180, 44)})
        platforms.add(Platform(0, HEIGHT - 60, WIDTH, 60), Platform(200, 460, 120, 30), Platform(420, 380, 150, 30), Platform(650, 300, 100, 30))
        vines.add(Vine(250, 0, 460), Vine(480, 0, 380))
        npcs.add(NPC(150, HEIGHT - 110, "Space/W/Up to Jump AND Climb!"))
        portals.add(Portal(700, 300)) 
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 2:
        env_colors.update({"sky": (60, 100, 130), "dirt": (86, 52, 24), "grass": (34, 120, 34)})
        platforms.add(Platform(0, HEIGHT - 60, WIDTH, 60), Platform(150, 460, 80, 30), Platform(300, 370, 80, 30), Platform(450, 280, 80, 30), Platform(600, 190, 150, 30))
        vines.add(Vine(490, 0, 280))
        npcs.add(NPC(200, 400, "It's getting darker... Watch your step!"))
        portals.add(Portal(675, 190))
        player.spawn_point = vec(50, HEIGHT - 100)
        
    elif level_num == 3:
        env_colors.update({"sky": (30, 50, 70), "dirt": (60, 40, 20), "grass": (20, 80, 20)})
        platforms.add(Platform(0, HEIGHT - 60, 200, 60), Platform(600, HEIGHT - 60, 200, 60))
        hazards.add(Hazard(200, HEIGHT - 30, 400, 30)) 
        platforms.add(Platform(150, 440, 80, 30), Platform(320, 340, 80, 30), Platform(500, 360, 100, 30))
        vines.add(Vine(210, 0, 440), Vine(380, 0, 340))
        npcs.add(NPC(150, HEIGHT - 110, "Don't fall in the toxic sludge!"))
        portals.add(Portal(700, HEIGHT - 60)) 
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 4: 
        env_colors.update({"sky": (20, 20, 40), "dirt": (40, 30, 30), "grass": (20, 50, 40)})
        platforms.add(Platform(0, HEIGHT - 60, 300, 60), Platform(450, HEIGHT - 60, 400, 60))
        platforms.add(Platform(250, 440, 80, 30), Platform(400, 340, 80, 30))
        scenery.add(CaveEntrance(650, HEIGHT - 60, 250, 300))
        npcs.add(NPC(150, HEIGHT - 110, "The air feels cold up ahead..."))
        portals.add(Portal(650, HEIGHT - 60)) 
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 5: 
        env_colors.update({"sky": (10, 10, 15), "dirt": (70, 70, 75), "grass": (50, 60, 50)})
        platforms.add(Platform(0, HEIGHT - 60, 150, 60), Platform(200, 450, 80, 30), Platform(380, 370, 80, 30), Platform(580, 290, 80, 30), Platform(350, 200, 100, 30), Platform(150, 150, 150, 30))
        cannons.add(Cannon(WIDTH - 40, 420, -1, 0), Cannon(0, 320, 1, 500), Cannon(WIDTH - 40, 220, -1, 1000)) 
        npcs.add(NPC(150, HEIGHT - 110, "Watch out for the automated defenses!"))
        portals.add(Portal(225, 150)) 
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 6: 
        env_colors.update({"sky": (5, 5, 10), "dirt": (40, 40, 45), "grass": (60, 20, 60)}) 
        platforms.add(Platform(0, HEIGHT - 60, WIDTH, 60)) 
        trampolines.add(Trampoline(100, HEIGHT - 90, 60, 30), Trampoline(WIDTH - 160, HEIGHT - 90, 60, 30))
        npcs.add(NPC(200, HEIGHT - 110, "Use the glowing geysers to launch high!"))
        npcs.add(NPC(WIDTH - 200, HEIGHT - 110, "Bounce on the spider's head to defeat it!"))
        boss_entity = SpiderBoss(WIDTH//2, 20)
        player.spawn_point = vec(WIDTH//2, HEIGHT - 100)

    # Syncing Partner's Levels!
    elif level_num == 7: 
        env_colors.update({"sky": (150, 200, 250), "dirt": (200, 200, 220), "grass": (220, 220, 250)}) 
        platforms.add(Platform(0, HEIGHT - 60, 100, 60), Platform(WIDTH - 100, HEIGHT - 60, 100, 60))
        platforms.add(Platform(200, 450, 60, 30), Platform(400, 350, 60, 30), Platform(600, 250, 60, 30))
        trampolines.add(Trampoline(300, HEIGHT - 60, 60, 30), Trampoline(500, HEIGHT - 60, 60, 30))
        cannons.add(Cannon(WIDTH - 40, 330, -1, 0), Cannon(WIDTH - 40, 230, -1, 1000))
        npcs.add(NPC(50, HEIGHT - 110, "You survived! Now ascend the sky ruins!"))
        portals.add(Portal(WIDTH - 50, HEIGHT - 60))
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 8:
        env_colors.update({"sky": (40, 80, 40), "dirt": (60, 40, 20), "grass": (20, 80, 20)})
        platforms.add(Platform(0, HEIGHT - 60, 150, 60), Platform(WIDTH - 150, 100, 150, 30))
        hazards.add(Hazard(150, HEIGHT - 30, WIDTH - 150, 30)) 
        vines.add(Vine(200, 150, 400), Vine(350, 50, 350), Vine(500, 200, 350))
        cannons.add(Cannon(0, 250, 1, 0), Cannon(0, 400, 1, 1000))
        npcs.add(NPC(100, HEIGHT - 110, "Don't look down. Keep moving!"))
        portals.add(Portal(WIDTH - 75, 100))
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 9:
        env_colors.update({"sky": (255, 100, 50), "dirt": (50, 20, 20), "grass": (100, 30, 30)}) 
        platforms.add(Platform(0, HEIGHT - 60, 100, 60), Platform(WIDTH - 100, 80, 100, 30))
        platforms.add(Platform(200, 480, 50, 30), Platform(350, 380, 50, 30), Platform(500, 280, 50, 30), Platform(650, 180, 50, 30))
        trampolines.add(Trampoline(250, HEIGHT - 40, 40, 30), Trampoline(550, HEIGHT - 40, 40, 30))
        vines.add(Vine(420, 180, 200))
        hazards.add(Hazard(100, HEIGHT - 30, WIDTH - 100, 30))
        cannons.add(Cannon(WIDTH - 40, 460, -1, 0), Cannon(0, 360, 1, 500), Cannon(WIDTH - 40, 260, -1, 1000), Cannon(0, 160, 1, 1500))
        npcs.add(NPC(50, HEIGHT - 110, "The final stretch! You can do this!"))
        portals.add(Portal(WIDTH - 50, 80))
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 10:
        env_colors.update({"sky": (20, 30, 20), "dirt": (40, 50, 40), "grass": (20, 40, 20)})
        platforms.add(Platform(0, HEIGHT - 60, WIDTH, 60))
        boss_entity = ZombieBoss(WIDTH//2, HEIGHT - 60)
        npcs.add(NPC(100, HEIGHT - 110, "A huge zombie! Defeat it to get its dagger!"))
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 11:
        env_colors.update({"sky": (30, 20, 40), "dirt": (50, 40, 50), "grass": (30, 20, 30)})
        platforms.add(Platform(0, HEIGHT - 60, WIDTH, 60))
        zombies.add(Zombie(300, HEIGHT - 60, 50), Zombie(500, HEIGHT - 60, 50))
        npcs.add(NPC(100, HEIGHT - 110, "Use SPACE to swing your dagger at zombies!"))
        portals.add(Portal(WIDTH - 50, HEIGHT - 60))
        player.spawn_point = vec(50, HEIGHT - 100)

    elif level_num == 12:
        env_colors.update({"sky": (40, 20, 20), "dirt": (50, 30, 30), "grass": (30, 10, 10)})
        platforms.add(Platform(0, HEIGHT - 60, 200, 60), Platform(300, HEIGHT - 60, 200, 60), Platform(600, HEIGHT - 60, 200, 60))
        hazards.add(Hazard(200, HEIGHT - 30, 100, 30), Hazard(500, HEIGHT - 30, 100, 30))
        zombies.add(Zombie(400, HEIGHT - 60, 40), Zombie(700, HEIGHT - 60, 40))
        portals.add(Portal(WIDTH - 50, HEIGHT - 60))
        player.spawn_point = vec(50, HEIGHT - 100)

    player.pos = vec(player.spawn_point)

# --- Background Environment Globals ---
light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.polygon(light_surface, (255, 240, 150, 25), [(100, -50), (250, -50), (200, HEIGHT), (-50, HEIGHT)])
pygame.draw.polygon(light_surface, (255, 240, 150, 20), [(450, -50), (600, -50), (550, HEIGHT), (300, HEIGHT)])
clouds = [Cloud() for _ in range(3)] 
bg_trees = [Tree(x, HEIGHT - 40, is_bg=True) for x in range(-50, WIDTH + 100, 120)]
fg_trees = [Tree(x, HEIGHT - 40, is_bg=False) for x in range(80, WIDTH, 250)]
bats = [Bat() for _ in range(5)]
stalactites = [Stalactite() for _ in range(10)]
rock_tumblers = [RockTumbler() for _ in range(15)]

# --- Game State Variables ---
GAME_STATE = "LOGIN" # Includes: LOGIN, SPLASH, MENU, PLAYING, VICTORY
current_level = 1
splash_start_time = 0

# Login UI Setup
login_user_input = TextInput(WIDTH//2 - 125, HEIGHT//2 - 40, 250, 40, "Username")
login_pass_input = TextInput(WIDTH//2 - 125, HEIGHT//2 + 10, 250, 40, "Password", is_password=True)
btn_login = Button(WIDTH//2 - 125, HEIGHT//2 + 70, 120, 40, "LOGIN")
btn_register = Button(WIDTH//2 + 5, HEIGHT//2 + 70, 120, 40, "REGISTER")
login_message = ""

# Main Menu UI Setup
btn_play = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 50, "PLAY")
btn_levels = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50, "LEVEL SELECT")
btn_shop_main = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50, "SHOP")
btn_settings = Button(WIDTH//2 - 100, HEIGHT//2 + 160, 200, 50, "SETTINGS")

# Level Select UI Setup
level_btns = []
columns = 4
button_w, button_h = 100, 80
spacing_x, spacing_y = 140, 110
start_x = WIDTH//2 - (spacing_x * 1.5)
start_y = HEIGHT//2 - (spacing_y * 1) - 20 

for i in range(12):
    level_btns.append(LevelButton(start_x + (i%columns)*spacing_x - button_w//2, start_y + (i//columns)*spacing_y, button_w, button_h, i+1))
btn_back_ls = Button(WIDTH//2 - 100, HEIGHT - 60, 200, 50, "BACK")

# Settings UI Setup
is_music_on = True
is_sound_on = True
btn_music = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40, "MUSIC: ON")
btn_sound = Button(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 40, "SOUND: ON")
btn_back_st = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "BACK")

btn_color_cycle = Button(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 50, "COLOR: DEFAULT")
btn_buy = Button(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, "EQUIPPED")
btn_back_shop = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "BACK")

available_colors = [
    {"id": "DEFAULT", "name": "DEFAULT", "color": "DEFAULT", "cost": 0},
    {"id": "RED", "name": "CRIMSON RED", "color": (180, 40, 40), "cost": 10},
    {"id": "GREEN", "name": "FOREST GREEN", "color": (40, 150, 50), "cost": 10},
    {"id": "BLUE", "name": "OCEAN BLUE", "color": (40, 80, 180), "cost": 10},
    {"id": "PURPLE", "name": "ROYAL PURPLE", "color": (120, 40, 180), "cost": 10},
    {"id": "RAINBOW", "name": "RAINBOW", "color": "RAINBOW", "cost": 50},
    {"id": "BW_GRADIENT", "name": "B/W GRADIENT", "color": "BW_GRADIENT", "cost": 50}
]
current_color_index = 0
unlocked_colors = ["DEFAULT"]
total_coins = 0

btn_pause = IconButton(WIDTH - 50, 10, 40, 40, "hamburger")
btn_resume = IconButton(WIDTH//2 - 80, HEIGHT//2 - 40, 40, 40, "resume")
btn_shop_pause = IconButton(WIDTH//2 - 80, HEIGHT//2 + 20, 40, 40, "shop")
btn_quit_menu = IconButton(WIDTH//2 - 80, HEIGHT//2 + 80, 40, 40, "quit")

previous_state = "MENU"
menu_fade_alpha = 255
menu_bg_timer = 0
menu_scene_index = 0
menu_scenes = [
    {"sky": (100, 180, 210), "dirt": (86, 52, 24), "grass": (54, 180, 44)},   # Jungle
    {"sky": (20, 20, 40), "dirt": (40, 30, 30), "grass": (20, 50, 40)},       # Cave Entrance
    {"sky": (10, 10, 15), "dirt": (70, 70, 75), "grass": (50, 60, 50)}        # Deep Cave
]

load_level(current_level)

# --- Main Game Loop ---
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if GAME_STATE == "LOGIN":
            login_user_input.handle_event(event)
            login_pass_input.handle_event(event)
            
            if btn_login.is_clicked(event):
                u, p = login_user_input.text, login_pass_input.text
                if u in accounts_db and accounts_db[u]["password"] == p:
                    current_user = u
                    total_coins = accounts_db[u]["coins"]
                    unlocked_colors = accounts_db[u]["unlocked_colors"]
                    player.color = accounts_db[u]["equipped_color"]
                    
                    GAME_STATE = "SPLASH"
                    splash_start_time = current_time
                else:
                    login_message = "Invalid username or password"
                    
            elif btn_register.is_clicked(event):
                u, p = login_user_input.text, login_pass_input.text
                if not u or not p:
                    login_message = "Fields cannot be empty"
                elif u in accounts_db:
                    login_message = "Username already exists"
                else:
                    accounts_db[u] = {
                        "password": p,
                        "coins": 0,
                        "unlocked_colors": ["DEFAULT"],
                        "equipped_color": "DEFAULT"
                    }
                    save_accounts(accounts_db)
                    
                    current_user = u
                    total_coins = accounts_db[u]["coins"]
                    unlocked_colors = accounts_db[u]["unlocked_colors"]
                    player.color = accounts_db[u]["equipped_color"]
                    
                    GAME_STATE = "SPLASH"
                    splash_start_time = current_time
        
        elif GAME_STATE == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): player.jump(platforms, vines)
                if event.key == pygame.K_ESCAPE: GAME_STATE = "PAUSED"
                if event.key == pygame.K_s:
                    GAME_STATE = "SHOP"
                    previous_state = "PAUSED"
            if btn_pause.is_clicked(event):
                GAME_STATE = "PAUSED"
                
        elif GAME_STATE == "PAUSED":
            if btn_resume.is_clicked(event) or btn_pause.is_clicked(event):
                GAME_STATE = "PLAYING"
            elif btn_shop_pause.is_clicked(event):
                GAME_STATE = "SHOP"
                previous_state = "PAUSED"
            elif btn_quit_menu.is_clicked(event):
                GAME_STATE = "MENU"
                current_level = 1
                load_level(1)
                player.rect.centerx, player.rect.centery = WIDTH // 2, HEIGHT - 60
                
        elif GAME_STATE == "MENU":
            if btn_play.is_clicked(event):
                GAME_STATE = "PLAYING"
                current_level = 1
                load_level(current_level)
            elif btn_levels.is_clicked(event):
                GAME_STATE = "LEVEL_SELECT"
            elif btn_shop_main.is_clicked(event):
                GAME_STATE = "SHOP"
                previous_state = "MENU"
            elif btn_settings.is_clicked(event):
                GAME_STATE = "SETTINGS"
                
        elif GAME_STATE == "LEVEL_SELECT":
            if btn_back_ls.is_clicked(event):
                GAME_STATE = "MENU"
            else:
                for i, btn in enumerate(level_btns):
                    if btn.is_clicked(event):
                        GAME_STATE = "PLAYING"
                        current_level = i + 1
                        load_level(current_level)
                        
        elif GAME_STATE == "SETTINGS":
            if btn_back_st.is_clicked(event):
                GAME_STATE = "MENU"
            elif btn_music.is_clicked(event):
                is_music_on = not is_music_on
                btn_music.text = "MUSIC: ON" if is_music_on else "MUSIC: OFF"
            elif btn_sound.is_clicked(event):
                is_sound_on = not is_sound_on
                btn_sound.text = "SOUND: ON" if is_sound_on else "SOUND: OFF"

        elif GAME_STATE == "SHOP":
            if btn_back_shop.is_clicked(event):
                GAME_STATE = previous_state
            elif btn_color_cycle.is_clicked(event):
                current_color_index = (current_color_index + 1) % len(available_colors)
                cd = available_colors[current_color_index]
                btn_color_cycle.text = f"COLOR: {cd['name']}"
                if cd["id"] in unlocked_colors:
                    btn_buy.text = "EQUIPPED" if player.color == cd["color"] else "EQUIP"
                else:
                    btn_buy.text = f"BUY: {cd['cost']} COINS"
            elif btn_buy.is_clicked(event):
                cd = available_colors[current_color_index]
                if cd["id"] in unlocked_colors:
                    player.color = cd["color"]
                    btn_buy.text = "EQUIPPED"
                    if current_user:
                        accounts_db[current_user]["equipped_color"] = cd["color"]
                        save_accounts(accounts_db)
                elif total_coins >= cd["cost"]:
                    total_coins -= cd["cost"]
                    unlocked_colors.append(cd["id"])
                    player.color = cd["color"]
                    btn_buy.text = "EQUIPPED"
                    if current_user:
                        accounts_db[current_user]["coins"] = total_coins
                        accounts_db[current_user]["unlocked_colors"] = unlocked_colors
                        accounts_db[current_user]["equipped_color"] = cd["color"]
                        save_accounts(accounts_db)

        elif GAME_STATE == "VICTORY":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press R to play again synced!
                    current_level = 1
                    GAME_STATE = 'PLAYING'
                    load_level(current_level)

    # 2. STATE LOGIC & DRAWING
    if GAME_STATE == "LOGIN":
        screen.fill((20, 20, 30))
        
        title_surf = title_font.render("CUBE'S JOURNEY", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_surf, title_rect)
        
        login_user_input.draw(screen)
        login_pass_input.draw(screen)
        btn_login.draw(screen)
        btn_register.draw(screen)
        
        if login_message:
            msg_surf = font.render(login_message, True, (255, 100, 100))
            screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, login_user_input.rect.top - 20)))

    elif GAME_STATE == "SPLASH":
        screen.fill((10, 10, 15)) 
        title_surf = title_font.render("CUBE'S JOURNEY HOME", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(title_surf, title_rect)
        
        if current_time - splash_start_time > 2000:
            GAME_STATE = "MENU"
            menu_bg_timer = current_time

    elif GAME_STATE == "MENU":
        if current_time - menu_bg_timer > 2000:
            menu_bg_timer = current_time
            menu_scene_index = (menu_scene_index + 1) % len(menu_scenes)
            env_colors.update(menu_scenes[menu_scene_index])

        screen.fill(env_colors["sky"])
        
        if menu_scene_index == 0: 
            for cloud in clouds: cloud.update(); cloud.draw(screen)
            for tree in bg_trees: tree.draw(screen)
            for tree in fg_trees: tree.draw(screen)
            screen.blit(light_surface, (0, 0))
        elif menu_scene_index == 1: 
            pygame.draw.rect(screen, (10, 10, 15), (WIDTH//4, 0, WIDTH//2, HEIGHT)) 
        else: 
            for bat in bats: bat.update(); bat.draw(screen)
            for stalactite in stalactites: stalactite.update(); stalactite.draw(screen)
            dim_light = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim_light.fill((50, 30, 10, 50))
            screen.blit(dim_light, (0,0))

        pygame.draw.rect(screen, env_colors["dirt"], (0, HEIGHT - 40, WIDTH, 40))
        pygame.draw.rect(screen, env_colors["grass"], (0, HEIGHT - 40, WIDTH, 10))

        player.rect.center = (WIDTH // 2, HEIGHT - 60)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx, dy = mouse_x - player.rect.centerx, mouse_y - player.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            player.look_dir = vec(dx/dist, dy/dist)
        player.draw(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title_surf = title_font.render("CUBE'S JOURNEY HOME", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_surf, title_rect)

        btn_play.draw(screen)
        btn_levels.draw(screen)
        btn_shop_main.draw(screen)
        btn_settings.draw(screen)

        if menu_fade_alpha > 0:
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.fill((10, 10, 15))
            fade_surf.set_alpha(menu_fade_alpha)
            screen.blit(fade_surf, (0, 0))
            menu_fade_alpha = max(0, menu_fade_alpha - 5)

    elif GAME_STATE == "LEVEL_SELECT":
        screen.fill((20, 20, 30))
        title_surf = title_font.render("SELECT LEVEL", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//8))
        screen.blit(title_surf, title_rect)
        
        for btn in level_btns:
            btn.draw(screen)
        btn_back_ls.draw(screen)

    elif GAME_STATE == "SETTINGS":
        screen.fill((20, 20, 30))
        title_surf = title_font.render("SETTINGS", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//8))
        screen.blit(title_surf, title_rect)
        
        btn_music.draw(screen)
        btn_sound.draw(screen)
        btn_back_st.draw(screen)

    elif GAME_STATE == "SHOP":
        screen.fill((20, 20, 30))
        title_surf = title_font.render("SHOP", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//8))
        screen.blit(title_surf, title_rect)
        
        coin_t = btn_font.render(f"COINS: {total_coins}", True, (255, 215, 0))
        screen.blit(coin_t, (WIDTH//2 - coin_t.get_width()//2, HEIGHT//8 + 50))
        
        btn_color_cycle.draw(screen)
        btn_buy.draw(screen)
        btn_back_shop.draw(screen)

    elif GAME_STATE in ["PLAYING", "PAUSED"]:
        if GAME_STATE == "PLAYING":
            if pygame.sprite.spritecollide(player, portals, False) and player.state == 'alive':
                current_level += 1
                total_coins += 10
                if current_user:
                    accounts_db[current_user]["coins"] = total_coins
                    save_accounts(accounts_db)
                    
                if current_level > 12: 
                    GAME_STATE = "VICTORY"
                else:
                    load_level(current_level)

            for h in hazards:
                if isinstance(h, WebTrap): h.update(platforms)
                else: h.update()
                
            player.update(platforms, vines, hazards, projectiles, trampolines, boss_entity)
            cannons.update(projectiles)
            projectiles.update()
            zombies.update()
            if boss_entity: boss_entity.update(hazards)
            for npc in npcs: npc.update()

        # Updated drawing logic to account for the new levels!
        screen.fill(env_colors["sky"])
        
        if current_level < 5 or current_level > 6:
            for cloud in clouds: cloud.update(); cloud.draw(screen)
            for tree in bg_trees: tree.draw(screen)
            for tree in fg_trees: tree.draw(screen)
            screen.blit(light_surface, (0, 0))
        elif current_level in [5, 6]: 
            for bat in bats: bat.update(); bat.draw(screen)
            for stalactite in stalactites: stalactite.update(); stalactite.draw(screen)
            for rt in rock_tumblers: rt.update(); rt.draw(screen)
            dim_light = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim_light.fill((50, 30, 10, 50))
            screen.blit(dim_light, (0,0))
        
        if current_level == 4:
            for s in scenery: screen.blit(s.image, s.rect)
        
        hazards.draw(screen)
        vines.draw(screen)
        trampolines.draw(screen)
        platforms.draw(screen)
        cannons.draw(screen)
        projectiles.draw(screen)
        zombies.draw(screen)
        
        if boss_entity: boss_entity.draw(screen)
        
        for portal in portals: portal.draw(screen)
        for npc in npcs:
            screen.blit(npc.image, npc.rect)
            npc.draw_tooltip(screen, player.pos) 

        player.draw(screen)
        
        coin_t = btn_font.render(f"COINS: {total_coins}", True, (255, 215, 0))
        screen.blit(coin_t, (10, 10))
        btn_pause.draw(screen)

        if GAME_STATE == "PAUSED":
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 150))
            screen.blit(dim, (0, 0))
            
            p_text = title_font.render("PAUSED", True, (255, 255, 255))
            screen.blit(p_text, p_text.get_rect(center=(WIDTH//2, HEIGHT//4)))
            
            btn_resume.draw(screen)
            res_text = font.render("Resume", True, (255, 255, 255))
            screen.blit(res_text, (btn_resume.rect.right + 10, btn_resume.rect.centery - 10))
            
            btn_shop_pause.draw(screen)
            shop_text = font.render("Shop", True, (255, 255, 255))
            screen.blit(shop_text, (btn_shop_pause.rect.right + 10, btn_shop_pause.rect.centery - 10))
            
            btn_quit_menu.draw(screen)
            quit_text = font.render("Main Menu", True, (255, 255, 255))
            screen.blit(quit_text, (btn_quit_menu.rect.right + 10, btn_quit_menu.rect.centery - 10))

    elif GAME_STATE == "VICTORY":
        # The Golden Celebration screen!
        screen.fill((255, 215, 0)) 
        
        title_text = title_font.render("VICTORY!", True, (255, 255, 255))
        subtitle_text = font.render("Cube has finally returned home!", True, (0, 0, 0))
        restart_text = font.render("Press 'R' to play again", True, (50, 50, 50))
        
        screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
        screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
