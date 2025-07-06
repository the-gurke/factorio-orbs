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
        local magic_orb_inserted = player.insert({name = "magic-orb", count = 5})
        local conjuration_orb_inserted = player.insert({name = "conjuration-orb", count = 2})
        
        if magic_orb_inserted > 0 or conjuration_orb_inserted > 0 then
          player.print("You have unlocked orbs technology! You've been given " .. magic_orb_inserted .. " Magic Orbs and " .. conjuration_orb_inserted .. " Conjuration Orbs to begin your magical journey!")
        else
          player.print("Orbs technology unlocked! Your inventory is full - make space to receive your starting orbs.")
        end
      end
    end
  end
end)
