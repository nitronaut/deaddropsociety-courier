// ==================== CONSTANTS ====================

const SCREEN_WIDTH = 1280;
const SCREEN_HEIGHT = 720;
const TILE_SIZE = 32;
const MINIMAP_SIZE = 200;

const MAP_WIDTH = 200 * TILE_SIZE;
const MAP_HEIGHT = 120 * TILE_SIZE;
const CITY_CENTER_X = MAP_WIDTH / 2;
const CITY_CENTER_Y = MAP_HEIGHT / 2;
const CITY_RADIUS = 40 * TILE_SIZE;
const EXURB_RADIUS = 80 * TILE_SIZE;

const PLAYER_SPEED = 200;
const PLAYER_SPRINT_MULTIPLIER = 1.8;
const SCAN_RADIUS = 200;
const SCAN_DURATION = 500;
const SCAN_COOLDOWN = 3000;
const EXTRACTION_TIME = 1500;
const UPLOAD_TIME = 2000;
const DATA_DECAY_RATE = 0.1;
const RIVAL_SPAWN_RATE = 15000;
const PATROL_DETECTION_RADIUS = 150;
const PATROL_MOVE_SPEED = 120;
const RIVAL_MOVE_SPEED = 150;

const NUM_DEAD_DROPS = 20;
const NUM_TERMINALS = 5;
const NUM_PATROLS = 8;

const COLORS = {
    background: '#0f0f14',
    city_dark: '#191923',
    city_medium: '#282837',
    city_light: '#3c3c4c',
    accent_cyan: '#00c8ff',
    accent_orange: '#ff7800',
    accent_red: '#ff5050',
    accent_green: '#00ff96',
    text_primary: '#f0f0fa',
    text_secondary: '#c0c0d0',
    text_warning: '#ffc800',
    text_danger: '#ff6666',
    player: '#00c8ff',
    patrol: '#ff5050',
    terminal: '#00b4ff',
    dead_drop_fresh: '#00ff96',
    dead_drop_stale: '#ffc800',
    dead_drop_decayed: '#c83232',
    scan_radius: 'rgba(0, 150, 255, 0.3)',
    alert_radius: 'rgba(255, 50, 50, 0.3)',
    grid_lines: '#1e1e28',
    road: '#282837',
    suburb: '#232d23',
    water: '#141e30'
};

const GameState = {
    MENU: 'menu',
    PLAYING: 'playing',
    SCANNING: 'scanning',
    UPLOADING: 'uploading',
    GAME_OVER: 'game_over',
    VICTORY: 'victory'
};

const DistrictType = {
    DOWNTOWN: 'downtown',
    RESIDENTIAL: 'residential',
    INDUSTRIAL: 'industrial',
    COMMERCIAL: 'commercial',
    SUBURBS: 'suburbs',
    EXURBS: 'exurbs',
    PARK: 'park',
    WATER: 'water'
};

const DeadDropStatus = {
    FRESH: 'fresh',
    STALE: 'stale',
    DECAYED: 'decayed',
    UPDATED: 'updated'
};

const DistrictColors = {
    [DistrictType.DOWNTOWN]: '#505064',
    [DistrictType.RESIDENTIAL]: '#3c3c4c',
    [DistrictType.INDUSTRIAL]: '#282838',
    [DistrictType.COMMERCIAL]: '#46465c',
    [DistrictType.SUBURBS]: '#323c32',
    [DistrictType.EXURBS]: '#1e281e',
    [DistrictType.PARK]: '#283c28',
    [DistrictType.WATER]: '#141e30'
};

// ==================== VECTOR2 CLASS ====================

class Vector2 {
    constructor(x = 0, y = 0) {
        this.x = x;
        this.y = y;
    }
    
    add(other) {
        return new Vector2(this.x + other.x, this.y + other.y);
    }
    
    sub(other) {
        return new Vector2(this.x - other.x, this.y - other.y);
    }
    
    mul(scalar) {
        return new Vector2(this.x * scalar, this.y * scalar);
    }
    
    div(scalar) {
        return new Vector2(this.x / scalar, this.y / scalar);
    }
    
    length() {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    }
    
    normalized() {
        const len = this.length();
        if (len === 0) return new Vector2(0, 0);
        return this.div(len);
    }
    
    distanceTo(other) {
        return this.sub(other).length();
    }
    
    toTuple() {
        return [this.x, this.y];
    }
}

// ==================== DATA CACHE CLASS ====================

class DataCache {
    constructor(id, position, freshness = 100, size = 1.0) {
        this.id = id;
        this.position = position;
        this.freshness = freshness;
        this.size = size;
        this.status = DeadDropStatus.FRESH;
        this.discovered = false;
        this.extracted = false;
        this.updated = false;
    }
    
    update(dt) {
        this.freshness -= DATA_DECAY_RATE * dt * (1 + Math.random() * 0.5);
        this.freshness = Math.max(0, this.freshness);
        
        if (this.freshness > 70) {
            this.status = DeadDropStatus.FRESH;
        } else if (this.freshness > 30) {
            this.status = DeadDropStatus.STALE;
        } else {
            this.status = DeadDropStatus.DECAYED;
        }
    }
    
    getColor() {
        if (this.updated) return COLORS.accent_green;
        if (this.status === DeadDropStatus.FRESH) return COLORS.dead_drop_fresh;
        if (this.status === DeadDropStatus.STALE) return COLORS.dead_drop_stale;
        return COLORS.dead_drop_decayed;
    }
    
    getRadius() {
        if (this.updated) return 8;
        return 10 + Math.floor(this.size * 4);
    }
}

// ==================== DEAD DROP CLASS ====================

class DeadDrop {
    constructor(cache) {
        this.cache = cache;
        this.hidden = true;
        this.pulse_timer = 0;
        this.pulse_alpha = 0;
    }
    
    update(dt) {
        this.cache.update(dt);
        if (this.cache.discovered) {
            this.pulse_timer += dt * 2;
            this.pulse_alpha = Math.floor(100 + 100 * Math.sin(this.pulse_timer));
        }
    }
}

// ==================== PLAYER CLASS ====================

class Player {
    constructor(position) {
        this.position = position;
        this.radius = 12;
        this.color = COLORS.player;
        this.speed = PLAYER_SPEED;
        this.sprinting = false;
        this.scanning = false;
        this.scan_progress = 0;
        this.scan_cooldown = 0;
        this.extracted_cache = null;
        this.upload_progress = 0;
        this.alert_level = 0;
        this.stealth_mode = false;
        this.velocity = new Vector2(0, 0);
    }
    
    update(dt, keys) {
        let direction = new Vector2(0, 0);
        if (keys.w || keys.ArrowUp) direction.y -= 1;
        if (keys.s || keys.ArrowDown) direction.y += 1;
        if (keys.a || keys.ArrowLeft) direction.x -= 1;
        if (keys.d || keys.ArrowRight) direction.x += 1;
        
        if (direction.length() > 0) {
            direction = direction.normalized();
            this.velocity = direction.mul(this.speed);
            if (this.sprinting) {
                this.velocity = this.velocity.mul(PLAYER_SPRINT_MULTIPLIER);
            }
        } else {
            this.velocity = new Vector2(0, 0);
        }
        
        this.position = this.position.add(this.velocity.mul(dt));
        
        this.stealth_mode = keys.shiftLeft || keys.shiftRight;
        
        if (this.scan_cooldown > 0) {
            this.scan_cooldown -= dt;
        }
        
        if (this.alert_level > 0) {
            this.alert_level -= dt * 5;
            this.alert_level = Math.max(0, this.alert_level);
        }
    }
}

// ==================== PATROL CLASS ====================

class Patrol {
    constructor(position, path) {
        this.position = position;
        this.radius = 10;
        this.color = COLORS.patrol;
        this.path = path;
        this.path_index = 0;
        this.alertness = 0;
        this.chase_target = null;
        this.chase_timer = 0;
        this.move_speed = PATROL_MOVE_SPEED;
    }
    
    update(dt, player, dead_drops) {
        if (this.alertness > 0) {
            this.alertness -= dt * 2;
            this.alertness = Math.max(0, this.alertness);
        }
        
        if (this.chase_target === null) {
            const distance_to_player = this.position.distanceTo(player.position);
            if (distance_to_player < PATROL_DETECTION_RADIUS) {
                const detection_chance = dt * (0.5 + player.alert_level / 200 + (player.stealth_mode ? 0 : 0.3));
                if (Math.random() < detection_chance) {
                    this.chase_target = player.position;
                    this.chase_timer = 10;
                    this.alertness = 100;
                }
            }
            
            for (const drop of dead_drops) {
                if (drop.cache.extracted && !drop.cache.updated) {
                    const distance = this.position.distanceTo(drop.cache.position);
                    if (distance < PATROL_DETECTION_RADIUS * 0.7) {
                        this.chase_target = drop.cache.position;
                        this.chase_timer = 5;
                        this.alertness = 80;
                        break;
                    }
                }
            }
        }
        
        if (this.chase_target !== null) {
            const direction = this.chase_target.sub(this.position).normalized();
            this.position = this.position.add(direction.mul(this.move_speed * dt));
            this.chase_timer -= dt;
            if (this.chase_timer <= 0) {
                this.chase_target = null;
            }
        } else {
            if (this.path.length > 0) {
                const target = this.path[this.path_index];
                const distance = this.position.distanceTo(target);
                if (distance < 10) {
                    this.path_index = (this.path_index + 1) % this.path.length;
                }
                const direction = target.sub(this.position).normalized();
                this.position = this.position.add(direction.mul(this.move_speed * dt));
            }
        }
    }
}

// ==================== RIVAL CLASS ====================

class Rival {
    constructor(position) {
        this.position = position;
        this.radius = 10;
        this.color = COLORS.accent_orange;
        this.move_speed = RIVAL_MOVE_SPEED;
        this.target_drop = null;
        this.target_terminal = null;
        this.action_timer = 0;
        this.state = 'searching';
    }
    
    update(dt, player, dead_drops, terminals) {
        if (this.state === 'searching') {
            const fresh_drops = dead_drops.filter(d => !d.cache.discovered && d.cache.status === DeadDropStatus.FRESH);
            if (fresh_drops.length > 0) {
                this.target_drop = fresh_drops.reduce((a, b) => 
                    this.position.distanceTo(a.cache.position) < this.position.distanceTo(b.cache.position) ? a : b);
                this.state = 'moving_to_drop';
            } else {
                const stale_drops = dead_drops.filter(d => d.cache.status === DeadDropStatus.STALE && !d.cache.extracted);
                if (stale_drops.length > 0) {
                    this.target_drop = stale_drops.reduce((a, b) => 
                        this.position.distanceTo(a.cache.position) < this.position.distanceTo(b.cache.position) ? a : b);
                    this.state = 'moving_to_drop';
                }
            }
        } else if (this.state === 'moving_to_drop') {
            if (this.target_drop) {
                const direction = this.target_drop.cache.position.sub(this.position).normalized();
                this.position = this.position.add(direction.mul(this.move_speed * dt));
                if (this.position.distanceTo(this.target_drop.cache.position) < 20) {
                    this.state = 'extracting';
                    this.action_timer = EXTRACTION_TIME / 1000;
                }
            }
        } else if (this.state === 'extracting') {
            this.action_timer -= dt;
            if (this.action_timer <= 0) {
                if (this.target_drop) {
                    this.target_drop.cache.extracted = true;
                    this.state = 'searching_terminal';
                }
            }
        } else if (this.state === 'searching_terminal') {
            const available_terminals = terminals.filter(t => !t.occupied);
            if (available_terminals.length > 0) {
                this.target_terminal = available_terminals.reduce((a, b) => 
                    this.position.distanceTo(a.position) < this.position.distanceTo(b.position) ? a : b);
                this.state = 'moving_to_terminal';
            }
        } else if (this.state === 'moving_to_terminal') {
            if (this.target_terminal) {
                const direction = this.target_terminal.position.sub(this.position).normalized();
                this.position = this.position.add(direction.mul(this.move_speed * dt));
                if (this.position.distanceTo(this.target_terminal.position) < 20) {
                    this.state = 'uploading';
                    this.action_timer = UPLOAD_TIME / 1000;
                    this.target_terminal.occupied = true;
                }
            }
        } else if (this.state === 'uploading') {
            this.action_timer -= dt;
            if (this.action_timer <= 0) {
                if (this.target_terminal && this.target_drop) {
                    for (const drop of dead_drops) {
                        if (drop !== this.target_drop && !drop.cache.updated) {
                            drop.cache.updated = true;
                            drop.cache.freshness = 100;
                        }
                    }
                    this.target_terminal.occupied = false;
                    this.state = 'fleeing';
                    this.action_timer = 3;
                }
            }
        } else if (this.state === 'fleeing') {
            const direction = this.position.sub(player.position).normalized();
            this.position = this.position.add(direction.mul(this.move_speed * 1.5 * dt));
            this.action_timer -= dt;
            if (this.action_timer <= 0) {
                this.state = 'searching';
            }
        }
    }
}

// ==================== TERMINAL CLASS ====================

class Terminal {
    constructor(position) {
        this.position = position;
        this.radius = 16;
        this.color = COLORS.terminal;
        this.occupied = false;
        this.pulse_timer = 0;
    }
    
    update(dt) {
        this.pulse_timer += dt * 2;
    }
}

// ==================== DISTRICT CLASS ====================

class District {
    constructor(center, radius, type) {
        this.center = center;
        this.radius = radius;
        this.type = type;
    }
    
    contains(position) {
        return this.center.distanceTo(position) < this.radius;
    }
}

// ==================== MAP TILE CLASS ====================

class MapTile {
    constructor(position, district_type, building_density = 0, road = false) {
        this.position = position;
        this.district_type = district_type;
        this.building_density = building_density;
        this.road = road;
    }
    
    getColor() {
        return DistrictColors[this.district_type] || COLORS.city_dark;
    }
}

// ==================== WORLD GENERATOR ====================

class WorldGenerator {
    constructor() {
        this.districts = [];
        this.tiles = [];
        this.road_points = [];
    }
    
    generate() {
        this.districts = [];
        
        // Downtown core
        this.districts.push(new District(
            new Vector2(CITY_CENTER_X, CITY_CENTER_Y),
            CITY_RADIUS / 2,
            DistrictType.DOWNTOWN
        ));
        
        // Inner city districts
        for (let angle = 0; angle < 360; angle += 90) {
            const rad = angle * Math.PI / 180;
            const offset_x = Math.cos(rad) * CITY_RADIUS * 0.6;
            const offset_y = Math.sin(rad) * CITY_RADIUS * 0.6;
            const types = [DistrictType.RESIDENTIAL, DistrictType.COMMERCIAL, DistrictType.INDUSTRIAL];
            const district_type = types[Math.floor(Math.random() * types.length)];
            this.districts.push(new District(
                new Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                CITY_RADIUS * 0.4,
                district_type
            ));
        }
        
        // Suburbs
        for (let angle = 0; angle < 360; angle += 60) {
            const rad = angle * Math.PI / 180;
            const offset_x = Math.cos(rad) * EXURB_RADIUS * 0.7;
            const offset_y = Math.sin(rad) * EXURB_RADIUS * 0.7;
            this.districts.push(new District(
                new Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                EXURB_RADIUS * 0.3,
                DistrictType.SUBURBS
            ));
        }
        
        // Exurbs
        for (let angle = 0; angle < 360; angle += 120) {
            const rad = angle * Math.PI / 180;
            const offset_x = Math.cos(rad) * EXURB_RADIUS * 1.2;
            const offset_y = Math.sin(rad) * EXURB_RADIUS * 1.2;
            this.districts.push(new District(
                new Vector2(CITY_CENTER_X + offset_x, CITY_CENTER_Y + offset_y),
                EXURB_RADIUS * 0.4,
                DistrictType.EXURBS
            ));
        }
        
        // Parks
        this.districts.push(new District(
            new Vector2(CITY_CENTER_X - 30 * TILE_SIZE, CITY_CENTER_Y - 30 * TILE_SIZE),
            20 * TILE_SIZE, DistrictType.PARK
        ));
        this.districts.push(new District(
            new Vector2(CITY_CENTER_X + 40 * TILE_SIZE, CITY_CENTER_Y + 20 * TILE_SIZE),
            15 * TILE_SIZE, DistrictType.PARK
        ));
        
        // Water
        this.districts.push(new District(
            new Vector2(CITY_CENTER_X + 60 * TILE_SIZE, CITY_CENTER_Y - 40 * TILE_SIZE),
            25 * TILE_SIZE, DistrictType.WATER
        ));
        
        // Generate tiles
        this.tiles = [];
        for (let x = 0; x < MAP_WIDTH; x += TILE_SIZE) {
            for (let y = 0; y < MAP_HEIGHT; y += TILE_SIZE) {
                const pos = new Vector2(x + TILE_SIZE / 2, y + TILE_SIZE / 2);
                let district = null;
                for (let i = this.districts.length - 1; i >= 0; i--) {
                    if (this.districts[i].contains(pos)) {
                        district = this.districts[i];
                        break;
                    }
                }
                const district_type = district ? district.type : DistrictType.RESIDENTIAL;
                const road = Math.abs(pos.x - CITY_CENTER_X) < 5 * TILE_SIZE || 
                           Math.abs(pos.y - CITY_CENTER_Y) < 5 * TILE_SIZE ||
                           pos.x % (40 * TILE_SIZE) === 0 || pos.y % (40 * TILE_SIZE) === 0;
                this.tiles.push(new MapTile(pos, district_type, Math.random() * 0.5, road));
            }
        }
        
        // Generate road network
        this.road_points = [];
        for (let x = 0; x < MAP_WIDTH; x += TILE_SIZE * 4) {
            this.road_points.push(new Vector2(x, CITY_CENTER_Y));
        }
        for (let y = 0; y < MAP_HEIGHT; y += TILE_SIZE * 4) {
            this.road_points.push(new Vector2(CITY_CENTER_X, y));
        }
        for (let i = -30; i < 30; i += TILE_SIZE * 2) {
            this.road_points.push(new Vector2(CITY_CENTER_X + i, CITY_CENTER_Y + i));
            this.road_points.push(new Vector2(CITY_CENTER_X + i, CITY_CENTER_Y - i));
        }
        for (let angle = 0; angle < 360; angle += 15) {
            const rad = angle * Math.PI / 180;
            const radius = CITY_RADIUS * 0.8;
            this.road_points.push(new Vector2(
                CITY_CENTER_X + Math.cos(rad) * radius,
                CITY_CENTER_Y + Math.sin(rad) * radius
            ));
        }
        
        return { districts: this.districts, tiles: this.tiles, road_points: this.road_points };
    }
}

// ==================== UTILITY FUNCTIONS ====================

function darkenColor(hex, amount) {
    const r = Math.max(0, parseInt(hex.slice(1, 3), 16) - amount);
    const g = Math.max(0, parseInt(hex.slice(3, 5), 16) - amount);
    const b = Math.max(0, parseInt(hex.slice(5, 7), 16) - amount);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// ==================== MAIN GAME CLASS ====================

class DeadDropSociety {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.minimapCanvas = document.getElementById('minimap-canvas');
        this.minimapCtx = this.minimapCanvas.getContext('2d');
        
        this.canvas.width = SCREEN_WIDTH;
        this.canvas.height = SCREEN_HEIGHT;
        this.minimapCanvas.width = MINIMAP_SIZE;
        this.minimapCanvas.height = MINIMAP_SIZE;
        
        this.state = GameState.MENU;
        this.running = true;
        this.lastTime = 0;
        this.playTime = 0;
        this.score = 0;
        
        this.keys = {};
        this.alertMessages = [];
        this.showMinimap = true;
        this.showHUD = true;
        
        // Initialize world
        const worldGen = new WorldGenerator();
        const world = worldGen.generate();
        this.districts = world.districts;
        this.tiles = world.tiles;
        this.roadPoints = world.road_points;
        
        // Initialize entities
        this.player = new Player(new Vector2(CITY_CENTER_X, CITY_CENTER_Y));
        this.deadDrops = [];
        this.terminals = [];
        this.patrols = [];
        this.rivals = [];
        
        // Camera
        this.cameraOffset = new Vector2(0, 0);
        this.cameraTarget = new Vector2(0, 0);
        
        // Game state
        this.scanRadius = SCAN_RADIUS;
        this.scanActive = false;
        this.scanResults = [];
        this.rivalSpawnTimer = 0;
        
        // Stats
        this.stats = {
            drops_discovered: 0,
            drops_extracted: 0,
            drops_updated: 0,
            drops_decayed: 0,
            rival_intercepts: 0
        };
        
        this.generateDeadDrops();
        this.generateTerminals();
        this.generatePatrols();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start game loop
        this.lastTime = performance.now();
        this.gameLoop();
    }
    
    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            
            if (e.code === 'Escape') {
                if (this.state === GameState.PLAYING) {
                    this.state = GameState.MENU;
                } else if (this.state === GameState.MENU) {
                    this.running = false;
                }
            }
            
            if (e.code === 'Space' && this.state === GameState.PLAYING && this.player.scan_cooldown <= 0) {
                this.startScan();
            }
            
            if (e.code === 'KeyE' && this.state === GameState.PLAYING) {
                this.tryExtract();
            }
            
            if (e.code === 'KeyQ' && this.state === GameState.PLAYING) {
                this.tryUpload();
            }
            
            if (e.code === 'Tab') {
                this.showMinimap = !this.showMinimap;
                document.getElementById('minimap-container').style.display = 
                    this.showMinimap ? 'block' : 'none';
            }
            
            if (e.code === 'KeyM') {
                this.showHUD = !this.showHUD;
            }
            
            if (e.code === 'Enter') {
                if (this.state === GameState.MENU) {
                    this.state = GameState.PLAYING;
                } else if (this.state === GameState.GAME_OVER || this.state === GameState.VICTORY) {
                    this.resetGame();
                    this.state = GameState.PLAYING;
                }
            }
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
        
        this.canvas.addEventListener('click', (e) => {
            if (this.showMinimap) {
                const rect = this.canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                
                const minimapRect = {
                    x: SCREEN_WIDTH - MINIMAP_SIZE - 20,
                    y: SCREEN_HEIGHT - MINIMAP_SIZE - 20,
                    width: MINIMAP_SIZE,
                    height: MINIMAP_SIZE
                };
                
                if (mouseX >= minimapRect.x && mouseX <= minimapRect.x + minimapRect.width &&
                    mouseY >= minimapRect.y && mouseY <= minimapRect.y + minimapRect.height) {
                    const relX = (mouseX - minimapRect.x) / MINIMAP_SIZE;
                    const relY = (mouseY - minimapRect.y) / MINIMAP_SIZE;
                    this.player.position = new Vector2(relX * MAP_WIDTH, relY * MAP_HEIGHT);
                }
            }
        });
    }
    
    generateDeadDrops() {
        this.deadDrops = [];
        for (let i = 0; i < NUM_DEAD_DROPS; i++) {
            let angle, radius, pos, freshness, size;
            
            if (i < NUM_DEAD_DROPS / 3) {
                angle = Math.random() * Math.PI * 2;
                radius = Math.random() * CITY_RADIUS * 0.8;
                pos = new Vector2(CITY_CENTER_X + Math.cos(angle) * radius,
                                 CITY_CENTER_Y + Math.sin(angle) * radius);
                freshness = 100;
                size = Math.random() * 0.5 + 0.5;
            } else if (i < NUM_DEAD_DROPS * 2 / 3) {
                angle = Math.random() * Math.PI * 2;
                radius = CITY_RADIUS + Math.random() * (EXURB_RADIUS - CITY_RADIUS) * 0.7;
                pos = new Vector2(CITY_CENTER_X + Math.cos(angle) * radius,
                                 CITY_CENTER_Y + Math.sin(angle) * radius);
                freshness = Math.random() * 40 + 60;
                size = Math.random() * 0.5 + 0.5;
            } else {
                angle = Math.random() * Math.PI * 2;
                radius = EXURB_RADIUS + Math.random() * 20 * TILE_SIZE;
                pos = new Vector2(CITY_CENTER_X + Math.cos(angle) * radius,
                                 CITY_CENTER_Y + Math.sin(angle) * radius);
                freshness = Math.random() * 30 + 40;
                size = Math.random() * 0.3 + 0.3;
            }
            
            this.deadDrops.push(new DeadDrop(new DataCache(i, pos, freshness, size)));
        }
    }
    
    generateTerminals() {
        this.terminals = [];
        for (let i = 0; i < NUM_TERMINALS; i++) {
            const angle = Math.random() * Math.PI * 2;
            const radius = Math.random() * EXURB_RADIUS * 0.8;
            const pos = new Vector2(
                CITY_CENTER_X + Math.cos(angle) * radius,
                CITY_CENTER_Y + Math.sin(angle) * radius
            );
            this.terminals.push(new Terminal(pos));
        }
    }
    
    generatePatrols() {
        this.patrols = [];
        for (let i = 0; i < NUM_PATROLS; i++) {
            const pathLength = Math.floor(Math.random() * 5) + 4;
            const path = [this.roadPoints[Math.floor(Math.random() * this.roadPoints.length)]];
            for (let j = 1; j < pathLength; j++) {
                const nearby = this.roadPoints.filter(p => 
                    p.distanceTo(path[j - 1]) < 100 * TILE_SIZE);
                if (nearby.length > 0) {
                    path.push(nearby[Math.floor(Math.random() * nearby.length)]);
                }
            }
            this.patrols.push(new Patrol(path[0], path));
        }
    }
    
    spawnRival() {
        const side = ['north', 'south', 'east', 'west'][Math.floor(Math.random() * 4)];
        let pos;
        if (side === 'north') {
            pos = new Vector2(Math.random() * MAP_WIDTH, 0);
        } else if (side === 'south') {
            pos = new Vector2(Math.random() * MAP_WIDTH, MAP_HEIGHT);
        } else if (side === 'east') {
            pos = new Vector2(MAP_WIDTH, Math.random() * MAP_HEIGHT);
        } else {
            pos = new Vector2(0, Math.random() * MAP_HEIGHT);
        }
        this.rivals.push(new Rival(pos));
        this.addAlertMessage(`Rival detected at ${side} border`, 3000);
    }
    
    startScan() {
        if (this.player.scan_cooldown > 0) return;
        
        this.player.scanning = true;
        this.player.scan_progress = 0;
        this.scanActive = true;
        this.scanResults = [];
        
        for (const drop of this.deadDrops) {
            if (!drop.cache.discovered) {
                if (this.player.position.distanceTo(drop.cache.position) < this.scanRadius) {
                    this.scanResults.push(drop);
                }
            }
        }
        
        this.scanResults.sort((a, b) => b.cache.freshness - a.cache.freshness);
    }
    
    completeScan() {
        this.player.scanning = false;
        this.scanActive = false;
        this.player.scan_cooldown = SCAN_COOLDOWN;
        
        for (const drop of this.scanResults) {
            drop.cache.discovered = true;
            drop.hidden = false;
            this.stats.drops_discovered++;
            this.addAlertMessage(`Dead Drop #${drop.cache.id} discovered`, 2000);
        }
        
        if (this.scanResults.length > 0) {
            const freshest = this.scanResults[0];
            this.addAlertMessage(`Freshest cache: DD#${freshest.cache.id} (${Math.floor(freshest.cache.freshness)}%)`, 4000);
        }
    }
    
    tryExtract() {
        if (this.player.extracted_cache !== null) {
            this.addAlertMessage("Already carrying a cache", 1000);
            return;
        }
        
        let nearestDrop = null;
        let nearestDistance = Infinity;
        
        for (const drop of this.deadDrops) {
            if (drop.cache.discovered && !drop.cache.extracted && drop.cache.status !== DeadDropStatus.DECAYED) {
                const distance = this.player.position.distanceTo(drop.cache.position);
                if (distance < nearestDistance && distance < 30) {
                    nearestDistance = distance;
                    nearestDrop = drop;
                }
            }
        }
        
        if (nearestDrop) {
            this.player.extracted_cache = nearestDrop.cache;
            nearestDrop.cache.extracted = true;
            this.player.upload_progress = 0;
            this.stats.drops_extracted++;
            this.addAlertMessage(`Extracted cache from DD#${nearestDrop.cache.id}`, 2000);
            this.player.alert_level += 20;
            
            for (const patrol of this.patrols) {
                const distance = patrol.position.distanceTo(nearestDrop.cache.position);
                if (distance < PATROL_DETECTION_RADIUS * 1.5) {
                    patrol.alertness = Math.min(100, patrol.alertness + 30);
                    if (patrol.chase_target === null) {
                        patrol.chase_target = nearestDrop.cache.position;
                        patrol.chase_timer = 8;
                    }
                }
            }
        } else {
            this.addAlertMessage("No extractable cache nearby", 1000);
        }
    }
    
    tryUpload() {
        if (this.player.extracted_cache === null) {
            this.addAlertMessage("No cache to upload", 1000);
            return;
        }
        
        let nearestTerminal = null;
        let nearestDistance = Infinity;
        
        for (const terminal of this.terminals) {
            if (!terminal.occupied) {
                const distance = this.player.position.distanceTo(terminal.position);
                if (distance < nearestDistance && distance < 30) {
                    nearestDistance = distance;
                    nearestTerminal = terminal;
                }
            }
        }
        
        if (nearestTerminal) {
            this.player.upload_progress = 0;
            nearestTerminal.occupied = true;
            this.state = GameState.UPLOADING;
            this.addAlertMessage("Uploading cache to terminal...", 2000);
        } else {
            this.addAlertMessage("No available terminal nearby", 1000);
        }
    }
    
    completeUpload() {
        if (this.player.extracted_cache === null) return;
        
        for (const terminal of this.terminals) {
            if (terminal.occupied && this.player.position.distanceTo(terminal.position) < 40) {
                terminal.occupied = false;
                break;
            }
        }
        
        for (const drop of this.deadDrops) {
            if (!drop.cache.updated && !drop.cache.extracted) {
                drop.cache.updated = true;
                drop.cache.freshness = 100;
                this.stats.drops_updated++;
            }
        }
        
        this.stats.drops_updated++;
        this.player.extracted_cache = null;
        this.player.upload_progress = 0;
        this.state = GameState.PLAYING;
        
        const scoreGain = 100 * this.deadDrops.filter(d => d.cache.updated).length;
        this.score += scoreGain;
        this.addAlertMessage(`Upload complete! +${scoreGain} points`, 4000);
        
        if (this.deadDrops.every(d => d.cache.updated)) {
            this.state = GameState.VICTORY;
            this.addAlertMessage("All dead drops updated! VICTORY!", 10000);
        }
    }
    
    addAlertMessage(message, duration) {
        this.alertMessages.push({ message, duration, remaining: duration });
        if (this.alertMessages.length > 5) {
            this.alertMessages.shift();
        }
    }
    
    resetGame() {
        this.player = new Player(new Vector2(CITY_CENTER_X, CITY_CENTER_Y));
        this.cameraOffset = new Vector2(0, 0);
        this.cameraTarget = new Vector2(0, 0);
        this.deadDrops = [];
        this.generateDeadDrops();
        this.terminals = [];
        this.generateTerminals();
        this.patrols = [];
        this.generatePatrols();
        this.rivals = [];
        this.rivalSpawnTimer = 0;
        this.playTime = 0;
        this.score = 0;
        this.scanActive = false;
        this.scanResults = [];
        this.alertMessages = [];
        this.stats = {
            drops_discovered: 0,
            drops_extracted: 0,
            drops_updated: 0,
            drops_decayed: 0,
            rival_intercepts: 0
        };
    }

    // ==================== RENDERING METHODS ====================

    drawMap() {
        const startX = Math.floor(this.cameraOffset.x / TILE_SIZE) * TILE_SIZE;
        const startY = Math.floor(this.cameraOffset.y / TILE_SIZE) * TILE_SIZE;
        const endX = startX + SCREEN_WIDTH + TILE_SIZE;
        const endY = startY + SCREEN_HEIGHT + TILE_SIZE;
        
        for (const tile of this.tiles) {
            if (tile.position.x >= startX && tile.position.x <= endX &&
                tile.position.y >= startY && tile.position.y <= endY) {
                const drawPos = tile.position.sub(this.cameraOffset);
                
                let color = tile.getColor();
                if (tile.building_density > 0.3) {
                    color = darkenColor(color, 20);
                }
                
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    Math.floor(drawPos.x - TILE_SIZE / 2),
                    Math.floor(drawPos.y - TILE_SIZE / 2),
                    TILE_SIZE, TILE_SIZE
                );
                
                if (tile.road) {
                    this.ctx.fillStyle = COLORS.road;
                    this.ctx.fillRect(
                        Math.floor(drawPos.x - TILE_SIZE / 2 + 2),
                        Math.floor(drawPos.y - TILE_SIZE / 2 + 2),
                        TILE_SIZE - 4, TILE_SIZE - 4
                    );
                }
            }
        }
        
        // Draw grid lines
        for (let x = startX; x <= endX; x += TILE_SIZE) {
            const screenX = x - this.cameraOffset.x;
            this.ctx.strokeStyle = COLORS.grid_lines;
            this.ctx.beginPath();
            this.ctx.moveTo(screenX, 0);
            this.ctx.lineTo(screenX, SCREEN_HEIGHT);
            this.ctx.stroke();
        }
        
        for (let y = startY; y <= endY; y += TILE_SIZE) {
            const screenY = y - this.cameraOffset.y;
            this.ctx.strokeStyle = COLORS.grid_lines;
            this.ctx.beginPath();
            this.ctx.moveTo(0, screenY);
            this.ctx.lineTo(SCREEN_WIDTH, screenY);
            this.ctx.stroke();
        }
    }
    
    drawEntities() {
        // Draw dead drops
        for (const drop of this.deadDrops) {
            if (drop.hidden && !drop.cache.discovered) continue;
            
            const drawPos = drop.cache.position.sub(this.cameraOffset);
            const radius = drop.cache.getRadius();
            const color = drop.cache.getColor();
            
            // Draw glow for discovered
            if (drop.cache.discovered) {
                const alpha = drop.pulse_alpha / 255;
                const glowRadius = radius * 1.5;
                const gradient = this.ctx.createRadialGradient(
                    drawPos.x, drawPos.y, 0,
                    drawPos.x, drawPos.y, glowRadius
                );
                gradient.addColorStop(0, color + '80');
                gradient.addColorStop(1, color + '00');
                this.ctx.fillStyle = gradient;
                this.ctx.beginPath();
                this.ctx.arc(drawPos.x, drawPos.y, glowRadius, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            // Draw main circle
            this.ctx.fillStyle = color;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw update indicator
            if (drop.cache.updated) {
                this.ctx.fillStyle = COLORS.accent_green;
                this.ctx.beginPath();
                this.ctx.arc(drawPos.x, drawPos.y, radius * 0.6, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        
        // Draw terminals
        for (const terminal of this.terminals) {
            const drawPos = terminal.position.sub(this.cameraOffset);
            const alpha = 0.5 + 0.5 * Math.sin(terminal.pulse_timer);
            
            // Draw glow
            const glowGradient = this.ctx.createRadialGradient(
                drawPos.x, drawPos.y, 0,
                drawPos.x, drawPos.y, terminal.radius * 1.5
            );
            glowGradient.addColorStop(0, COLORS.terminal + Math.floor(alpha * 255).toString(16).padStart(2, '0'));
            glowGradient.addColorStop(1, COLORS.terminal + '00');
            this.ctx.fillStyle = glowGradient;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, terminal.radius * 1.5, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw main terminal
            this.ctx.fillStyle = COLORS.terminal;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, terminal.radius, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw occupied indicator
            if (terminal.occupied) {
                this.ctx.fillStyle = COLORS.accent_green;
                this.ctx.beginPath();
                this.ctx.arc(drawPos.x, drawPos.y, terminal.radius * 0.7, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        
        // Draw patrols
        for (const patrol of this.patrols) {
            const drawPos = patrol.position.sub(this.cameraOffset);
            
            // Draw alert indicator
            if (patrol.alertness > 50) {
                const alertRadius = 8 + patrol.alertness / 25;
                this.ctx.strokeStyle = COLORS.accent_red;
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                this.ctx.arc(drawPos.x, drawPos.y, alertRadius, 0, Math.PI * 2);
                this.ctx.stroke();
            }
            
            // Draw patrol
            this.ctx.fillStyle = COLORS.patrol;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, patrol.radius, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Draw rivals
        for (const rival of this.rivals) {
            const drawPos = rival.position.sub(this.cameraOffset);
            this.ctx.fillStyle = COLORS.accent_orange;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, rival.radius, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Draw player
        const playerDrawPos = this.player.position.sub(this.cameraOffset);
        this.ctx.fillStyle = COLORS.player;
        this.ctx.beginPath();
        this.ctx.arc(playerDrawPos.x, playerDrawPos.y, this.player.radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw stealth indicator
        if (this.player.stealth_mode) {
            this.ctx.strokeStyle = COLORS.accent_cyan;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(playerDrawPos.x, playerDrawPos.y, this.player.radius * 1.5, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }
    
    drawScanRadius() {
        const drawPos = this.player.position.sub(this.cameraOffset);
        const radius = this.scanRadius;
        
        this.ctx.strokeStyle = COLORS.scan_radius;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(drawPos.x, drawPos.y, radius, 0, Math.PI * 2);
        this.ctx.stroke();
        
        if (this.player.scanning) {
            const startAngle = -Math.PI / 2;
            const endAngle = startAngle + this.player.scan_progress * Math.PI * 2;
            this.ctx.strokeStyle = 'rgba(0, 180, 255, 0.8)';
            this.ctx.lineWidth = 4;
            this.ctx.beginPath();
            this.ctx.arc(drawPos.x, drawPos.y, radius, startAngle, endAngle);
            this.ctx.stroke();
        }
    }
    
    drawAlertRadius() {
        const drawPos = this.player.position.sub(this.cameraOffset);
        const radius = 50 + this.player.alert_level * 2;
        
        this.ctx.strokeStyle = COLORS.alert_radius;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(drawPos.x, drawPos.y, radius, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    drawMinimap() {
        this.minimapCtx.fillStyle = 'rgba(20, 20, 30, 0.9)';
        this.minimapCtx.fillRect(0, 0, MINIMAP_SIZE, MINIMAP_SIZE);
        this.minimapCtx.strokeStyle = COLORS.text_primary;
        this.minimapCtx.lineWidth = 1;
        this.minimapCtx.strokeRect(0, 0, MINIMAP_SIZE, MINIMAP_SIZE);
        
        const scale = MINIMAP_SIZE / Math.max(MAP_WIDTH, MAP_HEIGHT);
        
        // Draw districts
        for (const district of this.districts) {
            const centerX = (district.center.x / MAP_WIDTH) * MINIMAP_SIZE;
            const centerY = (district.center.y / MAP_HEIGHT) * MINIMAP_SIZE;
            const radius = district.radius * scale;
            this.minimapCtx.fillStyle = DistrictColors[district.type] || '#323240';
            this.minimapCtx.beginPath();
            this.minimapCtx.arc(centerX, centerY, Math.max(1, radius), 0, Math.PI * 2);
            this.minimapCtx.fill();
        }
        
        // Draw player
        const playerX = (this.player.position.x / MAP_WIDTH) * MINIMAP_SIZE;
        const playerY = (this.player.position.y / MAP_HEIGHT) * MINIMAP_SIZE;
        this.minimapCtx.fillStyle = COLORS.player;
        this.minimapCtx.beginPath();
        this.minimapCtx.arc(playerX, playerY, 3, 0, Math.PI * 2);
        this.minimapCtx.fill();
        
        // Draw dead drops
        for (const drop of this.deadDrops) {
            if (drop.cache.discovered || drop.cache.updated) {
                const dropX = (drop.cache.position.x / MAP_WIDTH) * MINIMAP_SIZE;
                const dropY = (drop.cache.position.y / MAP_HEIGHT) * MINIMAP_SIZE;
                this.minimapCtx.fillStyle = drop.cache.getColor();
                this.minimapCtx.beginPath();
                this.minimapCtx.arc(dropX, dropY, 2, 0, Math.PI * 2);
                this.minimapCtx.fill();
            }
        }
        
        // Draw terminals
        for (const terminal of this.terminals) {
            const termX = (terminal.position.x / MAP_WIDTH) * MINIMAP_SIZE;
            const termY = (terminal.position.y / MAP_HEIGHT) * MINIMAP_SIZE;
            this.minimapCtx.fillStyle = COLORS.terminal;
            this.minimapCtx.beginPath();
            this.minimapCtx.arc(termX, termY, 2, 0, Math.PI * 2);
            this.minimapCtx.fill();
        }
        
        // Draw patrols
        for (const patrol of this.patrols) {
            const patrolX = (patrol.position.x / MAP_WIDTH) * MINIMAP_SIZE;
            const patrolY = (patrol.position.y / MAP_HEIGHT) * MINIMAP_SIZE;
            this.minimapCtx.fillStyle = COLORS.patrol;
            this.minimapCtx.beginPath();
            this.minimapCtx.arc(patrolX, patrolY, 2, 0, Math.PI * 2);
            this.minimapCtx.fill();
        }
        
        // Draw rivals
        for (const rival of this.rivals) {
            const rivalX = (rival.position.x / MAP_WIDTH) * MINIMAP_SIZE;
            const rivalY = (rival.position.y / MAP_HEIGHT) * MINIMAP_SIZE;
            this.minimapCtx.fillStyle = COLORS.accent_orange;
            this.minimapCtx.beginPath();
            this.minimapCtx.arc(rivalX, rivalY, 2, 0, Math.PI * 2);
            this.minimapCtx.fill();
        }
        
        // Draw viewport
        const viewportX = (this.cameraOffset.x / MAP_WIDTH) * MINIMAP_SIZE;
        const viewportY = (this.cameraOffset.y / MAP_HEIGHT) * MINIMAP_SIZE;
        const viewportW = (SCREEN_WIDTH / MAP_WIDTH) * MINIMAP_SIZE;
        const viewportH = (SCREEN_HEIGHT / MAP_HEIGHT) * MINIMAP_SIZE;
        this.minimapCtx.strokeStyle = 'white';
        this.minimapCtx.strokeRect(viewportX, viewportY, viewportW, viewportH);
    }
    
    drawStatusBar() {
        this.ctx.fillStyle = 'rgba(20, 20, 30, 0.9)';
        this.ctx.fillRect(10, 10, SCREEN_WIDTH - 20, 40);
        this.ctx.strokeStyle = COLORS.text_primary;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(10, 10, SCREEN_WIDTH - 20, 40);
        
        let xOffset = 20;
        const yPos = 28;
        
        // Time
        const minutes = Math.floor(this.playTime / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((this.playTime % 60000) / 1000).toString().padStart(2, '0');
        this.drawText(`Time: ${minutes}:${seconds}`, xOffset, 25, COLORS.text_primary);
        xOffset += 120;
        
        // Score
        this.drawText(`Score: ${this.score}`, xOffset, 25, COLORS.accent_cyan);
        xOffset += 120;
        
        // Scan cooldown
        if (this.player.scan_cooldown > 0) {
            this.drawText(`Scan: ${(this.player.scan_cooldown / 1000).toFixed(1)}s`, xOffset, 25, COLORS.text_secondary);
        } else {
            this.drawText('Scan: READY', xOffset, 25, COLORS.accent_green);
        }
        xOffset += 120;
        
        // Alert level
        let alertColor = COLORS.text_primary;
        if (this.player.alert_level > 50) alertColor = COLORS.text_danger;
        else if (this.player.alert_level > 25) alertColor = COLORS.text_warning;
        this.drawText(`Alert: ${Math.floor(this.player.alert_level)}%`, xOffset, 25, alertColor);
        xOffset += 120;
        
        // Stealth mode
        const stealthText = this.player.stealth_mode ? 'STEALTH' : 'NORMAL';
        const stealthColor = this.player.stealth_mode ? COLORS.accent_cyan : COLORS.text_secondary;
        this.drawText(stealthText, xOffset, 25, stealthColor);
        xOffset += 120;
        
        // Carrying cache
        if (this.player.extracted_cache) {
            this.drawText(`Carrying: DD#${this.player.extracted_cache.id}`, xOffset, 25, COLORS.accent_green);
            if (this.state === GameState.UPLOADING) {
                this.drawText(`Upload: ${Math.floor(this.player.upload_progress * 100)}%`, xOffset, 40, COLORS.accent_cyan);
            }
        }
        
        // Freshest drop
        const discoveredDrops = this.deadDrops.filter(d => d.cache.discovered);
        if (discoveredDrops.length > 0) {
            const freshest = discoveredDrops.reduce((a, b) => a.cache.freshness > b.cache.freshness ? a : b);
            this.drawText(`Freshest: DD#${freshest.cache.id} ${Math.floor(freshest.cache.freshness)}%`, 
                           SCREEN_WIDTH - 250, 25, freshest.cache.getColor());
        }
        
        // Stats summary
        this.drawText(
            `Found: ${this.stats.drops_discovered} | Extracted: ${this.stats.drops_extracted} | Updated: ${this.stats.drops_updated} | Decayed: ${this.stats.drops_decayed}`,
            10, SCREEN_HEIGHT - 25, COLORS.text_secondary
        );
    }
    
    drawAlertMessages() {
        for (let i = 0; i < this.alertMessages.length; i++) {
            const msg = this.alertMessages[i];
            const opacity = Math.min(1, msg.remaining / 3000);
            const yOffset = 60 + i * 25;
            
            this.ctx.globalAlpha = opacity;
            this.ctx.fillStyle = COLORS.text_warning;
            this.ctx.font = 'bold 14px Courier New';
            const textWidth = this.ctx.measureText(msg.message).width;
            this.ctx.fillText(msg.message, SCREEN_WIDTH / 2 - textWidth / 2, yOffset);
            this.ctx.globalAlpha = 1;
        }
    }
    
    drawText(text, x, y, color) {
        this.ctx.fillStyle = 'black';
        this.ctx.font = '14px Courier New';
        this.ctx.fillText(text, x + 1, y + 1);
        this.ctx.fillStyle = color;
        this.ctx.fillText(text, x, y);
    }
    
    updateGameOverUI() {
        document.getElementById('final-score').textContent = this.score;
        const minutes = Math.floor(this.playTime / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((this.playTime % 60000) / 1000).toString().padStart(2, '0');
        document.getElementById('final-time').textContent = `${minutes}:${seconds}`;
        document.getElementById('final-discovered').textContent = this.stats.drops_discovered;
        document.getElementById('total-drops').textContent = this.deadDrops.length;
        document.getElementById('final-extracted').textContent = this.stats.drops_extracted;
        document.getElementById('final-updated').textContent = this.stats.drops_updated;
        document.getElementById('final-decayed').textContent = this.stats.drops_decayed;
    }
    
    updateVictoryUI() {
        document.getElementById('victory-score').textContent = this.score;
        const minutes = Math.floor(this.playTime / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((this.playTime % 60000) / 1000).toString().padStart(2, '0');
        document.getElementById('victory-time').textContent = `${minutes}:${seconds}`;
        document.getElementById('victory-drops').textContent = this.deadDrops.length;
    }
    
    update(dt) {
        if (this.state === GameState.MENU || this.state === GameState.GAME_OVER || this.state === GameState.VICTORY) {
            return;
        }
        
        // Update player
        this.player.update(dt, this.keys);
        this.player.sprinting = this.keys.ShiftLeft || this.keys.ShiftRight;
        
        // Update camera
        this.cameraTarget = new Vector2(
            this.player.position.x - SCREEN_WIDTH / 2,
            this.player.position.y - SCREEN_HEIGHT / 2
        );
        this.cameraOffset = this.cameraOffset.add(
            this.cameraTarget.sub(this.cameraOffset).mul(dt * 5)
        );
        this.cameraOffset.x = Math.max(0, Math.min(MAP_WIDTH - SCREEN_WIDTH, this.cameraOffset.x));
        this.cameraOffset.y = Math.max(0, Math.min(MAP_HEIGHT - SCREEN_HEIGHT, this.cameraOffset.y));
        
        // Update scan
        if (this.player.scanning) {
            this.player.scan_progress += dt / (SCAN_DURATION / 1000);
            if (this.player.scan_progress >= 1) {
                this.completeScan();
            }
        }
        
        // Update upload
        if (this.state === GameState.UPLOADING && this.player.extracted_cache !== null) {
            this.player.upload_progress += dt / (UPLOAD_TIME / 1000);
            if (this.player.upload_progress >= 1) {
                this.completeUpload();
            }
        }
        
        // Update dead drops
        for (const drop of this.deadDrops) {
            drop.update(dt);
            if (drop.cache.freshness <= 0 && drop.cache.status !== DeadDropStatus.DECAYED) {
                drop.cache.status = DeadDropStatus.DECAYED;
                this.stats.drops_decayed++;
                this.addAlertMessage(`Dead Drop #${drop.cache.id} has decayed!`, 3000);
            }
        }
        
        // Update patrols
        for (const patrol of this.patrols) {
            patrol.update(dt, this.player, this.deadDrops);
        }
        
        // Update rivals
        for (const rival of this.rivals) {
            rival.update(dt, this.player, this.deadDrops, this.terminals);
        }
        
        // Update terminals
        for (const terminal of this.terminals) {
            terminal.update(dt);
        }
        
        // Spawn rivals
        this.rivalSpawnTimer += dt;
        if (this.rivalSpawnTimer >= RIVAL_SPAWN_RATE && this.rivals.length < 10) {
            this.spawnRival();
            this.rivalSpawnTimer = 0;
        }
        
        // Update alert messages
        for (let i = this.alertMessages.length - 1; i >= 0; i--) {
            this.alertMessages[i].remaining -= dt;
            if (this.alertMessages[i].remaining <= 0) {
                this.alertMessages.splice(i, 1);
            }
        }
        
        this.playTime += dt;
        
        // Check game over conditions
        const decayedCount = this.deadDrops.filter(d => d.cache.status === DeadDropStatus.DECAYED).length;
        if (decayedCount >= this.deadDrops.length / 2) {
            this.state = GameState.GAME_OVER;
            this.addAlertMessage("Too many caches decayed! GAME OVER", 10000);
            this.updateGameOverUI();
        }
        
        for (const patrol of this.patrols) {
            if (patrol.alertness > 80 && patrol.position.distanceTo(this.player.position) < 20) {
                this.state = GameState.GAME_OVER;
                this.addAlertMessage("Caught by patrol! GAME OVER", 10000);
                this.updateGameOverUI();
                break;
            }
        }
        
        for (const rival of this.rivals) {
            if (rival.state === 'uploading' && rival.action_timer < UPLOAD_TIME / 2000) {
                this.stats.rival_intercepts++;
                this.addAlertMessage("Rival is uploading! Hurry!", 3000);
            }
        }
    }
    
    draw() {
        // Clear screen
        this.ctx.fillStyle = COLORS.background;
        this.ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
        
        // Draw map
        this.drawMap();
        
        // Draw entities
        this.drawEntities();
        
        // Draw scan radius
        if (this.player.scanning || this.player.scan_cooldown > SCAN_COOLDOWN - 500) {
            this.drawScanRadius();
        }
        
        // Draw alert radius
        if (this.player.alert_level > 30) {
            this.drawAlertRadius();
        }
        
        // Draw UI
        if (this.showHUD) {
            if (this.showMinimap) {
                this.drawMinimap();
            }
            this.drawStatusBar();
            this.drawAlertMessages();
        }
        
        // Update UI elements
        const minutes = Math.floor(this.playTime / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((this.playTime % 60000) / 1000).toString().padStart(2, '0');
        document.getElementById('time-display').textContent = `Time: ${minutes}:${seconds}`;
        document.getElementById('score-display').textContent = `Score: ${this.score}`;
        
        if (this.player.scan_cooldown > 0) {
            document.getElementById('scan-display').textContent = `Scan: ${(this.player.scan_cooldown / 1000).toFixed(1)}s`;
        } else {
            document.getElementById('scan-display').textContent = 'Scan: READY';
        }
        
        document.getElementById('alert-display').textContent = `Alert: ${Math.floor(this.player.alert_level)}%`;
        document.getElementById('stealth-display').textContent = this.player.stealth_mode ? 'STEALTH' : 'NORMAL';
        
        // Show/hide overlays
        document.getElementById('menu-overlay').style.display = 
            this.state === GameState.MENU ? 'flex' : 'none';
        document.getElementById('game-over-overlay').style.display = 
            this.state === GameState.GAME_OVER ? 'flex' : 'none';
        document.getElementById('victory-overlay').style.display = 
            this.state === GameState.VICTORY ? 'flex' : 'none';
    }
    
    gameLoop(timestamp) {
        if (!this.running) return;
        
        const dt = Math.min(timestamp - this.lastTime, 100);
        this.lastTime = timestamp;
        
        if (this.state === GameState.PLAYING) {
            this.update(dt);
        }
        
        this.draw();
        
        requestAnimationFrame((t) => this.gameLoop(t));
    }
}

// Start the game when loaded
window.addEventListener('load', () => {
    new DeadDropSociety();
});
