#!/usr/bin/env python3
"""
Dead Drop Society - Main Game File
Top-down 2D open-world game about locating and updating encrypted data caches
"""

import pygame
import sys
import random
import math
import time
from typing import List, Tuple, Optional
from game.entities import (
    Vector2, Entity, DataCache, DeadDrop, Player, Patrol, Rival, Terminal,
    MapTile, District, GameState, DistrictType, DeadDropStatus, COLORS,
    PLAYER_SPEED, PLAYER_SPRINT_MULTIPLIER, SCAN_RADIUS, SCAN_DURATION, SCAN_COOLDOWN,
    EXTRACTION_TIME, UPLOAD_TIME, DATA_DECAY_RATE, RIVAL_SPAWN_RATE,
    PATROL_DETECTION_RADIUS, PATROL_MOVE_SPEED, RIVAL_MOVE_SPEED,
    MAP_WIDTH, MAP_HEIGHT, CITY_CENTER_X, CITY_CENTER_Y, CITY_RADIUS, EXURB_RADIUS
)

# Try to initialize mixer
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MINIMAP_SIZE = 200
TILE_SIZE = 32

# Game settings
NUM_DEAD_DROPS = 20
NUM_TERMINALS = 5
NUM_PATROLS = 8

# ==================== WORLD GENERATION ====================

class WorldGenerator:
    def __init__(self):
        self.districts: List[District] = []
        self.tiles: List[MapTile] = []
        self.road_points: List[Vector2] = []
    
    def generate(self) -> Tuple[List[District], List[MapTile], List[Vector2]]:
        self.districts = []
        
        # Downtown core
        self.districts.append(District(
            Vector2(CITY_CENTER_X, CITY_CENTER_Y),
            CITY_RADIUS // 2,
            DistrictType.DOWNTOWN
        ))
        
        # Inner city districts
        for angle in range(0, 360, 90):
            rad = math.radians(angle)
            offset_x = math.cos(rad) * CITY_RADIUS * 0.6
            offset_y = math.sin(rad) * CITY_RADIUS * 0.6
            district_type = random.choice([
                DistrictType.RESIDENTIAL,
                DistrictType.COMMERCIAL,
                DistrictType.INDUSTRIAL
            ])
            self.districts.append(District(
                Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                CITY_RADIUS * 0.4,
                district_type
            ))
        
        # Suburbs
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            offset_x = math.cos(rad) * EXURB_RADIUS * 0.7
            offset_y = math.sin(rad) * EXURB_RADIUS * 0.7
            self.districts.append(District(
                Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                EXURB_RADIUS * 0.3,
                DistrictType.SUBURBS
            ))
        
        # Exurbs
        for angle in range(0, 360, 120):
            rad = math.radians(angle)
            offset_x = math.cos(rad) * EXURB_RADIUS * 1.2
            offset_y = math.sin(rad) * EXURB_RADIUS * 1.2
            self.districts.append(District(
                Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                EXURB_RADIUS * 0.4,
                DistrictType.EXURBS
            ))
        
        # Parks
        self.districts.append(District(
            Vector2(CITY_CENTER_X - 30, CITY_CENTER_Y - 30), 20, DistrictType.PARK
        ))
        self.districts.append(District(
            Vector2(CITY_CENTER_X + 40, CITY_CENTER_Y + 20), 15, DistrictType.PARK
        ))
        
        # Water
        self.districts.append(District(
            Vector2(CITY_CENTER_X + 60, CITY_CENTER_Y - 40), 25, DistrictType.WATER
        ))
        
        # Generate tiles
        self.tiles = []
        for x in range(0, MAP_WIDTH, TILE_SIZE):
            for y in range(0, MAP_HEIGHT, TILE_SIZE):
                pos = Vector2(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                district = None
                for d in reversed(self.districts):
                    if d.contains(pos):
                        district = d
                        break
                district_type = district.district_type if district else DistrictType.RESIDENTIAL
                road = (abs(pos.x - CITY_CENTER_X) < 5 or abs(pos.y - CITY_CENTER_Y) < 5 or
                       pos.x % 40 == 0 or pos.y % 40 == 0)
                self.tiles.append(MapTile(pos, district_type, random.random() * 0.5, road))
        
        # Generate road network
        self.road_points = []
        for x in range(0, MAP_WIDTH, TILE_SIZE * 4):
            self.road_points.append(Vector2(x, CITY_CENTER_Y))
        for y in range(0, MAP_HEIGHT, TILE_SIZE * 4):
            self.road_points.append(Vector2(CITY_CENTER_X, y))
        for i in range(-30, 30, TILE_SIZE * 2):
            self.road_points.append(Vector2(CITY_CENTER_X + i, CITY_CENTER_Y + i))
            self.road_points.append(Vector2(CITY_CENTER_X + i, CITY_CENTER_Y - i))
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            radius = CITY_RADIUS * 0.8
            self.road_points.append(Vector2(
                CITY_CENTER_X + math.cos(rad) * radius,
                CITY_CENTER_Y + math.sin(rad) * radius
            ))
        
        return self.districts, self.tiles, self.road_points

# ==================== GAME CLASS ====================

class DeadDropSociety:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dead Drop Society")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Courier New', 16)
        self.font_large = pygame.font.SysFont('Courier New', 24)
        self.font_title = pygame.font.SysFont('Courier New', 36, bold=True)
        
        self.state = GameState.MENU
        self.running = True
        self.paused = False
        
        self.world_gen = WorldGenerator()
        self.districts, self.tiles, self.road_points = self.world_gen.generate()
        
        self.player = Player(Vector2(CITY_CENTER_X, CITY_CENTER_Y))
        self.dead_drops: List[DeadDrop] = []
        self.terminals: List[Terminal] = []
        self.patrols: List[Patrol] = []
        self.rivals: List[Rival] = []
        
        self.camera_offset = Vector2(0, 0)
        self.camera_target = Vector2(0, 0)
        
        self.scan_radius = SCAN_RADIUS
        self.scan_active = False
        self.scan_results: List[DeadDrop] = []
        
        self.play_time = 0.0
        self.score = 0
        self.high_score = 0
        
        self.show_minimap = True
        self.show_hud = True
        self.alert_messages: List[Tuple[str, float]] = []
        
        self.sound_system = None
        self.sounds_enabled = SOUND_AVAILABLE
        if SOUND_AVAILABLE:
            try:
                from sounds import SoundGenerator
                self.sound_system = SoundGenerator()
            except:
                self.sounds_enabled = False
        else:
            self.sounds_enabled = False
        
        self.rival_spawn_timer = 0.0
        
        self.stats = {
            'drops_discovered': 0,
            'drops_extracted': 0,
            'drops_updated': 0,
            'drops_decayed': 0,
            'rival_intercepts': 0,
            'patrol_alerts': 0,
        }
        
        self.generate_dead_drops()
        self.generate_terminals()
        self.generate_patrols()
    
    def generate_dead_drops(self):
        self.dead_drops = []
        for i in range(NUM_DEAD_DROPS):
            if i < NUM_DEAD_DROPS // 3:
                angle = random.random() * math.pi * 2
                radius = random.random() * CITY_RADIUS * 0.8
                pos = Vector2(CITY_CENTER_X + math.cos(angle) * radius,
                             CITY_CENTER_Y + math.sin(angle) * radius)
                freshness = 100
                size = random.random() * 0.5 + 0.5
            elif i < NUM_DEAD_DROPS * 2 // 3:
                angle = random.random() * math.pi * 2
                radius = CITY_RADIUS + random.random() * (EXURB_RADIUS - CITY_RADIUS) * 0.7
                pos = Vector2(CITY_CENTER_X + math.cos(angle) * radius,
                             CITY_CENTER_Y + math.sin(angle) * radius)
                freshness = random.random() * 40 + 60
                size = random.random() * 0.5 + 0.5
            else:
                angle = random.random() * math.pi * 2
                radius = EXURB_RADIUS + random.random() * 20
                pos = Vector2(CITY_CENTER_X + math.cos(angle) * radius,
                             CITY_CENTER_Y + math.sin(angle) * radius)
                freshness = random.random() * 30 + 40
                size = random.random() * 0.3 + 0.3
            
            self.dead_drops.append(DeadDrop(DataCache(len(self.dead_drops), pos, freshness, size)))
    
    def generate_terminals(self):
        self.terminals = []
        for i in range(NUM_TERMINALS):
            angle = random.random() * math.pi * 2
            radius = random.random() * EXURB_RADIUS * 0.8
            pos = Vector2(CITY_CENTER_X + math.cos(angle) * radius,
                         CITY_CENTER_Y + math.sin(angle) * radius)
            self.terminals.append(Terminal(pos))
    
    def generate_patrols(self):
        self.patrols = []
        for _ in range(NUM_PATROLS):
            path_length = random.randint(4, 8)
            path = [random.choice(self.road_points)]
            for _ in range(path_length - 1):
                nearby = [p for p in self.road_points if p.distance_to(path[-1]) < 100]
                if nearby:
                    path.append(random.choice(nearby))
            self.patrols.append(Patrol(path[0], path))
    
    def spawn_rival(self):
        side = random.choice(['north', 'south', 'east', 'west'])
        if side == 'north':
            pos = Vector2(random.random() * MAP_WIDTH, 0)
        elif side == 'south':
            pos = Vector2(random.random() * MAP_WIDTH, MAP_HEIGHT)
        elif side == 'east':
            pos = Vector2(MAP_WIDTH, random.random() * MAP_HEIGHT)
        else:
            pos = Vector2(0, random.random() * MAP_HEIGHT)
        self.rivals.append(Rival(pos))
        self.add_alert_message(f"Rival detected at {side} border", 3.0)
        if self.sound_system and self.sounds_enabled:
            self.sound_system.play('rival_spawn', volume=0.6)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    elif self.state == GameState.MENU:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.PLAYING and self.player.scan_cooldown <= 0:
                        self.start_scan()
                elif event.key == pygame.K_e:
                    if self.state == GameState.PLAYING:
                        self.try_extract()
                elif event.key == pygame.K_q:
                    if self.state == GameState.PLAYING:
                        self.try_upload()
                elif event.key == pygame.K_TAB:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_m:
                    self.show_hud = not self.show_hud
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self.reset_game()
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.VICTORY, GameState.GAME_OVER]:
                        self.reset_game()
                        self.state = GameState.PLAYING
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_minimap:
                    mouse_pos = pygame.mouse.get_pos()
                    minimap_rect = pygame.Rect(
                        SCREEN_WIDTH - MINIMAP_SIZE - 20,
                        SCREEN_HEIGHT - MINIMAP_SIZE - 20,
                        MINIMAP_SIZE, MINIMAP_SIZE
                    )
                    if minimap_rect.collidepoint(mouse_pos):
                        rel_x = (mouse_pos[0] - minimap_rect.x) / MINIMAP_SIZE
                        rel_y = (mouse_pos[1] - minimap_rect.y) / MINIMAP_SIZE
                        self.player.position = Vector2(rel_x * MAP_WIDTH, rel_y * MAP_HEIGHT)
        
        return pygame.key.get_pressed()
    
    def start_scan(self):
        if self.player.scan_cooldown > 0:
            return
        self.player.scanning = True
        self.player.scan_progress = 0.0
        self.scan_active = True
        self.scan_results = []
        if self.sound_system and self.sounds_enabled:
            self.sound_system.play('scan_start', volume=0.7)
        for drop in self.dead_drops:
            if not drop.cache.discovered:
                if self.player.position.distance_to(drop.position) < self.scan_radius:
                    self.scan_results.append(drop)
        self.scan_results.sort(key=lambda d: -d.cache.freshness)
    
    def complete_scan(self):
        self.player.scanning = False
        self.scan_active = False
        self.player.scan_cooldown = SCAN_COOLDOWN
        if self.sound_system and self.sounds_enabled and self.scan_results:
            self.sound_system.play('scan_complete', volume=0.8)
        for drop in self.scan_results:
            drop.cache.discovered = True
            drop.hidden = False
            self.stats['drops_discovered'] += 1
            self.add_alert_message(f"Dead Drop #{drop.cache.id} discovered", 2.0)
        if self.scan_results:
            freshest = self.scan_results[0]
            self.add_alert_message(f"Freshest cache: DD#{freshest.cache.id} ({freshest.cache.freshness:.0f}%)", 4.0)
    
    def try_extract(self):
        if self.player.extracted_cache is not None:
            self.add_alert_message("Already carrying a cache", 1.0)
            return
        nearest_drop = None
        nearest_distance = float('inf')
        for drop in self.dead_drops:
            if drop.cache.discovered and not drop.cache.extracted and drop.cache.status != DeadDropStatus.DECAYED:
                distance = self.player.position.distance_to(drop.position)
                if distance < nearest_distance and distance < 30:
                    nearest_distance = distance
                    nearest_drop = drop
        if nearest_drop:
            self.player.extracted_cache = nearest_drop.cache
            nearest_drop.cache.extracted = True
            self.player.upload_progress = 0.0
            self.stats['drops_extracted'] += 1
            self.add_alert_message(f"Extracted cache from DD#{nearest_drop.cache.id}", 2.0)
            if self.sound_system and self.sounds_enabled:
                self.sound_system.play('extract', volume=0.8)
            self.player.alert_level += 20
            for patrol in self.patrols:
                distance = patrol.position.distance_to(nearest_drop.position)
                if distance < PATROL_DETECTION_RADIUS * 1.5:
                    patrol.alertness = min(100, patrol.alertness + 30)
                    if patrol.chase_target is None:
                        patrol.chase_target = nearest_drop.position
                        patrol.chase_timer = 8.0
        else:
            self.add_alert_message("No extractable cache nearby", 1.0)
    
    def try_upload(self):
        if self.player.extracted_cache is None:
            self.add_alert_message("No cache to upload", 1.0)
            return
        nearest_terminal = None
        nearest_distance = float('inf')
        for terminal in self.terminals:
            if not terminal.occupied:
                distance = self.player.position.distance_to(terminal.position)
                if distance < nearest_distance and distance < 30:
                    nearest_distance = distance
                    nearest_terminal = terminal
        if nearest_terminal:
            self.player.upload_progress = 0.0
            nearest_terminal.occupied = True
            self.state = GameState.UPLOADING
            self.add_alert_message("Uploading cache to terminal...", 2.0)
        else:
            self.add_alert_message("No available terminal nearby", 1.0)
    
    def complete_upload(self):
        if self.player.extracted_cache is None:
            return
        for terminal in self.terminals:
            if terminal.occupied and self.player.position.distance_to(terminal.position) < 40:
                terminal.occupied = False
                break
        for drop in self.dead_drops:
            if not drop.cache.updated and not drop.cache.extracted:
                drop.cache.updated = True
                drop.cache.freshness = 100
                self.stats['drops_updated'] += 1
        self.stats['drops_updated'] += 1
        self.player.extracted_cache = None
        self.player.upload_progress = 0.0
        self.state = GameState.PLAYING
        if self.sound_system and self.sounds_enabled:
            self.sound_system.play('upload', volume=0.9)
        score_gain = 100 * len([d for d in self.dead_drops if d.cache.updated])
        self.score += score_gain
        self.add_alert_message(f"Upload complete! +{score_gain} points", 4.0)
        if all(d.cache.updated for d in self.dead_drops):
            self.state = GameState.VICTORY
            self.add_alert_message("All dead drops updated! VICTORY!", 10.0)
            if self.sound_system and self.sounds_enabled:
                self.sound_system.play('victory', volume=0.9)
    
    def add_alert_message(self, message: str, duration: float):
        self.alert_messages.append((message, duration))
        if len(self.alert_messages) > 5:
            self.alert_messages.pop(0)
    
    def update(self, dt: float, keys):
        if self.state in [GameState.MENU, GameState.GAME_OVER, GameState.VICTORY]:
            return
        if self.paused:
            return
        
        self.player.update(dt, keys)
        self.player.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        self.camera_target = Vector2(
            self.player.position.x - SCREEN_WIDTH / 2,
            self.player.position.y - SCREEN_HEIGHT / 2
        )
        self.camera_offset += (self.camera_target - self.camera_offset) * dt * 5
        self.camera_offset.x = max(0, min(MAP_WIDTH - SCREEN_WIDTH, self.camera_offset.x))
        self.camera_offset.y = max(0, min(MAP_HEIGHT - SCREEN_HEIGHT, self.camera_offset.y))
        
        if self.player.scanning:
            self.player.scan_progress += dt / SCAN_DURATION
            if self.player.scan_progress >= 1.0:
                self.complete_scan()
        
        if self.state == GameState.UPLOADING and self.player.extracted_cache is not None:
            self.player.upload_progress += dt / UPLOAD_TIME
            if self.player.upload_progress >= 1.0:
                self.complete_upload()
        
        for drop in self.dead_drops:
            drop.update(dt)
            if drop.cache.freshness <= 0 and drop.cache.status != DeadDropStatus.DECAYED:
                drop.cache.status = DeadDropStatus.DECAYED
                self.stats['drops_decayed'] += 1
                self.add_alert_message(f"Dead Drop #{drop.cache.id} has decayed!", 3.0)
                if self.sound_system and self.sounds_enabled:
                    self.sound_system.play('decay', volume=0.5)
        
        for patrol in self.patrols:
            patrol.update(dt, self.player, self.dead_drops)
        
        for rival in self.rivals:
            rival.update(dt, self.player, self.dead_drops, self.terminals)
        
        for terminal in self.terminals:
            terminal.update(dt)
        
        self.rival_spawn_timer += dt
        if self.rival_spawn_timer >= RIVAL_SPAWN_RATE and len(self.rivals) < 10:
            self.spawn_rival()
            self.rival_spawn_timer = 0.0
        
        self.alert_messages = [(msg, duration - dt) for msg, duration in self.alert_messages if duration > 0]
        self.play_time += dt
        
        decayed_count = sum(1 for d in self.dead_drops if d.cache.status == DeadDropStatus.DECAYED)
        if decayed_count >= len(self.dead_drops) // 2:
            self.state = GameState.GAME_OVER
            self.add_alert_message("Too many caches decayed! GAME OVER", 10.0)
            if self.sound_system and self.sounds_enabled:
                self.sound_system.play('game_over', volume=0.8)
        
        for patrol in self.patrols:
            if patrol.alertness > 80 and patrol.position.distance_to(self.player.position) < 20:
                self.state = GameState.GAME_OVER
                self.add_alert_message("Caught by patrol! GAME OVER", 10.0)
                break
        
        for rival in self.rivals:
            if rival.state == "uploading" and rival.action_timer < UPLOAD_TIME * 0.5:
                self.stats['rival_intercepts'] += 1
                self.add_alert_message("Rival is uploading! Hurry!", 3.0)
    
    def draw_map(self):
        for tile in self.tiles:
            draw_pos = tile.position - self.camera_offset
            if (draw_pos.x < -TILE_SIZE or draw_pos.x > SCREEN_WIDTH + TILE_SIZE or
                draw_pos.y < -TILE_SIZE or draw_pos.y > SCREEN_HEIGHT + TILE_SIZE):
                continue
            base_color = tile.get_color()
            if tile.building_density > 0.3:
                base_color = tuple(max(0, c - 20) for c in base_color)
            pygame.draw.rect(
                self.screen, base_color,
                (int(draw_pos.x - TILE_SIZE // 2), int(draw_pos.y - TILE_SIZE // 2), TILE_SIZE, TILE_SIZE)
            )
            if tile.road:
                pygame.draw.rect(
                    self.screen, COLORS['road'],
                    (int(draw_pos.x - TILE_SIZE // 2 + 2), int(draw_pos.y - TILE_SIZE // 2 + 2),
                     TILE_SIZE - 4, TILE_SIZE - 4)
                )
        
        start_x = int((self.camera_offset.x // TILE_SIZE) * TILE_SIZE)
        start_y = int((self.camera_offset.y // TILE_SIZE) * TILE_SIZE)
        for x in range(start_x, start_x + SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_lines'],
                           (x - self.camera_offset.x, 0), (x - self.camera_offset.x, SCREEN_HEIGHT), 1)
        for y in range(start_y, start_y + SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_lines'],
                           (0, y - self.camera_offset.y), (SCREEN_WIDTH, y - self.camera_offset.y), 1)
    
    def draw_entities(self):
        for drop in self.dead_drops:
            drop.draw(self.screen, self.camera_offset)
        for terminal in self.terminals:
            terminal.draw(self.screen, self.camera_offset)
        for patrol in self.patrols:
            patrol.draw(self.screen, self.camera_offset)
        for rival in self.rivals:
            rival.draw(self.screen, self.camera_offset)
        self.player.draw(self.screen, self.camera_offset)
        if self.player.stealth_mode:
            draw_pos = self.player.position - self.camera_offset
            pygame.draw.circle(self.screen, COLORS['accent_cyan'],
                             (int(draw_pos.x), int(draw_pos.y)), int(self.player.radius * 1.5), 2)
    
    def draw_scan_radius(self):
        draw_pos = self.player.position - self.camera_offset
        scan_surface = pygame.Surface((int(self.scan_radius * 2), int(self.scan_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(scan_surface, COLORS['scan_radius'],
                         (int(self.scan_radius), int(self.scan_radius)), int(self.scan_radius), 2)
        if self.player.scanning:
            start_angle = -math.pi / 2
            end_angle = start_angle + self.player.scan_progress * math.pi * 2
            pygame.draw.arc(scan_surface, (0, 180, 255, 200),
                         (0, 0, int(self.scan_radius * 2), int(self.scan_radius * 2)),
                         start_angle, end_angle, 4)
        self.screen.blit(scan_surface, (int(draw_pos.x - self.scan_radius), int(draw_pos.y - self.scan_radius)))
    
    def draw_alert_radius(self):
        draw_pos = self.player.position - self.camera_offset
        alert_radius = 50 + self.player.alert_level * 2
        alert_surface = pygame.Surface((int(alert_radius * 2), int(alert_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(alert_surface, COLORS['alert_radius'],
                         (int(alert_radius), int(alert_radius)), int(alert_radius), 2)
        self.screen.blit(alert_surface, (int(draw_pos.x - alert_radius), int(draw_pos.y - alert_radius)))
    
    def draw_minimap(self):
        minimap_x = SCREEN_WIDTH - MINIMAP_SIZE - 20
        minimap_y = SCREEN_HEIGHT - MINIMAP_SIZE - 20
        pygame.draw.rect(self.screen, (20, 20, 30), (minimap_x, minimap_y, MINIMAP_SIZE, MINIMAP_SIZE))
        pygame.draw.rect(self.screen, COLORS['text_primary'], (minimap_x, minimap_y, MINIMAP_SIZE, MINIMAP_SIZE), 1)
        minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        
        district_colors = {
            DistrictType.DOWNTOWN: (80, 80, 100),
            DistrictType.RESIDENTIAL: (60, 60, 80),
            DistrictType.INDUSTRIAL: (40, 40, 60),
            DistrictType.COMMERCIAL: (70, 70, 90),
            DistrictType.SUBURBS: (50, 60, 50),
            DistrictType.EXURBS: (30, 40, 30),
            DistrictType.PARK: (40, 60, 40),
            DistrictType.WATER: (20, 30, 50),
        }
        
        for district in self.districts:
            scale = MINIMAP_SIZE / max(MAP_WIDTH, MAP_HEIGHT)
            center_x = int((district.center.x / MAP_WIDTH) * MINIMAP_SIZE)
            center_y = int((district.center.y / MAP_HEIGHT) * MINIMAP_SIZE)
            radius = int(district.radius * scale)
            pygame.draw.circle(minimap_surface, district_colors.get(district.district_type, (50, 50, 70)),
                             (center_x, center_y), max(1, radius))
        
        player_x = int((self.player.position.x / MAP_WIDTH) * MINIMAP_SIZE)
        player_y = int((self.player.position.y / MAP_HEIGHT) * MINIMAP_SIZE)
        pygame.draw.circle(minimap_surface, COLORS['player'], (player_x, player_y), 3)
        
        for drop in self.dead_drops:
            if drop.cache.discovered or drop.cache.updated:
                drop_x = int((drop.position.x / MAP_WIDTH) * MINIMAP_SIZE)
                drop_y = int((drop.position.y / MAP_HEIGHT) * MINIMAP_SIZE)
                pygame.draw.circle(minimap_surface, drop.cache.get_color(), (drop_x, drop_y), 2)
        
        for terminal in self.terminals:
            term_x = int((terminal.position.x / MAP_WIDTH) * MINIMAP_SIZE)
            term_y = int((terminal.position.y / MAP_HEIGHT) * MINIMAP_SIZE)
            pygame.draw.circle(minimap_surface, COLORS['terminal'], (term_x, term_y), 2)
        
        for patrol in self.patrols:
            patrol_x = int((patrol.position.x / MAP_WIDTH) * MINIMAP_SIZE)
            patrol_y = int((patrol.position.y / MAP_HEIGHT) * MINIMAP_SIZE)
            pygame.draw.circle(minimap_surface, COLORS['patrol'], (patrol_x, patrol_y), 2)
        
        for rival in self.rivals:
            rival_x = int((rival.position.x / MAP_WIDTH) * MINIMAP_SIZE)
            rival_y = int((rival.position.y / MAP_HEIGHT) * MINIMAP_SIZE)
            pygame.draw.circle(minimap_surface, COLORS['accent_orange'], (rival_x, rival_y), 2)
        
        viewport_x = int((self.camera_offset.x / MAP_WIDTH) * MINIMAP_SIZE)
        viewport_y = int((self.camera_offset.y / MAP_HEIGHT) * MINIMAP_SIZE)
        viewport_w = int((SCREEN_WIDTH / MAP_WIDTH) * MINIMAP_SIZE)
        viewport_h = int((SCREEN_HEIGHT / MAP_HEIGHT) * MINIMAP_SIZE)
        pygame.draw.rect(minimap_surface, (255, 255, 255), (viewport_x, viewport_y, viewport_w, viewport_h), 1)
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
    
    def draw_status_bar(self):
        bar_height = 40
        pygame.draw.rect(self.screen, (20, 20, 30), (10, 10, SCREEN_WIDTH - 20, bar_height))
        pygame.draw.rect(self.screen, COLORS['text_primary'], (10, 10, SCREEN_WIDTH - 20, bar_height), 1)
        
        x_offset = 20
        time_text = f"Time: {int(self.play_time // 60):02d}:{int(self.play_time % 60):02d}"
        self.draw_text(time_text, (x_offset, 15), COLORS['text_primary'])
        x_offset += 120
        
        score_text = f"Score: {self.score}"
        self.draw_text(score_text, (x_offset, 15), COLORS['accent_cyan'])
        x_offset += 120
        
        if self.player.scan_cooldown > 0:
            scan_text = f"Scan: {self.player.scan_cooldown:.1f}s"
            self.draw_text(scan_text, (x_offset, 15), COLORS['text_secondary'])
        else:
            self.draw_text("Scan: READY", (x_offset, 15), COLORS['accent_green'])
        x_offset += 120
        
        alert_text = f"Alert: {int(self.player.alert_level)}%"
        alert_color = (COLORS['text_danger'] if self.player.alert_level > 50 else
                      COLORS['text_warning'] if self.player.alert_level > 25 else
                      COLORS['text_primary'])
        self.draw_text(alert_text, (x_offset, 15), alert_color)
        x_offset += 120
        
        stealth_text = "STEALTH" if self.player.stealth_mode else "NORMAL"
        stealth_color = COLORS['accent_cyan'] if self.player.stealth_mode else COLORS['text_secondary']
        self.draw_text(stealth_text, (x_offset, 15), stealth_color)
        x_offset += 120
        
        if self.player.extracted_cache:
            cache_text = f"Carrying: DD#{self.player.extracted_cache.id}"
            self.draw_text(cache_text, (x_offset, 15), COLORS['accent_green'])
            if self.state == GameState.UPLOADING:
                upload_text = f"Upload: {int(self.player.upload_progress * 100)}%"
                self.draw_text(upload_text, (x_offset, 30), COLORS['accent_cyan'])
        
        discovered_drops = [d for d in self.dead_drops if d.cache.discovered]
        if discovered_drops:
            freshest = max(discovered_drops, key=lambda d: d.cache.freshness)
            fresh_text = f"Freshest: DD#{freshest.cache.id} {freshest.cache.freshness:.0f}%"
            self.draw_text(fresh_text, (SCREEN_WIDTH - 200, 15), freshest.cache.get_color())
        
        stats_text = f"Found: {self.stats['drops_discovered']} | Extracted: {self.stats['drops_extracted']} | Updated: {self.stats['drops_updated']} | Decayed: {self.stats['drops_decayed']}"
        self.draw_text(stats_text, (10, SCREEN_HEIGHT - 25), COLORS['text_secondary'])
    
    def draw_alert_messages(self):
        y_offset = 60
        for message, duration in self.alert_messages:
            alpha = min(255, int(255 * duration / 3.0))
            text_surface = self.font.render(message, True, COLORS['text_warning'])
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 25
    
    def draw_text(self, text: str, position: Tuple[int, int], color: Tuple[int, int, int]):
        shadow_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(shadow_surface, (position[0] + 1, position[1] + 1))
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)
    
    def draw_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        title = self.font_title.render("DEAD DROP SOCIETY", True, COLORS['accent_cyan'])
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        subtitle = self.font.render("A Near-Future Courier Game", True, COLORS['text_secondary'])
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 3 + 50))
        
        instructions = [
            "", "You are a DDS courier in a near-future city.",
            "Locate physical dead drops holding encrypted data caches.",
            "", "Controls:", "WASD/Arrow Keys - Move",
            "Shift - Stealth Mode (slower, less detectable)", "Space - Scan for dead drops",
            "E - Extract cache from dead drop", "Q - Upload cache at terminal",
            "Tab - Toggle minimap", "M - Toggle HUD", "",
            "Find the freshest cache, extract it, and upload it",
            "at a terminal to update all remaining dead drops.",
            "Race against time and rivals before data decays!", "", "Press ENTER to start"
        ]
        y_offset = SCREEN_HEIGHT // 2 + 50
        for line in instructions:
            text = self.font.render(line, True, COLORS['text_primary'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 25
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        self.screen.blit(overlay, (0, 0))
        title = self.font_title.render("GAME OVER", True, COLORS['accent_red'])
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        
        stats = [
            f"Final Score: {self.score}",
            f"Time Survived: {int(self.play_time // 60):02d}:{int(self.play_time % 60):02d}",
            f"Dead Drops Discovered: {self.stats['drops_discovered']}/{len(self.dead_drops)}",
            f"Caches Extracted: {self.stats['drops_extracted']}",
            f"Dead Drops Updated: {self.stats['drops_updated']}",
            f"Caches Decayed: {self.stats['drops_decayed']}",
            f"Rival Intercepts: {self.stats['rival_intercepts']}",
        ]
        y_offset = SCREEN_HEIGHT // 2
        for line in stats:
            text = self.font.render(line, True, COLORS['text_primary'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 30
        restart = self.font_large.render("Press ENTER to restart", True, COLORS['accent_cyan'])
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        self.screen.blit(overlay, (0, 0))
        title = self.font_title.render("VICTORY", True, COLORS['accent_green'])
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        message = self.font_large.render("All dead drops updated successfully!", True, COLORS['text_primary'])
        self.screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        stats = [
            f"Final Score: {self.score}",
            f"Time: {int(self.play_time // 60):02d}:{int(self.play_time % 60):02d}",
            f"All {len(self.dead_drops)} dead drops updated!",
        ]
        y_offset = SCREEN_HEIGHT // 2 + 20
        for line in stats:
            text = self.font.render(line, True, COLORS['text_primary'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 30
        continue_text = self.font_large.render("Press ENTER to play again", True, COLORS['accent_cyan'])
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def reset_game(self):
        self.player = Player(Vector2(CITY_CENTER_X, CITY_CENTER_Y))
        self.camera_offset = Vector2(0, 0)
        self.camera_target = Vector2(0, 0)
        self.dead_drops = []
        self.generate_dead_drops()
        self.terminals = []
        self.generate_terminals()
        self.patrols = []
        self.generate_patrols()
        self.rivals = []
        self.rival_spawn_timer = 0.0
        self.play_time = 0.0
        self.score = 0
        self.scan_active = False
        self.scan_results = []
        self.alert_messages = []
        self.stats = {
            'drops_discovered': 0, 'drops_extracted': 0, 'drops_updated': 0,
            'drops_decayed': 0, 'rival_intercepts': 0, 'patrol_alerts': 0,
        }
    
    def draw(self):
        self.screen.fill(COLORS['background'])
        self.draw_map()
        self.draw_entities()
        if self.player.scanning or self.player.scan_cooldown > SCAN_COOLDOWN - 0.5:
            self.draw_scan_radius()
        if self.player.alert_level > 30:
            self.draw_alert_radius()
        
        if self.show_hud:
            if self.show_minimap:
                self.draw_minimap()
            self.draw_status_bar()
            self.draw_alert_messages()
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.flip()
    
    def run(self):
        last_time = time.time()
        while self.running:
            current_time = time.time()
            dt = min(current_time - last_time, 0.1)
            last_time = current_time
            
            keys = self.handle_events()
            if keys is not None:
                self.update(dt, keys)
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DeadDropSociety()
    game.run()
