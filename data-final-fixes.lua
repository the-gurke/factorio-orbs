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
  assembler_1.energy_usage = "1kW"
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


-- Create wooden inserter from burner inserter prototype
local wooden_inserter = table.deepcopy(data.raw["inserter"]["burner-inserter"])
wooden_inserter.name = "wooden-inserter"
wooden_inserter.localised_name = {"item-name.wooden-inserter"}
wooden_inserter.energy_per_movement = "4kW"
wooden_inserter.energy_per_rotation = "4kW"

-- Add brownish tint to the wooden inserter
if wooden_inserter.hand_base_picture then
  wooden_inserter.hand_base_picture.tint = {r = 0.7, g = 0.4, b = 0.2, a = 1}
end
if wooden_inserter.hand_open_picture then
  wooden_inserter.hand_open_picture.tint = {r = 0.7, g = 0.4, b = 0.2, a = 1}
end
if wooden_inserter.hand_closed_picture then
  wooden_inserter.hand_closed_picture.tint = {r = 0.7, g = 0.4, b = 0.2, a = 1}
end
if wooden_inserter.platform_picture then
  wooden_inserter.platform_picture.tint = {r = 0.7, g = 0.4, b = 0.2, a = 1}
end

-- Set wooden inserter to use water as fluid fuel
wooden_inserter.energy_source = {
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

-- Create wooden inserter item
local wooden_inserter_item = table.deepcopy(data.raw.item["burner-inserter"])
wooden_inserter_item.name = "wooden-inserter"
wooden_inserter_item.localised_name = {"item-name.wooden-inserter"}
wooden_inserter_item.place_result = "wooden-inserter"
-- Add brownish tint to the item icon
if not wooden_inserter_item.icons then
  wooden_inserter_item.icons = {
    {
      icon = wooden_inserter_item.icon,
      icon_size = wooden_inserter_item.icon_size or 64,
      tint = {r = 0.7, g = 0.4, b = 0.2, a = 1}
    }
  }
  wooden_inserter_item.icon = nil
  wooden_inserter_item.icon_size = nil
end

-- Create new burner inserter from burner inserter prototype with normal inserter speed
local new_burner_inserter = table.deepcopy(data.raw["inserter"]["burner-inserter"])
new_burner_inserter.name = "burner-inserter"
new_burner_inserter.localised_name = {"item-name.burner-inserter"}
-- Copy speed stats from normal inserter but keep same energy as wooden inserter
if data.raw["inserter"]["inserter"] then
  new_burner_inserter.extension_speed = data.raw["inserter"]["inserter"].extension_speed
  new_burner_inserter.rotation_speed = data.raw["inserter"]["inserter"].rotation_speed
end
-- in-game 8kW corresponds to 786W somehow
new_burner_inserter.energy_per_movement = "8kW"
new_burner_inserter.energy_per_rotation = "8kW"
new_burner_inserter.energy_source = {
  type = "burner",
  fuel_categories = {"chemical"},
  initial_fuel = "glimming-remains",
  initial_fuel_percent = 0.1,
  effectivity = 0.5,
  fuel_inventory_size = 1,
  light_flicker = {color = {0,0,0}},
  smoke = {
    {
      name = "smoke",
      deviation = {0.1, 0.1},
      frequency = 9
    }
  }
}

-- Create new burner inserter item
local new_burner_inserter_item = table.deepcopy(data.raw.item["burner-inserter"])
new_burner_inserter_item.name = "burner-inserter"
new_burner_inserter_item.localised_name = {"item-name.burner-inserter"}
new_burner_inserter_item.place_result = "burner-inserter"

-- Update fast inserter to use double fuel consumption
if data.raw["inserter"]["fast-inserter"] then
  local fast_inserter = data.raw["inserter"]["fast-inserter"]
  fast_inserter.energy_per_movement = "16kW"
  fast_inserter.energy_per_rotation = "16kW"
  fast_inserter.energy_source = {
    type = "burner",
    fuel_categories = {"chemical"},
    initial_fuel = "glimming-remains",
    initial_fuel_percent = 0.1,
    effectivity = 0.5,
    fuel_inventory_size = 1
  }
end

-- Update long-handed inserter to be a burner inserter
if data.raw["inserter"]["long-handed-inserter"] then
  local long_inserter = data.raw["inserter"]["long-handed-inserter"]
  long_inserter.energy_source = {
    type = "burner",
    fuel_categories = {"chemical"},
    effectivity = 0.5,
    fuel_inventory_size = 1
  }
end

-- Clear all next_upgrade references that point to inserter before hiding it
for _, prototype_type in pairs({"inserter", "loader-1x1"}) do
  if data.raw[prototype_type] then
    for _, entity in pairs(data.raw[prototype_type]) do
      if entity.next_upgrade == "inserter" then
        entity.next_upgrade = nil
      end
    end
  end
end

-- Clear next_upgrade on the inserter itself and hide it
if data.raw["inserter"]["inserter"] then
  data.raw["inserter"]["inserter"].next_upgrade = nil
end
if data.raw.recipe["inserter"] then
  data.raw.recipe["inserter"].enabled = false
  data.raw.recipe["inserter"].hidden = true
end
if data.raw.item["inserter"] then
  data.raw.item["inserter"].hidden = true
end

-- Set burner inserter to upgrade to fast inserter
new_burner_inserter.next_upgrade = "fast-inserter"

-- Override the original burner-inserter recipe
if data.raw.recipe["burner-inserter"] then
  data.raw.recipe["burner-inserter"].ingredients = {
    {type = "item", name = "iron-stick", amount = 2},
    {type = "item", name = "iron-gear-wheel", amount = 1}
  }
  data.raw.recipe["burner-inserter"].enabled = false
end

-- Remove the original burner-inserter entity to avoid conflicts
data.raw["inserter"]["burner-inserter"] = nil
data.raw.item["burner-inserter"] = nil


-- Create magic inserter from regular inserter
local magic_inserter = table.deepcopy(data.raw["inserter"]["inserter"])
magic_inserter.name = "magic-inserter"
magic_inserter.localised_name = {"entity-name.magic-inserter"}
magic_inserter.minable.result = "magic-inserter"
magic_inserter.energy_source = {
  type = "void"
}
magic_inserter.energy_per_movement = "0kW"
magic_inserter.energy_per_rotation = "0kW"
magic_inserter.next_upgrade = "magic-fast-inserter"

-- Create magic inserter item
local magic_inserter_item = table.deepcopy(data.raw.item["inserter"])
magic_inserter_item.name = "magic-inserter"
magic_inserter_item.localised_name = {"item-name.magic-inserter"}
magic_inserter_item.place_result = "magic-inserter"
magic_inserter_item.hidden = nil

-- Create magic fast inserter from fast inserter
local magic_fast_inserter = table.deepcopy(data.raw["inserter"]["fast-inserter"])
magic_fast_inserter.name = "magic-fast-inserter"
magic_fast_inserter.localised_name = {"entity-name.magic-fast-inserter"}
magic_fast_inserter.minable.result = "magic-fast-inserter"
magic_fast_inserter.energy_source = {
  type = "void"
}
magic_fast_inserter.energy_per_movement = "0kW"
magic_fast_inserter.energy_per_rotation = "0kW"

-- Create magic fast inserter item
local magic_fast_inserter_item = table.deepcopy(data.raw.item["fast-inserter"])
magic_fast_inserter_item.name = "magic-fast-inserter"
magic_fast_inserter_item.localised_name = {"item-name.magic-fast-inserter"}
magic_fast_inserter_item.place_result = "magic-fast-inserter"
magic_fast_inserter_item.hidden = nil

-- Add new inserters to data
data:extend({wooden_inserter, wooden_inserter_item, new_burner_inserter, new_burner_inserter_item, magic_inserter, magic_inserter_item, magic_fast_inserter, magic_fast_inserter_item})

-- Update automation science pack to contraption science pack (it's a tool, not item!)
data.raw.tool["automation-science-pack"].localised_name = {"item-name.contraption-science-pack"}
data.raw.tool["automation-science-pack"].icon = "__orbs__/graphics/contraption-science-pack.png"
data.raw.tool["automation-science-pack"].icon_size = 1024
data.raw.tool["automation-science-pack"].icon_mipmaps = nil
data.raw.tool["automation-science-pack"].icons = nil

-- Update automation science pack recipe
data.raw.recipe["automation-science-pack"].localised_name = {"recipe-name.contraption-science-pack"}
data.raw.recipe["automation-science-pack"].ingredients = {
  {type = "item", name = "wooden-gear-wheel", amount = 1},
  {type = "item", name = "iron-stick", amount = 2},
  {type = "item", name = "copper-cable", amount = 1}
}
data.raw.recipe["automation-science-pack"].icon = "__orbs__/graphics/contraption-science-pack.png"
data.raw.recipe["automation-science-pack"].icon_size = 1024
data.raw.recipe["automation-science-pack"].icon_mipmaps = nil
data.raw.recipe["automation-science-pack"].icons = nil

-- Update automation-science-pack technology (the one that unlocks automation science pack)
data.raw.technology["automation-science-pack"].localised_name = {"technology-name.contraption-science"}
data.raw.technology["automation-science-pack"].icon = "__orbs__/graphics/contraption-science-pack.png"
data.raw.technology["automation-science-pack"].icon_size = 1024
data.raw.technology["automation-science-pack"].icon_mipmaps = nil
data.raw.technology["automation-science-pack"].icons = nil


