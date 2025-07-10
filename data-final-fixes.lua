-- data-final-fixes.lua
-- Override Nanobots2 technologies and items to use magical theming

-- Check if Nanobots2 is loaded
if mods["Nanobots2"] then
  
  -- Override main nanobots technology
  if data.raw.technology["nanobots"] then
    local tech = data.raw.technology["nanobots"]
    tech.icon = "__orbs__/graphics/summoning-technology.png"
    tech.icon_size = 1024
    tech.prerequisites = {"orbs-technology"}
    tech.unit.count = 20
    tech.unit.ingredients = {{"conjuration-research-pack", 1}}
    tech.localised_name = {"technology-name.summon-machines"}
    tech.localised_description = {"technology-description.summon-machines"}
  end
  
  -- Override nanobots cliff technology
  if data.raw.technology["nanobots-cliff"] then
    local tech = data.raw.technology["nanobots-cliff"]
    tech.icon = "__orbs__/graphics/cliff-explosion.png"
    tech.icon_size = 1024
    tech.prerequisites = {"nanobots"}
    tech.unit.count = 50
    tech.unit.ingredients = {{"conjuration-research-pack", 1}}
    tech.localised_name = {"technology-name.mystic-explosives"}
    tech.localised_description = {"technology-description.mystic-explosives"}
  end
  
  -- Override nano range technologies
  for i = 1, 4 do
    if data.raw.technology["nano-range-" .. i] then
      local tech = data.raw.technology["nano-range-" .. i]
      -- Update prerequisites
      if i == 1 then
        tech.prerequisites = {"nanobots"}
      else
        tech.prerequisites = {"nano-range-" .. (i-1)}
      end
      tech.unit.count = 20 * math.pow(2, i-1) -- 20, 40, 80, 160
      tech.unit.ingredients = {{"conjuration-research-pack", 1}}
      tech.localised_name = {"technology-name.summoning-range-" .. i}
      tech.localised_description = {"technology-description.summoning-range-" .. i}
    end
  end
  
  -- Override nano speed technologies
  for i = 1, 4 do
    if data.raw.technology["nano-speed-" .. i] then
      local tech = data.raw.technology["nano-speed-" .. i]
      -- Update prerequisites
      if i == 1 then
        tech.prerequisites = {"nanobots"}
      else
        tech.prerequisites = {"nano-speed-" .. (i-1)}
      end
      tech.unit.count = 20 * math.pow(2, i-1) -- 20, 40, 80, 160
      tech.unit.ingredients = {{"conjuration-research-pack", 1}}
      tech.localised_name = {"technology-name.summoning-speed-" .. i}
      tech.localised_description = {"technology-description.summoning-speed-" .. i}
    end
  end
  
  -- Remove roboport interface technology completely
  if data.raw.technology["roboport-interface"] then
    data.raw.technology["roboport-interface"] = nil
  end
  
  -- Override nano gun item
  if data.raw.gun["gun-nano-emitter"] then
    local gun = data.raw.gun["gun-nano-emitter"]
    gun.icon = "__orbs__/graphics/magic-wand.png"
    gun.icon_size = 1024
    gun.localised_name = {"item-name.magic-wand"}
    gun.localised_description = {"item-description.magic-wand"}
  end
  
  -- Override nano gun recipe
  if data.raw.recipe["gun-nano-emitter"] then
    local recipe = data.raw.recipe["gun-nano-emitter"]
    recipe.icon = "__orbs__/graphics/magic-wand.png"
    recipe.icon_size = 1024
    recipe.localised_name = {"item-name.magic-wand"}
    recipe.localised_description = {"item-description.magic-wand"}
    -- Update recipe to use magical ingredients
    recipe.ingredients = {
      {type = "item", name = "wood", amount = 1},
      {type = "item", name = "active-magic-shard", amount = 10}
    }
  end
  
  -- Override ammo category
  if data.raw["ammo-category"]["nano-ammo"] then
    local ammo_cat = data.raw["ammo-category"]["nano-ammo"]
    ammo_cat.localised_name = {"ammo-category-name.spirit-ammo"}
    ammo_cat.localised_description = {"ammo-category-description.spirit-ammo"}
  end
  
  -- Update all ammo items to use spirit theming
  local ammo_items = {
    ["ammo-nano-termites"] = "tree-conflagration-essence",
    ["ammo-nano-scrappers"] = "summoning-essence", 
    ["ammo-nano-constructors"] = "summoning-essence",
    ["ammo-nano-deconstructors"] = "summoning-essence"
  }
  
  for old_name, new_name in pairs(ammo_items) do
    if data.raw.ammo[old_name] then
      local ammo = data.raw.ammo[old_name]
      ammo.localised_name = {"item-name." .. new_name}
      ammo.localised_description = {"item-description." .. new_name}
      if old_name == "ammo-nano-termites" then
        ammo.icon = "__orbs__/graphics/tree-conflagration-essence.png"
        ammo.icon_size = 1024
      else
        ammo.icon = "__orbs__/graphics/summoning-essence.png"
        ammo.icon_size = 1024
      end
    end
  end
  
  -- Update ammo recipes to use magical ingredients
  local ammo_recipes = {
    "ammo-nano-termites",
    "ammo-nano-scrappers", 
    "ammo-nano-constructors",
    "ammo-nano-deconstructors"
  }
  
  for _, recipe_name in pairs(ammo_recipes) do
    if data.raw.recipe[recipe_name] then
      local recipe = data.raw.recipe[recipe_name]
      recipe.ingredients = {
        {type = "item", name = "active-magic-shard", amount = 1},
        {type = "item", name = "iron-stick", amount = 1}
      }
      -- Update the localized names for recipes too
      if recipe_name == "ammo-nano-termites" then
        recipe.localised_name = {"item-name.tree-conflagration-essence"}
        recipe.icon = "__orbs__/graphics/tree-conflagration-essence.png"
        recipe.icon_size = 1024
        recipe.localised_description = {"item-description.tree-conflagration-essence"}
      else
        recipe.localised_name = {"item-name.summoning-essence"}
        recipe.icon = "__orbs__/graphics/summoning-essence.png"
        recipe.icon_size = 1024
        recipe.localised_description = {"item-description.summoning-essence"}
      end
    end
  end
  
end

-- Modify red transport belt recipes to require stability
if data.raw.recipe["fast-transport-belt"] then
  data.raw.recipe["fast-transport-belt"].ingredients = {
    {type = "item", name = "transport-belt", amount = 1},
    {type = "fluid", name = "stability", amount = 1}
  }
end

if data.raw.recipe["fast-splitter"] then
  data.raw.recipe["fast-splitter"].ingredients = {
    {type = "item", name = "splitter", amount = 1},
    {type = "fluid", name = "stability", amount = 1}
  }
end

if data.raw.recipe["fast-underground-belt"] then
  data.raw.recipe["fast-underground-belt"].ingredients = {
    {type = "item", name = "underground-belt", amount = 1},
    {type = "fluid", name = "stability", amount = 1}
  }
end

-- Modify logistics-2 technology to require stability extraction
if data.raw.technology["logistics-2"] then
  local tech = data.raw.technology["logistics-2"]
  tech.prerequisites = {"logistics", "stability-extraction"}
  tech.unit = {
    count = 20,
    ingredients = {
      {"conjuration-research-pack", 1},
      {"divination-research-pack", 1}
    },
    time = 30
  }
end

-- Modify assembling machine 1 to require water fuel through pipes
if data.raw["assembling-machine"]["assembling-machine-1"] then
  local assembler_1 = data.raw["assembling-machine"]["assembling-machine-1"]
  assembler_1.energy_usage = "100W"
  assembler_1.energy_source = {
    type = "fluid",
    effectivity = 1,
    burns_fluid = true,
    scale_fluid_usage = true,
    fluid_box = {
      production_type = "input",
      pipe_connections = {
        {
          flow_direction = "input",
          direction = defines.direction.north,
          position = {0, -1}
        }
      },
      volume = 1000,
      filter = "water"
    },
    light_flicker = {
      color = {0.5, 0.5, 1.0},
      minimum_intensity = 0.6,
      maximum_intensity = 0.95
    },
    smoke = {
      {
        name = "smoke",
        deviation = {0.1, 0.1},
        frequency = 5,
        position = {0.0, -0.8},
        starting_vertical_speed = 0.08,
        starting_frame_deviation = 60
      }
    }
  }
end

-- Remove fuel values from wood and coal
if data.raw.item.wood then
  data.raw.item.wood.fuel_value = nil
  data.raw.item.wood.fuel_category = nil
end
if data.raw.item.coal then
  data.raw.item.coal.fuel_value = nil
  data.raw.item.coal.fuel_category = nil
end


-- Modify burner inserter to use water as fluid fuel
if data.raw["inserter"]["burner-inserter"] then
  local burner_inserter = data.raw["inserter"]["burner-inserter"]
  burner_inserter.energy_per_movement = "300W"
  burner_inserter.energy_per_rotation = "300W"
  burner_inserter.energy_source = {
    type = "fluid",
    effectivity = 1,
    burns_fluid = true,
    scale_fluid_usage = true,
    fluid_box = {
      production_type = "input-output",
      pipe_connections = {
        {
          flow_direction = "input-output",
          direction = defines.direction.west,
          position = {-0.1, 0}
        },
        {
          flow_direction = "input-output",
          direction = defines.direction.east,
          position = {0.1, 0}
        }
      },
      volume = 200,
      filter = "water"
    }
  }
end
