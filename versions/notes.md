##Core Loop & Interaction Design##
The game turns a data-decay timer into a tense stealth sprint. You start by scanning to reveal the freshest dead drop, then hold E to extract it, upload at a secure terminal, and finally race to update every remaining cache before they expire. Each cache has its own freshness bar that drains at a variable rate, so prioritizing which drops to save first matters.

Real-time pressure: Drops visibly decay, primary cache is highlighted in pink, and a minimap tracks your progress across the open city.

Stealth vs speed: Crouch to reduce detection range, sprint to move faster but attract attention, and manage your heat and HP as rival units patrol with dynamic awareness cones.

Living map: Rival patrols reroute toward your last known position, terminals glow when active, and scanning emits a pulse that briefly marks enemies and reveals caches.

Optimization Tip: You can adjust difficulty by tuning decay per drop (0.22–0.5 baseline) and the decayMul value in the UPDATE phase (2.3–3.0) inside the update() function, or tweak rival view distances (viewDist 360/470) and awareness buildup (1.9) in updateRival() for easier or harder stealth.

##Core Gameplay & Stealth Systems##

The game runs on a tight three-phase loop that constantly forces you to weigh speed against safety.

-- Scan → Extract → Upload → Update: Press SPACE to pulse-scan the map, revealing nearby dead drops. The freshest cache becomes your primary target — hold E to extract it, then find a green secure terminal to upload the data. Once uploaded, every remaining drop is revealed and begins decaying faster, turning the endgame into a frantic race across districts.

-- Stealth vs. speed: Crouching cuts enemy view distance by more than half, while sprinting makes you faster but easier to spot. Rival patrols sweep the map with visible vision cones; if they fill their awareness arc, they alert and hunt your last known position. Heat rises when you’re seen or when you scan, drawing more patrols into the area.

-- Living world feedback: Drops visually decay as their freshness bars drain, the minimap tracks known caches, terminals, and rival positions, and your actions ripple outward — extracting a cache spikes heat, uploading accelerates decay, and every cache lost is permanently marked on the map.

#added#
##Opium Lots & the Zigzag Subway##

The Finance category adds a new currency — Opium Lots — that drops in three denominations and feeds directly into the subway system.

Finance Loot (Opium Lots): Dead drops now have a 30% chance of yielding finance instead of a blueprint. Drops come in three tiers:

Small (×1) — purple, common (50 weight)

Medium (×5) — violet, uncommon (35 weight)

Large (×15) — magenta, rare (15 weight)

Your credit balance appears in the top-right vitals panel as ◈ OPIUM LOTS and in the Loot Bag's new FINANCE section.

The Subway Line: Four stations zigzag east–west across the map — Station 1 (far left, north), Station 2 (left-center, south), Station 3 (right-center, north), Station 4 (far right, south). The line is drawn as a glowing violet track with dashed center markings, and it appears on the minimap too.

Riding the Line: Walk within 90 units of a station to board. The ◈ SUBWAY LINE panel (bottom-left, above the weapon bar) shows every station, your current position, and the cost to reach each one. Press H to ride to the next station in the line. Each stop costs 10 Opium Lots — so a full cross-map jump from Station 1 to Station 4 costs 30 Lots and takes roughly 2.6 seconds. During transit the player is locked to the track, rivals reset their alert state, and violet particles trail behind.

Economy Loop: Saving caches earns score; saving finance drops earns Lots; Lots buy subway hops that let you reach distant drops before they decay. Dying wipes your Lots along with everything else, so every ride is a calculated spend.
