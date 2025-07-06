-- control.lua
-- Runtime script that handles events during gameplay

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
  end
end)
