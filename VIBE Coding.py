import pygame
import sys
import math
import random

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
        self.particles = []

    def trigger_death(self):
        if self.state == 'alive':
            self.state, self.death_timer = 'dying', pygame.time.get_ticks()
            self.vel, self.acc = vec(0, 0), vec(0, 0)
            for _ in range(40):
                self.particles.append(Particle(self.rect.centerx, self.rect.centery, random.choice([(20, 20, 25), (255, 255, 255)])))

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
        
        ascend = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        descend = keys[pygame.K_DOWN] or keys[pygame.K_s]
        moving_horizontally = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
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
                    if boss_died: portals.add(Portal(WIDTH//2, HEIGHT - 60)) 
                elif current_time - self.invincible_timer > 2000:
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

        pygame.draw.rect(surface, (20, 20, 25), self.rect, border_radius=10)
        pygame.draw.rect(surface, (80, 80, 90), (self.rect.x + 5, self.rect.y + 5, 10, 10), border_radius=5)
        
        c_x, c_y = self.rect.x + self.width / 2, self.rect.y + self.height / 2
        e_x, e_y = self.look_dir.x * 6, self.look_dir.y * 6
        pygame.draw.circle(surface, (255, 255, 255), (c_x + e_x, c_y + e_y), 14)
        pygame.draw.circle(surface, (0, 0, 0), (c_x + e_x * 1.8, c_y + e_y * 1.8), 6)

# --- Level Manager ---
player = Player()
platforms, vines, hazards, trampolines, cannons, projectiles, npcs, portals, scenery = [pygame.sprite.Group() for _ in range(9)]
boss_entity = None

def load_level(level_num):
    global boss_entity
    for g in [platforms, vines, hazards, trampolines, cannons, projectiles, npcs, portals, scenery]: g.empty()
    boss_entity = None
    
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
GAME_STATE = "SPLASH" # Includes: SPLASH, MENU, PLAYING, VICTORY
current_level = 1
splash_start_time = pygame.time.get_ticks()

# Main Menu UI Setup
btn_play = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 50, "PLAY")
btn_levels = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "LEVEL SELECT")
btn_settings = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50, "SETTINGS")

# Level Select UI Setup
level_btns = []
columns = 3
button_w, button_h = 150, 100
spacing_x, spacing_y = 180, 120
start_x = WIDTH//2 - (spacing_x * 1)
start_y = HEIGHT//2 - (spacing_y * 1) - 40 

for i in range(9):
    level_btns.append(LevelButton(start_x + (i%columns)*spacing_x - button_w//2, start_y + (i//columns)*spacing_y, button_w, button_h, i+1))
btn_back_ls = Button(WIDTH//2 - 100, HEIGHT - 70, 200, 50, "BACK")

# Settings UI Setup
is_music_on = True
is_sound_on = True
btn_music = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "MUSIC: ON")
btn_sound = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "SOUND: ON")
btn_back_st = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "BACK")
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
        
        if GAME_STATE == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): player.jump(platforms, vines)
                
        elif GAME_STATE == "MENU":
            if btn_play.is_clicked(event):
                GAME_STATE = "PLAYING"
                current_level = 1
                load_level(current_level)
            elif btn_levels.is_clicked(event):
                GAME_STATE = "LEVEL_SELECT"
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

        elif GAME_STATE == "VICTORY":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press R to play again synced!
                    current_level = 1
                    GAME_STATE = 'PLAYING'
                    load_level(current_level)

    # 2. STATE LOGIC & DRAWING
    if GAME_STATE == "SPLASH":
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
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//4 - 20))
        screen.blit(title_surf, title_rect)
        
        btn_music.draw(screen)
        btn_sound.draw(screen)
        btn_back_st.draw(screen)

    elif GAME_STATE == "PLAYING":
        if pygame.sprite.spritecollide(player, portals, False) and player.state == 'alive':
            current_level += 1
            if current_level > 9: # Updated to trigger Victory after level 9! 
                GAME_STATE = "VICTORY"
            else:
                load_level(current_level)

        for h in hazards:
            if isinstance(h, WebTrap): h.update(platforms)
            else: h.update()
            
        player.update(platforms, vines, hazards, projectiles, trampolines, boss_entity)
        cannons.update(projectiles)
        projectiles.update()
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
        
        if boss_entity: boss_entity.draw(screen)
        
        for portal in portals: portal.draw(screen)
        for npc in npcs:
            screen.blit(npc.image, npc.rect)
            npc.draw_tooltip(screen, player.pos) 

        player.draw(screen)

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
