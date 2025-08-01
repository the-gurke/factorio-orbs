-- item.lua

data:extend({
  -- Magic Orb
  {
    type = "item",
    name = "magic-orb",
    icon = "__orbs__/graphics/magic-orb.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    order = "a[magic-orb]",
    stack_size = 5
  },

  -- Active Magic Shard (spoils in 30 seconds)
  {
    type = "item",
    name = "active-magic-shard",
    icon = "__orbs__/graphics/active-magic-shard.png",
    icon_size = 1024,
    subgroup = "orbs-shards",
    order = "b[active-magic-shard]",
    stack_size = 200,
    spoil_ticks = 30 * 60, -- 30 seconds * 60 ticks per second
    spoil_result = "inactive-magic-shard"
  },

  -- Inactive Magic Shard
  {
    type = "item",
    name = "inactive-magic-shard",
    icon = "__orbs__/graphics/inactive-magic-shard.png",
    icon_size = 1024,
    subgroup = "orbs-shards",
    order = "c[inactive-magic-shard]",
    stack_size = 200
  },

  -- Conjuration Orb
  {
    type = "item",
    name = "conjuration-orb",
    icon = "__orbs__/graphics/conjuration-orb.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    order = "d[conjuration-orb]",
    stack_size = 5
  },

  -- Conjuration Research Pack
  {
    type = "tool",
    name = "conjuration-research-pack",
    icon = "__orbs__/graphics/conjuration-research-pack.png",
    icon_size = 1024,
    subgroup = "orbs-research",
    order = "a[conjuration-research-pack]",
    stack_size = 200,
    durability = 1,
    durability_description_key = "description.science-pack-remaining-amount-key",
    durability_description_value = "description.science-pack-remaining-amount-value"
  },

  -- Divination Research Pack
  {
    type = "tool",
    name = "divination-research-pack",
    icon = "__orbs__/graphics/divination-research-pack.png",
    icon_size = 1024,
    subgroup = "orbs-research",
    order = "b[divination-research-pack]",
    stack_size = 200,
    durability = 1,
    durability_description_key = "description.science-pack-remaining-amount-key",
    durability_description_value = "description.science-pack-remaining-amount-value"
  },

  -- Haste Orb (also a module)
  {
    type = "module",
    name = "haste-orb",
    icon = "__orbs__/graphics/haste-orb.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    category = "orb-speed", -- Custom category for orb modules
    tier = 1,
    order = "f[haste-orb]",
    stack_size = 5,
    effect = {
      speed = 0.2
    },
    limitation = {"conjuration-machine"}, -- Only works in conjuration machines
    limitation_message_key = "haste-orb-usable-only-on-conjuration-machines"
  },

  -- Productivity Orb (spoils in 2m to magic orb, +5% productivity, -5% speed)
  {
    type = "module",
    name = "productivity-orb",
    icon = "__orbs__/graphics/productivity-orb.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    category = "orb-productivity", -- Custom category for orb modules
    tier = 1,
    order = "f[productivity-orb]",
    stack_size = 5,
    spoil_ticks = 2 * 60 * 60, -- 2 minutes * 60 seconds * 60 ticks per second
    spoil_result = "magic-orb",
    effect = {
      productivity = 0.15,
      speed = -0.15
    },
    limitation = {"resonance-spire"}, -- Only works in resonance spires
    limitation_message_key = "productivity-orb-usable-only-on-resonance-spires"
  },

  -- Cleansing Orb (spoils in 7m to magic orb, -5% pollution)
  {
    type = "module",
    name = "cleansing-orb",
    icon = "__orbs__/graphics/cleansing-orb.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    category = "orb-pollution", -- Custom category for orb modules
    tier = 1,
    order = "f[cleansing-orb]",
    stack_size = 5,
    spoil_ticks = 7 * 60 * 60, -- 7 minutes * 60 seconds * 60 ticks per second
    spoil_result = "magic-orb",
    effect = {
      pollution = -0.30
    },
    limitation = {"resonance-spire", "conjuration-machine"}, -- Works in resonance spires and conjuration machines
    limitation_message_key = "cleansing-orb-usable-only-on-resonance-spires-and-conjuration-machines"
  },

  -- Unstable Orb [Alpha State] (spoils in 30s to beta)
  {
    type = "item",
    name = "unstable-orb-alpha",
    icon = "__orbs__/graphics/unstable-orb-alpha.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    order = "g[unstable-orb-alpha]",
    stack_size = 5,
    spoil_ticks = 30 * 60, -- 30 seconds * 60 ticks per second
    spoil_result = "unstable-orb-beta"
  },

  -- Unstable Orb [Beta State] (spoils in 1s to gamma)
  {
    type = "item",
    name = "unstable-orb-beta",
    icon = "__orbs__/graphics/unstable-orb-beta.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    order = "h[unstable-orb-beta]",
    stack_size = 5,
    spoil_ticks = 1 * 60, -- 1 second * 60 ticks per second
    spoil_result = "unstable-orb-gamma"
  },

  -- Unstable Orb [Gamma State] (spoils in 1s to alpha)
  {
    type = "item",
    name = "unstable-orb-gamma",
    icon = "__orbs__/graphics/unstable-orb-gamma.png",
    icon_size = 1024,
    subgroup = "orbs-manifest",
    order = "i[unstable-orb-gamma]",
    stack_size = 5,
    spoil_ticks = 1 * 60, -- 1 second * 60 ticks per second
    spoil_result = "unstable-orb-alpha"
  },

  -- Divination Essence (spoils in 10s to nothing)
  {
    type = "item",
    name = "divination-essence",
    icon = "__orbs__/graphics/divination-essence.png",
    icon_size = 1024,
    subgroup = "divination",
    order = "a[divination-essence]",
    stack_size = 50,
    spoil_ticks = 10 * 60, -- 10 seconds * 60 ticks per second
    spoil_result = nil -- Spoils into nothing
  },

  -- Spark of Luck (spoils in 1s to nothing)
  {
    type = "item",
    name = "spark-of-luck",
    icon = "__orbs__/graphics/spark-of-luck.png",
    icon_size = 1024,
    subgroup = "divination",
    order = "b[spark-of-luck]",
    stack_size = 100,
    spoil_ticks = 1 * 60, -- 1 second * 60 ticks per second
    spoil_result = nil -- Spoils into nothing
  },

  -- Dust of Serendipity (spoils in 5s to stone)
  {
    type = "item",
    name = "dust-of-serendipity",
    icon = "__orbs__/graphics/dust-of-serendipity.png",
    icon_size = 1024,
    subgroup = "divination",
    order = "c[dust-of-serendipity]",
    stack_size = 50,
    spoil_ticks = 5 * 60, -- 5 seconds * 60 ticks per second
    spoil_result = "stone"
  },

  -- Magic Grenade / Glitter bomb (capsule item)
  {
    type = "capsule",
    name = "magic-grenade",
    icon = "__orbs__/graphics/magic-grenade.png",
    icon_size = 1024,
    subgroup = "capsule",
    order = "a[grenade]-b[normal]",
    stack_size = 100,
    weight = 10000,
    capsule_action = {
      type = "throw",
      attack_parameters = {
        type = "projectile",
        activation_type = "throw",
        ammo_category = "grenade",
        cooldown = 30,
        projectile_creation_distance = 0.6,
        range = 15,
        ammo_type = {
          target_type = "position",
          action = {
            {
              type = "direct",
              action_delivery = {
                type = "projectile",
                projectile = "magic-grenade-projectile",
                starting_speed = 0.3
              }
            }
          }
        }
      }
    }
  },

  -- Soul Item (spoils in 2 hours to nothing)
  {
    type = "item",
    name = "soul",
    icon = "__orbs__/graphics/soul.png",
    icon_size = 1024,
    subgroup = "souls",
    order = "a[soul]",
    stack_size = 1,
    spoil_ticks = 2 * 60 * 60 * 60, -- 2 hours * 60 minutes * 60 seconds * 60 ticks per second
    spoil_result = nil -- Spoils into nothing
  },

  -- Element of Stability (does not decay)
  {
    type = "item",
    name = "element-of-stability",
    icon = "__orbs__/graphics/element-of-stability.png",
    icon_size = 1024,
    subgroup = "divination",
    order = "k[element-of-stability]",
    stack_size = 100
  },

  -- Stability (liquid)
  {
    type = "fluid",
    name = "stability",
    icon = "__orbs__/graphics/stability-liquid.png",
    icon_size = 1024,
    subgroup = "divination",
    order = "l[stability]",
    default_temperature = 15,
    max_temperature = 30,
    heat_capacity = "0.1kJ",
    base_color = {r = 0.95, g = 0.95, b = 0.9},
    flow_color = {r = 1.0, g = 1.0, b = 0.95}
  },

  -- Rage
  {
    type = "fluid",
    name = "rage",
    icon = "__base__/graphics/icons/fluid/heavy-oil.png",
    icon_size = 64,
    subgroup = "souls",
    order = "b[rage]",
    default_temperature = 37,
    max_temperature = 80,
    heat_capacity = "0.1kJ",
    base_color = {r = 1.0, g = 0.1, b = 0.1},
    flow_color = {r = 1.0, g = 0.2, b = 0.2}
  },

  -- Rage Orb (spoils in 10 minutes to magic orb, has fuel value, also ammo)
  {
    type = "ammo",
    name = "rage-orb",
    icon = "__orbs__/graphics/rage-orb.png",
    icon_size = 1024,
    ammo_category = "rage-orb",
    subgroup = "orbs-manifest",
    order = "j[rage-orb]",
    stack_size = 5,
    spoil_ticks = 10 * 60 * 60, -- 10 minutes * 60 seconds * 60 ticks per second
    spoil_result = "magic-orb",
    fuel_category = "chemical",
    fuel_value = "100MJ",
    burnt_result = "magic-orb",
    magazine_size = 100,
    ammo_type = {
      category = "rage-orb",
      target_type = "position",
      clamp_position = true,
      action = {
        type = "direct",
        action_delivery = {
          type = "stream",
          stream = "rage-flamethrower-fire-stream",
          max_length = 15,
          duration = 480
        }
      }
    }
  },

  -- Glimming Remains (low fuel value, lasts 1 hour)
  {
    type = "item",
    name = "glimming-remains",
    icon = "__orbs__/graphics/glimming-remains.png",
    icon_size = 1024,
    subgroup = "intermediate-product",
    order = "z[glimming-remains]",
    stack_size = 50,
    fuel_category = "chemical",
    fuel_value = "100kJ",
    spoil_ticks = 60 * 60 * 60, -- 1 hour
    spoil_result = nil -- Spoils into nothing
  },

  -- Burning Wood (4MJ fuel, decays to glimming remains in 2 min)
  {
    type = "item",
    name = "burning-wood",
    icon = "__orbs__/graphics/burning-wood.png",
    icon_size = 1024,
    subgroup = "intermediate-product",
    order = "z[burning-wood]",
    stack_size = 50,
    fuel_category = "chemical",
    fuel_value = "4MJ",
    spoil_ticks = 2 * 60 * 60,
    spoil_result = "glimming-remains"
  },

  -- Burning Coal (8MJ fuel, decays to glimming remains in 5 min)
  {
    type = "item",
    name = "burning-coal",
    icon = "__orbs__/graphics/burning-coal.png",
    icon_size = 1024,
    subgroup = "intermediate-product",
    order = "z[burning-coal]",
    stack_size = 50,
    fuel_category = "chemical",
    fuel_value = "8MJ",
    spoil_ticks = 5 * 60 * 60,
    spoil_result = "glimming-remains"
  },

  -- Stick
  {
    type = "item",
    name = "stick",
    icon = "__orbs__/graphics/wooden-stick.png",
    icon_size = 1024,
    subgroup = "intermediate-product",
    order = "a[stick]",
    stack_size = 200
  },

  -- Rune Word Items (9 different)
  {
    type = "item",
    name = "rune-word-ignis",
    icon = "__base__/graphics/icons/signal/signal_I.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-ignis]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-aqua",
    icon = "__base__/graphics/icons/signal/signal_A.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-aqua]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-ventus",
    icon = "__base__/graphics/icons/signal/signal_S.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-ventus]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-terra",
    icon = "__base__/graphics/icons/signal/signal_R.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-terra]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-umbra",
    icon = "__base__/graphics/icons/signal/signal_U.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-umbra]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-lux",
    icon = "__base__/graphics/icons/signal/signal_L.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-lux]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-tempus",
    icon = "__base__/graphics/icons/signal/signal_T.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-tempus]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-vitae",
    icon = "__base__/graphics/icons/signal/signal_V.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-vitae]",
    stack_size = 1
  },
  {
    type = "item",
    name = "rune-word-mortis",
    icon = "__base__/graphics/icons/signal/signal_M.png",
    icon_size = 64,
    subgroup = "orbs-manifest",
    order = "r[rune-word-mortis]",
    stack_size = 1
  },

  -- Rune Research Pack (requires 6 specific runes)
  {
    type = "tool",
    name = "rune-research-pack",
    icon = "__base__/graphics/icons/utility-science-pack.png",
    icon_size = 64,
    subgroup = "orbs-research",
    order = "c[rune-research-pack]",
    stack_size = 200,
    durability = 1,
    durability_description_key = "description.science-pack-remaining-amount-key",
    durability_description_value = "description.science-pack-remaining-amount-value"
  },

  -- Gold Plate (placeable tile item)
  {
    type = "item",
    name = "gold-plate",
    icon = "__orbs__/graphics/gold-plate.png",
    icon_size = 1024,
    subgroup = "terrain",
    order = "b[gold-plate]",
    stack_size = 100,
    place_as_tile = {
      result = "gold-plate-tile",
      condition_size = 1,
      condition = {layers = {}}
    }
  }
})

-- Generate volatile orb variants 2-6 with Latin letter names

local volatile_orb_names = {
  [2] = "Q",
  [3] = "R",
  [4] = "S",
  [5] = "T",
  [6] = "U"
}

for i = 2, 6 do
  local letter_name = volatile_orb_names[i]
  local letter_icons = {}

  -- Base orb icon
  table.insert(letter_icons, {
    icon = "__orbs__/graphics/volatile-orb.png",
    icon_size = 1024
  })

  -- Add letter overlay using signal icons (small, lower left)
  table.insert(letter_icons, {
    icon = "__base__/graphics/icons/signal/signal_" .. letter_name .. ".png",
    icon_size = 64,
    scale = 0.3,
    shift = {-16, 16}
  })

  data:extend({
    {
      type = "item",
      name = "volatile-orb-" .. letter_name,
      icons = letter_icons,
      subgroup = "orbs-manifest",
      order = "j[volatile-orb-" .. string.format("%02d", i) .. "]",
      stack_size = 5,
      spoil_ticks = 40 * 60, -- 40 seconds * 60 ticks per second
      spoil_result = nil, -- Spoils into nothing
      spoil_to_trigger_result = {
        items_per_trigger = 1,
        trigger = {
          type = "direct",
          action_delivery = {
            type = "instant",
            source_effects = {
              {
                type = "create-entity",
                entity_name = "volatile-orb-explosion"
              }
            }
          }
        }
      }
    }
  })
end
