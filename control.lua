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

-- Apply telekinesis bonuses to all players on configuration change
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

-- Give orbs to players when they research orbs technology
script.on_event(defines.events.on_research_finished, function(event)
  local research = event.research

  if research.name == "orbs-technology" then
    -- Give orbs to all players in the force that researched the technology
    for _, player in pairs(research.force.players) do
      if player.valid then
        -- Try to insert orbs into player inventory
        local magic_orb_inserted = player.insert({name = "magic-orb", count = 1})
        local conjuration_orb_inserted = player.insert({name = "conjuration-orb", count = 2})

        -- Calculate how many orbs couldn't be inserted
        local magic_orb_dropped = 1 - magic_orb_inserted
        local conjuration_orb_dropped = 2 - conjuration_orb_inserted

        -- Drop any orbs that couldn't be inserted to the ground
        if magic_orb_dropped > 0 then
          player.surface.spill_item_stack(player.position, {name = "magic-orb", count = magic_orb_dropped}, true, player.force, false)
        end

        if conjuration_orb_dropped > 0 then
          player.surface.spill_item_stack(player.position, {name = "conjuration-orb", count = conjuration_orb_dropped}, true, player.force, false)
        end

        -- Give appropriate message based on what happened
        if magic_orb_inserted > 0 or conjuration_orb_inserted > 0 then
          local message = "You have unlocked orbs technology! You've been given " .. magic_orb_inserted .. " Magic Orb and " .. conjuration_orb_inserted .. " Conjuration Orbs"
          if magic_orb_dropped > 0 or conjuration_orb_dropped > 0 then
            message = message .. " (some items dropped on the ground due to full inventory)"
          end
          message = message .. " to begin your magical journey!"
          player.print(message)
        else
          player.print("Orbs technology unlocked! Your inventory is full - starting orbs have been dropped on the ground near you.")
        end
      end
    end
  elseif research.name:match("^telekinesis%-") then
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

-- Rune transformation system
local rune_transformation_chains = require("rune-chains")

-- Initialize global rune transformation state
local function init_rune_transformation_state()
  if not global then
    global = {}
  end
  if not global.rune_transformation_indices then
    global.rune_transformation_indices = {}
    for rune_name, _ in pairs(rune_transformation_chains) do
      global.rune_transformation_indices[rune_name] = 1 -- Start at first transformation
    end
  end
end

-- Function to enable the current transformation recipe for a rune
local function enable_current_rune_recipe(rune_name)
  if not global or not global.rune_transformation_indices then
    init_rune_transformation_state()
  end

  local current_index = global.rune_transformation_indices[rune_name]
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
  if not global or not global.rune_transformation_indices then
    init_rune_transformation_state()
  end

  local current_index = global.rune_transformation_indices[rune_name]
  local target_chain = rune_transformation_chains[rune_name]

  if current_index and target_chain then
    -- Disable current recipe
    disable_all_rune_recipes(rune_name)

    -- Move to next recipe in sequence
    current_index = current_index + 1
    if current_index > #target_chain then
      current_index = 1 -- Loop back to first
    end

    global.rune_transformation_indices[rune_name] = current_index

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
        end
      end
    end
  end
end)
