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
    tech.unit.count = 1
    tech.unit.ingredients = {{"magic-research-pack", 1}}
    tech.localised_name = {"technology-name.summon-machines"}
    tech.localised_description = {"technology-description.summon-machines"}
    
    -- Remove unwanted effects and keep only the magic wand and summoning essence recipes
    local filtered_effects = {}
    if tech.effects then
      for _, effect in pairs(tech.effects) do
        if effect.type == "unlock-recipe" then
          local recipe_name = effect.recipe
          -- Keep only the gun-nano-emitter (magic wand) and summoning essence recipes
          if recipe_name == "gun-nano-emitter" or 
             recipe_name == "ammo-nano-scrappers" or 
             recipe_name == "ammo-nano-constructors" or 
             recipe_name == "ammo-nano-deconstructors" then
            table.insert(filtered_effects, effect)
          end
          -- Remove iron-stick and termite bots recipes
        else
          -- Keep non-recipe effects
          table.insert(filtered_effects, effect)
        end
      end
    end
    tech.effects = filtered_effects
    
    -- Add ghost creation effect (entities leave ghosts when destroyed)
    table.insert(tech.effects, {
      type = "create-ghost-on-entity-death",
      modifier = true
    })
  end

  -- Override nanobots cliff technology
  if data.raw.technology["nanobots-cliff"] then
    local tech = data.raw.technology["nanobots-cliff"]
    tech.icon = "__orbs__/graphics/cliff-explosion.png"
    tech.icon_size = 1024
    tech.prerequisites = {"conjuration-research", "nanobots"}
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
        tech.prerequisites = {"conjuration-research", "nanobots"}
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
        tech.prerequisites = {"conjuration-research", "nanobots"}
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
    gun.icon = "__orbs__/graphics/summoning-wand.png"
    gun.icon_size = 1024
    gun.localised_name = {"item-name.summoning-wand"}
    gun.localised_description = {"item-description.summoning-wand"}
  end

  -- Override nano gun recipe
  if data.raw.recipe["gun-nano-emitter"] then
    local recipe = data.raw.recipe["gun-nano-emitter"]
    recipe.icon = "__orbs__/graphics/summoning-wand.png"
    recipe.icon_size = 1024
    recipe.localised_name = {"item-name.summoning-wand"}
    recipe.localised_description = {"item-description.summoning-wand"}
    -- Update recipe to use magical ingredients
    recipe.ingredients = {
      {type = "item", name = "stick", amount = 1},
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
    ["ammo-nano-scrappers"] = "summoning-essence",
    ["ammo-nano-constructors"] = "summoning-essence",
    ["ammo-nano-deconstructors"] = "summoning-essence"
  }

  for old_name, new_name in pairs(ammo_items) do
    if data.raw.ammo[old_name] then
      local ammo = data.raw.ammo[old_name]
      ammo.localised_name = {"item-name." .. new_name}
      ammo.localised_description = {"item-description." .. new_name}
      ammo.icon = "__orbs__/graphics/summoning-essence.png"
      ammo.icon_size = 1024
    end
  end

  -- Update ammo recipes to use magical ingredients
  local ammo_recipes = {
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
      recipe.localised_name = {"item-name.summoning-essence"}
      recipe.icon = "__orbs__/graphics/summoning-essence.png"
      recipe.icon_size = 1024
      recipe.localised_description = {"item-description.summoning-essence"}
    end
  end

end

-- Modify red transport belt recipes to require stability
if data.raw.recipe["fast-transport-belt"] then
  data.raw.recipe["fast-transport-belt"].category = "orbs"
  data.raw.recipe["fast-transport-belt"].ingredients = {
    {type = "item", name = "transport-belt", amount = 1},
    {type = "fluid", name = "stability", amount = 5}
  }
end

if data.raw.recipe["fast-splitter"] then
  data.raw.recipe["fast-splitter"].category = "orbs"
  data.raw.recipe["fast-splitter"].ingredients = {
    {type = "item", name = "splitter", amount = 1},
    {type = "fluid", name = "stability", amount = 20}
  }
end

if data.raw.recipe["fast-underground-belt"] then
  data.raw.recipe["fast-underground-belt"].category = "orbs"
  data.raw.recipe["fast-underground-belt"].ingredients = {
    {type = "item", name = "underground-belt", amount = 1},
    {type = "fluid", name = "stability", amount = 20}
  }
end

-- Modify logistics-2 technology to require stability extraction
if data.raw.technology["logistics-2"] then
  local tech = data.raw.technology["logistics-2"]
  tech.prerequisites = {"logistics", "stability-extraction"}
  tech.unit = {
    count = 20,
    ingredients = {
      {"automation-science-pack", 3},
      {"divination-research-pack", 1}
    },
    time = 30
  }
end

-- Modify assembling machine 1 to use steam fuel
if data.raw["assembling-machine"]["assembling-machine-1"] then
  local assembler_1 = data.raw["assembling-machine"]["assembling-machine-1"]
  assembler_1.energy_usage = "200kW"
  assembler_1.energy_source = {
    type = "fluid",
    fluid_box = {
      production_type = "input-output",
      volume = 100,
      pipe_connections = {
        {flow_direction="input-output", direction = defines.direction.west, position = {-1, 0}},
        {flow_direction="input-output", direction = defines.direction.east, position = {1, 0}}
      },
      pipe_picture = data.raw["assembling-machine"]["assembling-machine-2"] and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes[1] and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes[1].pipe_picture,
      pipe_covers = data.raw["assembling-machine"]["assembling-machine-2"] and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes[1] and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes[1].pipe_covers,
      filter = "steam"
    },
    effectivity = 1,
    burns_fluid = true,
    scale_fluid_usage = true
  }
  assembler_1.energy_source.emissions_per_minute = {pollution = 10}
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
-- Copy speed stats from fast inserter but keep same energy as wooden inserter
if data.raw["inserter"]["fast-inserter"] then
  new_burner_inserter.extension_speed = data.raw["inserter"]["fast-inserter"].extension_speed
  new_burner_inserter.rotation_speed = data.raw["inserter"]["fast-inserter"].rotation_speed
end
-- in-game 8kW corresponds to 786W somehow
new_burner_inserter.energy_per_movement = "8kW"
new_burner_inserter.energy_per_rotation = "8kW"
new_burner_inserter.energy_source = {
  type = "burner",
  fuel_categories = {"chemical"},
  initial_fuel = "smoldering-remains",
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
    initial_fuel = "smoldering-remains",
    initial_fuel_percent = 0.1,
    effectivity = 0.5,
    fuel_inventory_size = 1
  }
end

-- Update long-handed inserter to be a burner inserter
if data.raw["inserter"]["long-handed-inserter"] then
  local long_inserter = data.raw["inserter"]["long-handed-inserter"]
  -- Copy rotation speed from fast inserter
  if data.raw["inserter"]["fast-inserter"] then
    long_inserter.rotation_speed = data.raw["inserter"]["fast-inserter"].rotation_speed
  end
  -- Half fuel consumption compared to fast inserter
  long_inserter.energy_per_movement = "8kW"
  long_inserter.energy_per_rotation = "8kW"
  long_inserter.energy_source = {
    type = "burner",
    fuel_categories = {"chemical"},
    initial_fuel = "smoldering-remains",
    initial_fuel_percent = 0.1,
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


-- Create magic inserter from fast inserter
local magic_inserter = table.deepcopy(data.raw["inserter"]["fast-inserter"])
magic_inserter.name = "magic-inserter"
magic_inserter.localised_name = {"entity-name.magic-inserter"}
magic_inserter.minable.result = "magic-inserter"
magic_inserter.energy_source = {
  type = "void"
}
magic_inserter.energy_per_movement = "0kW"
magic_inserter.energy_per_rotation = "0kW"

-- Create magic inserter item
local magic_inserter_item = table.deepcopy(data.raw.item["fast-inserter"])
magic_inserter_item.name = "magic-inserter"
magic_inserter_item.localised_name = {"item-name.magic-inserter"}
magic_inserter_item.place_result = "magic-inserter"
magic_inserter_item.hidden = nil

-- Create magic long handed inserter from long handed inserter
local magic_long_inserter = table.deepcopy(data.raw["inserter"]["long-handed-inserter"])
magic_long_inserter.name = "magic-long-handed-inserter"
magic_long_inserter.localised_name = {"entity-name.magic-long-handed-inserter"}
magic_long_inserter.minable.result = "magic-long-handed-inserter"
magic_long_inserter.energy_source = {
  type = "void"
}
magic_long_inserter.energy_per_movement = "0kW"
magic_long_inserter.energy_per_rotation = "0kW"

-- Create magic long handed inserter item
local magic_long_inserter_item = table.deepcopy(data.raw.item["long-handed-inserter"])
magic_long_inserter_item.name = "magic-long-handed-inserter"
magic_long_inserter_item.localised_name = {"item-name.magic-long-handed-inserter"}
magic_long_inserter_item.place_result = "magic-long-handed-inserter"
magic_long_inserter_item.hidden = nil

-- Add new inserters to data
data:extend({new_burner_inserter, new_burner_inserter_item, magic_inserter, magic_inserter_item, magic_long_inserter, magic_long_inserter_item})

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

  -- Remove all barreling recipes except water and stability
  if tech.effects then
    for i = #tech.effects, 1, -1 do
      local effect = tech.effects[i]
      if effect.type == "unlock-recipe" then
        local recipe_name = effect.recipe
        -- Keep only water and stability barreling/unbarreling recipes
        if recipe_name and (
          string.find(recipe_name, "barrel") and
          not string.find(recipe_name, "water") and
          not string.find(recipe_name, "stability")
        ) then
          table.remove(tech.effects, i)
        end
      end
    end
  end
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
  data.raw.recipe["lab"].localised_name = {"recipe-name.alchemy-research-laboratory"}
  data.raw.recipe["lab"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 10},
    {type = "item", name = "iron-stick", amount = 20},
    {type = "item", name = "copper-cable", amount = 8}
  }
end

-- Override lab item name
if data.raw.item["lab"] then
  data.raw.item["lab"].localised_name = {"item-name.alchemy-research-laboratory"}
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

-- Modify combinator recipes to use mechanical components
if data.raw.recipe["constant-combinator"] then
  data.raw.recipe["constant-combinator"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 3},
    {type = "item", name = "iron-plate", amount = 1},
  }
end

if data.raw.recipe["arithmetic-combinator"] then
  data.raw.recipe["arithmetic-combinator"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 10},
    {type = "item", name = "iron-plate", amount = 2}
  }
end

if data.raw.recipe["decider-combinator"] then
  data.raw.recipe["decider-combinator"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 10},
    {type = "item", name = "iron-plate", amount = 2}
  }
end

if data.raw.recipe["selector-combinator"] then
  data.raw.recipe["selector-combinator"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 20},
    {type = "item", name = "iron-plate", amount = 2}
  }
end

-- Update combinator entities and names
if data.raw["constant-combinator"]["constant-combinator"] then
  local entity = data.raw["constant-combinator"]["constant-combinator"]
  entity.energy_source = {type = "void"}
  entity.energy_usage = "0kW"
  entity.localised_name = {"entity-name.constant-signal-generator"}

  if data.raw.item["constant-combinator"] then
    data.raw.item["constant-combinator"].localised_name = {"item-name.constant-signal-generator"}
  end
end

if data.raw["arithmetic-combinator"]["arithmetic-combinator"] then
  local entity = data.raw["arithmetic-combinator"]["arithmetic-combinator"]
  entity.energy_source = {type = "void"}
  entity.energy_usage = "0kW"
  entity.localised_name = {"entity-name.analytical-engine"}

  if data.raw.item["arithmetic-combinator"] then
    data.raw.item["arithmetic-combinator"].localised_name = {"item-name.analytical-engine"}
  end
end

if data.raw["decider-combinator"]["decider-combinator"] then
  local entity = data.raw["decider-combinator"]["decider-combinator"]
  entity.energy_source = {type = "void"}
  entity.energy_usage = "0kW"
  entity.localised_name = {"entity-name.decider-engine"}

  if data.raw.item["decider-combinator"] then
    data.raw.item["decider-combinator"].localised_name = {"item-name.decider-engine"}
  end
end

if data.raw["selector-combinator"]["selector-combinator"] then
  local entity = data.raw["selector-combinator"]["selector-combinator"]
  entity.energy_source = {type = "void"}
  entity.energy_usage = "0kW"
  entity.localised_name = {"entity-name.selector-engine"}

  if data.raw.item["selector-combinator"] then
    data.raw.item["selector-combinator"].localised_name = {"item-name.selector-engine"}
  end
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

-- Update bulk inserter technology
if data.raw.technology["bulk-inserter"] then
  data.raw.technology["bulk-inserter"].prerequisites = {"rune-words", "magic-inserters"}
  data.raw.technology["bulk-inserter"].unit = {
    count = 20,
    ingredients = {
      {"automation-science-pack", 5},
      {"rune-research-pack", 1}
    },
    time = 30
  }
end

-- Update bulk inserter recipe
if data.raw.recipe["bulk-inserter"] then
  data.raw.recipe["bulk-inserter"].category = "crafting-with-fluid"
  data.raw.recipe["bulk-inserter"].ingredients = {
    {type = "item", name = "magic-inserter", amount = 1},
    {type = "item", name = "iron-gear-wheel", amount = 10},
    {type = "item", name = "rune-word-terra", amount = 1},
    {type = "fluid", name = "stability", amount = 25}
  }
end

-- Make bulk inserter require no power
if data.raw["inserter"]["bulk-inserter"] then
  data.raw["inserter"]["bulk-inserter"].energy_source = {type = "void"}
  data.raw["inserter"]["bulk-inserter"].energy_per_movement = "0kW"
  data.raw["inserter"]["bulk-inserter"].energy_per_rotation = "0kW"
end

-- Modify burner mining drill to have 4x4 mining area
if data.raw["mining-drill"]["burner-mining-drill"] then
  data.raw["mining-drill"]["burner-mining-drill"].resource_searching_radius = 1.99
end

-- Set steam fuel value to 30kJ
if data.raw.fluid.steam then
  data.raw.fluid.steam.fuel_value = "30kJ"
end

-- Modify pump to use chemical fuel and update recipe
if data.raw.pump.pump then
  data.raw.pump.pump.energy_source = {
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
        frequency = 5
      }
    }
  }
end

-- Update pump recipe
if data.raw.recipe.pump then
  data.raw.recipe.pump.ingredients = {
    {type = "item", name = "pipe", amount = 2},
    {type = "item", name = "iron-plate", amount = 4},
    {type = "item", name = "iron-gear-wheel", amount = 4},
    {type = "item", name = "stone-furnace", amount = 1}
  }
end

-- Modify offshore pump to use chemical fuel
if data.raw["offshore-pump"]["offshore-pump"] then
  data.raw["offshore-pump"]["offshore-pump"].energy_source = {
    type = "burner",
    fuel_categories = {"chemical"},
    effectivity = 1,
    fuel_inventory_size = 1,
    burnt_inventory_size = 1,
    fuel_inventory_offset = {0, -1},
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
  data.raw["offshore-pump"]["offshore-pump"].energy_usage = "300kW"
end

-- Update offshore pump recipe
if data.raw.recipe["offshore-pump"] then
  data.raw.recipe["offshore-pump"].ingredients = {
    {type = "item", name = "iron-plate", amount = 3},
    {type = "item", name = "iron-gear-wheel", amount = 4},
    {type = "item", name = "pipe", amount = 3},
    {type = "item", name = "stone-furnace", amount = 1}
  }
end

-- Modify lamp recipe and entity
if data.raw.recipe["small-lamp"] then
  data.raw.recipe["small-lamp"].ingredients = {
    {type = "item", name = "copper-cable", amount = 3},
    {type = "item", name = "iron-plate", amount = 1},
    {type = "item", name = "magic-orb", amount = 1}
  }
end

if data.raw.lamp["small-lamp"] then
  data.raw.lamp["small-lamp"].energy_source = {type = "void"}
  data.raw.lamp["small-lamp"].energy_usage = "0kW"
end

-- Update lamp technology to use conjuration research packs
if data.raw.technology["lamp"] then
  data.raw.technology["lamp"].prerequisites = {"conjuration-research", "metallurgy"}
  data.raw.technology["lamp"].unit = {
    count = 5,
    ingredients = {
      {"conjuration-research-pack", 1}
    },
    time = 30
  }
end

-- Modify speaker recipe
if data.raw.recipe["programmable-speaker"] then
  data.raw.recipe["programmable-speaker"].ingredients = {
    {type = "item", name = "iron-stick", amount = 1},
    {type = "item", name = "iron-gear-wheel", amount = 5},
    {type = "item", name = "iron-plate", amount = 2}
  }
end

-- Modify display panel recipe
if data.raw.recipe["display-panel"] then
  data.raw.recipe["display-panel"].ingredients = {
    {type = "item", name = "copper-plate", amount = 1}
  }
end

-- Modify storage tank recipe
if data.raw.recipe["storage-tank"] then
  data.raw.recipe["storage-tank"].ingredients = {
    {type = "item", name = "iron-plate", amount = 50},
    {type = "item", name = "iron-stick", amount = 10}
  }
end

-- Override heating tower recipe to use stone bricks, boiler, and heat pipes
if data.raw.recipe["heating-tower"] then
  data.raw.recipe["heating-tower"].ingredients = {
    {type = "item", name = "stone-brick", amount = 10},
    {type = "item", name = "boiler", amount = 1},
    {type = "item", name = "heat-pipe", amount = 5}
  }
end

-- Override heat pipes recipe to use pipe and copper
if data.raw.recipe["heat-pipe"] then
  data.raw.recipe["heat-pipe"].ingredients = {
    {type = "item", name = "pipe", amount = 1},
    {type = "item", name = "copper-plate", amount = 1}
  }
end

-- Override pistol to become starter wand
if data.raw.gun["pistol"] then
  local pistol = data.raw.gun["pistol"]
  pistol.icon = "__orbs__/graphics/starter-wand.png"
  pistol.icon_size = 1024
  pistol.localised_name = {"item-name.starter-wand"}
  pistol.localised_description = {"item-description.starter-wand"}
  -- Update ammo category to only accept channeled-mana
  pistol.attack_parameters.ammo_categories = {"channeled-mana"}
end

-- Override pistol recipe to use wooden stick and 10s craft time
if data.raw.recipe["pistol"] then
  local recipe = data.raw.recipe["pistol"]
  recipe.energy_required = 10
  recipe.ingredients = {
    {type = "item", name = "stick", amount = 1}
  }
  recipe.enabled = true
  recipe.hidden = false
end

-- Replace firearm magazine with channeled-mana
if data.raw.ammo["firearm-magazine"] then
  local firearm_mag = data.raw.ammo["firearm-magazine"]
  firearm_mag.icon = "__orbs__/graphics/channeled-mana.png"
  firearm_mag.icon_size = 1024
  firearm_mag.localised_name = {"item-name.channeled-mana"}
  firearm_mag.localised_description = {"item-description.channeled-mana"}
  firearm_mag.ammo_category = "channeled-mana"
  firearm_mag.spoil_ticks = 30 * 60 * 60 -- 30 minutes
  firearm_mag.spoil_result = nil
  firearm_mag.ammo_type = {
    category = "channeled-mana",
    action = {
      {
        type = "direct",
        action_delivery = {
          {
            type = "instant",
            source_effects = {
              {
                type = "create-explosion",
                entity_name = "laser-bubble",
                only_when_visible = true
              }
            },
            target_effects = {
              {
                type = "create-entity",
                entity_name = "purple-magical-splash",
                offsets = {{0, 0}},
                offset_deviation = {{-0.3, -0.3}, {0.3, 0.3}},
                only_when_visible = true
              },
              {
                type = "damage",
                damage = {amount = 5, type = "physical"}
              }
            }
          }
        }
      }
    }
  }
end

-- Hide base game firearm magazine recipe (the one that takes iron plates)
if data.raw.recipe["firearm-magazine"] then
  data.raw.recipe["firearm-magazine"].enabled = false
  data.raw.recipe["firearm-magazine"].hidden = true
end

-- Override freeplay starting items to remove pistol and ammo
if data.raw.scenario and data.raw.scenario["freeplay"] then
  -- Override the starting items for freeplay scenario
  data.raw.scenario["freeplay"].starting_items = {
    ["iron-plate"] = 8,
    ["wood"] = 1,
    ["burner-mining-drill"] = 1,
    ["stone-furnace"] = 1
  }
end

-- Reorder intermediate product recipes for better crafting menu organization
-- Row 1: stick, fire through friction, light wood, light coal
-- Row 2: iron plate, copper plate, sand  
-- Row 3: iron gear wheel, iron stick, copper cable
-- Row 4: contraption research, magic research, conjuration research, divination research, rune research

-- Base game intermediate products
if data.raw.recipe["iron-plate"] then
  data.raw.recipe["iron-plate"].subgroup = "intermediate-product"
  data.raw.recipe["iron-plate"].order = "b[plates]-a[iron-plate]"
end

if data.raw.recipe["copper-plate"] then
  data.raw.recipe["copper-plate"].subgroup = "intermediate-product"
  data.raw.recipe["copper-plate"].order = "b[plates]-b[copper-plate]"
end

if data.raw.recipe["iron-gear-wheel"] then
  data.raw.recipe["iron-gear-wheel"].subgroup = "intermediate-product"
  data.raw.recipe["iron-gear-wheel"].order = "c[components]-a[iron-gear-wheel]"
end

if data.raw.recipe["iron-stick"] then
  data.raw.recipe["iron-stick"].subgroup = "intermediate-product"
  data.raw.recipe["iron-stick"].order = "c[components]-b[iron-stick]"
end

if data.raw.recipe["copper-cable"] then
  data.raw.recipe["copper-cable"].subgroup = "intermediate-product"
  data.raw.recipe["copper-cable"].order = "c[components]-c[copper-cable]"
end

-- Sand recipe (if it exists)
if data.raw.recipe["stone-to-sand"] then
  data.raw.recipe["stone-to-sand"].subgroup = "intermediate-product"  
  data.raw.recipe["stone-to-sand"].order = "b[plates]-c[sand]"
end

-- Automation science pack (contraption research pack)
if data.raw.recipe["automation-science-pack"] then
  data.raw.recipe["automation-science-pack"].subgroup = "intermediate-product"
  data.raw.recipe["automation-science-pack"].order = "d[research]-a[contraption-research-pack]"
end

-- Finally, as a last step, remove all the content we don't want
require("removals")
