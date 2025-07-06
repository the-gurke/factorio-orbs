-- control.lua
-- Runtime script that handles events during gameplay

-- Give the first player starting orbs in a chest when they are created
script.on_event(defines.events.on_player_created, function(event)
  -- Only give orbs to the very first player (index 1)
  if event.player_index == 1 then
    -- Wait 1 second (60 ticks) before creating the chest to ensure player is ready
    script.on_nth_tick(60, function()
      local player = game.get_player(event.player_index)
      if player and player.valid then
        -- Find a good position near the player for the chest
        local player_pos = player.position
        local surface = player.surface

        -- Try to find a free position within 3 tiles of the player
        local chest_position = nil
        for dx = -3, 3 do
          for dy = -3, 3 do
            local test_pos = {x = player_pos.x + dx, y = player_pos.y + dy}
            if surface.can_place_entity({name = "iron-chest", position = test_pos}) then
              chest_position = test_pos
              break
            end
          end
          if chest_position then break end
        end

        -- If we couldn't find a spot nearby, just place it at player position + 2
        if not chest_position then
          chest_position = {x = player_pos.x + 2, y = player_pos.y}
        end

        -- Create the iron chest
        local chest = surface.create_entity({
          name = "iron-chest",
          position = chest_position,
          force = player.force
        })

        if chest then
          -- Add the starting orbs to the chest
          local inventory = chest.get_inventory(defines.inventory.chest)
          if inventory then
            inventory.insert({name = "magic-orb", count = 1})
            inventory.insert({name = "conjuration-orb", count = 2})

            player.print("A chest with magical orbs has appeared nearby! Check your surroundings.")
          else
            player.print("Failed to create starting chest inventory")
          end
        else
          -- Fallback: try to give directly to player
          local magic_orb_inserted = player.insert({name = "magic-orb", count = 1})
          local conjuration_orb_inserted = player.insert({name = "conjuration-orb", count = 2})

          if magic_orb_inserted > 0 and conjuration_orb_inserted > 0 then
            player.print("You have been given a Magic Orb and a Conjuration Orb to start your magical journey!")
          else
            player.print("Failed to give starting orbs - items may not exist or inventory full")
          end
        end
      end

      -- Remove this tick handler after it runs once
      script.on_nth_tick(60, nil)
    end)
  end
end)
