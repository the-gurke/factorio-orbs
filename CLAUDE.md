# Orbs Mod Documentation

## Overview

**Orbs** is a comprehensive magical modification for Factorio that introduces a complete magic system centered around orbs, runes, and alchemy. The mod fundamentally transforms the gameplay experience by replacing traditional electricity-based automation with magical alternatives, while maintaining the core factory-building mechanics.

For humans: The following contains a lot of spoilers! You might not want to read this.

## Key Features

### 1. Magical Items System

**Primary Items:**
- **Magic Orb**: Base magical energy item with stack size of 5
- **Active Magic Shard**: Spoils in 30 seconds to inactive shards (stack size 200)
- **Inactive Magic Shard**: Spoiled shards that can be banished or recycled
- **Conjuration Orb**: Special orb for crafting conjuration machines
- **Haste Orb**: Speed module that only works in conjuration machines (+20% speed)

**Unstable Orbs:**
- **Alpha State**: Spoils to Beta in 30 seconds
- **Beta State**: Spoils to Gamma in 1 second  
- **Gamma State**: Spoils to Alpha in 1 second

**Volatile Orbs:**
- Created as a byproduct of essence of stability
- Five variants (Q, R, S, T, U) that explode after 40 seconds
- Need to be neutralized through operations that mimick the simple group of order 6.

### 2. Magical Machines

**Conjuration Machine:**
- Purple-tinted assembler that only crafts "orbs" category recipes
- No power required (void energy source)
- 3 module slots accepting only haste orbs

**Soul Collector:**
- Collects souls from deaths within 35 tile radius
- Single slot inventory
- Based on iron chest design

**Rune Transformer:**
- Transforms rune words in cycling patterns
- Based on stone furnace, no power required
- Recipes change dynamically during gameplay

**Rune Altar:**
- Creates rune research packs from specific rune sequences
- Requires exact placement: Vitae, Ignis, Tempus, Terra, Umbra, Mortis

### 3. Research System

**Research Packs:**
- **Contraption Research Pack**: Replaces automation science pack
- **Conjuration Research Pack**: Made from active magic shards + copper cables
- **Divination Research Pack**: Made from divination essence + serendipity + luck
- **Rune Research Pack**: Created from specific

Note: this mod uses "research" instead of "science" since we don't do science.

### 4. Recipe Categories

**Conjuration Recipes** (orbs category):
- Conjure Shards: 1-32 orb variants creating n² shards
- Replicate Shards: 50% chance bonus shards
- Manifest Orb: 10 active shards → 1 magic orb
- Transfigure: Create specialized orbs
- Neutralize: Convert specialized orbs back to magic orbs

**Early-game Fuel Recipes:**
- Light Wood: Wood → Burning Wood (4MJ fuel, decays in 2 min)
- Light Coal: Coal → Burning Coal (8MJ fuel, decays in 5 min)
- Fire through Friction: Stick + Wood → 10% chance Burning Wood

### 5. Integration with Nanobots2

**Thematic Overrides:**
- Nano gun → Magic Wand
- Nano ammo → Summoning Essences
- Technologies rebranded with magical themes
- Magical ingredients replace technological components

### 6. Game Balance Changes

**Fuel System:**
- Base wood/coal have no fuel value
- Must be lit on fire to become usable fuel
- Burning fuels decay over time to glimming remains

**Inserter System:**
- Burner inserters work at fast inserter speed
- Magic inserters require no power
- All inserters except magic ones require fuel

**Transportation:**
- Red belts require stability liquid
- Gold plates provide speed boost flooring

## File Structure

### Core Data Files
- **`data.lua`**: Main data loader, includes all other data files
- **`categories.lua`**: Item groups, subgroups, and recipe categories
- **`item.lua`**: All item definitions including orbs, shards, and tools
- **`recipe.lua`**: All recipe definitions and generation logic
- **`entities.lua`**: Machine and entity definitions
- **`technology.lua`**: Research tree and technology definitions

### Runtime Control
- **`control.lua`**: Runtime scripts for telekinesis, soul collection, orbs research rewards, and rune transformation system
- **`rune-chains.lua`**: Defines cyclic transformation patterns for rune words

### Modifications
- **`data-final-fixes.lua`**: Late-stage modifications to base game and other mods
- **`removals.lua`**: Removes unwanted base game content and handles dependencies

### Localization
- **`locale/en/strings.cfg`**: All text strings for items, recipes, and technologies

### Graphics
- **`graphics/`**: 60+ custom graphics for all magical items and effects

## Magic System Mechanics

### Orb Conjuration
1. **Basic Process**: Magic Orbs → Active Magic Shards (with time limit)
2. **Scaling**: Higher tier conjurations create n² shards from n+1 orbs
3. **Efficiency**: Balance between speed and shard output

### Spoilage System
- Active shards spoil to inactive in 30 seconds
- Unstable orbs cycle through three states
- Volatile orbs explode after 40 seconds
- Proper timing essential for magical processes

### Divination System
**Divination Essence:**
- **Creation**: Combine one Unstable Orb [Beta State] + one Unstable Orb [Gamma State] → 2 Unstable Orb [Alpha State] + 1 Divination Essence (resets freshness on craft)
- **Spoilage**: Spoils in 10 seconds to nothing - extremely volatile!
- **Stabilization**: Can be stabilized using coal - consumes 1 coal with 50% chance to return it, resets spoilage timer
- **Usage**: Primary ingredient for Divination Research Pack and Soul Collector crafting

**Related Items:**
- **Spark of Luck**: 1% chance from conjuring luck with Magic Orb, spoils in 1 second
- **Dust of Serendipity**: Created from Stone + Magic Orb, spoils to Stone in 5 seconds
- **Divination Research Pack**: Requires Divination Essence + Dust of Serendipity + Spark of Luck

The divination system requires precise timing and coordination - you need to capture the extremely short-lived Spark of Luck (1 second), manage the quickly-spoiling Dust of Serendipity (5 seconds), and use freshly-stabilized Divination Essence (10 seconds) all within a narrow time window to create research packs.

### Stability Mechanics
- Extract stability from magic orbs
- Liquify for use in volatile orb manipulation
- Required for advanced belt upgrades

### Rune System
- 9 rune words: Ignis, Aqua, Ventus, Terra, Lux, Umbra, Tempus, Vitae, Mortis
- Transformation chains create complex puzzle mechanics
- Altar crafting requires precise ordering

## Implementation Notes

### Performance Considerations
- Periodic tick handlers for rune transformations (every 11 ticks)
- Soul collection on death events
- Efficient spoilage handling through built-in Factorio systems

### Mod Compatibility
- Integrates with Nanobots2 for magical automation
- Preserves Space Age compatibility
- Removes a lot of base game technologies that we don't want

## To keep in mind for Claude
- Technologies-related code should be added to `technology.lua`, not `data-final-fixes.lua`.
- Whenever you introduce new items, entities, technologies, etc., you need to add the corresponding locale strings for their names to `locale/en/strings.cfg`.
- Don't try to run the lua code.
