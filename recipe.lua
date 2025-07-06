-- recipe.lua
-- Define all the new recipes

local recipes = {}

-- Conjure Shards recipes (conjure-shards subgroup)
-- Start with conjure-shards-0 for the 1:1 ratio with 20% chance
table.insert(recipes, {
  type = "recipe",
  name = "conjure-shards-0",
  category = "orbs",
  subgroup = "orbs-conjure",
  energy_required = 1,
  icon = "__orbs__/graphics/conjure-shards.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 1, probability = 0.05}
  },
  enabled = false,
  order = "a[conjure-shards]-a[0]"
})

-- Then the existing conjure recipes with proper ordering
local conjure_inputs = {1, 2, 4, 8, 16, 32}
for i, n in ipairs(conjure_inputs) do
  table.insert(recipes, {
    type = "recipe",
    name = "conjure-shards-" .. n,
    category = "orbs",
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
    enabled = false,
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
  enabled = false,
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
  enabled = false,
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
  enabled = false,
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
  enabled = false,
  order = "a[manifest-orb]"
})

-- Transfigure to Conjuration Orb
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
  enabled = false,
  order = "b[transfigure-conjuration-orb]"
})

-- Conjuration Research Pack
table.insert(recipes, {
  type = "recipe",
  name = "conjuration-research-pack",
  category = "orbs",
  subgroup = "orbs-research",
  energy_required = 25,
  icon = "__orbs__/graphics/conjuration-research-pack.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "active-magic-shard", amount = 20},
    {type = "item", name = "copper-cable", amount = 4}
  },
  results = {
    {type = "item", name = "conjuration-research-pack", amount = 1}
  },
  enabled = false,
  order = "a[conjuration-research-pack]"
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
  enabled = false,
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
  enabled = false,
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
  enabled = false,
  order = "e[neutralize-conjuration-orb]"
})

-- Extend all recipes
data:extend(recipes)
