# Dead Drop Society

A top-down 2D open-world game set in a near-future city and its exurbs. You play as a DDS courier who must locate physical dead drops holding encrypted data caches, extract the freshest one, upload it at a secure terminal, then race across urban districts and quiet suburbs to update every remaining dead drop before the data decays or rivals intercept it.

## Game Features

### Core Gameplay
- **Open World**: Explore a procedurally generated city with downtown, residential, industrial, commercial, suburban, and exurban districts
- **Dead Drop System**: Locate, scan, extract, and update encrypted data caches
- **Data Decay**: Caches lose freshness over time - prioritize the freshest ones
- **Secure Terminals**: Upload extracted caches to update all remaining dead drops
- **Tense Prioritization**: Balance stealth vs speed while managing time pressure

### Mechanics
- **Scanning**: Use your scanner to detect nearby dead drops (Space)
- **Extraction**: Extract caches from discovered dead drops (E)
- **Uploading**: Upload extracted caches at terminals (Q)
- **Stealth Mode**: Hold Shift to move slower but reduce detection chance
- **Sprinting**: Hold Shift (when not in stealth) to move faster

### AI Systems
- **Dynamic Patrols**: Patrol units follow paths and investigate suspicious activity
- **Rival Couriers**: Competing agents that also seek to extract and upload caches
- **Alert System**: Your actions increase alert levels, attracting patrol attention

### Visual Style
- Clean, high-contrast top-down 2D graphics
- Gritty, paranoid atmosphere
- Color-coded status indicators
- Minimap for navigation

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move |
| Shift | Stealth Mode (toggle) |
| Space | Scan for dead drops |
| E | Extract cache from dead drop |
| Q | Upload cache at terminal |
| Tab | Toggle minimap |
| M | Toggle HUD |
| Escape | Return to menu / Quit |
| Enter | Start game / Restart |

## Installation

```bash
# Clone or download the repository
cd dead_drop_society

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Gameplay Tips

1. **Scan Frequently**: Use your scanner to discover dead drops in the area
2. **Prioritize Freshness**: Always go for the freshest cache first
3. **Manage Alert Level**: Use stealth mode when near patrols
4. **Watch Rivals**: They're competing for the same caches
5. **Plan Your Route**: Use the minimap to navigate efficiently
6. **Don't Wait Too Long**: Data decays over time - act fast!

## Color Coding

- **Cyan**: Player
- **Green**: Fresh dead drops / Updated drops
- **Yellow**: Stale dead drops
- **Red**: Decayed dead drops / Patrols on alert
- **Orange**: Rival couriers
- **Blue**: Secure terminals

## Development

The game is built with Pygame and uses procedural generation for the city map. The code is organized into:

- `main.py`: Main game file with all systems
- Core classes for entities, AI, and gameplay mechanics
- High-contrast visual theme with gritty aesthetic

## Future Enhancements

- [ ] Sound effects and music
- [ ] Multiple difficulty levels
- [ ] Persistent high scores
- [ ] More district types and features
- [ ] Additional power-ups and abilities
- [ ] Day/night cycle
- [ ] Weather effects

## License

This game is provided as-is for entertainment purposes. Feel free to modify and distribute.

---

*Inspired by the Dead Drop Society book and web series*
