-- control.lua
-- Runtime script that handles events during gameplay

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

-- Apply telekinesis bonuses to all players on init and configuration change
script.on_init(function()
  for _, force in pairs(game.forces) do
    apply_telekinesis_bonuses_to_force(force)
  end
end)

script.on_configuration_changed(function()
  for _, force in pairs(game.forces) do
    apply_telekinesis_bonuses_to_force(force)
  end
end)
