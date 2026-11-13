# GAME DESIGN DOCUMENT
## DEAD DROP // DDS COURIER

**Version:** 1.0 (Playable Prototype)
**Genre:** Top-down 2D stealth-action / open-world courier
**Platform:** Web (HTML5 Canvas), desktop-first
**Session length:** 8–15 minutes per run
**Tone:** Gritty, paranoid, near-future cyberpunk

---

## 1. EXECUTIVE SUMMARY

**DEAD DROP // DDS COURIER** is a top-down, high-contrast 2D stealth-action game set in a near-future city and its surrounding exurbs. The player is a "Dead Drop System" (DDS) courier — a disposable data mule who must locate physical dead drops holding encrypted caches, extract the freshest one, upload it at a secure terminal, then race to update every remaining dead drop before the data decays or rival operatives intercept it.

The game's tension comes from a **single, brutal resource: time**. Every cache is decaying in real time. The player must choose which drops to save, when to sprint and risk detection, and when to crouch and lose seconds. Rival patrols adapt to the player's actions, hunting the last known position, and the map itself reacts — terminals light up, drops rot visibly, and the minimap fills in as the player survives.

**Core fantasy:** You are the last reliable node in a dying network. Move fast, stay quiet, trust nothing.

---

## 2. CONCEPT & VISION

### 2.1 Elevator Pitch
*"A courier must run encrypted dead drops across a paranoid city before the data rots — and before the people hunting her find the drops first."*

### 2.2 Design Pillars

| Pillar | What it means in play |
|---|---|
| **Tense prioritization** | Every cache decays. You cannot save them all. Choose which to update first, and accept the losses. |
| **Stealth vs. speed** | Crouching is safe but slow. Sprinting is fast but loud and visible. Every second has a cost. |
| **Dynamic patrols** | Rivals react to your presence. Alerts propagate, last-known positions are hunted, and reinforcements spawn as heat rises. |
| **A living map** | The world reflects your actions: drops decay, terminals glow, the minimap reveals itself, and rivals reroute in real time. |
| **Gritty paranoia** | Clean high-contrast visuals, harsh neon accents, minimal hand-holding. The UI feels like a dying terminal. |

### 2.3 Unique Selling Points
- **Decay as a mechanic, not a timer.** Each cache has an independent, visible freshness bar, so the player is constantly triaging.
- **A single scanning verb that reshapes the map.** Scanning reveals drops *and* marks enemies — it is both reconnaissance and a beacon.
- **Three-phase escalation.** LOCATE → UPLOAD → UPDATE transforms the entire map state mid-run, forcing a strategic pivot.
- **No hard fail from losing data.** The run ends when all drops are resolved (saved *or* lost) or the player dies — losing caches is a soft failure that costs score, not the run.

---

## 3. TARGET AUDIENCE & PLATFORM

### 3.1 Audience
- **Primary:** Fans of top-down stealth (e.g., *Hotline Miami*, *Heat Signature*, *Mark of the Ninja*) who want a lighter, faster, "arcade stealth" experience.
- **Secondary:** Fans of courier/delivery sims (*Death Stranding*, *Cloudpunk*) who enjoy logistics under pressure.
- **Age:** 15+ (mild violence, tense themes, no explicit content).

### 3.2 Platform
- **Primary:** Desktop browser (Chrome/Firefox/Edge), keyboard + mouse.
- **Secondary (post-launch):** Gamepad support; optional mobile with virtual stick and radial action button.
- **Performance target:** 60 FPS at 1080p on integrated graphics; canvas-based, single-threaded.

---

## 4. CORE GAMEPLAY LOOP

```
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                                             │
   ┌─────────┐    scan     ┌──────────┐   hold E   ┌──────────┐
   │ LOCATE  │────────────▶│ EXTRACT  │───────────▶│ UPLOAD   │
   │ (scan)  │             │ (cache)  │            │(terminal)│
   └─────────┘             └──────────┘            └────┬─────┘
        ▲                                               │
        │                                               │
        │           ┌──────────────────┐                │
        └───────────│  UPDATE (race)   │◀───────────────┘
                    │  all remaining   │
                    │     drops        │
                    └────────┬─────────┘
                             │ all drops resolved
                             ▼
                    ┌─────────────────┐
                    │   RUN COMPLETE  │
                    │  (score, cycle) │
                    └─────────────────┘
```

### 4.1 Phase Breakdown

**Phase 1 — LOCATE**
- Player scans (SPACE) to emit a radial pulse that reveals nearby drops.
- The freshest known drop becomes the **primary** target, highlighted in pink.
- Player navigates to it and holds E to extract.

**Phase 2 — UPLOAD**
- Player now carries a data cache (visual indicator above head).
- Must reach one of the secure terminals (green, rotating).
- On upload, the entire map is revealed and the **decay multiplier doubles**.

**Phase 3 — UPDATE**
- Every remaining drop is now visible and decaying fast.
- Player races between drops, holding E for 2.0s each.
- When all drops are resolved (updated or lost), the run ends.

### 4.2 Win / Loss Conditions
- **Win:** All drops resolved with more saved than lost (or any state where all are resolved). Score is calculated from freshness of saved caches.
- **Death:** Player HP reaches 0 → **COURIER DOWN**, restart.
- **Soft loss:** Individual caches decay to 0% → marked lost, score penalty, run continues.

---

## 5. MECHANICS (DETAILED)

### 5.1 Player

| Property | Value | Notes |
|---|---|---|
| Move speed | 205 u/s | Base |
| Crouch speed | 105 u/s | ~49% of base |
| Sprint speed | 330 u/s | ~161% of base |
| HP | 100 | Regens 5/s when no rival within 340u |
| Contact damage | 34/s | From any rival touching the player |
| Collision radius | 11u | Circle vs. AABB |

**Movement states:**
- **Normal:** Standard speed, standard detection.
- **Crouch (hold C):** Halves speed, reduces rival vision range to 42%, adds a dashed detection ring.
- **Sprint (hold SHIFT):** Increases speed, increases rival vision range to 118%, cannot crouch simultaneously.

**Interaction:** Hold **E** near an interactable. Progress bar appears at bottom center. Releasing E drains progress at 1.6× rate. Taking contact damage resets progress.

### 5.2 Scanning

| Property | Value |
|---|---|
| Cooldown | 2.6s |
| Radius | 1450u |
| Heat cost | +9 |
| Reveals | Drops in range (become `known`), rivals in range (get `marked` for 4s) |
| Visual | Expanding cyan ring; fades as radius reaches 1450 |

**Fallback:** If no drops are in range after a scan, the freshest drop anywhere is revealed (prevents soft-lock).

### 5.3 Dead Drops

| Property | Value |
|---|---|
| Count per cycle | `min(10, 6 + cycleNum)` |
| Initial freshness | rand(72, 100) |
| Base decay rate | rand(0.24, 0.55) × (1 + cycleNum × 0.13) per second |
| Update-phase decay multiplier | 2.3 + cycleNum × 0.18 |
| Extraction time | 3.2s |
| Update time | 2.0s |
| Interaction radius | 72u |
| Visual | Rotating diamond, freshness bar, pulse ring |

**Decay math example (cycle 1):**
- Base decay ~0.4%/s. Over a 90-second locate+upload window, a drop loses ~36% freshness.
- After upload, decay jumps to ~2.5%/s. A 40% freshness drop now has ~16 seconds to live.
- This forces the player to plan the UPDATE route *before* uploading.

### 5.4 Terminals

| Property | Value |
|---|---|
| Count | 3 |
| Upload time | 4.0s |
| Interaction radius | 85u |
| Visual | Rotating green bracket, glow when active |

**On upload:**
- All drops become `known`.
- Phase changes to UPDATE.
- Decay multiplier applied.
- Heat +14.
- Message: "UPLINK COMPLETE // UPDATE ALL REMAINING DROPS".

### 5.5 Rival Patrols

| Property | Patrol | Search | Alert |
|---|---|---|---|
| Speed | 92 u/s | 130 u/s | 208 u/s |
| Vision range | 360u | 360u | 470u |
| FOV | 1.85 rad (~106°) | 1.85 rad | 1.85 rad |
| Awareness gain (seeing) | +1.9/s | +1.9/s | +3.1/s |
| Awareness decay (not seeing) | -0.75/s | -0.75/s | -0.75/s |
| Transition to next state | — | 5.5s no-sight → Search | 6.0s no-sight → Patrol |

**Stealth modifiers to vision range:**
- Player crouching: ×0.42
- Player sprinting: ×1.18
- Player behind solid cover: ×0.30

**Detection states:**
- **Patrol:** Wander along road graph via BFS pathfinding.
- **Search:** Move to last known position, then wander.
- **Alert:** Direct pursuit if close (within 200u) with LOS; otherwise path to last known position.

**Detection event:** On entering Alert, a message fires ("DETECTED // UNIT xx-xx"), a red square synth plays, and screen shakes briefly.

### 5.6 Heat System

| Source | Delta |
|---|---|
| Scan | +9 |
| Extract cache | +26 |
| Upload | +14 |
| Per alert rival (per second) | +7 |
| Passive decay | -4.5/s |

**Effects of heat:**
- Increases the rival spawn cap: `6 + cycleNum × 2 + floor(heat / 16)`.
- Above 70, HUD bar turns red (visual cue).
- No direct gameplay penalty beyond more rivals — heat is a *pressure* mechanic.

### 5.7 Spawning

| Property | Value |
|---|---|
| Spawn interval | max(1.4, 4.5 - cycleNum × 0.25) seconds |
| Spawn cap | min(16, 6 + cycleNum × 2 + floor(heat / 16)) |
| Spawn location | Random road graph node, far from player (min 1100u if possible) |
| Initial rivals | min(14, 5 + cycleNum × 2) |

### 5.8 Scoring

- **Per cache saved (extracted or updated):** +`round(freshness)` points.
- **Per cache lost:** +0 points, increments `lost` counter.
- **End-of-run total:** Sum of all saved cache points.
- **Cycle display:** Shows `CYCLE N` and `SCORE` in HUD.

---

## 6. WORLD DESIGN

### 6.1 Map Layout
- **Grid:** 16 columns × 12 rows of cells.
- **Cell size:** 280 × 280 world units.
- **Road width:** 52u (cell border).
- **Total world size:** 4480 × 3360 world units.
- **Road graph:** 17 × 13 nodes at cell corners, used for rival pathfinding.

### 6.2 Districts

| District | X-range | Ground | Accent | Building density |
|---|---|---|---|---|
| **DOWNTOWN** | 0–28% | `#080b12` | Cyan `#2de2ff` | Dense, tall blocks (split 42% of time) |
| **MIDTOWN** | 28–56% | `#090b12` | Purple `#8a6bff` | Medium, quad-split lots |
| **SUBURBS** | 56–82% | `#070d0b` | Green `#39d98a` | Sparse houses with gaps |
| **EXURBS** | 82–100% | `#0b0b08` | Amber `#c9a227` | Very sparse, 0–2 small structures per cell |

Districts are **visual and structural only** in this prototype — no per-district mechanics yet. They exist to give the map geographic identity and to hint at different risk profiles (downtown = more cover, exurbs = more open).

### 6.3 Buildings
Buildings are simple AABBs generated per-cell with a district-specific generator. They block movement, LOS, and create natural stealth corridors.

**Collision:** Circle-vs-AABB with corner resolution; player and rivals both collide.

### 6.4 Points of Interest
- **Dead drops:** Placed on roads, min 380u apart.
- **Terminals:** Placed at 3 fixed node positions, rotated per cycle.
- **Rival spawns:** Any road node.

### 6.5 Living Map Elements
- **Minimap (180×135):** Shows district bands, roads, drops (color-coded by state), terminals, rivals (only when marked or alerted), player, and camera view rectangle.
- **World-space labels:** Drops show `DD-xx  NN%` above them; terminals show "SECURE TERMINAL" when active.
- **Visual state changes:** Drops transition from glowing diamond → checkmark/X; terminals from dim → bright; rivals change cone color by state.

---

## 7. PROGRESSION & DIFFICULTY

### 7.1 Cycle System
The game uses a **cycle** (not level) structure. Each completed run increments `cycleNum`, which scales:

| Variable | Scaling |
|---|---|
| Drop count | `min(10, 6 + cycle)` |
| Drop decay rate | ×(1 + cycle × 0.13) |
| Update-phase multiplier | 2.3 + cycle × 0.18 |
| Initial rivals | 5 + cycle × 2 (cap 14) |
| Rival spawn interval | 4.5 - cycle × 0.25 (floor 1.4) |
| Rival spawn cap | 6 + cycle × 2 + heat/16 (cap 16) |

**Cycle 1** is a tutorial-equivalent: 7 drops, slow decay, 7 rivals.
**Cycle 5+** is a knife's edge: 10 drops, rapid decay, up to 16 rivals, spawns every 1.4s.

### 7.2 Failure Curve
- Death resets the cycle counter to 0 (full restart).
- Losing caches does **not** reset the cycle — it only costs score.
- This rewards completion over perfection: a messy win is still a win.

### 7.3 Score
Total data score per run is displayed on the end screen alongside caches secured and caches lost.

---

## 8. ART DIRECTION

### 8.1 Visual Style
**Clean, high-contrast top-down 2D.** Think a cross between *Hotline Miami*'s neon-and-black palette and a surveillance terminal UI.

- **Palette:** Near-black backgrounds (`#04050a`), desaturated building fills, and **one saturated accent color per interactive element**:
  - Player: cyan `#3df0ff`
  - Primary drop: pink `#ff2d95`
  - Secondary drop: amber `#ffd23f`
  - Terminal: green `#2bff88`
  - Rival: red `#ff3b30` (alert) / amber (search) / dull red (patrol)
- **Line work:** 1.5–2px outlines, corner ticks on buildings, no gradients on structures.
- **Glow:** Radial gradients only on interactive entities (drops, terminals, player, alerts) — never on background.
- **Screen effects:** Vignette (dark edges), scanlines (3px spacing, 3.5% alpha), damage flash, screen shake.

### 8.2 Animation
- **Player:** Rotating arrow shape, orientation matches movement direction.
- **Drops:** Pulsing diamond (scale + brightness), rotating at extraction.
- **Terminals:** Rotating 4-segment bracket, faster when active.
- **Rivals:** Arrow triangles, awareness arc fills as they notice the player.
- **Pulses:** Expanding cyan ring, fading alpha.
- **Particles:** 3×3 squares, fading over 0.3–0.9s.

### 8.3 Readability Rules
1. **Every interactive element has a unique color.** No two interactable types share a hue.
2. **State is always visual.** Freshness bars, cone colors, terminal glow, and rival awareness arcs are the primary feedback.
3. **The minimap never shows hidden information.** Unexplored drops are invisible; unmarked patrols are invisible.
4. **The player is always the brightest thing on screen.** The radial glow and cyan outline are non-negotiable.

---

## 9. AUDIO DIRECTION

### 9.1 Approach
Minimal, synthesized, diegetic. No music track — only **event-driven tones** generated with the Web Audio API.

### 9.2 Sound Map

| Event | Sound |
|---|---|
| Scan | Rising sine 880→220Hz (0.28s) + triangle 1320→660Hz (0.14s) |
| Extraction | Square 520Hz (0.15s) → 780Hz (0.25s) |
| Upload | Sine 440→880Hz (0.2s) → 880Hz (0.4s) |
| Cache update | Square 700–1060Hz (0.12s), pitch scaled by drop ID |
| Cache lost | Sawtooth 140→60Hz (0.5s) |
| Detected | Square 300→900Hz (0.18s) |
| Death | Sawtooth 90→40Hz (1.2s) |
| Run complete | 660Hz → 990Hz → 1320Hz square arpeggio |

### 9.3 Audio Mix Rules
- All sounds are short (<1.5s) to avoid overlap fatigue.
- Volumes are low (0.03–0.08 gain) to keep the game playable without audio.
- No ambient loop in prototype; future: a low drone that intensifies with heat.

---

## 10. UI / UX

### 10.1 HUD Layout

```
┌──────────────────────────────────────────────────────────────┐
│ [PHASE NAME]                        [INTEGRITY ████████░░]   │
│ [OBJECTIVE TEXT]                    [HEAT      ███░░░░░░░]   │
│ [CONTROLS HINT]                     [CYCLE N  SCORE NNNN]    │
│                                                              │
│                    [CENTRAL MESSAGES]                        │
│                                                              │
│                                                              │
│                                                              │
│ [SCAN READY]                                     [MINIMAP]   │
│                    [INTERACTION PROMPT]                      │
└──────────────────────────────────────────────────────────────┘
```

### 10.2 Interaction Prompt
- Appears when within range of an interactable.
- Shows the verb (`HOLD [E] TO EXTRACT CACHE`).
- Color-coded by action type (pink / green / amber).
- Replaced by a progress bar while E is held.

### 10.3 Message Feed
- Centered, stacked, fading.
- Max ~4 visible at once.
- Color-coded by severity: cyan (info), amber (hint), pink (extract), green (success), red (failure).

### 10.4 Minimap
- 180×135px, bottom-right.
- District color bands, road grid, drops, terminals, rivals, player, camera rectangle.
- Drops only shown if `known` or if in UPDATE phase.
- Rivals only shown if alerted or marked by scan.

### 10.5 End Screens
- **RUN COMPLETE** (green) with caches secured / lost / score, "PRESS [R] FOR NEXT CYCLE".
- **COURIER DOWN** (red) with same stats, "PRESS [R] TO RESTART" (resets cycle to 0).

### 10.6 Accessibility Considerations (post-prototype)
- Colorblind-safe palette toggle (drop pink/amber → blue/white).
- Screen shake intensity slider.
- Scanline toggle.
- Full keyboard remapping.
- Reduced-motion mode (disables shake and pulse rings).

---

## 11. TECHNICAL ARCHITECTURE

### 11.1 Stack
- **Language:** Vanilla JavaScript (ES2020+), no framework.
- **Rendering:** HTML5 Canvas 2D, DPR-aware.
- **Audio:** Web Audio API (oscillator + gain nodes).
- **State:** Single-file closure, module-pattern with `"use strict"`.
- **No build step, no dependencies.** Runs from a single `.html` file.

### 11.2 Core Modules

| Module | Responsibility |
|---|---|
| `resize()` | DPR-aware canvas sizing |
| `genWorld()` | Procedural district & building generation |
| `solidAt()`, `losClear()` | Collision & line-of-sight queries |
| `bfsPath()` | Road-graph pathfinding for rivals |
| `newMission()` | Per-cycle reset and entity spawning |
| `update(dt)` | Master simulation tick |
| `updateInteraction(dt)` | Hold-to-interact state machine |
| `updateRival(r, dt)` | Per-rival FSM (patrol/search/alert) + movement |
| `render()` | Master draw call, camera transform, HUD |
| `draw*()` | Per-entity render functions |

### 11.3 Game Loop
```
requestAnimationFrame(frame)
  ├─ dt = clamp(now - last, 0, 0.05)   // cap to 20 FPS minimum step
  ├─ if PLAY: update(dt)
  ├─ render()
  └─ schedule next frame
```

**Fixed-timestep consideration:** The prototype uses variable timestep with a 50ms cap, which is adequate for the movement speeds and collision tolerances. A future version should use a fixed accumulator (60Hz) for deterministic replay.

### 11.4 Performance Notes
- Buildings are culled per-frame by camera bounds before drawing.
- Entities are culled by a ±200px margin around the camera.
- No per-frame allocations in hot paths (`draw*` functions use primitive math).
- `bfsPath` is called per-rival every 0.45–0.75s, not per-frame.
- Target: 60 FPS at 1080p with 16 rivals on integrated graphics.

### 11.5 Known Limitations & Future Work
- Rival pathfinding is BFS on an unweighted grid (adequate but not optimal).
- No spatial hash for collision queries (fine at current entity counts).
- No save system (runs are ephemeral by design).
- No mobile input yet.

---

## 12. CONTENT & SCOPE

### 12.1 In Prototype (v1.0)
- 1 world, procedurally generated per session (districts fixed, buildings random).
- 3-phase mission loop.
- 1 enemy type (rival patrol).
- 3 terminals.
- 6–10 dead drops per run.
- Heat system, scoring, cycle progression.
- Full HUD, minimap, end screens.
- Title screen, in-game messages, synthesized audio.

### 12.2 Out of Scope (v1.0)
- Multiple enemy types (drones, stationary cameras, snipers).
- Weapons or combat.
- NPC civilians.
- Narrative / dialogue.
- Multiple maps.
- Save/load.
- Multiplayer.
- Localization.

### 12.3 Post-Launch Roadmap (Proposed)

| Priority | Feature | Rationale |
|---|---|---|
| **P0** | Second enemy type (static security camera) | Adds map-reading depth; cameras don't chase but alert patrols |
| **P0** | Gamepad support | Standard for desktop action games |
| **P1** | District modifiers (e.g., downtown rivals move faster, exurbs have longer sightlines) | Makes district identity mechanically meaningful |
| **P1** | Consumable items (EMP burst, decoy, temporary cloak) | Adds moment-to-moment tactical choices |
| **P2** | Daily seed / leaderboard | Retention and community |
| **P2** | Narrative intel drops (short text logs) | Adds tone and worldbuilding at low cost |
| **P3** | Mobile touch controls | Accessibility / reach |
| **P3** | Level editor | Community content |

---

## 13. RISKS & MITIGATIONS

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **Decay pacing feels unfair** | High (core loop breaks) | Medium | Expose decay rate as a tunable constant; add a "decay preview" UI element showing seconds-to-live |
| **Rival pathfinding gets stuck on buildings** | Medium (AI looks dumb) | Medium | Current fallback: if path < 2 nodes, wander by angle. Future: add A* with corner smoothing |
| **Scan feels like a chore** | Medium (repetitive input) | Low | Already mitigated: scan reveals *and* marks enemies; cooldown creates rhythm |
| **Heat is invisible** | Low (unfair pressure) | Medium | HUD bar + color shift at 70 + spawn rate increases naturally signal heat |
| **Colorblind players can't distinguish drops** | High (accessibility) | High | Add colorblind palette toggle (post-prototype) |
| **End-state ambiguity** ("did I win?") | Medium | Low | Clear "RUN COMPLETE" screen with score breakdown and "PRESS R" prompt |

---

## 14. SUCCESS METRICS (IF SHIPPED COMMERCIALLY)

- **Session length:** 8–15 minutes median.
- **Completion rate:** ≥60% of first runs reach "RUN COMPLETE".
- **Replay rate:** ≥40% of players start a second cycle within the same session.
- **Cycle depth:** Median max cycle ≥3.
- **Frustration threshold:** <20% of players die in the first 60 seconds of cycle 1.

---

## 15. APPENDIX: TUNING CONSTANTS

All constants below are pulled directly from the prototype and should be the starting point for any balance pass.

```js
// Player
MOVE_SPEED        = 205
CROUCH_SPEED      = 105
SPRINT_SPEED      = 330
PLAYER_RADIUS     = 11
PLAYER_HP         = 100
CONTACT_DAMAGE    = 34    // per second
HP_REGEN          = 5     // per second, when no rival within 340

// Scan
SCAN_CD           = 2.6
SCAN_RADIUS       = 1450
SCAN_HEAT         = 9

// Drops
DROP_COUNT        = min(10, 6 + cycle)
DROP_FRESH_MIN    = 72
DROP_FRESH_MAX    = 100
DROP_DECAY_MIN    = 0.24 * (1 + cycle * 0.13)
DROP_DECAY_MAX    = 0.55 * (1 + cycle * 0.13)
UPDATE_DECAY_MUL  = 2.3 + cycle * 0.18

// Interaction
EXTRACT_TIME      = 3.2
UPLOAD_TIME       = 4.0
UPDATE_TIME       = 2.0
DROP_RANGE        = 72
TERMINAL_RANGE    = 85
RELEASE_DRAIN     = 1.6   // multiplier on progress drain

// Rivals
RIVAL_PATROL_SPD  = 92
RIVAL_SEARCH_SPD  = 130
RIVAL_ALERT_SPD   = 208
RIVAL_VIEW_PATROL = 360
RIVAL_VIEW_ALERT  = 470
RIVAL_FOV         = 1.85
AWARE_GAIN        = 1.9
AWARE_GAIN_ALERT  = 3.1
AWARE_DECAY       = 0.75
ALERT_TO_SEARCH   = 5.5
SEARCH_TO_PATROL  = 6.0
CROUCH_VIS_MUL    = 0.42
SPRINT_VIS_MUL    = 1.18
COVER_VIS_MUL     = 0.30

// Spawning
SPAWN_INTERVAL    = max(1.4, 4.5 - cycle * 0.25)
SPAWN_CAP         = min(16, 6 + cycle * 2 + floor(heat / 16))
START_RIVALS      = min(14, 5 + cycle * 2)

// Heat
HEAT_SCAN         = 9
HEAT_EXTRACT      = 26
HEAT_UPLOAD       = 14
HEAT_ALERT_PER_SEC= 7
HEAT_DECAY        = 4.5
```

---

*End of document.*