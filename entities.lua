-- entities.lua

-- Create the conjuration machine
local conjuration_machine = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-2"])

conjuration_machine.name = "conjuration-machine"
conjuration_machine.minable = {mining_time = 0.2, result = "conjuration-machine"}
conjuration_machine.crafting_categories = {"orbs"} -- ONLY orbs category
conjuration_machine.crafting_speed = 1
conjuration_machine.energy_source = {type = "void"} -- No power required
conjuration_machine.energy_usage = "1W" -- Minimal energy usage
conjuration_machine.allowed_effects = {"speed"} -- Allow speed effects for haste orbs
conjuration_machine.effect_receiver = {
  base_effect = {},
  uses_module_effects = true,
  uses_beacon_effects = false, -- Prevent beacon effects
  uses_surface_effects = true
}
conjuration_machine.module_specification = {
  module_slots = 3,
  module_info_icon_shift = {0, 0.5},
  module_info_multi_row_initial_height_modifier = -0.3
}
conjuration_machine.allowed_module_categories = {"orb-speed"} -- Only allow orb-speed modules (haste orbs)
conjuration_machine.module_slots = 3

-- Create the conjuration lab
local conjuration_lab = util.table.deepcopy(data.raw["lab"]["lab"])

conjuration_lab.name = "conjuration-lab"
conjuration_lab.minable = {mining_time = 0.2, result = "conjuration-lab"}
conjuration_lab.energy_source = {type = "void"} -- No power required
conjuration_lab.energy_usage = "1W"
conjuration_lab.researching_speed = 1
conjuration_lab.inputs = {"conjuration-research-pack", "divination-research-pack"}

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

data:extend({
  conjuration_machine,
  conjuration_lab,
  soul_collector,
  {
    type = "item",
    name = "conjuration-machine",
    icon = "__base__/graphics/icons/assembling-machine-2.png",
    icon_size = 64,
    subgroup = "orbs-machines",
    order = "a[conjuration-machine]",
    place_result = "conjuration-machine",
    stack_size = 20
  },
  {
    type = "item",
    name = "conjuration-lab",
    icon = "__base__/graphics/icons/lab.png",
    icon_size = 64,
    subgroup = "orbs-machines",
    order = "b[conjuration-lab]",
    place_result = "conjuration-lab",
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
  {
    type = "recipe",
    name = "craft-conjuration-lab",
    category = "crafting",
    energy_required = 5,
    icon = "__base__/graphics/icons/lab.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "lab", amount = 1},
      {type = "item", name = "magic-orb", amount = 2}
    },
    results = {
      {type = "item", name = "conjuration-lab", amount = 1}
    },
    enabled = false
  },
  -- Soul Collector Recipe
  {
    type = "recipe",
    name = "craft-soul-collector",
    category = "crafting",
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
          amount = 270,
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

-- Extend the entities
data:extend({
  magic_grenade_projectile,
  magic_grenade_explosion,
  magic_explosion,
  volatile_orb_explosion,
  volatile_explosion
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
      category = "crafting",
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

-- Create the rune transformer (based on stone furnace)
local rune_transformer = util.table.deepcopy(data.raw["furnace"]["stone-furnace"])

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
  icon = "__base__/graphics/icons/stone-furnace.png",
  icon_size = 64,
  subgroup = "orbs-machines",
  order = "e[rune-transformer]",
  place_result = "rune-transformer",
  stack_size = 10
}

-- Create the rune transformer recipe
local rune_transformer_recipe = {
  type = "recipe",
  name = "rune-transformer",
  category = "crafting",
  energy_required = 5,
  icon = "__base__/graphics/icons/stone-furnace.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "stone-brick", amount = 20},
    {type = "item", name = "iron-plate", amount = 6},
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "element-of-stability", amount = 1}
  },
  results = {
    {type = "item", name = "rune-transformer", amount = 1}
  },
  enabled = false
}

data:extend({
  rune_transformer,
  rune_transformer_item,
  rune_transformer_recipe
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
  subgroup = "orbs-machines",
  order = "f[rune-altar]",
  place_result = "rune-altar",
  stack_size = 10
}

-- Create the rune altar recipe
local rune_altar_recipe = {
  type = "recipe",
  name = "rune-altar",
  category = "crafting",
  energy_required = 3,
  icon = "__orbs__/graphics/rune-altar.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "stone-brick", amount = 10},
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
