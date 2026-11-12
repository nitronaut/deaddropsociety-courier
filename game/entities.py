"""
Entity classes for Dead Drop Society
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from enum import Enum

# ==================== CONSTANTS ====================

# Colors - High contrast, gritty aesthetic
COLORS = {
    'background': (15, 15, 20),
    'city_dark': (25, 25, 35),
    'city_medium': (40, 40, 55),
    'city_light': (60, 60, 80),
    'accent_cyan': (0, 200, 255),
    'accent_orange': (255, 120, 0),
    'accent_red': (255, 50, 50),
    'accent_green': (0, 200, 100),
    'text_primary': (240, 240, 250),
    'text_secondary': (180, 180, 200),
    'text_warning': (255, 200, 100),
    'text_danger': (255, 100, 100),
    'player': (0, 200, 255),
    'patrol': (255, 80, 80),
    'terminal': (0, 180, 255),
    'dead_drop_fresh': (0, 255, 150),
    'dead_drop_stale': (255, 200, 0),
    'dead_drop_decayed': (200, 50, 50),
    'scan_radius': (0, 150, 255, 50),
    'alert_radius': (255, 50, 50, 80),
    'grid_lines': (30, 30, 40),
    'building_1': (50, 50, 70),
    'building_2': (70, 70, 90),
    'road': (40, 40, 50),
    'suburb': (35, 45, 35),
    'water': (20, 30, 50),
}

# Game parameters
PLAYER_SPEED = 200
PLAYER_SPRINT_MULTIPLIER = 1.8
SCAN_RADIUS = 200
SCAN_DURATION = 0.5
SCAN_COOLDOWN = 3.0
EXTRACTION_TIME = 1.5
UPLOAD_TIME = 2.0
DATA_DECAY_RATE = 0.1
RIVAL_SPAWN_RATE = 15.0
PATROL_DETECTION_RADIUS = 150
PATROL_MOVE_SPEED = 120
RIVAL_MOVE_SPEED = 150

# Map parameters
MAP_WIDTH = 200
MAP_HEIGHT = 120
CITY_CENTER_X = MAP_WIDTH // 2
CITY_CENTER_Y = MAP_HEIGHT // 2
CITY_RADIUS = 40
EXURB_RADIUS = 80

# ==================== ENUMS ====================

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    SCANNING = "scanning"
    EXTRACTING = "extracting"
    UPLOADING = "uploading"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class DistrictType(Enum):
    DOWNTOWN = "downtown"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    COMMERCIAL = "commercial"
    SUBURBS = "suburbs"
    EXURBS = "exurbs"
    PARK = "park"
    WATER = "water"

class DeadDropStatus(Enum):
    FRESH = "fresh"
    STALE = "stale"
    DECAYED = "decayed"
    UPDATED = "updated"

# ==================== DATA CLASSES ====================

class Vector2:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalized(self) -> 'Vector2':
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return self / length
    
    def distance_to(self, other: 'Vector2') -> float:
        return (self - other).length()
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))

class Entity:
    def __init__(self, position: Vector2, radius: float = 16, color: Tuple[int, int, int] = (255, 255, 255), visible: bool = True):
        self.position = position
        self.radius = radius
        self.color = color
        self.visible = visible
    
    def draw(self, screen, camera_offset: Vector2):
        if not self.visible:
            return
        draw_pos = self.position - camera_offset
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), int(self.radius))

class DataCache:
    def __init__(self, id: int, position: Vector2, freshness: float = 100.0, size: float = 1.0, encryption_level: int = 1):
        self.id = id
        self.position = position
        self.freshness = freshness
        self.size = size
        self.encryption_level = encryption_level
        self.status = DeadDropStatus.FRESH
        self.discovered = False
        self.extracted = False
        self.updated = False
    
    def update(self, dt: float):
        self.freshness -= DATA_DECAY_RATE * dt * (1 + random.random() * 0.5)
        self.freshness = max(0, self.freshness)
        
        if self.freshness > 70:
            self.status = DeadDropStatus.FRESH
        elif self.freshness > 30:
            self.status = DeadDropStatus.STALE
        else:
            self.status = DeadDropStatus.DECAYED
    
    def get_color(self) -> Tuple[int, int, int]:
        if self.updated:
            return COLORS['accent_green']
        if self.status == DeadDropStatus.FRESH:
            return COLORS['dead_drop_fresh']
        elif self.status == DeadDropStatus.STALE:
            return COLORS['dead_drop_stale']
        else:
            return COLORS['dead_drop_decayed']
    
    def get_radius(self) -> int:
        if self.updated:
            return 8
        return 10 + int(self.size * 4)

class DeadDrop(Entity):
    def __init__(self, cache: DataCache):
        super().__init__(cache.position, cache.get_radius(), cache.get_color())
        self.cache = cache
        self.hidden = True
        self.pulse_timer = 0.0
        self.pulse_alpha = 0
    
    def update(self, dt: float):
        self.cache.update(dt)
        self.color = self.cache.get_color()
        self.radius = self.cache.get_radius()
        
        if self.cache.discovered:
            self.pulse_timer += dt * 2
            self.pulse_alpha = int(100 + 100 * math.sin(self.pulse_timer))
    
    def draw(self, screen, camera_offset: Vector2):
        if self.hidden and not self.cache.discovered:
            return
        
        draw_pos = self.position - camera_offset
        
        if self.cache.discovered:
            alpha = self.pulse_alpha if self.cache.status == DeadDropStatus.FRESH else 150
            glow_surface = pygame.Surface((int(self.radius * 3), int(self.radius * 3)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha), (int(self.radius * 1.5), int(self.radius * 1.5)), int(self.radius * 1.5))
            screen.blit(glow_surface, (int(draw_pos.x - self.radius * 1.5), int(draw_pos.y - self.radius * 1.5)))
        
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), int(self.radius))
        
        if self.cache.updated:
            pygame.draw.circle(screen, COLORS['accent_green'], (int(draw_pos.x), int(draw_pos.y)), int(self.radius * 0.6))

class Player(Entity):
    def __init__(self, position: Vector2):
        super().__init__(position, 12, COLORS['player'])
        self.speed = PLAYER_SPEED
        self.sprinting = False
        self.scanning = False
        self.scan_progress = 0.0
        self.scan_cooldown = 0.0
        self.extracted_cache = None
        self.upload_progress = 0.0
        self.alert_level = 0.0
        self.stealth_mode = False
        self.inventory = []
        self.last_position = position
        self.velocity = Vector2(0, 0)
    
    def update(self, dt: float, keys):
        direction = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        
        if direction.length() > 0:
            direction = direction.normalized()
            self.velocity = direction * self.speed
            if self.sprinting:
                self.velocity = self.velocity * PLAYER_SPRINT_MULTIPLIER
        else:
            self.velocity = Vector2(0, 0)
        
        self.last_position = self.position
        self.position = self.position + self.velocity * dt
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.stealth_mode = True
        else:
            self.stealth_mode = False
        
        if self.scan_cooldown > 0:
            self.scan_cooldown -= dt
        
        if self.alert_level > 0:
            self.alert_level -= dt * 5
            self.alert_level = max(0, self.alert_level)

class Patrol(Entity):
    def __init__(self, position: Vector2, path: List[Vector2]):
        super().__init__(position, 10, COLORS['patrol'])
        self.path = path
        self.path_index = 0
        self.alertness = 0.0
        self.chase_target = None
        self.chase_timer = 0.0
        self.move_speed = PATROL_MOVE_SPEED
        self.target_position = position
        self.investigation_timer = 0.0
    
    def update(self, dt: float, player: Player, dead_drops: List['DeadDrop']):
        if self.alertness > 0:
            self.alertness -= dt * 2
            self.alertness = max(0, self.alertness)
        
        if self.chase_target is None:
            distance_to_player = self.position.distance_to(player.position)
            if distance_to_player < PATROL_DETECTION_RADIUS:
                detection_chance = dt * (0.5 + player.alert_level / 200 + (0 if player.stealth_mode else 0.3))
                if random.random() < detection_chance:
                    self.chase_target = player.position
                    self.chase_timer = 10.0
                    self.alertness = 100
            
            for drop in dead_drops:
                if drop.cache.extracted and not drop.cache.updated:
                    distance = self.position.distance_to(drop.position)
                    if distance < PATROL_DETECTION_RADIUS * 0.7:
                        self.chase_target = drop.position
                        self.chase_timer = 5.0
                        self.alertness = 80
                        break
        
        if self.chase_target is not None:
            direction = (self.chase_target - self.position).normalized()
            self.position = self.position + direction * self.move_speed * dt
            self.chase_timer -= dt
            if self.chase_timer <= 0:
                self.chase_target = None
        else:
            if len(self.path) > 0:
                target = self.path[self.path_index]
                distance = self.position.distance_to(target)
                if distance < 10:
                    self.path_index = (self.path_index + 1) % len(self.path)
                    target = self.path[self.path_index]
                direction = (target - self.position).normalized()
                self.position = self.position + direction * self.move_speed * dt
    
    def draw(self, screen, camera_offset: Vector2):
        super().draw(screen, camera_offset)
        draw_pos = self.position - camera_offset
        if self.alertness > 50:
            alert_radius = int(8 + self.alertness / 25)
            pygame.draw.circle(screen, COLORS['accent_red'], (int(draw_pos.x), int(draw_pos.y)), alert_radius, 2)

class Rival(Entity):
    def __init__(self, position: Vector2):
        super().__init__(position, 10, COLORS['accent_orange'])
        self.move_speed = RIVAL_MOVE_SPEED
        self.target_drop = None
        self.target_terminal = None
        self.action_timer = 0.0
        self.state = "searching"
    
    def update(self, dt: float, player: Player, dead_drops: List['DeadDrop'], terminals: List['Terminal']):
        if self.state == "searching":
            fresh_drops = [d for d in dead_drops if not d.cache.discovered and d.cache.status == DeadDropStatus.FRESH]
            if fresh_drops:
                nearest = min(fresh_drops, key=lambda d: self.position.distance_to(d.position))
                self.target_drop = nearest
                self.state = "moving_to_drop"
            else:
                fresh_drops = [d for d in dead_drops if d.cache.status == DeadDropStatus.FRESH and not d.cache.extracted]
                if fresh_drops:
                    nearest = min(fresh_drops, key=lambda d: self.position.distance_to(d.position))
                    self.target_drop = nearest
                    self.state = "moving_to_drop"
        
        elif self.state == "moving_to_drop":
            if self.target_drop:
                direction = (self.target_drop.position - self.position).normalized()
                self.position = self.position + direction * self.move_speed * dt
                if self.position.distance_to(self.target_drop.position) < 20:
                    self.state = "extracting"
                    self.action_timer = EXTRACTION_TIME
        
        elif self.state == "extracting":
            self.action_timer -= dt
            if self.action_timer <= 0:
                if self.target_drop:
                    self.target_drop.cache.extracted = True
                    self.state = "searching_terminal"
        
        elif self.state == "searching_terminal":
            available_terminals = [t for t in terminals if not t.occupied]
            if available_terminals:
                nearest = min(available_terminals, key=lambda t: self.position.distance_to(t.position))
                self.target_terminal = nearest
                self.state = "moving_to_terminal"
        
        elif self.state == "moving_to_terminal":
            if self.target_terminal:
                direction = (self.target_terminal.position - self.position).normalized()
                self.position = self.position + direction * self.move_speed * dt
                if self.position.distance_to(self.target_terminal.position) < 20:
                    self.state = "uploading"
                    self.action_timer = UPLOAD_TIME
                    self.target_terminal.occupied = True
        
        elif self.state == "uploading":
            self.action_timer -= dt
            if self.action_timer <= 0:
                if self.target_terminal and self.target_drop:
                    for drop in dead_drops:
                        if drop != self.target_drop and not drop.cache.updated:
                            drop.cache.updated = True
                            drop.cache.freshness = 100
                    self.target_terminal.occupied = False
                    self.state = "fleeing"
                    self.action_timer = 3.0
        
        elif self.state == "fleeing":
            direction = (self.position - player.position).normalized()
            self.position = self.position + direction * self.move_speed * 1.5 * dt
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.state = "searching"

class Terminal(Entity):
    def __init__(self, position: Vector2):
        super().__init__(position, 16, COLORS['terminal'])
        self.occupied = False
        self.upload_progress = 0.0
        self.pulse_timer = 0.0
    
    def update(self, dt: float):
        self.pulse_timer += dt * 2
    
    def draw(self, screen, camera_offset: Vector2):
        draw_pos = self.position - camera_offset
        alpha = int(150 + 100 * math.sin(self.pulse_timer))
        glow_surface = pygame.Surface((int(self.radius * 3), int(self.radius * 3)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (0, 180, 255, alpha), (int(self.radius * 1.5), int(self.radius * 1.5)), int(self.radius * 1.5))
        screen.blit(glow_surface, (int(draw_pos.x - self.radius * 1.5), int(draw_pos.y - self.radius * 1.5)))
        pygame.draw.circle(screen, self.color, (int(draw_pos.x), int(draw_pos.y)), int(self.radius))
        if self.occupied:
            pygame.draw.circle(screen, COLORS['accent_green'], (int(draw_pos.x), int(draw_pos.y)), int(self.radius * 0.7))

class MapTile:
    def __init__(self, position: Vector2, district_type: DistrictType, building_density: float = 0.0, road: bool = False):
        self.position = position
        self.district_type = district_type
        self.building_density = building_density
        self.road = road
    
    def get_color(self) -> Tuple[int, int, int]:
        colors = {
            DistrictType.DOWNTOWN: COLORS['city_light'],
            DistrictType.RESIDENTIAL: COLORS['city_medium'],
            DistrictType.INDUSTRIAL: COLORS['city_dark'],
            DistrictType.COMMERCIAL: COLORS['city_medium'],
            DistrictType.SUBURBS: COLORS['suburb'],
            DistrictType.EXURBS: COLORS['city_dark'],
            DistrictType.PARK: (30, 60, 30),
            DistrictType.WATER: COLORS['water'],
        }
        return colors.get(self.district_type, COLORS['city_dark'])

class District:
    def __init__(self, center: Vector2, radius: int, district_type: DistrictType):
        self.center = center
        self.radius = radius
        self.district_type = district_type
    
    def contains(self, position: Vector2) -> bool:
        return self.center.distance_to(position) < self.radius
