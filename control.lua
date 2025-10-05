-- control.lua
-- Runtime script that handles events during gameplay

--------------------------------------------------------
--  Defense Ward Management                           --
--------------------------------------------------------

-- Handle defense ward script triggers (when they fire)
script.on_event(defines.events.on_script_trigger_effect, function(event)
  if event.effect_id == "defense-ward-fired" and event.source_entity then
    if event.source_entity.valid and event.source_entity.name == "defense-ward" then
      -- Remove the defense ward immediately after it fires
      event.source_entity.destroy()
    end
  end

  -- Handle teleportation wand usage
  if event.effect_id == "teleportation-wand-used" then
    -- Find the player who triggered this
    local player = nil
    local source_position = nil
    local target_position = event.target_position

    -- Try to get player from source entity
    if event.source_entity and event.source_entity.valid then
      if event.source_entity.player then
        player = event.source_entity.player
      elseif event.source_entity.name == "character" then
        player = event.source_entity.player
      end
      source_position = event.source_entity.position
    end

    -- If we still don't have a player, try to find nearby players
    if not player and source_position and event.surface then
      local nearby_players = event.surface.find_entities_filtered{
        position = source_position,
        radius = 2,
        type = "character"
      }
      if #nearby_players > 0 then
        player = nearby_players[1].player
      end
    end

    if not player or not target_position then
      return
    end

    if player and player.valid and player.character then
      -- Check if player has teleportation wand equipped
      local gun_inventory = player.get_inventory(defines.inventory.character_guns)
      if not gun_inventory then return end

      local selected_gun_index = player.character.selected_gun_index
      if not selected_gun_index then return end

      local selected_gun = gun_inventory[selected_gun_index]
      if not (selected_gun and selected_gun.valid_for_read and selected_gun.name == "teleportation-wand") then
        return  -- Not using teleportation wand, ignore
      end

      -- Calculate direction from player to target
      local player_pos = player.character.position
      local dx = target_position.x - player_pos.x
      local dy = target_position.y - player_pos.y
      local distance = math.sqrt(dx * dx + dy * dy)

      -- Normalize direction and teleport 20 tiles in that direction
      if distance > 0 then
        local teleport_distance = 20
        local normalized_dx = dx / distance
        local normalized_dy = dy / distance

        local new_x = player_pos.x + normalized_dx * teleport_distance
        local new_y = player_pos.y + normalized_dy * teleport_distance

        -- Find a safe position to teleport to
        local safe_position = player.surface.find_non_colliding_position(
          "character",
          {x = new_x, y = new_y},
          5,  -- Search radius
          0.5  -- Precision
        )

        if safe_position then
          -- Create visual effect at old position
          player.surface.create_entity{
            name = "teleportation-cloud",
            position = player_pos,
            force = player.force
          }

          -- Teleport the player
          player.teleport(safe_position)

          -- Create visual effect at new position
          player.surface.create_entity{
            name = "teleportation-cloud",
            position = safe_position,
            force = player.force
          }
        end
      end
    end
  end
end)

--------------------------------------------------------
--  Telekinesis                                       --
--------------------------------------------------------

-- Function to apply telekinesis reach bonuses to a player
function apply_telekinesis_bonuses(player)
  if not player.character then return end

  -- Reset bonuses first
  player.character_build_distance_bonus = 0
  player.character_reach_distance_bonus = 0
  player.character_resource_reach_distance_bonus = 0
  player.character_item_drop_distance_bonus = 0

  -- Calculate total telekinesis bonus
  local total_bonus = 0
  for i = 1, 10 do
    if player.force.technologies["telekinesis-" .. i].researched then
      total_bonus = total_bonus + 9 -- +9 per tier (90 total max)
    end
  end

  -- Apply bonuses
  player.character_build_distance_bonus = total_bonus
  player.character_reach_distance_bonus = total_bonus
  player.character_resource_reach_distance_bonus = total_bonus
  player.character_item_drop_distance_bonus = total_bonus
end

-- Function to apply telekinesis bonuses to all players in a force
function apply_telekinesis_bonuses_to_force(force)
  for _, player in pairs(force.players) do
    if player.valid then
      apply_telekinesis_bonuses(player)
    end
  end
end

-- Apply telekinesis bonuses when players join, respawn, or change forces
script.on_event({
  defines.events.on_player_joined_game,
  defines.events.on_player_respawned,
  defines.events.on_player_changed_force,
  defines.events.on_player_created
}, function(event)
  local player = game.get_player(event.player_index)
  if player and player.valid then
    apply_telekinesis_bonuses(player)
  end
end)

script.on_configuration_changed(function()
  for _, force in pairs(game.forces) do
    apply_telekinesis_bonuses_to_force(force)
  end
end)

--------------------------------------------------------
--  Soul collectors                                   --
--------------------------------------------------------

-- Function to find soul collectors within range and add a soul
function collect_soul_from_death(surface, position, force)
  local soul_collectors = surface.find_entities_filtered{
    name = "soul-collector",
    position = position,
    radius = 35,
    force = force
  }

  for _, collector in pairs(soul_collectors) do
    if collector.valid then
      local inventory = collector.get_inventory(defines.inventory.chest)
      if inventory then
        -- Try to insert a soul into the collector
        local inserted = inventory.insert({name = "soul", count = 1})
        if inserted > 0 then
          -- Successfully collected a soul
          -- game.print("A soul has been collected by a Soul Collector at " ..
          --          string.format("%.1f, %.1f", collector.position.x, collector.position.y))
          return true -- Only collect one soul per death, first collector wins
        end
      end
    end
  end
  return false
end


-- Handle player death and soul collection
script.on_event(defines.events.on_player_died, function(event)
  local player = game.get_player(event.player_index)
  if player and player.valid and player.character then
    -- Check for nearby soul collectors
    local success = collect_soul_from_death(player.surface, player.character.position, player.force)
    if success then
      player.print("Your soul has been collected successfully.")
    end
  end
end)

--------------------------------------------------------
--  Orbs research                                     --
--------------------------------------------------------

-- Handle research completion events
script.on_event(defines.events.on_research_finished, function(event)
  local research = event.research

  if research.name:match("^telekinesis%-") then
    -- Apply telekinesis bonuses when any telekinesis technology is researched
    apply_telekinesis_bonuses_to_force(research.force)

    local tier = research.name:match("^telekinesis%-(%d+)$")
    if tier then
      for _, player in pairs(research.force.players) do
        if player.valid then
          player.print("Telekinesis " .. tier .. " researched! Your reach has been enhanced by magical forces.")
        end
      end
    end
  end
end)

--------------------------------------------------------
--  Runes                                             --
--------------------------------------------------------

-- Function to grow trees around a position
local function grow_trees_around_position(surface, center_position, tree_count, radius)
  local trees_planted = 0
  local max_attempts = tree_count * 5 -- Prevent infinite loop
  local attempts = 0

  while trees_planted < tree_count and attempts < max_attempts do
    attempts = attempts + 1

    -- Generate random position within radius
    local angle = math.random() * 2 * math.pi
    local distance = math.random() * radius
    local x = center_position.x + math.cos(angle) * distance
    local y = center_position.y + math.sin(angle) * distance
    local position = {x = x, y = y}

    -- Check if position is valid for tree placement
    if surface.can_place_entity{name = "tree-01", position = position} then
      -- Choose a random tree type
      local tree_types = {"tree-01", "tree-02", "tree-03", "tree-04", "tree-05", "tree-06", "tree-07", "tree-08", "tree-09"}
      local tree_type = tree_types[math.random(#tree_types)]

      -- Create the tree
      surface.create_entity{
        name = tree_type,
        position = position,
        force = "neutral"
      }
      trees_planted = trees_planted + 1
    end
  end

  return trees_planted
end

-- Rune transformation system
local rune_transformation_chains = require("rune-chains")

-- Initialize rune transformation state
local function init_rune_transformation_state()
  if not storage.rune_transformation_indices then
    storage.rune_transformation_indices = {}
    for rune_name, _ in pairs(rune_transformation_chains) do
      storage.rune_transformation_indices[rune_name] = 1
    end
  end
end

-- Function to enable the current transformation recipe for a rune
local function enable_current_rune_recipe(rune_name)
  if not storage.rune_transformation_indices then
    init_rune_transformation_state()
  end

  local current_index = storage.rune_transformation_indices[rune_name]
  local target_chain = rune_transformation_chains[rune_name]

  if current_index and target_chain and current_index <= #target_chain then
    local target_rune = target_chain[current_index]
    local recipe_name = "transform-" .. rune_name .. "-to-" .. target_rune .. "-" .. current_index

    -- Enable the current recipe for all forces
    for _, force in pairs(game.forces) do
      if force.recipes[recipe_name] then
        force.recipes[recipe_name].enabled = true
      end
    end
  end
end

-- Function to disable all transformation recipes for a rune
local function disable_all_rune_recipes(rune_name)
  local target_chain = rune_transformation_chains[rune_name]

  if target_chain then
    for i, target_rune in ipairs(target_chain) do
      local recipe_name = "transform-" .. rune_name .. "-to-" .. target_rune .. "-" .. i
      for _, force in pairs(game.forces) do
        if force.recipes[recipe_name] then
          force.recipes[recipe_name].enabled = false
        end
      end
    end
  end
end

-- Function to cycle to the next transformation recipe for a rune
local function cycle_rune_transformation(rune_name)
  if not storage.rune_transformation_indices then
    init_rune_transformation_state()
  end

  local current_index = storage.rune_transformation_indices[rune_name]
  local target_chain = rune_transformation_chains[rune_name]

  if current_index and target_chain then
    -- Disable current recipe
    disable_all_rune_recipes(rune_name)

    -- Move to next recipe in sequence
    current_index = current_index + 1
    if current_index > #target_chain then
      current_index = 1 -- Loop back to first
    end

    storage.rune_transformation_indices[rune_name] = current_index

    -- Enable new recipe
    enable_current_rune_recipe(rune_name)
  end
end

-- Initialize rune transformation state on game start
script.on_init(function()
  init_rune_transformation_state()

  -- Enable initial recipes for all runes
  for rune_name, _ in pairs(rune_transformation_chains) do
    enable_current_rune_recipe(rune_name)
  end

  -- Apply telekinesis bonuses to all players
  for _, force in pairs(game.forces) do
    apply_telekinesis_bonuses_to_force(force)
  end

  -- Remove crash site and customize intro using freeplay remote interface
  if remote.interfaces["freeplay"] then
    remote.call("freeplay", "set_disable_crashsite", true)
    remote.call("freeplay", "set_custom_intro_message", "How did I end up here? I don't remember... I need to get back... Where is my satchel with the orbs? Maybe there is some way to open a portal back?")
  end

  -- Spawn magic satchel randomly in -20,-20 to 20,20 range after crash site removal
  local surface = game.surfaces["nauvis"]
  if surface then
    local max_attempts = 100
    local attempts = 0
    local satchel_placed = false

    while not satchel_placed and attempts < max_attempts do
      attempts = attempts + 1
      local x = math.random(-20, 20)
      local y = math.random(-20, 20)
      local position = {x = x, y = y}

      -- Check if position is valid for placement
      if surface.can_place_entity{name = "magic-satchel", position = position} then
        surface.create_entity{
          name = "magic-satchel",
          position = position,
          force = "neutral"
        }
        satchel_placed = true
      end
    end
  end
end)

-- Periodic check for rune transformer completion
-- Check every 0.2*60-1 ticks (just before 0.2 seconds) to catch completed recipes
-- (The Spiritus rune crafting recipe completes in 0.2 seconds)
script.on_nth_tick(0.2*60-1, function(event)
  -- Check all rune transformers on all surfaces
  for _, surface in pairs(game.surfaces) do
    local rune_transformers = surface.find_entities_filtered{name = "rune-transformer"}

    for _, transformer in pairs(rune_transformers) do
      if transformer.valid then
        -- Check if the transformer is currently crafting
        local recipe = transformer.get_recipe()
        if recipe and recipe.category == "rune-transformation" then
          -- Check if the recipe is about to complete (progress > 0.95)
          local progress = transformer.crafting_progress
          if progress > 0 then
            -- Extract the rune name from the recipe name
            -- Recipe format: "transform-rune-word-{source}-to-rune-word-{target}-{index}"
            local recipe_name = recipe.name
            local source_rune = recipe_name:match("transform%-(rune%-word%-[^%-]+)%-to")

            if source_rune and rune_transformation_chains[source_rune] then
              -- Cycle to the next transformation for this rune
              cycle_rune_transformation(source_rune)
            end
          end
        end
      end
    end
  end
end)

-- Periodic check for rune altar crafting
-- Check every 120 ticks if rune altars have the correct rune sequence
script.on_nth_tick(120, function(event)
  -- Check all rune altars on all surfaces
  for _, surface in pairs(game.surfaces) do
    local rune_altars = surface.find_entities_filtered{name = "rune-altar"}

    for _, altar in pairs(rune_altars) do
      if altar.valid then
        local inventory = altar.get_inventory(defines.inventory.chest)
        if inventory then
          -- Check if inventory has exactly 6 items in the correct order
          local expected_runes = {
            "rune-word-vitae",
            "rune-word-ignis",
            "rune-word-tempus",
            "rune-word-terra",
            "rune-word-umbra",
            "rune-word-mortis"
          }

          -- Count total items
          local total_items = 0
          for i = 1, math.min(inventory.get_bar(), #inventory) do
            local stack = inventory[i]
            if stack and stack.valid_for_read then
              total_items = total_items + stack.count
            end
          end

          -- Check if we have exactly 6 items
          if total_items == 6 then
            local match = true

            -- Check each slot for the correct rune
            for i = 1, 6 do
              if i <= #inventory then
                local stack = inventory[i]
                if not stack or not stack.valid_for_read or
                   stack.name ~= expected_runes[i] or stack.count ~= 1 then
                  match = false
                  break
                end
              else
                match = false
                break
              end
            end

            -- Check that slots 7-10 are empty
            for i = 7, math.min(10, #inventory) do
              local stack = inventory[i]
              if stack and stack.valid_for_read then
                match = false
                break
              end
            end

            if match then
              -- Remove all runes
              for i = 1, 6 do
                if i <= #inventory then
                  inventory[i].clear()
                end
              end

              -- Add rune research pack
              inventory.insert({name = "rune-research-pack", count = 1})
            end
          end

          -- Check SILVA sequence: Spiritus, Ignis, Lux, Vitae, Aqua (5 items)
          if total_items == 5 then
            local expected_runes_silva = {
              "rune-word-spiritus",
              "rune-word-ignis",
              "rune-word-lux",
              "rune-word-vitae",
              "rune-word-aqua"
            }

            local match = true

            -- Check each slot for the correct rune
            for i = 1, 5 do
              if i <= #inventory then
                local stack = inventory[i]
                if not stack or not stack.valid_for_read or
                   stack.name ~= expected_runes_silva[i] or stack.count ~= 1 then
                  match = false
                  break
                end
              else
                match = false
                break
              end
            end

            -- Check that remaining slots are empty
            for i = 6, math.min(10, #inventory) do
              local stack = inventory[i]
              if stack and stack.valid_for_read then
                match = false
                break
              end
            end

            if match then
              -- Check if SILVA ritual technology is researched
              local force = altar.force
              if force.technologies["silva-ritual"] and force.technologies["silva-ritual"].researched then
                -- Remove all runes
                for i = 1, 5 do
                  if i <= #inventory then
                    inventory[i].clear()
                  end
                end

                -- Grow 30 trees randomly within 15 tiles of the altar
                local trees_planted = grow_trees_around_position(surface, altar.position, 30, 15)

                -- Notify players nearby
                for _, player in pairs(game.connected_players) do
                  if player.surface == surface then
                    local distance_to_altar = math.sqrt((player.position.x - altar.position.x)^2 + (player.position.y - altar.position.y)^2)
                    if distance_to_altar <= 50 then -- Notify players within 50 tiles
                      player.print("The SILVA ritual has been completed! " .. trees_planted .. " trees have grown from the magical energy.")
                    end
                  end
                end
              end
              -- If technology not researched, nothing happens (no notification)
            end
          end
        end
      end
    end
  end
end)

--------------------------------------------------------
--  Handcrafting Triggers                            --
--------------------------------------------------------

-- Handle special items when crafted
script.on_event(defines.events.on_player_crafted_item, function(event)
  local player = game.get_player(event.player_index)
  if not player or not player.valid then return end

  local crafted_item = event.item_stack

  -- Death Magic System
  if crafted_item and crafted_item.valid_for_read and crafted_item.name == "death" then
    game.print("Death has been summoned! The magic consumes you...")

    -- Schedule death for next tick to allow item to be transferred to inventory
    local death_count = crafted_item.count

    script.on_nth_tick(game.tick + 1, function()
      if player and player.valid and player.character then
        -- Remove death items from inventory
        local removed = player.remove_item({name = "death", count = death_count})
        -- Kill the player
        player.character.die()
      end
      -- Unregister this one-time callback
      script.on_nth_tick(game.tick, nil)
    end)
  end

  -- Night Magic System
  if crafted_item and crafted_item.valid_for_read and crafted_item.name == "night" then
    game.print("Night has been summoned! Darkness falls...")

    -- Schedule night summoning for next tick to allow item to be transferred to inventory
    local night_count = crafted_item.count

    script.on_nth_tick(game.tick + 1, function()
      if player and player.valid then
        -- Remove night items from inventory
        local removed = player.remove_item({name = "night", count = night_count})
        -- Set time to midnight (0.5 = midnight in Factorio)
        player.surface.daytime = 0.5
      end
      -- Unregister this one-time callback
      script.on_nth_tick(game.tick, nil)
    end)
  end
end)

--------------------------------------------------------
--  Portal System                                    --
--------------------------------------------------------

-- Combined portal management every 60 ticks (fuel checking and power management)
script.on_nth_tick(60, function(event)
  for _, surface in pairs(game.surfaces) do
    -- Process inactive portals (fuel checking)
    local inactive_portals = surface.find_entities_filtered{name = "inactive-portal"}

    for _, portal in pairs(inactive_portals) do
      if portal.valid then
        -- Check if portal is crafting "portal-home"
        local recipe = portal.get_recipe()
        if recipe and recipe.name == "portal-home" then
          -- Check if portal has fuel (divination essence)
          local fuel_inventory = portal.get_fuel_inventory()
          if fuel_inventory and fuel_inventory.is_empty() then
            -- No fuel - reduce crafting progress significantly
            local current_progress = portal.crafting_progress
            portal.crafting_progress = math.max(0, current_progress - 0.02) -- Lose 2% progress per second
          end
        end
      end
    end

    -- Process active portals (power checking and conversion back to inactive)
    local active_portals = surface.find_entities_filtered{name = "active-portal"}

    for _, portal in pairs(active_portals) do
      if portal.valid then
        -- Check if portal has fuel (divination essence)
        local fuel_inventory = portal.get_fuel_inventory()
        if fuel_inventory and fuel_inventory.is_empty() then
          -- No fuel - convert back to inactive portal
          local position = portal.position
          local force = portal.force
          local surface_ref = portal.surface

          -- Remove active portal
          portal.destroy()

          -- Create inactive portal
          local new_inactive_portal = surface_ref.create_entity{
            name = "inactive-portal",
            position = position,
            force = force
          }

          -- Set the recipe to portal-home
          if new_inactive_portal then
            new_inactive_portal.set_recipe("portal-home")
          end
        end
      end
    end
  end
end)

-- Monitor portal crafting completion and entity replacement
script.on_nth_tick(10, function(event) -- Check every 10 ticks for responsiveness
  for _, surface in pairs(game.surfaces) do
    local inactive_portals = surface.find_entities_filtered{name = "inactive-portal"}

    for _, portal in pairs(inactive_portals) do
      if portal.valid then
        -- Check if portal just completed "portal-home" recipe
        local recipe = portal.get_recipe()
        if recipe and recipe.name == "portal-home" then
          -- Calculate remaining ticks (recipe energy is in seconds, convert to ticks)
          local recipe_time_ticks = recipe.energy * 60 -- 120s * 60 = 7200 ticks
          local remaining_ticks = recipe_time_ticks * (1 - portal.crafting_progress)
          if remaining_ticks < 10 then
            -- Recipe completed! Replace with active portal
            local position = portal.position
            local force = portal.force
            local surface_ref = portal.surface

            -- Store any remaining fuel
            local fuel_inventory = portal.get_fuel_inventory()
            local remaining_fuel = {}
            if fuel_inventory then
              for i = 1, #fuel_inventory do
                local stack = fuel_inventory[i]
                if stack and stack.valid_for_read then
                  table.insert(remaining_fuel, {name = stack.name, count = stack.count})
                end
              end
            end

            -- Store any modules
            local module_inventory = portal.get_module_inventory()
            local remaining_modules = {}
            if module_inventory then
              for i = 1, #module_inventory do
                local stack = module_inventory[i]
                if stack and stack.valid_for_read then
                  table.insert(remaining_modules, {name = stack.name, count = stack.count})
                end
              end
            end

            -- Remove inactive portal
            portal.destroy()

            -- Create active portal
            local active_portal = surface_ref.create_entity{
              name = "active-portal",
              position = position,
              force = force
            }

            if active_portal then
              -- Restore fuel to active portal
              local new_fuel_inventory = active_portal.get_fuel_inventory()
              if new_fuel_inventory then
                for _, fuel_item in pairs(remaining_fuel) do
                  new_fuel_inventory.insert(fuel_item)
                end
              end

              -- Restore modules to active portal
              local new_module_inventory = active_portal.get_module_inventory()
              if new_module_inventory then
                for _, module_item in pairs(remaining_modules) do
                  new_module_inventory.insert(module_item)
                end
              end

              -- Set the active portal to craft "sustain-portal-home"
              active_portal.set_recipe("sustain-portal-home")
            end
          end
        end
      end
    end
  end
end)


-- Win condition check - every tick for immediate response
script.on_event(defines.events.on_tick, function(event)
  -- Only check if there are active portals to improve performance
  for _, surface in pairs(game.surfaces) do
    local active_portals = surface.find_entities_filtered{name = "active-portal"}

    for _, portal in pairs(active_portals) do
      if portal.valid then
        -- Check if portal is crafting "sustain-portal-home"
        local recipe = portal.get_recipe()
        if recipe and recipe.name == "sustain-portal-home" then
          -- Check if any player is within 2 tiles of portal center
          for _, player in pairs(game.connected_players) do
            if player.surface == surface and player.character then
              local distance = math.sqrt((player.position.x - portal.position.x)^2 + (player.position.y - portal.position.y)^2)
              if distance <= 2 then
                -- Player is close enough - trigger win condition!
                game.set_game_state{
                  game_finished = true,
                  player_won = true,
                  can_continue = true,
                  victorious_force = player.force
                }
                return -- Exit early since game is won
              end
            end
          end
        end
      end
    end
  end
end)

--------------------------------------------------------
--  Summoning Essence Functionality (Nanobots-style)  --
--------------------------------------------------------

-- Helper function to insert items with spill to ground if inventory full
local function insert_with_spill(player, item_stacks)
  if not player or not player.valid or not player.character then
    return false
  end

  local new_stacks = {}
  if item_stacks then
    if item_stacks[1] and item_stacks[1].name then
      new_stacks = item_stacks
    elseif item_stacks and item_stacks.name then
      new_stacks = { item_stacks }
    end

    for _, stack in pairs(new_stacks) do
      local name, count, health = stack.name, stack.count, stack.health or 1
      if prototypes.item[name] and not prototypes.item[name].hidden then
        local inserted = player.insert({ name = name, count = count, health = health })
        if inserted ~= count then
          -- Spill remaining items to ground at player position
          player.surface.spill_item_stack(player.character.position, { name = name, count = count - inserted, health = health }, true)
        end
      end
    end
    return new_stacks[1] and new_stacks[1].name and true
  end
  return false
end

-- Helper function to get summoning wand and ammo if available
local function get_summoning_wand_and_ammo(player)
  if not player.character then return nil, nil end

  -- Check if player has summoning wand as the SELECTED gun
  local gun_inventory = player.get_inventory(defines.inventory.character_guns)
  if not gun_inventory then return nil, nil end

  local selected_gun_index = player.character.selected_gun_index
  if not selected_gun_index then return nil, nil end

  local selected_gun = gun_inventory[selected_gun_index]
  if not (selected_gun and selected_gun.valid_for_read and selected_gun.name == "summoning-wand") then
    return nil, nil
  end

  -- Get the ammo from the corresponding ammo slot
  local ammo_inventory = player.get_inventory(defines.inventory.character_ammo)
  if not ammo_inventory then return nil, nil end

  local ammo = ammo_inventory[selected_gun_index]
  if ammo and ammo.valid_for_read and ammo.name == "summoning-essence" then
    return selected_gun, ammo
  end

  -- Check if player has summoning essence in main inventory that could be loaded
  if player.get_item_count("summoning-essence") > 0 then
    return selected_gun, nil  -- Gun available, but need to load ammo
  end

  return nil, nil
end

-- Helper function to drain ammo and reload if needed (based on Nanobots2)
local function drain_summoning_ammo(player, ammo, amount)
  if player.cheat_mode then
    return true
  end

  amount = amount or 1
  local name = ammo.name
  ammo.drain_ammo(amount)

  if not ammo.valid_for_read then
    -- Ammo depleted, try to reload from main inventory
    local new_ammo = player.get_main_inventory().find_item_stack(name)
    if new_ammo then
      ammo.set_stack(new_ammo)
      new_ammo.clear()
    end
    return true
  end

  return true
end

-- Helper function to check if player has required items for ghost
local function player_has_items_for_ghost(player, ghost)
  if not ghost.valid or not ghost.ghost_prototype then return false end

  local items_to_place = ghost.ghost_prototype.items_to_place_this
  if not items_to_place then return false end

  -- Check if player has any of the items that can place this ghost
  for _, item_proto in pairs(items_to_place) do
    if player.get_item_count(item_proto.name) > 0 then
      return true, item_proto.name
    end
  end

  return false
end

-- Helper function to handle item-request-proxy based module insertion
local function handle_module_insertion(player, proxy)
  if not proxy.valid or proxy.name ~= "item-request-proxy" then
    return false
  end

  local target = proxy.proxy_target
  if not target or not target.valid then
    return false
  end

  -- Check if target has module inventory
  if not target.get_module_inventory then
    return false
  end

  local module_inventory = target.get_module_inventory()
  if not module_inventory then
    return false
  end

  -- Get the item requests from the proxy
  local item_requests = proxy.item_requests
  if not item_requests then
    return false
  end

  -- Check if player has ALL requested modules before doing anything
  local can_fulfill_all = true
  local module_requests = {}

  -- First pass: check if all requests can be fulfilled
  for i, request in pairs(item_requests) do
    if type(request) == "table" and request.name and request.count then
      local item_name = request.name
      local count = request.count

      -- Check if this is a module
      local item_prototype = prototypes.item[item_name]
      if item_prototype and item_prototype.type == "module" then
        -- Check if player has enough of this module
        if player.get_item_count(item_name) >= count then
          -- Check if target can accept all these modules
          if target.can_insert({name = item_name, count = count}) then
            table.insert(module_requests, {name = item_name, count = count})
          else
            can_fulfill_all = false
            break
          end
        else
          can_fulfill_all = false
          break
        end
      end
    end
  end

  -- If we can fulfill all requests, do it all at once
  if can_fulfill_all and #module_requests > 0 then
    local total_inserted = 0

    for _, req in pairs(module_requests) do
      local inserted = target.insert({name = req.name, count = req.count})
      if inserted > 0 then
        player.remove_item({name = req.name, count = inserted})
        total_inserted = total_inserted + inserted
      end
    end

    if total_inserted > 0 then
      -- All modules inserted successfully, destroy the proxy
      proxy.destroy()

      -- Create visual effect
      target.surface.create_entity{
        name = "summoning-cloud-small",
        position = target.position,
        force = player.force
      }

      return true
    end
  end

  return false
end

-- Helper function to handle entity deconstruction
local function handle_entity_deconstruction(player, entity)
  if not entity.valid or not entity.to_be_deconstructed(player.force) then
    return false
  end

  -- Store surface and position for visual effects
  local surface = entity.surface
  local position = entity.position

  -- Use player.mine_entity which automatically handles item returns
  local mined = player.mine_entity(entity)

  if mined then
    -- Successfully deconstructed - CREATE CLOUD EFFECT!
    surface.create_entity{
      name = "summoning-cloud-small",
      position = position,
      force = player.force
    }
    return true
  end

  return false
end

-- Helper function to handle ghost construction
local function handle_ghost_construction(player, ghost)
  if not ghost.valid then return false end

  -- Check if player has the required items BEFORE trying to revive
  local has_items, item_name = player_has_items_for_ghost(player, ghost)
  if not has_items then
    return false  -- Player doesn't have the required items
  end

  -- Store surface and position before reviving (ghost becomes invalid after revive)
  local surface = ghost.surface
  local position = ghost.position

  -- Remove the required item from player's inventory
  if player.remove_item({name = item_name, count = 1}) == 0 then
    return false  -- Couldn't remove item (shouldn't happen due to pre-check)
  end

  -- Try to revive the ghost
  local revived, entity, requests = ghost.revive({
    return_item_request_proxy = true,
    raise_revive = true
  })

  if revived and entity then
    -- Successfully placed building - CREATE CLOUD EFFECT!
    surface.create_entity{
      name = "summoning-cloud-small",
      position = position,
      force = player.force
    }

    return true
  else
    -- Failed to revive, give back the item
    player.insert({name = item_name, count = 1})
    return false
  end
end

-- Helper function to get summoning speed (how often to poll)
local function get_summoning_speed(player)
  -- Base polling rate: every 30 ticks (0.5 seconds)
  -- Speed research makes it faster: 30, 23, 16, 9
  local speed_modifier = player.force.get_gun_speed_modifier("summoning-essence")
  return math.floor(30 - speed_modifier * 14)
end

-- Helper function to get summoning range
local function get_summoning_range(player)
  -- range: 8 + 6 / level
  local damage_modifier = player.force.get_ammo_damage_modifier("summoning-essence")
  local base_range = 8
  return base_range + (damage_modifier * 6)
end

-- Main polling function (like nanobots poll_players)
local function poll_summoning_players(event)
  -- Dynamic polling rate based on any player's research
  local min_poll_rate = 30  -- Default slowest rate
  for _, player in pairs(game.connected_players) do
    if player.character and player.character.valid then
      local player_speed = get_summoning_speed(player)
      min_poll_rate = math.min(min_poll_rate, player_speed)
    end
  end

  -- Only run at the calculated rate
  if event.tick % min_poll_rate == 0 then
    for _, player in pairs(game.connected_players) do
      if player.character and player.character.valid then
        local gun, ammo = get_summoning_wand_and_ammo(player)
        if gun and ammo then
          -- Player has summoning wand equipped with essence
          local position = player.character.position
          local surface = player.character.surface
          local radius = get_summoning_range(player)  -- Dynamic range based on research

          -- Priority order: Construction first, then module insertion, then deconstruction
          local did_work = false

          -- Find ghosts in range for construction
          local ghosts = surface.find_entities_filtered{
            position = position,
            radius = radius,
            type = "entity-ghost",
            force = player.force
          }

          -- Try to construct one ghost per tick cycle
          for _, ghost in pairs(ghosts) do
            if handle_ghost_construction(player, ghost) then
              -- Successfully constructed something, consume ammo
              drain_summoning_ammo(player, ammo, 1)
              did_work = true
              break  -- Only do one action per cycle
            end
          end

          -- If no construction was done, try module insertion
          if not did_work then
            -- Find item-request-proxy entities in range
            local proxy_entities = surface.find_entities_filtered{
              position = position,
              radius = radius,
              force = player.force,
              name = "item-request-proxy"
            }

            -- Try to fulfill one module request per tick cycle
            for _, proxy in pairs(proxy_entities) do
              if handle_module_insertion(player, proxy) then
                -- Successfully inserted module, consume ammo
                drain_summoning_ammo(player, ammo, 1)
                did_work = true
                break  -- Only do one action per cycle
              end
            end
          end

          -- If no construction or module insertion was done, try deconstruction
          if not did_work then
            -- Find entities marked for deconstruction
            local entities_to_deconstruct = surface.find_entities_filtered{
              position = position,
              radius = radius,
              force = player.force,
              to_be_deconstructed = true
            }

            -- Try to deconstruct one entity per tick cycle
            for _, entity in pairs(entities_to_deconstruct) do
              if handle_entity_deconstruction(player, entity) then
                -- Successfully deconstructed something, consume ammo
                drain_summoning_ammo(player, ammo, 1)
                break  -- Only do one action per cycle
              end
            end
          end
        end
      end
    end
  end
end

script.on_event(defines.events.on_tick, poll_summoning_players)

