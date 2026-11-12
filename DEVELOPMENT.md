# Dead Drop Society - Development Notes

## Project Structure

```
dead_drop_society/
├── run.py                 # Entry point - run this to start the game
├── README.md              # Player documentation
├── requirements.txt       # Dependencies
├── sounds.py              # Sound generation system
└── game/
    ├── __init__.py
    ├── main.py             # Main game loop and rendering
    └── entities.py         # All game entities and data classes
```

## Game Architecture

### Core Systems

1. **Entity System** (`game/entities.py`)
   - `Vector2`: 2D vector math for positions and movement
   - `Entity`: Base class for all drawable objects
   - `DataCache`: Encrypted data with freshness/decay mechanics
   - `DeadDrop`: Physical locations holding caches
   - `Player`: Controllable courier with scanning/extraction abilities
   - `Patrol`: AI guards that detect suspicious activity
   - `Rival`: Competing couriers trying to beat you
   - `Terminal`: Secure upload points
   - `MapTile`/`District`: World generation components

2. **World Generation**
   - Procedurally generated city with multiple districts
   - Downtown, Residential, Industrial, Commercial, Suburbs, Exurbs
   - Parks and water features
   - Road network for patrol paths

3. **Game State Management**
   - Menu, Playing, Scanning, Extracting, Uploading, Game Over, Victory
   - Camera following with smooth movement
   - Minimap for navigation

4. **Sound System** (`sounds.py`)
   - Procedural sound generation using numpy
   - Scan sounds, extraction sounds, upload sounds
   - Alert sounds, decay sounds, rival spawn sounds
   - Graceful fallback if audio not available

### Gameplay Loop

1. **Scan Phase**: Player uses scanner (Space) to detect nearby dead drops
2. **Discovery**: Drops are revealed on map and minimap
3. **Prioritization**: Player identifies freshest cache
4. **Extraction**: Player moves to drop and extracts cache (E)
5. **Upload**: Player finds terminal and uploads cache (Q)
6. **Update**: All remaining dead drops are updated
7. **Victory**: All drops updated before decay

### AI Systems

**Patrols:**
- Follow predefined paths along roads
- Detect player based on distance and alert level
- Investigate extracted caches
- Chase player when alerted

**Rivals:**
- Search for freshest undiscovered caches
- Extract and upload caches
- Compete against player
- Flee when player is near

### Visual Design

**Color Palette:**
- Background: Dark blue-gray (#0F0F14)
- City areas: Various grays with district variations
- Player: Cyan (#00C8FF)
- Fresh drops: Green (#00FF96)
- Stale drops: Yellow (#FFC800)
- Decayed drops: Red (#C83232)
- Patrols: Red (#FF5050)
- Rivals: Orange (#FF7800)
- Terminals: Blue (#00B4FF)

**UI Elements:**
- Minimap in bottom-right corner
- Status bar with time, score, scan cooldown, alert level
- Alert messages with fade-out
- Color-coded status indicators

## Technical Details

### Performance
- Target: 60 FPS
- Map size: 200x120 tiles (32x32 pixels)
- Viewport: 1280x720
- Camera follows player with smoothing

### Controls

| Key | Action | Notes |
|-----|--------|-------|
| W/↑ | Move Up | Standard movement |
| A/← | Move Left | Standard movement |
| S/↓ | Move Down | Standard movement |
| D/→ | Move Right | Standard movement |
| Shift | Stealth/Sprint | Hold for stealth (slower, less detectable) |
| Space | Scan | Detect nearby dead drops |
| E | Extract | Extract cache from discovered drop |
| Q | Upload | Upload cache at terminal |
| Tab | Toggle Minimap | Show/hide minimap |
| M | Toggle HUD | Show/hide HUD |
| ESC | Menu/Quit | Return to menu or quit |
| Enter | Start/Restart | Begin game or restart |

### Game Parameters (Tunable)

```python
# Movement
PLAYER_SPEED = 200
PLAYER_SPRINT_MULTIPLIER = 1.8

# Scanning
SCAN_RADIUS = 200
SCAN_DURATION = 0.5
SCAN_COOLDOWN = 3.0

# Actions
EXTRACTION_TIME = 1.5
UPLOAD_TIME = 2.0

# Decay
DATA_DECAY_RATE = 0.1  # % per second

# AI
RIVAL_SPAWN_RATE = 15.0
PATROL_DETECTION_RADIUS = 150
PATROL_MOVE_SPEED = 120
RIVAL_MOVE_SPEED = 150

# World
NUM_DEAD_DROPS = 20
NUM_TERMINALS = 5
NUM_PATROLS = 8
CITY_RADIUS = 40
EXURB_RADIUS = 80
```

## Running the Game

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python run.py
```

## Known Issues & Limitations

1. **Audio**: Sound system requires SDL2 mixer and libgthread. Falls back gracefully if unavailable.
2. **Fonts**: System fonts may not be available on all platforms. Falls back to default.
3. **Performance**: Large maps with many entities may impact performance on low-end systems.
4. **Balance**: Game difficulty may need tuning based on player feedback.

## Future Enhancements

- [ ] Save/load game state
- [ ] Multiple difficulty levels
- [ ] Persistent high scores
- [ ] More district types and visual variety
- [ ] Additional power-ups and abilities
- [ ] Day/night cycle with visibility changes
- [ ] Weather effects
- [ ] More sound effects and music
- [ ] Particle effects for actions
- [ ] Improved AI pathfinding

## Development Tips

1. **Testing**: Run with `python run.py` to test changes
2. **Debug Mode**: Add debug overlays for development
3. **Profiling**: Use `python -m cProfile run.py` for performance analysis
4. **Logging**: Add logging for AI decision making

## License

This game is provided as-is for entertainment and educational purposes. Feel free to modify, extend, and distribute.

---

*Inspired by the Dead Drop Society book and web series*
*Built with Pygame and Python 3.12+*
