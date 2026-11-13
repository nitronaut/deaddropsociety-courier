# GAME DESIGN DOCUMENT
## DEAD DROP // DDS COURIER

**Version:** 2.0 (Loot, Progression & Transit Update)
**Supersedes:** v1.0 (Playable Prototype)
**Genre:** Top-down 2D stealth-action / open-world courier
**Platform:** Web (HTML5 Canvas), desktop-first
**Session length:** 8–20 minutes per run; persistent career across many runs
**Tone:** Gritty, paranoid, near-future cyberpunk

---

## CHANGE LOG (v1.0 → v2.0)

| Feature | Status |
|---|---|
| Dead drops yield loot (4 categories) | **New** |
| Weapons system (3 types × 3 levels, combat) | **New** |
| Transport upgrades (3 types × 3 levels) | **New** |
| Spiderphone consumables (3 types) | **New** |
| Finance / Opium Lots (3 denominations) | **New** |
| Subway system (4 stops, zigzag east–west) | **New** |
| Persistent score & loot across cycles | **New** |
| Permadeath — death wipes everything | **New** |
| Rival HP & player combat | **New** |
| Mouse aim + LMB fire | **New** |
| Expanded HUD (loot bag, weapon bar, subway panel, credit counter) | **New** |
| End-screen loot summary | **New** |
| Everything from v1.0 | Retained |

---

## 1. EXECUTIVE SUMMARY

**DEAD DROP // DDS COURIER** is a top-down, high-contrast 2D stealth-action game set in a near-future city and its surrounding exurbs. The player is a "Dead Drop System" (DDS) courier — a disposable data mule who must locate physical dead drops holding encrypted caches, extract the freshest one, upload it at a secure terminal, then race to update every remaining dead drop before the data decays or rival operatives intercept it.

As of v2.0, the game has grown into a **persistent career**: every dead drop can yield a blueprint — a weapon, a transport upgrade, a spiderphone, or a stack of Opium Lots. These blueprints and credits **carry forward across cycles** and fundamentally expand the player's options. Blueprints unlock new combat tools, movement modifiers, and remote data-manipulation abilities. Opium Lots buy **subway rides** across the map at 10 lots per stop, letting the player skip the risk of traversing hostile streets at the cost of hard-won currency.

**Death wipes the entire career.** Every run is a gamble: do you push for one more cache to afford that sprint upgrade, or do you bank what you have and take the safe update route?

**Core fantasy:** You are the last reliable node in a dying network. Move fast, stay quiet, trust nothing — and remember that everything you own can be taken in a single wrong turn.

---

## 2. CONCEPT & VISION

### 2.1 Elevator Pitch
*"A courier must run encrypted dead drops across a paranoid city before the data rots — and before the people hunting her find the drops first. Every cache could be a weapon, a faster run, or a stack of opium to buy a subway ticket out. Die, and it all vanishes."*

### 2.2 Design Pillars

| Pillar | What it means in play |
|---|---|
| **Tense prioritization** | Every cache decays. You cannot save them all. Choose which to update first, and accept the losses. |
| **Stealth vs. speed** | Crouching is safe but slow. Sprinting is fast but loud and visible. Every second has a cost. |
| **Loot-driven escalation** | Each cache is a lottery ticket. Weapons make you lethal, transport makes you slippery, spiderphones bend the map, Opium buys escape. |
| **Persistent risk** | Everything you build carries forward — and death takes it all. The career is a wager, not a grind. |
| **A living map** | The world reflects your actions: drops decay, terminals glow, the subway pulses, the minimap reveals itself, and rivals reroute in real time. |
| **Gritty paranoia** | Clean high-contrast visuals, harsh neon accents, minimal hand-holding. The UI feels like a dying terminal. |

### 2.3 Unique Selling Points
- **Decay as a mechanic, not a timer.** Each cache has an independent, visible freshness bar, so the player is constantly triaging.
- **A single scanning verb that reshapes the map.** Scanning reveals drops *and* marks enemies — it is both reconnaissance and a beacon.
- **Three-phase escalation.** LOCATE → UPLOAD → UPDATE transforms the entire map state mid-run, forcing a strategic pivot.
- **Four loot categories that all matter.** Weapons for defense, transport for movement, spiderphones for map control, Opium Lots for transit. No filler category.
- **Permadeath career.** Blueprints and credits carry across cycles but are wiped on death — a wager that gives each run real stakes.
- **A subway line that is a strategic tool, not a convenience.** 10 Opium Lots per stop, 4 zigzag stations, "H to ride" — every ride is an economic decision.

---

## 3. TARGET AUDIENCE & PLATFORM

### 3.1 Audience
- **Primary:** Fans of top-down stealth (e.g., *Hotline Miami*, *Heat Signature*, *Mark of the Ninja*) who want a lighter, faster, "arcade stealth" experience with real build progression.
- **Secondary:** Fans of roguelite persistence (e.g., *Hades*, *Risk of Rain*) who enjoy losing everything on death and rebuilding with new unlocks.
- **Secondary:** Fans of courier/delivery sims (*Death Stranding*, *Cloudpunk*) who enjoy logistics under pressure.
- **Age:** 15+ (mild violence, tense themes, no explicit content).

### 3.2 Platform
- **Primary:** Desktop browser (Chrome/Firefox/Edge), keyboard + mouse.
- **Secondary (post-launch):** Gamepad support; optional mobile with virtual stick and radial action button.
- **Performance target:** 60 FPS at 1080p on integrated graphics; canvas-based, single-threaded.

---

## 4. CORE GAMEPLAY LOOP

### 4.1 High-Level Flow

```
        ┌──────────────────────────────────────────────────────┐
        │                                                      │
        ▼                                                      │
   ┌─────────┐    scan     ┌──────────┐   hold E   ┌──────────┐ │
   │ LOCATE  │────────────▶│ EXTRACT  │───────────▶│ UPLOAD   │ │
   │ (scan)  │             │ (cache)  │            │(terminal)│ │
   └─────────┘             │ + LOOT   │            └────┬─────┘ │
        ▲                  └──────────┘                 │       │
        │                                               │       │
        │           ┌──────────────────┐                │       │
        └───────────│  UPDATE (race)   │◀───────────────┘       │
                    │  all remaining   │                        │
                    │  drops + LOOT    │                        │
                    └────────┬─────────┘                        │
                             │ all drops resolved               │
                             ▼                                  │
                    ┌─────────────────┐                         │
                    │   RUN COMPLETE  │                         │
                    │  bank score,    │─────────────────────────┘
                    │  keep loot,     │   (next cycle: harder,
                    │  next cycle     │    loot carried forward)
                    └─────────────────┘
                             │
                             │ player killed
                             ▼
                    ┌─────────────────┐
                    │  COURIER DOWN   │
                    │  WIPE ALL LOOT  │
                    │  AND SCORE      │
                    └─────────────────┘
```

### 4.2 Phase Breakdown

**Phase 1 — LOCATE**
- Player scans (SPACE) to emit a radial pulse that reveals nearby drops.
- The freshest known drop becomes the **primary** target, highlighted in pink.
- Player navigates to it and holds E to extract.
- **On extract:** a loot roll fires (72% chance), yielding a blueprint or Opium Lots.

**Phase 2 — UPLOAD**
- Player now carries a data cache (visual indicator above head).
- Must reach one of the secure terminals (green, rotating).
- On upload, the entire map is revealed and the **decay multiplier doubles**.

**Phase 3 — UPDATE**
- Every remaining drop is now visible and decaying fast.
- Player races between drops, holding E for 2.0s each.
- **Each update also rolls loot.**
- When all drops are resolved (updated or lost), the run ends.

**Post-run:** score and loot banked. Cycle counter increments. Next run is harder but the career persists.

### 4.3 Win / Loss Conditions
- **Win:** All drops resolved with more saved than lost. Score is calculated from freshness of saved caches, then **added to the persistent career total**. Loot and credits are kept.
- **Death:** Player HP reaches 0 → **COURIER DOWN**, restart. **All persistent score, loot, and credits are wiped**, and the cycle counter resets to 1.
- **Soft loss:** Individual caches decay to 0% → marked lost, score penalty, run continues.

---

## 5. MECHANICS (DETAILED)

### 5.1 Player

| Property | Value | Notes |
|---|---|---|
| Base move speed | 205 u/s | Modified by transport upgrades |
| Crouch speed | 105 u/s | ~51% of base; further modified by Ghost Crouch |
| Sprint speed | 330 u/s | ~161% of base; further modified by Vector Sprint |
| HP | 100 | Regens 5/s when no rival within 340u |
| Contact damage | 34/s | From any rival touching the player |
| Collision radius | 11u | Circle vs. AABB |
| Aim | Mouse cursor | Direction of weapon fire and visual facing |

**Movement states:**
- **Normal:** Standard speed, standard detection.
- **Crouch (hold C):** Halves speed, reduces rival vision range to 42%, adds a dashed detection ring.
- **Sprint (hold SHIFT):** Increases speed, increases rival vision range to 118%, cannot crouch simultaneously.

**Combat state:** If a weapon is equipped, the player can fire by holding **LMB**. Cooldown ring renders around the player. Rivals now have HP (140) and can be killed (+50 score each) or stunned (taser/EMP).

**Interaction:** Hold **E** near an interactable. Progress bar appears at bottom center. Releasing E drains progress at 1.6× rate. Taking contact damage resets progress.

**Transport upgrades modify:**
- `moveSpeedBonus()` — multiplier on all speed
- `sprintBonus()` — multiplier on sprint speed & visibility reduction
- `crouchBonus()` — multiplier on crouch speed & visibility reduction

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
| Count per cycle | `min(10, 6 + cycleNum)` (up to 15 with SPAWN spiderphone) |
| Initial freshness | rand(72, 100) |
| Base decay rate | rand(0.24, 0.55) × (1 + cycleNum × 0.13) per second |
| Update-phase decay multiplier | 2.3 + cycleNum × 0.18 |
| Extraction time | 3.2s |
| Update time | 2.0s |
| Interaction radius | 72u |
| Visual | Rotating diamond, freshness bar, pulse ring |
| **Loot on resolve** | 72% chance (see §5.7) |

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
| **HP** | 140 | 140 | 140 |
| **Stun duration** | 0 | 0 | 0 |

**Stealth modifiers to vision range:**
- Player crouching: ×0.42 × crouch transport bonus
- Player sprinting: ×1.18 × sprint transport bonus
- Player behind solid cover: ×0.30

**Detection states:**
- **Patrol:** Wander along road graph via BFS pathfinding.
- **Search:** Move to last known position, then wander.
- **Alert:** Direct pursuit if close (within 200u) with LOS; otherwise path to last known position.

**Combat vulnerability:**
- SMG bullets deal damage (25/40/60 by level).
- Ghost Taser stuns in radius (90/130/175u, 2/3/5s).
- Pulse EMP stuns in radius (200/280/370u, 3/5/8s).
- On kill: rival dies, +50 score, particles, kill sound.

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

### 5.7 Loot System (NEW)

Every dead drop resolution (extract or update) has a **72%** chance to yield loot. The drop rate and category split are designed so that a full run (6–10 drops) typically yields **4–7 items**.

**Loot category roll:**

| Roll range | Category | Weight |
|---|---|---|
| 0.00 – 0.30 | Weapon Blueprint | 30% |
| 0.30 – 0.52 | Transport Blueprint | 22% |
| 0.52 – 0.70 | Communications Blueprint | 18% |
| 0.70 – 1.00 | Finance (Opium Lots) | 30% |

**Maxed-category fallback:** If a category is fully maxed (weapons at L3, transport at L3, or comms at ×5), the roll converts to a **salvage bonus** of +100 score (weapons/transport), +50 score (comms), instead of granting a duplicate.

#### 5.7.1 Weapon Blueprints

| Weapon | Color | Levels | L1 | L2 | L3 | Behavior |
|---|---|---|---|---|---|---|
| VECTOR SMG | Orange `#ff6b3d` | 3 | Dmg 25, CD 0.15s | Dmg 40, CD 0.12s | Dmg 60, CD 0.09s | Fast projectile, mouse-aim |
| GHOST TASER | Amber `#ffd23f` | 3 | Radius 90u, Stun 2.0s, CD 2.5s | Radius 130u, Stun 3.0s, CD 2.0s | Radius 175u, Stun 5.0s, CD 1.5s | Instant AoE stun |
| PULSE EMP | Cyan `#3df0ff` | 3 | Radius 200u, Stun 3.0s, CD 9.0s | Radius 280u, Stun 5.0s, CD 7.0s | Radius 370u, Stun 8.0s, CD 5.0s | Large AoE stun + screen shake |

- **Switch weapons** with 1/2/3 keys or mouse wheel.
- **Auto-equip:** If the player has no active weapon and rolls a weapon blueprint, it auto-equips.
- **Locked weapons** cannot be selected; a message shows which blueprint is needed.
- Firing consumes a per-weapon cooldown. A cooldown arc renders around the player.

#### 5.7.2 Transport Blueprints

| Upgrade | Color | Effect per Level | Max |
|---|---|---|---|
| PACE RUNNER | Cyan `#3df0ff` | +6% base move speed | L3 |
| VECTOR SPRINT | Amber `#ffd23f` | +8% sprint speed, -6% sprint visibility | L3 |
| GHOST CROUCH | Green `#2bff88` | +10% crouch speed, -6% crouch visibility | L3 |

Transport upgrades are **passive** — they apply immediately and permanently until death.

#### 5.7.3 Communications Blueprints (Spiderphones)

| Spiderphone | Color | Key | Effect | Max |
|---|---|---|---|---|
| RESET | Amber `#ffd23f` | Q | Restores the nearest unresolved drop to 100% freshness | ×5 |
| SPAWN | Orange `#ff6b3d` | F | Deploys a fresh 100% drop at a random road point (cap: 15 total) | ×5 |
| REMOTE | Green `#2bff88` | G | Instantly resolves the nearest drop, scores it, and rolls its loot | ×5 |

Each spiderphone is a **consumable** with its own count. Using one decrements the counter. Counters carry across cycles until death.

#### 5.7.4 Finance — Opium Lots (NEW)

| Denomination | Color | Value | Weight |
|---|---|---|---|
| Small (×1) | Purple `#b873ff` | +1 Opium Lot | 50 |
| Medium (×5) | Violet `#8a3dff` | +5 Opium Lots | 35 |
| Large (×15) | Magenta `#d94bff` | +15 Opium Lots | 15 |

Opium Lots are the game's **secondary currency**. They drop from dead drops like blueprints, accumulate in the player's credit pool, and are spent on subway rides (§5.8). Like all persistent loot, they are wiped on death.

### 5.8 Subway System (NEW)

The city has a single **east–west subway line** with four stops arranged in a zigzag pattern.

**Layout:**

| Station | Approx. Cell | Position |
|---|---|---|
| Station 1 | (1, 2) | Far left, north |
| Station 2 | (5, 8) | Left-center, south |
| Station 3 | (10, 3) | Right-center, north |
| Station 4 | (14, 9) | Far right, south |

The track renders as a glowing violet line with a dashed center marking. Stations are drawn as rotating violet squares with a radial glow. The whole line appears on the minimap.

**Riding rules:**

| Property | Value |
|---|---|
| Boarding radius | 90u (player must be near a station) |
| Cost | 10 Opium Lots **per stop travelled** |
| Max cost (Station 1 → Station 4) | 30 Opium Lots |
| Ride duration | 1.6s + (stops × 0.35s) |
| Trigger key | **H** |

**During transit:**
- Player is locked to the track (interpolation through intermediate stations).
- Camera follows.
- Rivals reset alert state to patrol (they can't catch the train).
- Any in-progress interaction (E hold) is cancelled.
- Violet particle trail spawns behind the player.
- Weapon fire is disabled.

**On arrival:**
- Player is placed at the destination station.
- Message: "SUBWAY ARRIVED".
- Arrival chime.

**Why it matters:** The subway lets the player **skip hostile streets** at a cost. Combined with Opium Lots from Finance loot, this creates a meaningful economic loop: *save caches → earn lots → spend lots to save more caches faster*. A 30-lot full-cross trip is expensive enough to feel weighty but cheap enough to be worth it when the alternative is a 90-second sprint through three alerted patrol zones.

### 5.9 Persistent Progression & Permadeath (NEW)

**Carried forward across cycles (on run complete):**
- Total score (`persistent.score`)
- Opium Lots (`persistent.credits`)
- All weapon levels (`persistent.loot.weapons`)
- All transport levels (`persistent.loot.transport`)
- All spiderphone counts (`persistent.loot.comms`)

**Wiped on death:**
- Everything above is set to zero.
- `cycleNum` resets to 0 (displayed as "CYCLE 1").
- End screen shows "TOTAL SCORE LOST" and "OPIUM LOTS LOST" to make the loss tangible.

**Cycle scaling still applies** on top of persistence — the world gets harder each cycle regardless of the loot bag, so a player who survives five cycles will face cycle-6 difficulty with a maxed loadout, which is *the intended endgame*.

### 5.10 Spawning

| Property | Value |
|---|---|
| Spawn interval | max(1.4, 4.5 - cycleNum × 0.25) seconds |
| Spawn cap | min(16, 6 + cycleNum × 2 + floor(heat / 16)) |
| Spawn location | Random road graph node, far from player (min 1100u if possible) |
| Initial rivals | min(14, 5 + cycleNum × 2) |

### 5.11 Scoring

- **Per cache saved (extracted or updated):** +`round(freshness)` points.
- **Per rival killed:** +50 points.
- **Maxed-category salvage:** +100 (weapons/transport) or +50 (comms).
- **Per cache lost:** +0, increments `lost` counter.
- **Mission score (`stat.score`):** sums the above for the current run.
- **Career score (`persistent.score`):** accumulates across cycles on run complete; wiped on death.

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

Districts are **visual and structural only** in this version — no per-district mechanics. They exist to give the map geographic identity and to hint at different risk profiles (downtown = more cover, exurbs = more open).

### 6.3 Buildings
Buildings are simple AABBs generated per-cell with a district-specific generator. They block movement, LOS, and create natural stealth corridors.

**Collision:** Circle-vs-AABB with corner resolution; player and rivals both collide.

### 6.4 Points of Interest
- **Dead drops:** Placed on roads, min 380u apart.
- **Terminals:** Placed at 3 fixed node positions, rotated per cycle.
- **Rival spawns:** Any road node.
- **Subway stations:** Four fixed stations, zigzag east–west (see §5.8).

### 6.5 Living Map Elements
- **Minimap (180×135):** Shows district bands, road grid, **subway line & stations**, drops (color-coded by state), terminals, rivals (only when marked or alerted), player, and camera view rectangle.
- **World-space labels:** Drops show `DD-xx  NN%` above them; terminals show "SECURE TERMINAL" when active; subway stations show "STATION N" and either "◆ YOU ARE HERE ◆" or the cost to reach from the current station.
- **Visual state changes:** Drops transition from glowing diamond → checkmark/X; terminals from dim → bright; rivals change cone color by state; subway pulses continuously and glows brighter while riding.

---

## 7. PROGRESSION & DIFFICULTY

### 7.1 Dual Progression Systems

The game uses **two stacked progression tracks**:

1. **In-run mission progression** — LOCATE → UPLOAD → UPDATE.
2. **Persistent career progression** — loot bag and credits carried across cycles.

**Cycle scaling** applies to the world (drops, rivals, decay) independent of loot. **Loot scaling** applies to the player (weapons, transport, spiderphones, credits) independent of cycle. The two curves are meant to cross around cycle 4–5: by then the player has a partially-filled loot bag and the world has become genuinely hostile.

### 7.2 Cycle System

| Variable | Scaling |
|---|---|
| Drop count | `min(10, 6 + cycle)` |
| Drop decay rate | ×(1 + cycle × 0.13) |
| Update-phase multiplier | 2.3 + cycle × 0.18 |
| Initial rivals | 5 + cycle × 2 (cap 14) |
| Rival spawn interval | 4.5 - cycle × 0.25 (floor 1.4) |
| Rival spawn cap | 6 + cycle × 2 + heat/16 (cap 16) |

**Cycle 1** is a tutorial-equivalent: 7 drops, slow decay, 7 rivals, no weapons (unless carried from a previous career that somehow survived — which it can't, on a fresh start).
**Cycle 5+** is a knife's edge: 10 drops, rapid decay, up to 16 rivals, spawns every 1.4s — and the player likely has several weapons and transport upgrades, so the fight is *symmetric*.

### 7.3 Failure Curve

- **Death resets the entire career:** score, credits, loot bag, cycle counter.
- **Losing caches does not reset the cycle** — it only costs score.
- This rewards completion over perfection: a messy win still banks everything.
- The end screens make the loss explicit: "TOTAL SCORE LOST" and "OPIUM LOTS LOST" on death, "TOTAL SCORE" and "◈ OPIUM LOTS" on win.

### 7.4 Score

- **Mission score** is displayed during the run (top-right).
- **Career score** is displayed persistently next to mission score and on the end screens.
- **Score is wiped on death.** It is not a lifetime scoreboard — it is a stake.

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
  - **Vector SMG:** orange `#ff6b3d`
  - **Ghost Taser:** amber `#ffd23f`
  - **Pulse EMP:** cyan `#3df0ff`
  - **Pace Runner:** cyan `#3df0ff`
  - **Vector Sprint:** amber `#ffd23f`
  - **Ghost Crouch:** green `#2bff88`
  - **Spiderphone Reset:** amber `#ffd23f`
  - **Spiderphone Spawn:** orange `#ff6b3d`
  - **Spiderphone Remote:** green `#2bff88`
  - **Finance Small:** purple `#b873ff`
  - **Finance Medium:** violet `#8a3dff`
  - **Finance Large:** magenta `#d94bff`
  - **Subway:** violet `#b873ff`
- **Line work:** 1.5–2px outlines, corner ticks on buildings, no gradients on structures.
- **Glow:** Radial gradients only on interactive entities (drops, terminals, player, alerts, subway) — never on background.
- **Screen effects:** Vignette (dark edges), scanlines (3px spacing, 3.5% alpha), damage flash, screen shake.

### 8.2 Animation
- **Player:** Rotating arrow shape, orientation matches mouse aim. Cooldown ring when weapon is on cooldown. Crouch detection ring when crouching.
- **Drops:** Pulsing diamond (scale + brightness), rotating at extraction.
- **Terminals:** Rotating 4-segment bracket, faster when active.
- **Rivals:** Arrow triangles, awareness arc fills as they notice the player. HP bar appears when damaged. Stun indicator (✦) when stunned. Death burst particles.
- **Subway:** Stations rotate continuously, pulsing glow. Track has a dashed center line. Riding player leaves a violet particle trail.
- **Bullets:** Short linear streaks with white core.
- **Pulses:** Expanding cyan ring, fading alpha.
- **Particles:** 3×3 squares, fading over 0.3–0.9s. Loot bursts are 24 particles in the category color.

### 8.3 Readability Rules
1. **Every interactive element has a unique color.** No two interactable types share a hue.
2. **State is always visual.** Freshness bars, cone colors, terminal glow, rival awareness arcs, and cooldown rings are the primary feedback.
3. **The minimap never shows hidden information.** Unexplored drops are invisible; unmarked patrols are invisible.
4. **The player is always the brightest thing on screen.** The radial glow and cyan outline are non-negotiable.
5. **Every loot category has a recognizable signature color.** Players should be able to guess the category from the particle burst color alone.

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
| Rival killed | Sawtooth 180→60Hz (0.25s) |
| SMG fire | Square 640Hz (0.04s) |
| Taser | Sawtooth 220→900Hz (0.18s) |
| EMP | Sine 110→50Hz (0.4s) |
| Weapon equip | Square 520Hz (0.06s) |
| **Weapon blueprint** | Square 660Hz → 990Hz arpeggio |
| **Transport blueprint** | Square 660Hz → 990Hz arpeggio |
| **Comms blueprint** | Sine 880Hz (0.1s) |
| **Finance (Opium)** | Sine 740Hz → 1100Hz arpeggio |
| **Maxed salvage** | Sine 990Hz (0.15s) |
| **Subway board** | Sine 330→660Hz (0.2s) → 660→990Hz (0.3s) |
| **Subway arrive** | Sine 880→440Hz (0.2s) |
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
┌────────────────────────────────────────────────────────────────────┐
│ [PHASE]                                  [INTEGRITY ████████░░]    │
│ [OBJECTIVE]                              [HEAT      ███░░░░░░░]    │
│ [CONTROLS LINE 1]                        [◈ 42 OPIUM LOTS]        │
│ [CONTROLS LINE 2]                        [CYCLE 3  TOTAL 1240]     │
│                                          [MISSION +320]            │
│ ┌─ LOOT BAG ──────────┐                                           │
│ │ WEAPONS             │                                           │
│ │ ▶ VECTOR SMG  ▮▮▯   │                                           │
│ │   GHOST TASER ▮▯▯   │                                           │
│ │   PULSE EMP   ▮▮▮   │                                           │
│ │ TRANSPORT           │                                           │
│ │   PACE RUNNER ▮▯▯   │                                           │
│ │   VECTOR SPRINT ▮▮▯ │                                           │
│ │   GHOST CROUCH ▮▯▯  │                                           │
│ │ COMMS               │                                           │
│ │ [Q] RESET     ×3    │                                           │
│ │ [F] SPAWN     ×1    │                                           │
│ │ [G] REMOTE    ×2    │                                           │
│ │ FINANCE             │                                           │
│ │ ◈ OPIUM LOTS   42   │                                           │
│ └─────────────────────┘                                           │
│                                                                   │
│                                                                   │
│ ┌─ SUBWAY ────────────┐                          [MINIMAP]        │
│ │ ◈ SUBWAY LINE       │                                           │
│ │ ▶ STATION 1   HERE  │                                           │
│ │   STATION 2   10 ◈  │                                           │
│ │   STATION 3   20 ◈  │                                           │
│ │   STATION 4   30 ◈  │                                           │
│ │ [H] RIDE TO NEXT    │                                           │
│ └─────────────────────┘                                           │
│ ┌─ WEAPONS ───────────┐                                           │
│ │ [1] VECTOR SMG   L2 │                                           │
│ │ [2] GHOST TASER  L1 │                                           │
│ │ [3] PULSE EMP  LOCK │                                           │
│ └─────────────────────┘                                           │
│ [SCAN READY]                    [INTERACTION PROMPT]              │
└────────────────────────────────────────────────────────────────────┘
```

### 10.2 New HUD Panels (v2.0)

**Loot Bag (top-left, below phase panel):** 260×230px panel listing every weapon, transport upgrade, spiderphone count, and the current Opium Lot balance. Active weapon is marked with ▶. Level blocks (▮▯) show progress toward max.

**Weapon Bar (bottom-left, above subway panel):** 220×80px panel showing each weapon, its level, and the currently equipped weapon. Locked weapons display "LOCKED". Number keys [1][2][3] correspond to positions.

**Subway Panel (bottom-left, above scan):** 220×90px panel listing all four stations, the player's current station, and the cost to reach each station from the player's position. When riding, displays "▶ IN TRANSIT…".

**Credits display (top-right vitals):** Bold violet "◈ 42 OPIUM LOTS" below the heat bar. Also shown in the Loot Bag FINANCE section.

### 10.3 Interaction Prompt
- Appears when within range of an interactable.
- Shows the verb (`HOLD [E] TO EXTRACT CACHE`).
- Color-coded by action type (pink / green / amber).
- Replaced by a progress bar while E is held.

### 10.4 Message Feed
- Centered, stacked, fading.
- Max ~4 visible at once.
- Color-coded by severity: cyan (info), amber (hint), pink (extract), green (success), red (failure), violet (finance/subway), per-weapon colors for loot pickups.

### 10.5 Minimap
- 180×135px, bottom-right.
- District color bands, road grid, **subway line & stations**, drops, terminals, rivals, player, camera rectangle.
- Drops only shown if `known` or if in UPDATE phase.
- Rivals only shown if alerted, marked by scan, or stunned.

### 10.6 End Screens

**RUN COMPLETE:**
- Green "RUN COMPLETE" title
- Caches secured / lost / mission score
- **TOTAL SCORE** (persistent)
- **◈ OPIUM LOTS** (persistent)
- **Loot bag carried forward** — full list of weapons, transport, and spiderphones with levels
- "PRESS [R] FOR NEXT CYCLE"

**COURIER DOWN:**
- Red "COURIER DOWN" title
- Caches secured / lost / mission score
- **TOTAL SCORE LOST** (red, large)
- **OPIUM LOTS LOST** (violet)
- "Cycle counter reset to 1. Loot bag cleared."
- "PRESS [R] TO RESTART FROM SCRATCH"

### 10.7 Controls Summary

| Input | Action |
|---|---|
| WASD / Arrows | Move |
| SHIFT | Sprint |
| C | Crouch |
| E | Hold to interact (extract / upload / update) |
| SPACE | Scan |
| LMB | Fire active weapon |
| Mouse move | Aim |
| Mouse wheel | Cycle weapons |
| 1 / 2 / 3 | Select weapon |
| Q | Spiderphone: Reset |
| F | Spiderphone: Spawn |
| G | Spiderphone: Remote |
| **H** | **Ride subway to next station** |
| R | Restart / next cycle (on end screen) |

### 10.8 Accessibility Considerations (post-prototype)
- Colorblind-safe palette toggle (drop pink/amber → blue/white; finance purples → teal/magenta).
- Screen shake intensity slider.
- Scanline toggle.
- Full keyboard remapping.
- Reduced-motion mode (disables shake and pulse rings).
- **Subway cost preview toggle** — show the destination cost before the H press.

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
| `buildSubway()` | Builds 4-station zigzag track + segments |
| `subwayStationAt()` | Returns station index near a point, or -1 |
| `startSubwayRide()` / `updateSubwayRide()` | Subway cost check, transit interpolation, arrival |
| `solidAt()`, `losClear()` | Collision & line-of-sight queries |
| `bfsPath()` | Road-graph pathfinding for rivals |
| `newMission()` | Per-cycle reset and entity spawning |
| `update(dt)` | Master simulation tick |
| `updateInteraction(dt)` | Hold-to-interact state machine |
| `updateRival(r, dt)` | Per-rival FSM (patrol/search/alert) + movement + combat |
| `fireWeapon(type)` | Per-weapon firing logic (bullets / AoE / AoE) |
| `rollLoot(x, y)` | Loot category roll, persistence update, particle burst |
| `useSpiderphone(type)` | Spiderphone consumable logic |
| `render()` | Master draw call, camera transform, HUD |
| `draw*()` | Per-entity render functions |
| `drawLootBag()`, `drawWeaponBar()`, `drawSubwayPanel()` | New HUD panels |
| `initPersistent()` / `wipePersistent()` | Career state management |

### 11.3 Game Loop
```
requestAnimationFrame(frame)
  ├─ dt = clamp(now - last, 0, 0.05)   // cap to 20 FPS minimum step
  ├─ if PLAY: update(dt)
  ├─ render()
  └─ schedule next frame
```

**Fixed-timestep consideration:** The prototype uses variable timestep with a 50ms cap, which is adequate for the movement speeds and collision tolerances. A future version should use a fixed accumulator (60Hz) for deterministic replay.

### 11.4 Subway Transit Handling

The subway ride is a **modal movement state** that temporarily bypasses normal movement, collision, and combat. During a ride:
- The master `update(dt)` short-circuits into `updateSubwayRide(dt)` plus minimal housekeeping (particles, pulses, effects, rival patrols).
- Player position is interpolated along the stop chain (not a straight line) so the visual path follows the zigzag track.
- Rivals keep patrolling but cannot damage the player.
- Interaction state is reset.
- `player.angle` is not updated during transit.

### 11.5 Performance Notes
- Buildings are culled per-frame by camera bounds before drawing.
- Entities are culled by a ±200px margin around the camera.
- No per-frame allocations in hot paths (`draw*` functions use primitive math).
- `bfsPath` is called per-rival every 0.45–0.75s, not per-frame.
- Bullets, particles, effects, and pulses are all culled by lifetime and culled by screen bounds where cheap.
- Target: 60 FPS at 1080p with 16 rivals + combat on integrated graphics.

### 11.6 Known Limitations & Future Work
- Rival pathfinding is BFS on an unweighted grid (adequate but not optimal).
- No spatial hash for collision queries (fine at current entity counts).
- No save system — career is ephemeral, but **intentionally** so.
- No mobile input yet.
- Subway is a single linear line; multi-line networks are not supported.

---

## 12. CONTENT & SCOPE

### 12.1 In v2.0
- 1 world, procedurally generated per session (districts fixed, buildings random).
- 3-phase mission loop.
- 1 enemy type (rival patrol) with HP and stun states.
- 3 terminals.
- 6–10 dead drops per run (15 with SPAWN spiderphone).
- **4 loot categories:**
  - 3 weapon blueprints × 3 levels each
  - 3 transport blueprints × 3 levels each
  - 3 spiderphone consumables × 5 max each
  - 3 Opium Lot denominations
- **Subway system:** 4 stations, zigzag east–west, 10 lots per stop.
- **Persistent career:** score, credits, and loot bag carry across cycles.
- **Permadeath:** death wipes everything and resets cycle to 1.
- Combat: mouse aim, LMB fire, per-weapon cooldowns, kill score.
- Heat system, scoring, cycle progression.
- Full HUD with Loot Bag, Weapon Bar, Subway Panel, Minimap.
- Title screen, in-game messages, synthesized audio.
- End screens with carried-forward loot summary (win) or lost-score summary (death).

### 12.2 Out of Scope (v2.0)
- Multiple enemy types (drones, stationary cameras, snipers).
- NPC civilians.
- Narrative / dialogue.
- Multiple maps.
- Save/load (career is intentionally ephemeral).
- Multiplayer.
- Localization.
- Multiple subway lines / branching transit.

### 12.3 Post-Launch Roadmap (Proposed)

| Priority | Feature | Rationale |
|---|---|---|
| **P0** | Second enemy type (static security camera) | Adds map-reading depth; cameras don't chase but alert patrols |
| **P0** | Gamepad support | Standard for desktop action games |
| **P1** | District modifiers (e.g., downtown rivals move faster, exurbs have longer sightlines) | Makes district identity mechanically meaningful |
| **P1** | Expand subway to 2 crossing lines with transfer hubs | Turns transit into a routing puzzle |
| **P1** | Bank terminal — deposit score/lots mid-run to save them from a death | Deepens the risk/reward of permadeath |
| **P2** | Daily seed / leaderboard for career score | Retention and community |
| **P2** | Narrative intel drops (short text logs) | Adds tone and worldbuilding at low cost |
| **P3** | Mobile touch controls | Accessibility / reach |
| **P3** | Level editor | Community content |

---

## 13. RISKS & MITIGATIONS

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **Decay pacing feels unfair** | High (core loop breaks) | Medium | Expose decay rate as a tunable constant; add a "decay preview" UI element showing seconds-to-live |
| **Permadeath feels punishing after long career** | High (player churn) | High | Add mid-run bank terminals (post-launch P1); consider a "safe deposit" at terminals on upload |
| **Loot roll feels unrewarding** | Medium (build-up slows) | Medium | Already mitigated: 72% drop rate is generous; maxed categories convert to salvage score |
| **Subway costs feel too high / too low** | Medium (economy broken) | Medium | Cost is a single constant (10/stop); easy to tune. Monitor average lots earned per run vs. average spent. |
| **Rival pathfinding gets stuck on buildings** | Medium (AI looks dumb) | Medium | Current fallback: if path < 2 nodes, wander by angle. Future: add A* with corner smoothing |
| **Scan feels like a chore** | Medium (repetitive input) | Low | Already mitigated: scan reveals *and* marks enemies; cooldown creates rhythm |
| **Heat is invisible** | Low (unfair pressure) | Medium | HUD bar + color shift at 70 + spawn rate increases naturally signal heat |
| **Colorblind players can't distinguish loot categories** | High (accessibility) | High | Add colorblind palette toggle (post-prototype) — critical with 4 categories |
| **End-state ambiguity** ("did I win?") | Medium | Low | Clear "RUN COMPLETE" screen with score breakdown and "PRESS R" prompt; death screen explicitly says "wiped" |

---

## 14. SUCCESS METRICS (IF SHIPPED COMMERCIALLY)

- **Session length:** 8–20 minutes median; longer tail for skilled players.
- **Career length:** ≥3 completed cycles median before death (proves the loot loop is engaging enough to survive to).
- **Completion rate:** ≥55% of first runs reach "RUN COMPLETE".
- **Replay rate:** ≥60% of players start a second cycle within the same session (higher than v1.0 due to persistent loot).
- **Cycle depth:** Median max cycle ≥4 (up from ≥3 in v1.0).
- **Loot engagement:** ≥50% of players use at least one spiderphone per run; ≥30% use the subway at least once per run.
- **Death frustration:** <25% of players quit immediately after their first career death.
- **Subway adoption:** ≥40% of runs with ≥20 Opium Lots include at least one ride.

---

## 15. APPENDIX: TUNING CONSTANTS

All constants below are pulled directly from the v2.0 prototype and should be the starting point for any balance pass.

```js
// Player
MOVE_SPEED          = 205
CROUCH_SPEED        = 105
SPRINT_SPEED        = 330
PLAYER_RADIUS       = 11
PLAYER_HP           = 100
CONTACT_DAMAGE      = 34    // per second
HP_REGEN            = 5     // per second, when no rival within 340
RIVAL_HP            = 140
RIVAL_KILL_SCORE    = 50

// Scan
SCAN_CD             = 2.6
SCAN_RADIUS         = 1450
SCAN_HEAT           = 9

// Drops
DROP_COUNT          = min(10, 6 + cycle)
DROP_MAX            = 15     // with SPAWN spiderphone
DROP_FRESH_MIN      = 72
DROP_FRESH_MAX      = 100
DROP_DECAY_MIN      = 0.24 * (1 + cycle * 0.13)
DROP_DECAY_MAX      = 0.55 * (1 + cycle * 0.13)
UPDATE_DECAY_MUL    = 2.3 + cycle * 0.18

// Interaction
EXTRACT_TIME        = 3.2
UPLOAD_TIME         = 4.0
UPDATE_TIME         = 2.0
DROP_RANGE          = 72
TERMINAL_RANGE      = 85
RELEASE_DRAIN       = 1.6   // multiplier on progress drain

// Rivals
RIVAL_PATROL_SPD    = 92
RIVAL_SEARCH_SPD    = 130
RIVAL_ALERT_SPD     = 208
RIVAL_VIEW_PATROL   = 360
RIVAL_VIEW_ALERT    = 470
RIVAL_FOV           = 1.85
AWARE_GAIN          = 1.9
AWARE_GAIN_ALERT    = 3.1
AWARE_DECAY         = 0.75
ALERT_TO_SEARCH     = 5.5
SEARCH_TO_PATROL    = 6.0
CROUCH_VIS_MUL      = 0.42
SPRINT_VIS_MUL      = 1.18
COVER_VIS_MUL       = 0.30

// Spawning
SPAWN_INTERVAL      = max(1.4, 4.5 - cycle * 0.25)
SPAWN_CAP           = min(16, 6 + cycle * 2 + floor(heat / 16))
START_RIVALS        = min(14, 5 + cycle * 2)

// Heat
HEAT_SCAN           = 9
HEAT_EXTRACT        = 26
HEAT_UPLOAD         = 14
HEAT_ALERT_PER_SEC  = 7
HEAT_DECAY          = 4.5

// Loot
LOOT_CHANCE         = 0.72
MAX_WEAPON_LVL      = 3
MAX_TRANSPORT_LVL   = 3
MAX_COMM_COUNT      = 5

// Loot category roll
WEAPON_ROLL         = 0.30   // 0.00 – 0.30
TRANSPORT_ROLL      = 0.22   // 0.30 – 0.52
COMMS_ROLL          = 0.18   // 0.52 – 0.70
FINANCE_ROLL        = 0.30   // 0.70 – 1.00

// Weapons — SMG
SMG_DMG             = [0, 25, 40, 60]
SMG_CD              = [0, 0.15, 0.12, 0.09]
SMG_SPEED           = 800
SMG_LIFE            = 1.0

// Weapons — Taser
TASER_RADIUS        = [0, 90, 130, 175]
TASER_STUN          = [0, 2.0, 3.0, 5.0]
TASER_CD            = [0, 2.5, 2.0, 1.5]

// Weapons — EMP
EMP_RADIUS          = [0, 200, 280, 370]
EMP_STUN            = [0, 3.0, 5.0, 8.0]
EMP_CD              = [0, 9.0, 7.0, 5.0]

// Transport bonuses (per level)
RUNNER_MOVE_BONUS   = 0.06   // +6% base speed per L
SPRINTER_SPD_BONUS  = 0.08   // +8% sprint speed per L
SPRINTER_VIS_BONUS  = -0.06  // -6% sprint visibility per L
GHOST_CROUCH_SPD    = 0.10   // +10% crouch speed per L
GHOST_CROUCH_VIS    = -0.06  // -6% crouch visibility per L

// Finance (Opium Lots)
FINANCE_SMALL_VALUE = 1
FINANCE_SMALL_WEIGHT = 50
FINANCE_MEDIUM_VALUE = 5
FINANCE_MEDIUM_WEIGHT = 35
FINANCE_LARGE_VALUE = 15
FINANCE_LARGE_WEIGHT = 15

// Subway
SUBWAY_COST_PER_STOP = 10
SUBWAY_STOP_COUNT    = 4
SUBWAY_BOARD_RADIUS  = 90
SUBWAY_RIDE_BASE     = 1.6
SUBWAY_RIDE_PER_STOP = 0.35
SUBWAY_STOPS         = [
  { k: 1,  m: 2 },   // Station 1 — far left, north
  { k: 5,  m: 8 },   // Station 2 — left-center, south
  { k: 10, m: 3 },   // Station 3 — right-center, north
  { k: 14, m: 9 }    // Station 4 — far right, south
]

// Salvage bonuses
SALVAGE_WEAPON      = 100
SALVAGE_TRANSPORT   = 100
SALVAGE_COMMS       = 50
```

---

*End of document — v2.0*