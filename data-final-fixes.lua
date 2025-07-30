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

-- Modify assembling machine 1 to require coal fuel
if data.raw["assembling-machine"]["assembling-machine-1"] then
  local assembler_1 = data.raw["assembling-machine"]["assembling-machine-1"]
  assembler_1.energy_usage = "150kW"
  assembler_1.energy_source = {
    type = "burner",
    fuel_categories = {"chemical"},
    effectivity = 1,
    fuel_inventory_size = 1,
    light_flicker = {
      color = {1, 0.5, 0},
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
data:extend({new_burner_inserter, new_burner_inserter_item, magic_inserter, magic_inserter_item, magic_fast_inserter, magic_fast_inserter_item})

-- Update automation science pack to contraption science pack (it's a tool, not item!)
data.raw.tool["automation-science-pack"].localised_name = {"item-name.contraption-science-pack"}
data.raw.tool["automation-science-pack"].icon = "__orbs__/graphics/contraption-science-pack.png"
data.raw.tool["automation-science-pack"].icon_size = 1024
data.raw.tool["automation-science-pack"].icon_mipmaps = nil
data.raw.tool["automation-science-pack"].icons = nil

-- Update automation science pack recipe
data.raw.recipe["automation-science-pack"].localised_name = {"recipe-name.contraption-science-pack"}
data.raw.recipe["automation-science-pack"].ingredients = {
  {type = "item", name = "iron-gear-wheel", amount = 1},
  {type = "item", name = "iron-stick", amount = 2},
  {type = "item", name = "copper-cable", amount = 3}
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

-- Remove steam power and electronics technologies
data.raw.technology["steam-power"] = nil
data.raw.technology["electronics"] = nil

-- Remove or update shortcuts that reference deleted technologies
if data.raw.shortcut["give-copper-wire"] then
  data.raw.shortcut["give-copper-wire"].technology_to_unlock = "metallurgy"
end

-- Update automation-science-pack prerequisites (remove steam-power and electronics)
data.raw.technology["automation-science-pack"].prerequisites = {"metallurgy"}

-- Update metallurgy to depend on fire-science
data.raw.technology["metallurgy"].prerequisites = {"fire-science"}

-- Move copper wire recipe to metallurgy technology
if data.raw.technology["metallurgy"] and data.raw.technology["metallurgy"].effects then
  table.insert(data.raw.technology["metallurgy"].effects, {
    type = "unlock-recipe",
    recipe = "copper-cable"
  })
end

-- Modify fluid handling technology to use contraption science only
if data.raw.technology["fluid-handling"] then
  local tech = data.raw.technology["fluid-handling"]
  tech.prerequisites = {"automation-science-pack"}
  tech.unit = {
    count = 10,
    ingredients = {
      {"automation-science-pack", 1}
    },
    time = 30
  }
  -- Add offshore pump to fluid handling technology
  if not tech.effects then
    tech.effects = {}
  end
  table.insert(tech.effects, {
    type = "unlock-recipe",
    recipe = "offshore-pump"
  })
end

-- Lock stone furnace recipe initially (unlocked by fire science technology)
if data.raw.recipe["stone-furnace"] then
  data.raw.recipe["stone-furnace"].enabled = false
end

-- Lock recipes behind metallurgy technology
if data.raw.recipe["assembling-machine-1"] then
  data.raw.recipe["assembling-machine-1"].enabled = false
end

if data.raw.recipe["transport-belt"] then
  data.raw.recipe["transport-belt"].enabled = false
end

if data.raw.recipe["offshore-pump"] then
  data.raw.recipe["offshore-pump"].enabled = false
end

if data.raw.recipe["lab"] then
  data.raw.recipe["lab"].enabled = false
  data.raw.recipe["lab"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 10},
    {type = "item", name = "iron-stick", amount = 20},
    {type = "item", name = "copper-cable", amount = 8}
  }
end

-- Override splitter recipe to use copper cable instead of electronic circuits
if data.raw.recipe["splitter"] then
  data.raw.recipe["splitter"].ingredients = {
    {type = "item", name = "electronic-circuit", amount = 5},
    {type = "item", name = "iron-plate", amount = 5},
    {type = "item", name = "transport-belt", amount = 4}
  }
  -- Replace electronic-circuit with copper-cable
  for i, ingredient in pairs(data.raw.recipe["splitter"].ingredients) do
    if ingredient.name == "electronic-circuit" then
      data.raw.recipe["splitter"].ingredients[i] = {type = "item", name = "copper-cable", amount = 8}
      break
    end
  end
end

-- Override repair pack recipe to use copper cable instead of electronic circuits
if data.raw.recipe["repair-pack"] then
  data.raw.recipe["repair-pack"].ingredients = {
    {type = "item", name = "electronic-circuit", amount = 2},
    {type = "item", name = "iron-gear-wheel", amount = 2}
  }
  -- Replace electronic-circuit with copper-cable
  for i, ingredient in pairs(data.raw.recipe["repair-pack"].ingredients) do
    if ingredient.name == "electronic-circuit" then
      data.raw.recipe["repair-pack"].ingredients[i] = {type = "item", name = "copper-cable", amount = 4}
      break
    end
  end
end

-- Remove power requirements from all combinators
if data.raw["constant-combinator"]["constant-combinator"] then
  data.raw["constant-combinator"]["constant-combinator"].energy_source = {type = "void"}
  data.raw["constant-combinator"]["constant-combinator"].energy_usage = "0kW"
end

if data.raw["arithmetic-combinator"]["arithmetic-combinator"] then
  data.raw["arithmetic-combinator"]["arithmetic-combinator"].energy_source = {type = "void"}
  data.raw["arithmetic-combinator"]["arithmetic-combinator"].energy_usage = "0kW"
end

if data.raw["decider-combinator"]["decider-combinator"] then
  data.raw["decider-combinator"]["decider-combinator"].energy_source = {type = "void"}
  data.raw["decider-combinator"]["decider-combinator"].energy_usage = "0kW"
end

if data.raw["selector-combinator"]["selector-combinator"] then
  data.raw["selector-combinator"]["selector-combinator"].energy_source = {type = "void"}
  data.raw["selector-combinator"]["selector-combinator"].energy_usage = "0kW"
end

-- Add selector combinator to circuit-network technology and remove advanced-combinators
if data.raw.technology["circuit-network"] then
  if not data.raw.technology["circuit-network"].effects then
    data.raw.technology["circuit-network"].effects = {}
  end
  table.insert(data.raw.technology["circuit-network"].effects, {
    type = "unlock-recipe",
    recipe = "selector-combinator"
  })
end

-- Remove advanced-combinators technology
if data.raw.technology["advanced-combinators"] then
  data.raw.technology["advanced-combinators"] = nil
end


