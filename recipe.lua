-- recipe.lua
-- Define all the magical recipes with proper categorization and naming

local recipes = {}

-- Conjure Shards recipes (conjure-shards subgroup)
-- Start with conjure-shards-0 for the 1:1 ratio with 20% chance
table.insert(recipes, {
  type = "recipe",
  name = "conjure-shards-0",
  category = "orbs", -- Changed to orbs category
  subgroup = "orbs-conjure",
  energy_required = 1,
  icon = "__orbs__/graphics/conjure-shards.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 1, probability = 0.2}
  },
  enabled = true,
  order = "a[conjure-shards]-a[0]"
})

-- Then the existing conjure recipes with proper ordering
local conjure_inputs = {1, 2, 4, 8, 16, 32}
for i, n in ipairs(conjure_inputs) do
  table.insert(recipes, {
    type = "recipe",
    name = "conjure-shards-" .. n,
    category = "orbs", -- Changed to orbs category
    subgroup = "orbs-conjure",
    energy_required = n,
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "magic-orb", amount = n + 1}
    },
    results = {
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "active-magic-shard", amount = n * n}
    },
    enabled = true,
    order = "a[conjure-shards]-" .. string.char(97 + i) .. "[" .. n .. "]"
  })
end

-- Shard Proliferation recipes (orbs-proliferate subgroup)
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards",
  category = "orbs",
  subgroup = "orbs-proliferate",
  energy_required = 1,
  icon = "__orbs__/graphics/active-magic-shard.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 1, probability = 0.5}
  },
  enabled = true,
  order = "a[replicate-shards]"
})

-- Shard Proliferation II
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards-2",
  category = "orbs",
  subgroup = "orbs-proliferate",
  energy_required = 3,
  icon = "__orbs__/graphics/active-magic-shard.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 2},
    {type = "item", name = "active-magic-shard", amount = 10}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 2},
    {type = "item", name = "active-magic-shard", amount = 10},
    {type = "item", name = "active-magic-shard", amount_min = 2, amount_max = 4}
  },
  enabled = true,
  order = "b[replicate-shards-2]"
})

-- Shard Cleanup
table.insert(recipes, {
  type = "recipe",
  name = "banish-shards",
  category = "orbs",
  subgroup = "orbs-proliferate",
  energy_required = 2,
  icon = "__orbs__/graphics/inactive-magic-shard.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "inactive-magic-shard", amount = 10}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  enabled = true,
  order = "c[banish-shards]"
})

-- Orb Manifestation recipes (orbs-manifest subgroup)
table.insert(recipes, {
  type = "recipe",
  name = "manifest-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 5,
  icon = "__orbs__/graphics/magic-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "active-magic-shard", amount = 10}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  enabled = true,
  order = "a[manifest-orb]"
})

-- Transfigure to Conjurationg Orb
table.insert(recipes, {
  type = "recipe",
  name = "transfigure-conjuration-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 3,
  icon = "__orbs__/graphics/conjuration-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 2}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "conjuration-orb", amount = 1}
  },
  enabled = true,
  order = "b[transfigure-conjugating-orb]"
})

-- Transfigure to Haste Orb
table.insert(recipes, {
  type = "recipe",
  name = "transfigure-haste-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 3,
  icon = "__orbs__/graphics/haste-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 2}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "haste-orb", amount = 1}
  },
  enabled = true,
  order = "c[transfigure-haste-orb]"
})

-- Neutralize Haste Orb
table.insert(recipes, {
  type = "recipe",
  name = "neutralize-haste-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 1,
  icon = "__orbs__/graphics/magic-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "haste-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  enabled = true,
  order = "d[neutralize-haste-orb]"
})

-- Neutralize Conjuration Orb
table.insert(recipes, {
  type = "recipe",
  name = "neutralize-conjuration-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 1,
  icon = "__orbs__/graphics/magic-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "conjuration-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  enabled = true,
  order = "e[neutralize-conjuration-orb]"
})

-- Extend all recipes
data:extend(recipes)
