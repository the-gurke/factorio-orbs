-- data-final-fixes.lua
-- Late-stage modifications to base game and other mods

-- Modify red transport belt recipes to require stability
if data.raw.recipe["fast-transport-belt"] then
  data.raw.recipe["fast-transport-belt"].category = "crafting-with-fluid"
  data.raw.recipe["fast-transport-belt"].ingredients = {
    {type = "item", name = "transport-belt", amount = 1},
    {type = "fluid", name = "stability", amount = 5}
  }
end

if data.raw.recipe["fast-splitter"] then
  data.raw.recipe["fast-splitter"].category = "crafting-with-fluid"
  data.raw.recipe["fast-splitter"].ingredients = {
    {type = "item", name = "splitter", amount = 1},
    {type = "fluid", name = "stability", amount = 20}
  }
end

if data.raw.recipe["fast-underground-belt"] then
  data.raw.recipe["fast-underground-belt"].category = "crafting-with-fluid"
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

-- Modify assembling machine 1 to use steam fuel and accept fluids in recipes
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

  -- Add fluid boxes for recipe ingredients (copy from assembling-machine-2)
  if data.raw["assembling-machine"]["assembling-machine-2"] and data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes then
    assembler_1.fluid_boxes = table.deepcopy(data.raw["assembling-machine"]["assembling-machine-2"].fluid_boxes)
    -- Update crafting categories to include crafting-with-fluid
    assembler_1.crafting_categories = assembler_1.crafting_categories or {"basic-crafting"}
    table.insert(assembler_1.crafting_categories, "crafting-with-fluid")
  end
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

-- Remove fuel value from spoilage
if data.raw.item.spoilage then
  data.raw.item.spoilage.fuel_value = nil
  data.raw.item.spoilage.fuel_category = nil
  data.raw.item.spoilage.fuel_acceleration_multiplier = nil
  data.raw.item.spoilage.fuel_top_speed_multiplier = nil
  data.raw.item.spoilage.fuel_emissions_multiplier = nil
  data.raw.item.spoilage.fuel_glow_color = nil
end

-- Modify fish to be a throwable weapon instead of healing
if data.raw.capsule["raw-fish"] then
  local fish = data.raw.capsule["raw-fish"]

  -- Remove healing action and make it a throwable weapon
  fish.capsule_action = {
    type = "throw",
    attack_parameters = {
      type = "projectile",
      activation_type = "throw",
      ammo_category = "grenade",
      cooldown = 30,
      projectile_creation_distance = 0.6,
      range = 20,
      ammo_type = {
        target_type = "position",
        action = {
          {
            type = "direct",
            action_delivery = {
              type = "projectile",
              projectile = "fish-projectile",
              starting_speed = 1.3
            }
          }
        }
      }
    }
  }
end

-- Create fish projectile (based on grenade but without explosion graphics)
data:extend({
  {
    type = "projectile",
    name = "fish-projectile",
    flags = {"not-on-map"},
    acceleration = 0.005,
    turn_speed = 0.01,
    action = {
      {
        type = "direct",
        action_delivery = {
          type = "instant",
          target_effects = {
            {
              type = "damage",
              damage = {amount = 3, type = "physical"}
            }
          }
        }
      },
      {
        type = "area",
        radius = 1,
        action_delivery = {
          type = "instant",
          target_effects = {
            {
              type = "damage",
              damage = {amount = 3, type = "physical"}
            }
          }
        }
      }
    },
    animation = {
      filename = "__base__/graphics/icons/fish.png",
      frame_count = 1,
      width = 32,
      height = 32,
      priority = "high"
    },
    shadow = {
      filename = "__base__/graphics/icons/fish.png",
      frame_count = 1,
      width = 32,
      height = 32,
      priority = "high",
      draw_as_shadow = true
    }
  }
})

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
  -- Add gray tint to the entity
  local gray_tint = {r = 0.2, g = 0.2, b = 0.2}
  long_inserter.platform_picture.sheet.tint = gray_tint
  if long_inserter.platform_picture.sheet.hr_version then
    long_inserter.platform_picture.sheet.hr_version.tint = gray_tint
  end
  long_inserter.hand_base_picture.tint = gray_tint
  if long_inserter.hand_base_picture.hr_version then
    long_inserter.hand_base_picture.hr_version.tint = gray_tint
  end
  long_inserter.hand_open_picture.tint = gray_tint
  if long_inserter.hand_open_picture.hr_version then
    long_inserter.hand_open_picture.hr_version.tint = gray_tint
  end
  long_inserter.hand_closed_picture.tint = gray_tint
  if long_inserter.hand_closed_picture.hr_version then
    long_inserter.hand_closed_picture.hr_version.tint = gray_tint
  end
end

-- Update long-handed inserter item icon to use stack inserter with gray tint
if data.raw.item["long-handed-inserter"] then
  data.raw.item["long-handed-inserter"].icons = {
    {
      icon = "__space-age__/graphics/icons/stack-inserter.png",
      icon_size = 64,
      tint = {r = 0.2, g = 0.2, b = 0.2, a = 0.8}
    }
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
-- Add pink tint to make it distinct
local pink_tint = {r = 1.0, g = 0.1, b = 0.3}
magic_inserter.platform_picture.sheet.tint = pink_tint
if magic_inserter.platform_picture.sheet.hr_version then
  magic_inserter.platform_picture.sheet.hr_version.tint = pink_tint
end
magic_inserter.hand_base_picture.tint = pink_tint
if magic_inserter.hand_base_picture.hr_version then
  magic_inserter.hand_base_picture.hr_version.tint = pink_tint
end
magic_inserter.hand_open_picture.tint = pink_tint
if magic_inserter.hand_open_picture.hr_version then
  magic_inserter.hand_open_picture.hr_version.tint = pink_tint
end
magic_inserter.hand_closed_picture.tint = pink_tint
if magic_inserter.hand_closed_picture.hr_version then
  magic_inserter.hand_closed_picture.hr_version.tint = pink_tint
end

-- Create magic inserter item
local magic_inserter_item = table.deepcopy(data.raw.item["fast-inserter"])
magic_inserter_item.name = "magic-inserter"
magic_inserter_item.localised_name = {"item-name.magic-inserter"}
magic_inserter_item.place_result = "magic-inserter"
magic_inserter_item.hidden = nil
-- Use stack inserter icon from Space Age with pink tint
magic_inserter_item.icons = {
  {
    icon = "__space-age__/graphics/icons/stack-inserter.png",
    icon_size = 64,
    tint = {r = 1.0, g = 0.3, b = 1.0, a = 0.8}
  }
}

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
local purple_tint = {r = 0.4, g = 0.3, b = 0.9}
magic_long_inserter.platform_picture.sheet.tint = purple_tint
if magic_long_inserter.platform_picture.sheet.hr_version then
  magic_long_inserter.platform_picture.sheet.hr_version.tint = purple_tint
end
magic_long_inserter.hand_base_picture.tint = purple_tint
if magic_long_inserter.hand_base_picture.hr_version then
  magic_long_inserter.hand_base_picture.hr_version.tint = purple_tint
end
magic_long_inserter.hand_open_picture.tint = purple_tint
if magic_long_inserter.hand_open_picture.hr_version then
  magic_long_inserter.hand_open_picture.hr_version.tint = purple_tint
end
magic_long_inserter.hand_closed_picture.tint = purple_tint
if magic_long_inserter.hand_closed_picture.hr_version then
  magic_long_inserter.hand_closed_picture.hr_version.tint = purple_tint
end

-- Create magic long handed inserter item
local magic_long_inserter_item = table.deepcopy(data.raw.item["long-handed-inserter"])
magic_long_inserter_item.name = "magic-long-handed-inserter"
magic_long_inserter_item.localised_name = {"item-name.magic-long-handed-inserter"}
magic_long_inserter_item.place_result = "magic-long-handed-inserter"
magic_long_inserter_item.hidden = nil
-- Use stack inserter icon from Space Age (white) with blue tint
magic_long_inserter_item.icons = {
  {
    icon = "__space-age__/graphics/icons/stack-inserter.png",
    icon_size = 64,
    tint = {r = 0.5, g = 0.3, b = 1.0, a = 0.8}
  }
}

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
  data.raw.technology["bulk-inserter"].prerequisites = {"rune-research-packs", "magic-inserters"}
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
  data.raw.recipe["bulk-inserter"].category = "orbs"
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

-- Modify speaker recipe and entity
if data.raw.recipe["programmable-speaker"] then
  data.raw.recipe["programmable-speaker"].ingredients = {
    {type = "item", name = "iron-stick", amount = 1},
    {type = "item", name = "iron-gear-wheel", amount = 5},
    {type = "item", name = "iron-plate", amount = 2}
  }
end

if data.raw["programmable-speaker"]["programmable-speaker"] then
  data.raw["programmable-speaker"]["programmable-speaker"].energy_source = {type = "void"}
  data.raw["programmable-speaker"]["programmable-speaker"].energy_usage = "0kW"
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
  recipe.category = "hand-crafting-and-orbs"
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
                type = "create-entity",
                entity_name = "small-purple-cloud",
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

-- Add hand-crafting-only and hand-crafting-and-orbs as a crafting category to players
if data.raw["character"]["character"].crafting_categories then
  table.insert(data.raw["character"]["character"].crafting_categories, "hand-crafting-only")
  table.insert(data.raw["character"]["character"].crafting_categories, "hand-crafting-and-orbs")
else
  data.raw["character"]["character"].crafting_categories = {"crafting", "hand-crafting-only", "hand-crafting-and-orbs"}
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

-- Override combat item group icon
if data.raw["item-group"]["combat"] then
  data.raw["item-group"]["combat"].icon = "__orbs__/graphics/defense-ward.png"
  data.raw["item-group"]["combat"].icon_size = 1024
end

-- Disable all vanilla menu simulations and use our custom ones
if data.raw["utility-constants"] and data.raw["utility-constants"].default then
  -- Clear all vanilla simulations
  data.raw["utility-constants"].default.main_menu_simulations = {}

  -- Add our custom simulations
  local menu_simulations = require("__base__/menu-simulations/menu-simulations")

  menu_simulations.orbs_conjuration_machine_cycle = {
    checkboard = false,
    save = "__orbs__/menu_sims/conjuration-machine-cycle.zip",
    length = 60 * 60,
    init = [[
      game.tick_paused = false
    ]],
    update = [[
    ]]
  }

  menu_simulations.orbs_flux_orbs = {
    checkboard = false,
    save = "__orbs__/menu_sims/flux-orbs.zip",
    length = 60 * 60,
    init = [[
      game.tick_paused = false
    ]],
    update = [[
    ]]
  }

  menu_simulations.orbs_stability_explode = {
    checkboard = false,
    save = "__orbs__/menu_sims/stability_explode.zip",
    length = 60 * 60,
    init = [[
      game.tick_paused = false
    ]],
    update = [[
    ]]
  }

  data.raw["utility-constants"].default.main_menu_simulations.orbs_conjuration_machine_cycle = menu_simulations.orbs_conjuration_machine_cycle
  data.raw["utility-constants"].default.main_menu_simulations.orbs_flux_orbs = menu_simulations.orbs_flux_orbs
  data.raw["utility-constants"].default.main_menu_simulations.orbs_stability_explode = menu_simulations.orbs_stability_explode
end

-- Add apple drops to all trees (0.5% chance)
for _, tree in pairs(data.raw["tree"]) do
  if tree.minable then
    -- Store original results or use wood as default
    local original_results = tree.minable.results or {{type = "item", name = "wood", amount = 4}}

    -- If minable.result is used instead of results, convert it
    if tree.minable.result and not tree.minable.results then
      original_results = {{type = "item", name = tree.minable.result, amount = tree.minable.count or 1}}
    end

    -- Add apple as an additional loot with 0.5% chance
    tree.minable.results = original_results
    table.insert(tree.minable.results, {
      type = "item",
      name = "apple",
      amount = 1,
      probability = 0.1  -- 10% chance
    })

    -- Clear the old result field if it exists
    tree.minable.result = nil
    tree.minable.count = nil
  end
end

-- Modify poison capsule cloud color to be green instead of turquoise
if data.raw["smoke-with-trigger"]["poison-cloud"] then
  local poison_cloud = data.raw["smoke-with-trigger"]["poison-cloud"]
  -- Change the main cloud color to bright green
  poison_cloud.color = {r = 0.2, g = 0.8, b = 0.2, a = 0.690}
end

-- Modify the visual dummy clouds that surround the main poison cloud
if data.raw["smoke-with-trigger"]["poison-cloud-visual-dummy"] then
  local visual_dummy = data.raw["smoke-with-trigger"]["poison-cloud-visual-dummy"]
  -- Change the surrounding cloud color to darker green
  visual_dummy.color = {r = 0.014, g = 0.395, b = 0.1, a = 0.322}
end

-- Hide technologies until their prerequisites are met
for _, technology in pairs(data.raw.technology) do
  technology.visible_when_disabled = false
  -- Disable all technologies initially
  -- Technologies with research_trigger will auto-enable when triggered
  -- Technologies with prerequisites will auto-enable when prerequisites are met
  technology.enabled = false
end

-- Enable starter technologies that have no prerequisites
if data.raw.technology["fire-science"] then
  data.raw.technology["fire-science"].enabled = true
end
if data.raw.technology["orbs-technology"] then
  data.raw.technology["orbs-technology"].enabled = true
end

-- Finally, as a last step, remove all the content we don't want
require("removals")
