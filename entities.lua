-- entities.lua

-- Create the conjuration machine
local conjuration_machine = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-2"])

conjuration_machine.name = "conjuration-machine"
conjuration_machine.minable = {mining_time = 0.2, result = "conjuration-machine"}
conjuration_machine.crafting_categories = {"orbs", "hand-crafting-and-orbs"} -- Orbs and hand-crafting-and-orbs categories
conjuration_machine.crafting_speed = 1
conjuration_machine.energy_source = {
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
  scale_fluid_usage = true,
  emissions_per_minute = {pollution = 20}
}
conjuration_machine.energy_usage = "200kW"
conjuration_machine.allowed_effects = {"speed", "productivity", "pollution"} -- Allow speed, productivity, and pollution effects
conjuration_machine.effect_receiver = {
  base_effect = {},
  uses_module_effects = true,
  uses_beacon_effects = true, -- Allow beacon effects from resonance spires
  uses_surface_effects = true
}
conjuration_machine.module_specification = {
  module_slots = 3,
  module_info_icon_shift = {0, 0.5},
  module_info_multi_row_initial_height_modifier = -0.3
}
conjuration_machine.allowed_module_categories = {"orb-speed", "orb-pollution", "orb-productivity"} -- Allow haste orbs and cleansing orbs
conjuration_machine.module_slots = 3

-- Override the existing lab to be alchemy research laboratory
if data.raw["lab"]["lab"] then
  local lab = data.raw["lab"]["lab"]
  lab.localised_name = {"entity-name.alchemy-research-laboratory"}
  lab.energy_source = {
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
  lab.energy_usage = "150kW"
  lab.researching_speed = 1
  lab.inputs = {"automation-science-pack", "magic-research-pack", "conjuration-research-pack", "divination-research-pack", "rune-research-pack"}
  lab.effect_receiver = {
    uses_beacon_effects = true,
    uses_module_effects = true,
    uses_surface_effects = true
  }
  -- Allow rotation by setting direction count
  lab.direction_count = 4
end

-- Create the soul collector (based on iron chest)
local soul_collector = util.table.deepcopy(data.raw["container"]["iron-chest"])

soul_collector.name = "soul-collector"
soul_collector.minable = {mining_time = 1, result = "soul-collector"}
soul_collector.inventory_size = 1 -- Only one stack slot
soul_collector.icon = "__orbs__/graphics/soul-collector.png"
soul_collector.icon_size = 1024
soul_collector.picture = {
  layers = {
    {
      filename = "__orbs__/graphics/soul-collector-entity.png",
      priority = "extra-high",
      width = 1024,
      height = 1024,
      scale = 0.2,
      shift = {
            0,
            -2
      }
    }
  }
}
soul_collector.collision_box = {
  {
    -0.8,
    -0.8
  },
  {
    0.8,
    0.8
  }
}
soul_collector.selection_box = {
  {
    -1,
    -1
  },
  {
    1,
    1
  }
}

-- Update stone furnace to accept beacon effects
if data.raw["furnace"]["stone-furnace"] then
  data.raw["furnace"]["stone-furnace"].effect_receiver = {
    uses_beacon_effects = true,
    uses_module_effects = false,
    uses_surface_effects = true
  }
  data.raw["furnace"]["stone-furnace"].allowed_effects = {"speed", "productivity", "pollution"}
end

-- Update assembling machine 1 to accept beacon effects
if data.raw["assembling-machine"]["assembling-machine-1"] then
  data.raw["assembling-machine"]["assembling-machine-1"].effect_receiver = {
    uses_beacon_effects = true,
    uses_module_effects = true,
    uses_surface_effects = true
  }
  data.raw["assembling-machine"]["assembling-machine-1"].allowed_effects = {"speed", "productivity", "pollution"}
  data.raw["assembling-machine"]["assembling-machine-1"].crafting_speed = 1
end

-- Create the distillery (based on assembling machine)
local distillery = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-1"])

distillery.name = "distillery"
distillery.minable = {mining_time = 0.2, result = "distillery"}
distillery.crafting_categories = {"distilling"}
distillery.crafting_speed = 1
distillery.energy_source = {
  type = "heat",
  max_temperature = 85,
  default_temperature = 15,
  specific_heat = "1MJ",
  max_transfer = "2GW",
  min_working_temperature = 78,
  connections = {
    {position = {0, -1}, direction = defines.direction.north},
    {position = {1, 0}, direction = defines.direction.east},
    {position = {0, 1}, direction = defines.direction.south},
    {position = {-1, 0}, direction = defines.direction.west}
  }
}
distillery.energy_usage = "50kW"
distillery.icon = "__orbs__/graphics/distillery.png"
distillery.icon_size = 1024

-- Set custom graphics for the distillery entity
distillery.graphics_set = {
  animation = {
    layers = {
      {
        filename = "__orbs__/graphics/distillery.png",
        priority = "high",
        width = 1024,
        height = 1024,
        frame_count = 1,
        line_length = 1,
        scale = 0.1,
        shift = {0, 0}
      }
    }
  }
}

-- Create the crusher (based on assembling machine)
local crusher = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-1"])

crusher.name = "crusher"
crusher.minable = {mining_time = 0.2, result = "crusher"}
crusher.crafting_categories = {"crushing"}
crusher.crafting_speed = 1
crusher.energy_source = {type = "void"}
crusher.energy_usage = "1W"
crusher.icon = "__space-age__/graphics/icons/crusher.png"
crusher.icon_size = 64

data:extend({
  conjuration_machine,
  soul_collector,
  distillery,
  crusher,
  {
    type = "item",
    name = "conjuration-machine",
    icon = "__base__/graphics/icons/assembling-machine-2.png",
    icon_size = 64,
    subgroup = "production-machine",
    order = "b[assembling-machine-2]",
    place_result = "conjuration-machine",
    stack_size = 20
  },
  {
    type = "item",
    name = "soul-collector",
    icon = "__orbs__/graphics/soul-collector.png",
    icon_size = 1024,
    subgroup = "orbs-machines",
    order = "c[soul-collector]",
    place_result = "soul-collector",
    stack_size = 10
  },
  {
    type = "item",
    name = "distillery",
    icon = "__orbs__/graphics/distillery.png",
    icon_size = 1024,
    subgroup = "orbs-machines",
    order = "e[distillery]",
    place_result = "distillery",
    stack_size = 20
  },
  {
    type = "item",
    name = "crusher",
    icon = "__space-age__/graphics/icons/crusher.png",
    icon_size = 64,
    subgroup = "orbs-machines",
    order = "d[crusher]",
    place_result = "crusher",
    stack_size = 20
  }
})

-- Recipe to craft the conjuration machine
data:extend({
  {
    type = "recipe",
    name = "craft-conjuration-machine",
    category = "crafting",
    energy_required = 5,
    icon = "__base__/graphics/icons/assembling-machine-2.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "assembling-machine-1", amount = 1},
      {type = "item", name = "copper-cable", amount = 20},
      {type = "item", name = "iron-plate", amount = 5},
      {type = "item", name = "conjuration-orb", amount = 1}
    },
    results = {
      {type = "item", name = "conjuration-machine", amount = 1}
    },
    enabled = false
  },
  -- Soul Collector Recipe
  {
    type = "recipe",
    name = "craft-soul-collector",
    category = "hand-crafting-and-orbs",
    energy_required = 5,
    icon = "__orbs__/graphics/soul-collector.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "iron-chest", amount = 1},
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "divination-essence", amount = 10}
    },
    results = {
      {type = "item", name = "soul-collector", amount = 1}
    },
    enabled = false
  },
  -- Distillery Recipe
  {
    type = "recipe",
    name = "distillery",
    category = "crafting",
    energy_required = 5,
    icon = "__orbs__/graphics/distillery.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "copper-plate", amount = 2},
      {type = "item", name = "glass", amount = 4}
    },
    results = {
      {type = "item", name = "distillery", amount = 1}
    },
    enabled = false
  },
  -- Crusher Recipe
  {
    type = "recipe",
    name = "crusher",
    category = "crafting",
    energy_required = 5,
    icon = "__space-age__/graphics/icons/crusher.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "iron-plate", amount = 4},
      {type = "item", name = "iron-gear-wheel", amount = 10}
    },
    results = {
      {type = "item", name = "crusher", amount = 1}
    },
    enabled = false
  }
})


-- Magic Grenade Projectile
local magic_grenade_projectile = {
  type = "projectile",
  name = "magic-grenade-projectile",
  flags = {"not-on-map"},
  hidden = true,
  acceleration = 0.005,
  animation = {
    filename = "__base__/graphics/entity/grenade/grenade.png",
    frame_count = 15,
    width = 48,
    height = 54,
    line_length = 8,
    animation_speed = 0.25,
    priority = "high",
    scale = 0.5,
    shift = {0.015625, 0.015625},
    draw_as_glow = true,
    tint = {r = 1.0, g = 0.4, b = 1.0, a = 1.0} -- Pink tint
  },
  shadow = {
    filename = "__base__/graphics/entity/grenade/grenade-shadow.png",
    frame_count = 15,
    width = 50,
    height = 40,
    line_length = 8,
    animation_speed = 0.25,
    priority = "high",
    scale = 0.5,
    shift = {0.0625, 0.1875},
    draw_as_shadow = true
  },
  light = {
    intensity = 0.7,
    size = 6,
    color = {r = 1.0, g = 0.4, b = 1.0} -- Pink light
  },
  action = {
    {
      type = "direct",
      action_delivery = {
        type = "instant",
        target_effects = {
          {
            type = "create-entity",
            entity_name = "magic-grenade-explosion"
          },
          {
            type = "create-entity",
            entity_name = "small-scorchmark-tintable",
            check_buildability = true
          },
          {
            type = "invoke-tile-trigger",
            repeat_count = 1
          },
          {
            type = "destroy-decoratives",
            from_render_layer = "decorative",
            to_render_layer = "object",
            include_soft_decoratives = true,
            include_decals = false,
            invoke_decorative_trigger = true,
            decoratives_with_trigger_only = false,
            radius = 4.0
          }
        }
      }
    },
    {
      type = "area",
      radius = 16,
      action_delivery = {
        type = "instant",
        target_effects = {
          {
            type = "damage",
            damage = {
              amount = 45,
              type = "explosion"
            }
          },
          {
            type = "create-entity",
            entity_name = "magic-explosion"
          }
        }
      }
    }
  }
}

-- Magic Grenade Explosion Entity
local magic_grenade_explosion = util.table.deepcopy(data.raw["explosion"]["grenade-explosion"])
magic_grenade_explosion.name = "magic-grenade-explosion"
-- Safely set light properties
if not magic_grenade_explosion.light then
  magic_grenade_explosion.light = {}
end
magic_grenade_explosion.light.color = {r = 1.0, g = 0.4, b = 1.0}
magic_grenade_explosion.light.intensity = 1.0
magic_grenade_explosion.light.size = 20

-- Magic Explosion Entity (for area damage)
local magic_explosion = util.table.deepcopy(data.raw["explosion"]["explosion"])
magic_explosion.name = "magic-explosion"
-- Safely set light properties
if not magic_explosion.light then
  magic_explosion.light = {}
end
magic_explosion.light.color = {r = 1.0, g = 0.4, b = 1.0}
magic_explosion.light.intensity = 0.8
magic_explosion.light.size = 15

-- Volatile Orb Explosion Entity
local volatile_orb_explosion = util.table.deepcopy(data.raw["explosion"]["grenade-explosion"])
volatile_orb_explosion.name = "volatile-orb-explosion"
-- Use the custom explosion icon
volatile_orb_explosion.icon = "__orbs__/graphics/volatile-orb-explosion.png"
volatile_orb_explosion.icon_size = 1024
-- Safely set light properties
if not volatile_orb_explosion.light then
  volatile_orb_explosion.light = {}
end
volatile_orb_explosion.light.color = {r = 1.0, g = 0.2, b = 0.8}
volatile_orb_explosion.light.intensity = 1.2
volatile_orb_explosion.light.size = 12

-- Add area damage effect to the volatile orb explosion
volatile_orb_explosion.created_effect = {
  type = "area",
  radius = 4,
  action_delivery = {
    type = "instant",
    target_effects = {
      {
        type = "damage",
        damage = {
          amount = 350,
          type = "explosion"
        }
      },
      {
        type = "create-entity",
        entity_name = "volatile-explosion"
      }
    }
  }
}

-- Volatile Explosion Entity (for area damage visual)
local volatile_explosion = util.table.deepcopy(data.raw["explosion"]["explosion"])
volatile_explosion.name = "volatile-explosion"
-- Safely set light properties
if not volatile_explosion.light then
  volatile_explosion.light = {}
end
volatile_explosion.light.color = {r = 1.0, g = 0.2, b = 0.8}
volatile_explosion.light.intensity = 0.9
volatile_explosion.light.size = 10

-- Create custom laser beam for defense ward
local defense_ward_laser = util.table.deepcopy(data.raw["beam"]["laser-beam"])
defense_ward_laser.name = "defense-ward-laser"
defense_ward_laser.action = {
  type = "direct",
  action_delivery = {
    type = "instant",
    target_effects = {
      {
        type = "damage",
        damage = {
          amount = 300,
          type = "laser"
        }
      },
      {
        type = "script",
        effect_id = "defense-ward-fired"
      }
    }
  }
}

-- Create defense ward (based on laser turret)
local defense_ward = util.table.deepcopy(data.raw["electric-turret"]["laser-turret"])

defense_ward.name = "defense-ward"
defense_ward.minable = {mining_time = 0.2, result = "defense-ward"}
defense_ward.max_health = 50
defense_ward.energy_source = {type = "void"}
defense_ward.energy_usage = "0kW"

-- Set range to 8 and use custom beam
defense_ward.attack_parameters.range = 8
defense_ward.attack_parameters.ammo_type.action.action_delivery.beam = "defense-ward-laser"
defense_ward.collision_box = {{-0.35, -0.35}, {0.35, 0.35}}
defense_ward.selection_box = {{-0.5, -0.5}, {0.5, 0.5}}

-- Use custom graphics for all animation states
local defense_ward_animation = {
  layers = {
    {
      filename = "__orbs__/graphics/defense-ward-entity.png",
      priority = "high",
      width = 1024,
      height = 1024,
      frame_count = 1,
      line_length = 1,
      direction_count = 1,
      scale = 0.05,
      shift = {0, -0.2}
    }
  }
}

-- Set all required animation states to use the same static image
defense_ward.folded_animation = defense_ward_animation
defense_ward.preparing_animation = defense_ward_animation
defense_ward.prepared_animation = defense_ward_animation
defense_ward.attacking_animation = defense_ward_animation
defense_ward.ending_attack_animation = defense_ward_animation
defense_ward.folding_animation = defense_ward_animation

-- Try to hide all possible base graphics
defense_ward.base_picture = {
  layers = {
    {
      filename = "__core__/graphics/empty.png",
      width = 1,
      height = 1,
      frame_count = 1,
      direction_count = 1
    }
  }
}

-- Also try to clear other potential base graphics
defense_ward.base_picture_secondary_draw_order = nil
defense_ward.integration_patch = nil
defense_ward.shadow = nil


-- Create defense ward item
local defense_ward_item = {
  type = "item",
  name = "defense-ward",
  icon = "__orbs__/graphics/defense-ward.png",
  icon_size = 1024,
  subgroup = "defensive-structure",
  order = "i[defense-ward]",
  place_result = "defense-ward",
  stack_size = 10
}

-- Create defense ward recipe
local defense_ward_recipe = {
  type = "recipe",
  name = "defense-ward",
  category = "hand-crafting-and-orbs",
  energy_required = 3,
  icon = "__orbs__/graphics/defense-ward.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "active-magic-shard", amount = 1},
    {type = "item", name = "wood", amount = 2},
    {type = "item", name = "copper-cable", amount = 2}
  },
  results = {
    {type = "item", name = "defense-ward", amount = 1}
  },
  enabled = false
}

-- Extend the entities
data:extend({
  magic_grenade_projectile,
  magic_grenade_explosion,
  magic_explosion,
  volatile_orb_explosion,
  volatile_explosion,
  defense_ward_laser,
  defense_ward,
  defense_ward_item,
  defense_ward_recipe
})


-- Create a new rage flamethrower turret based on the regular flamethrower turret
if data.raw["fluid-turret"]["flamethrower-turret"] then
  local base_turret = data.raw["fluid-turret"]["flamethrower-turret"]
  local ragethrower_turret = util.table.deepcopy(base_turret)

  -- Convert to ammo turret
  ragethrower_turret.type = "ammo-turret"
  ragethrower_turret.name = "ragethrower-turret"
  ragethrower_turret.ammo_category = "rage-orb"
  ragethrower_turret.inventory_size = 1
  ragethrower_turret.automated_ammo_count = 10

  -- Update attack parameters to use rage-orb ammo category
  ragethrower_turret.attack_parameters.ammo_category = "rage-orb"

  -- Remove fluid-specific properties
  ragethrower_turret.fluid_box = nil
  ragethrower_turret.fluid_buffer_size = nil
  ragethrower_turret.fluid_buffer_input_flow = nil
  ragethrower_turret.activation_buffer_ratio = nil

  -- Add the new turret
  data:extend({ragethrower_turret})

  -- Create item for the new turret
  local ragethrower_item = util.table.deepcopy(data.raw.item["flamethrower-turret"])
  ragethrower_item.name = "ragethrower-turret"
  ragethrower_item.place_result = "ragethrower-turret"
  ragethrower_item.localised_name = {"item-name.ragethrower-turret"}
  ragethrower_item.subgroup = "orbs-machines"
  ragethrower_item.order = "d[ragethrower-turret]"

  data:extend({ragethrower_item})

  -- Create recipe for the new turret
  data:extend({
    {
      type = "recipe",
      name = "ragethrower-turret",
      category = "hand-crafting-and-orbs",
      subgroup = "orbs-machines",
      energy_required = 10,
      icon = "__base__/graphics/icons/flamethrower-turret.png",
      icon_size = 64,
      ingredients = {
        {type = "item", name = "engine-unit", amount = 5},
        {type = "item", name = "iron-gear-wheel", amount = 10},
        {type = "item", name = "steel-plate", amount = 20},
        {type = "item", name = "rage-orb", amount = 1}
      },
      results = {
        {type = "item", name = "ragethrower-turret", amount = 1}
      },
      enabled = false,
      order = "d[ragethrower-turret]"
    }
  })
end

-- Create rage orb ammo category
data:extend({
  {
    type = "ammo-category",
    name = "rage-orb",
    localised_name = {"ammo-category-name.rage-orb"}
  }
})

-- Create rage fire stream (based on flamethrower fire stream)
local rage_fire_stream = util.table.deepcopy(data.raw.stream["flamethrower-fire-stream"])
rage_fire_stream.name = "rage-flamethrower-fire-stream"

-- Change particle color to red/orange for rage
if rage_fire_stream.particle then
  rage_fire_stream.particle.tint = {r = 1.0, g = 0.3, b = 0.1, a = 1.0}
end

data:extend({rage_fire_stream})

-- Create the rune transformer (based on steel furnace)
local rune_transformer = util.table.deepcopy(data.raw["furnace"]["steel-furnace"])

-- Create water-cooler heat exchanger
local water_cooler = util.table.deepcopy(data.raw["boiler"]["heat-exchanger"])

water_cooler.name = "water-cooler"
water_cooler.minable = {mining_time = 0.1, result = "water-cooler"}
water_cooler.fast_replaceable_group = "water-cooler"
water_cooler.corpse = "heat-exchanger-remnants"
water_cooler.dying_explosion = "heat-exchanger-explosion"
water_cooler.target_temperature = 50 -- Target temperature of 50°C
water_cooler.energy_consumption = "1MW" -- Energy consumed for cooling
water_cooler.energy_source = {
  type = "heat",
  max_temperature = 100, -- Maximum input temperature
  specific_heat = "1MJ",
  max_transfer = "1GW",
  min_working_temperature = 50, -- Minimum working temperature (same as target)
  connections = {
    {
      position = {0, 0.5},
      direction = defines.direction.south
    }
  },
  pipe_covers = make_4way_animation_from_spritesheet({
    filename = "__base__/graphics/entity/heat-exchanger/heatex-endings.png",
    width = 64,
    height = 64,
    direction_count = 4,
    scale = 0.5
  }),
  heat_pipe_covers = make_4way_animation_from_spritesheet(
    apply_heat_pipe_glow{
      filename = "__base__/graphics/entity/heat-exchanger/heatex-endings-heated.png",
      width = 64,
      height = 64,
      direction_count = 4,
      scale = 0.5
    }),
  heat_picture = {
    north = apply_heat_pipe_glow{
      filename = "__base__/graphics/entity/heat-exchanger/heatex-N-heated.png",
      priority = "extra-high",
      width = 44,
      height = 96,
      shift = util.by_pixel(-0.5, 8.5),
      scale = 0.5
    },
    east = apply_heat_pipe_glow{
      filename = "__base__/graphics/entity/heat-exchanger/heatex-E-heated.png",
      priority = "extra-high",
      width = 80,
      height = 80,
      shift = util.by_pixel(-21, -13),
      scale = 0.5
    },
    south = apply_heat_pipe_glow{
      filename = "__base__/graphics/entity/heat-exchanger/heatex-S-heated.png",
      priority = "extra-high",
      width = 28,
      height = 40,
      shift = util.by_pixel(-1, -30),
      scale = 0.5
    },
    west = apply_heat_pipe_glow{
      filename = "__base__/graphics/entity/heat-exchanger/heatex-W-heated.png",
      priority = "extra-high",
      width = 64,
      height = 76,
      shift = util.by_pixel(23, -13),
      scale = 0.5
    }
  }
}

-- Configure fluid boxes for water input and output
water_cooler.fluid_box = {
  volume = 200,
  pipe_covers = pipecoverspictures(),
  pipe_connections = {
    {flow_direction = "input-output", direction = defines.direction.west, position = {-1, 0.5}},
    {flow_direction = "input-output", direction = defines.direction.east, position = {1, 0.5}}
  },
  production_type = "input",
  filter = "water"
}

water_cooler.output_fluid_box = {
  volume = 200,
  pipe_covers = pipecoverspictures(),
  pipe_connections = {
    {flow_direction = "output", direction = defines.direction.north, position = {0, -0.5}}
  },
  production_type = "output",
  filter = "water"
}

data:extend({
  water_cooler,
  {
    type = "item",
    name = "water-cooler",
    icon = "__base__/graphics/icons/heat-boiler.png",
    icon_size = 64,
    subgroup = "orbs-machines",
    order = "f[water-cooler]",
    place_result = "water-cooler",
    stack_size = 20
  },
  {
    type = "recipe",
    name = "water-cooler",
    category = "crafting",
    energy_required = 5,
    icon = "__base__/graphics/icons/heat-boiler.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "copper-plate", amount = 20},
      {type = "item", name = "pipe", amount = 10}
    },
    results = {
      {type = "item", name = "water-cooler", amount = 1}
    },
    enabled = false
  }
})

rune_transformer.name = "rune-transformer"
rune_transformer.minable = {mining_time = 1, result = "rune-transformer"}
rune_transformer.crafting_categories = {"rune-transformation"}
rune_transformer.crafting_speed = 1
rune_transformer.energy_source = {type = "void"}
rune_transformer.energy_usage = "1W"
rune_transformer.result_inventory_size = 1
rune_transformer.source_inventory_size = 1

-- Create the rune transformer item
local rune_transformer_item = {
  type = "item",
  name = "rune-transformer",
  icon = "__base__/graphics/icons/steel-furnace.png",
  icon_size = 64,
  subgroup = "orbs-runes",
  order = "e[rune-transformer]",
  place_result = "rune-transformer",
  stack_size = 10
}

-- Create the rune transformer recipe
local rune_transformer_recipe = {
  type = "recipe",
  name = "rune-transformer",
  category = "orbs",
  energy_required = 5,
  icon = "__base__/graphics/icons/steel-furnace.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "stone-brick", amount = 10},
    {type = "item", name = "iron-plate", amount = 6},
    {type = "item", name = "magic-orb", amount = 1},
    {type = "fluid", name = "stability", amount = 200}
  },
  results = {
    {type = "item", name = "rune-transformer", amount = 1}
  },
  enabled = false
}

-- Create magic satchel entity (like a rock that can be mined)
local magic_satchel = {
  type = "simple-entity",
  name = "magic-satchel",
  icon = "__orbs__/graphics/magic-satchel.png",
  icon_size = 1024,
  flags = {"placeable-neutral", "placeable-off-grid"},
  minable = {
    mining_time = 2,
    results = {
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "conjuration-orb", amount = 2}
    }
  },
  max_health = 50,
  collision_box = {{-0.4, -0.4}, {0.4, 0.4}},
  selection_box = {{-0.5, -0.5}, {0.5, 0.5}},
  pictures = {
    {
      filename = "__orbs__/graphics/magic-satchel.png",
      priority = "extra-high",
      width = 1024,
      height = 1024,
      scale = 0.04375 -- 0.03125 * 1.4 to make it 40% bigger (44.8x44.8 pixels)
    }
  }
}

-- Create inactive portal entity (based on assembling machine)
local inactive_portal = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-1"])

inactive_portal.name = "inactive-portal"
inactive_portal.minable = {mining_time = 2, result = "inactive-portal"}
inactive_portal.crafting_categories = {"inactive-portal"}
inactive_portal.crafting_speed = 1
inactive_portal.energy_source = {
  type = "burner",
  fuel_categories = {"divination-energy"},
  effectivity = 1,
  fuel_inventory_size = 10,
  emissions_per_minute = {pollution = 500}
}
inactive_portal.energy_usage = "1MW"
inactive_portal.module_specification = {
  module_slots = 2,
  module_info_icon_shift = {0, 0.5},
  module_info_multi_row_initial_height_modifier = -0.3
}
inactive_portal.module_slots = 2  -- Ensure module slots are set
inactive_portal.allowed_effects = {"speed", "pollution"}
inactive_portal.collision_box = {{-0.1, -0.1}, {2.9, 2.9}} -- 3x3 collision box containing [0,0]
inactive_portal.selection_box = {{-3.5, -3.5}, {3.5, 3.5}} -- 7x7 selection box
inactive_portal.icon = "__orbs__/graphics/portal.png"
inactive_portal.icon_size = 1024

-- Portal graphics
inactive_portal.graphics_set = {
  animation = {
    layers = {
      {
        filename = "__orbs__/graphics/portal-inactive-entity.png",
        priority = "high",
        width = 1024,
        height = 1024,
        scale = 0.25, -- Scale to fit 7x7 tiles better
        frame_count = 1
      }
    }
  }
}

-- Remove next_upgrade to avoid bounding box conflicts
inactive_portal.next_upgrade = nil

-- Create active portal entity (identical to inactive but different sprite and recipe category)
local active_portal = util.table.deepcopy(inactive_portal)

active_portal.name = "active-portal"
active_portal.minable = {mining_time = 2, result = "inactive-portal"} -- Always drops inactive portal
active_portal.crafting_categories = {"active-portal"}
active_portal.icon = "__orbs__/graphics/portal.png"
-- Module slots are inherited from inactive_portal via deepcopy

-- Active portal graphics
active_portal.graphics_set = {
  animation = {
    layers = {
      {
        filename = "__orbs__/graphics/portal-active-entity.png",
        priority = "high",
        width = 1024,
        height = 1024,
        scale = 0.25, -- Scale to fit 7x7 tiles better
        frame_count = 1
      }
    }
  }
}

-- Remove next_upgrade to avoid bounding box conflicts
active_portal.next_upgrade = nil

data:extend({
  rune_transformer,
  rune_transformer_item,
  rune_transformer_recipe,
  magic_satchel,
  inactive_portal,
  active_portal
})

-- Create the rune altar (based on iron chest)
local rune_altar = util.table.deepcopy(data.raw["container"]["iron-chest"])

rune_altar.name = "rune-altar"
rune_altar.minable = {mining_time = 1, result = "rune-altar"}
rune_altar.inventory_size = 10
rune_altar.picture = {
  layers = {
    {
      filename = "__orbs__/graphics/rune-altar.png",
      priority = "extra-high",
      width = 1024,
      height = 1024,
      scale = 0.06,
      shift = {
            0,
            0
      }
    }
  }
}
rune_altar.collision_box = {
  {
    -0.65,
    -0.65
  },
  {
    0.65,
    0.65
  }
}
rune_altar.selection_box = {
  {
    -1,
    -1
  },
  {
    1,
    1
  }
}

-- Create the rune altar item
local rune_altar_item = {
  type = "item",
  name = "rune-altar",
  icon = "__orbs__/graphics/rune-altar.png",
  icon_size = 1024,
  subgroup = "orbs-runes",
  order = "f[rune-altar]",
  place_result = "rune-altar",
  stack_size = 10
}

-- Create the rune altar recipe
local rune_altar_recipe = {
  type = "recipe",
  name = "rune-altar",
  category = "hand-crafting-and-orbs",
  energy_required = 3,
  icon = "__orbs__/graphics/rune-altar.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "stone-brick", amount = 20},
    {type = "item", name = "magic-orb", amount = 1},
  },
  results = {
    {type = "item", name = "rune-altar", amount = 1}
  },
  enabled = false
}

data:extend({
  rune_altar,
  rune_altar_item,
  rune_altar_recipe
})

-- Create steam-powered miner based on electric mining drill
if data.raw["mining-drill"]["electric-mining-drill"] then
  local steam_miner = util.table.deepcopy(data.raw["mining-drill"]["electric-mining-drill"])
  steam_miner.name = "steam-powered-miner"
  steam_miner.minable.result = "steam-powered-miner"

  -- Change energy source to steam
  steam_miner.energy_source = {
    type = "fluid",
    effectivity = 1,
    burns_fluid = true,
    scale_fluid_usage = true,
    fluid_box = {
      production_type = "input",
      volume = 200,
      pipe_connections = {
        {flow_direction = "input-output", direction = 8, position = {0, 1}},
        {flow_direction = "input-output", direction = 4, position = {1, 0}},
        {flow_direction = "input-output", direction = 12, position = {-1, 0}}
      },
      secondary_draw_orders = {north = -1}
    },
    smoke = {
      {
        name = "smoke",
        deviation = {0.1, 0.1},
        frequency = 3
      }
    }
  }
  steam_miner.energy_usage = "90kW"

  -- Remove module slots but keep allowed effects
  steam_miner.module_slots = 0
  steam_miner.module_specification = nil
  steam_miner.allowed_effects = {"speed", "productivity", "pollution"}

  -- Remove input_fluid_box (not needed for fuel)
  steam_miner.input_fluid_box = nil

  -- Force use of wet mining graphics by setting resource categories that require fluid
  steam_miner.resource_categories = {"basic-solid"}

  -- Override graphics_set to always use wet mining graphics
  steam_miner.graphics_set = steam_miner.wet_mining_graphics_set

  -- Create steam-powered miner item
  local steam_miner_item = util.table.deepcopy(data.raw.item["electric-mining-drill"])
  steam_miner_item.name = "steam-powered-miner"
  steam_miner_item.place_result = "steam-powered-miner"
  steam_miner_item.subgroup = "extraction-machine"
  steam_miner_item.order = "b[mining-drill]-b[steam-powered-miner]"

  -- Create steam-powered miner recipe
  local steam_miner_recipe = {
    type = "recipe",
    name = "steam-powered-miner",
    category = "crafting",
    energy_required = 2,
    icon = "__base__/graphics/icons/electric-mining-drill.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "burner-mining-drill", amount = 1},
      {type = "item", name = "iron-gear-wheel", amount = 10},
      {type = "item", name = "iron-stick", amount = 4},
      {type = "item", name = "pipe", amount = 4}
    },
    results = {
      {type = "item", name = "steam-powered-miner", amount = 1}
    },
    enabled = false
  }

  -- Add everything to data
  data:extend({
    steam_miner,
    steam_miner_item,
    steam_miner_recipe
  })
end

-- Create gold plate tile using concrete as base
local gold_plate_tile = util.table.deepcopy(data.raw["tile"]["concrete"])
gold_plate_tile.name = "gold-plate-tile"
gold_plate_tile.minable = {mining_time = 0.1, result = "gold-plate"}
gold_plate_tile.walking_speed_modifier = 1.5
gold_plate_tile.map_color = {r = 255, g = 215, b = 0}

-- Add metal build sound
gold_plate_tile.build_sound = {filename = "__space-age__/sound/entity/foundry/foundry-metal-clunk.ogg", volume = 0.7}
gold_plate_tile.mined_sound = {filename = "__space-age__/sound/entity/foundry/foundry-metal-clunk.ogg", volume = 0.8}

-- Override main variant to use gold floor texture
gold_plate_tile.variants.main = {
  {
    picture = "__orbs__/graphics/gold-floor.png",
    count = 1,
    size = 1,
    probability = 1,
    weights = {1.0}
  }
}

-- Keep transitions but tint them gold
if gold_plate_tile.variants.transition and gold_plate_tile.variants.transition.overlay then
  gold_plate_tile.variants.transition.overlay.tint = {r = 1.0, g = 0.8, b = 0.0, a = 0.5}
end

data:extend({gold_plate_tile})

-- Create sentry ward (based on radar)
local sentry_ward = util.table.deepcopy(data.raw["radar"]["radar"])

sentry_ward.name = "sentry-ward"
sentry_ward.minable = {mining_time = 0.5, result = "sentry-ward"}
sentry_ward.max_health = 50
sentry_ward.corpse = "small-electric-pole-remnants"
sentry_ward.energy_source = {type = "void"} -- No power required
sentry_ward.energy_usage = "1W"
sentry_ward.max_distance_of_sector_revealed = 0 -- No scanning
sentry_ward.max_distance_of_nearby_sector_revealed = 2 -- Reveal nearby chunks
sentry_ward.energy_per_sector = "1J"
sentry_ward.energy_per_nearby_scan = "1J"
sentry_ward.rotation_speed = 0 -- Don't rotate
sentry_ward.radar_range = 2

-- Make it 1x1 size with small bounding boxes
sentry_ward.collision_box = {{-0.25, -0.25}, {0.25, 0.25}}
sentry_ward.selection_box = {{-0.35, -0.35}, {0.35, 0.35}}

-- Use custom sentry ward graphics
sentry_ward.pictures = {
  layers = {
    {
      filename = "__orbs__/graphics/sentry-ward-entity.png",
      priority = "high",
      width = 1024,
      height = 1024,
      direction_count = 1,
      frame_count = 1,
      line_length = 1,
      scale = 0.05,
      shift = {0, -0.5}
    }
  }
}

-- Remove shadow
sentry_ward.integration_patch = nil

data:extend({
  sentry_ward,
  {
    type = "item",
    name = "sentry-ward",
    icon = "__orbs__/graphics/sentry-ward.png",
    icon_size = 1024,
    subgroup = "defensive-structure",
    order = "d[radar]-b[sentry-ward]",
    place_result = "sentry-ward",
    stack_size = 50
  }
})

-- Sentry Ward Recipe
data:extend({
  {
    type = "recipe",
    name = "craft-sentry-ward",
    category = "hand-crafting-and-orbs",
    energy_required = 2,
    icon = "__orbs__/graphics/sentry-ward.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "wood", amount = 1}
    },
    results = {
      {type = "item", name = "sentry-ward", amount = 1}
    },
    enabled = false
  }
})

-- Create the resonance spire (based on beacon)
local resonance_spire = util.table.deepcopy(data.raw["beacon"]["beacon"])

resonance_spire.name = "resonance-spire"
resonance_spire.minable = {mining_time = 2, result = "resonance-spire"}
resonance_spire.energy_source = {type = "void"} -- No power required
resonance_spire.energy_usage = "1W"
resonance_spire.supply_area_distance = 7 -- 15x15 area (radius 7)
resonance_spire.allowed_effects = {"productivity", "pollution", "speed"} -- Allow productivity, pollution, and speed effects
resonance_spire.module_icons_suppressed = false
resonance_spire.distribution_effectivity = 1.0
resonance_spire.effect_receiver = {
  base_effect = {},
  uses_module_effects = true,
  uses_beacon_effects = false,
  uses_surface_effects = true
}
resonance_spire.module_specification = {
  module_slots = 1,
  module_info_icon_shift = {0, -0.5},
  module_info_multi_row_initial_height_modifier = -0.3,
  module_info_icon_scale = 1.0,
  module_info_max_icons_per_row = 1,
  module_info_max_icon_rows = 1
}
resonance_spire.allowed_module_categories = {"orb-productivity", "orb-pollution"} -- Only allow productivity and cleansing orbs
resonance_spire.module_slots = 1

-- Make it 1x1 size but keep reasonable bounding boxes for module display
resonance_spire.collision_box = {{-0.4, -0.4}, {0.4, 0.4}}
resonance_spire.selection_box = {{-0.5, -0.8}, {0.5, 0.5}}
resonance_spire.drawing_box = {{-0.5, -1.0}, {0.5, 0.5}} -- Larger drawing box for better module visibility

-- Update graphics to use custom resonance spire entity graphics
resonance_spire.graphics_set = {
  animation_list = {
    {
      render_layer = "floor-mechanics",
      always_draw = true,
      animation = {
        layers = {
          {
            filename = "__orbs__/graphics/resonance-spire-entity.png",
            priority = "high",
            width = 1024,
            height = 1024,
            frame_count = 1,
            line_length = 1,
            scale = 0.06,
            shift = {0, -0.5}
          }
        }
      }
    }
  }
}

data:extend({
  resonance_spire,
  {
    type = "item",
    name = "resonance-spire",
    icon = "__orbs__/graphics/resonance-spire.png",
    icon_size = 1024,
    subgroup = "orbs-machines",
    order = "h[resonance-spire]",
    place_result = "resonance-spire",
    stack_size = 10
  }
})

-- Resonance Spire Recipe
data:extend({
  {
    type = "recipe",
    name = "craft-resonance-spire",
    category = "crafting",
    energy_required = 15,
    icon = "__orbs__/graphics/resonance-spire.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "gold-plate", amount = 10},
      {type = "item", name = "iron-stick", amount = 1},
      {type = "item", name = "divination-essence", amount = 4}
    },
    results = {
      {type = "item", name = "resonance-spire", amount = 1}
    },
    enabled = false
  }
})

-- Custom purple magical splash effect for channeled-mana
data:extend({
  {
    type = "explosion",
    name = "purple-magical-splash",
    localised_name = {"entity-name.purple-magical-splash"},
    flags = {"not-on-map"},
    subgroup = "explosions",
    order = "b-b-b",
    height = 0,
    animations = util.empty_sprite(),
    created_effect = {
      type = "direct",
      action_delivery = {
        type = "instant",
        target_effects = {
          type = "create-particle",
          repeat_count = 15, -- More particles for bigger effect
          repeat_count_deviation = 8,
          particle_name = "tintable-water-particle",
          tint = {r = 0.7, g = 0.4, b = 1.0, a = 0.8}, -- Purple tint
          initial_height = 0.2,
          initial_height_deviation = 0.1,
          initial_vertical_speed = 0.08,
          initial_vertical_speed_deviation = 0.05,
          speed_from_center = 0.04, -- Increased speed outward
          speed_from_center_deviation = 0.02, -- More variation in outward speed
          offset_deviation = {{-0.5, -0.5}, {0.5, 0.5}}, -- Random starting positions
          offsets = {{0, 0}} -- Center point
        }
      }
    },
    sound = {
      {
        filename = "__base__/sound/world/water/waterlap-5.ogg",
        volume = 0.4
      }
    }
  }
})
