-- item.lua
-- Define all the magical items

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
    subgroup = "orbs-conjure",
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
    subgroup = "orbs-proliferate",
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
  }
})
