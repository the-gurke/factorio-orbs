-- recipe.lua
-- Define all the new recipes

local recipes = {}

-- Conjure Shards recipes (conjure-shards subgroup)
-- Start with conjure-shards-0 for the 1:1 ratio with 5% chance
table.insert(recipes, {
  type = "recipe",
  name = "conjure-shards-0",
  category = "orbs",
  subgroup = "orbs-conjure",
  energy_required = 1,
  hide_from_signal_gui = false,
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
  main_product = "",
  order = "b[conjure-shards]-a[0]"
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
    hide_from_signal_gui = false,
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "magic-orb", amount = n + 1}
    },
    results = {
      {type = "item", name = "magic-orb", amount = 1},
      {type = "item", name = "active-magic-shard", amount = n * n}
    },
    enabled = false,
    main_product = "",
    order = "b[conjure-shards]-" .. string.char(97 + i) .. "[" .. n .. "]"
  })
end

-- Shard Proliferation recipes (orbs-proliferate subgroup)
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards",
  category = "orbs",
  subgroup = "orbs-proliferate",
  energy_required = 1,
  hide_from_signal_gui = false,
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
  main_product = "",
  order = "a[replicate-shards]"
})

-- Shard Proliferation II
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards-2",
  category = "orbs",
  subgroup = "orbs-proliferate",
  energy_required = 3,
  hide_from_signal_gui = false,
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
  main_product = "",
  order = "b[replicate-shards-2]"
})

-- Banish Shards
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
  hide_from_signal_gui = false,
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

-- Conjure Unstable Orb
table.insert(recipes, {
  type = "recipe",
  name = "conjure-unstable-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 10,
  icon = "__orbs__/graphics/unstable-orb-alpha.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "active-magic-shard", amount = 50}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "unstable-orb-alpha", amount = 10, probability = 0.05}
  },
  enabled = false,
  order = "f[conjure-unstable-orb]"
})

-- Align Unstable Orb
table.insert(recipes, {
  type = "recipe",
  name = "align-unstable-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 0.8,
  icon = "__orbs__/graphics/unstable-orb-alpha.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "unstable-orb-alpha", amount = 1}
  },
  results = {
    {type = "item", name = "unstable-orb-alpha", amount = 1}
  },
  reset_freshness_on_craft = true,
  enabled = false,
  order = "g[align-unstable-orb]"
})



-- Conjure Divination Essence
table.insert(recipes, {
  type = "recipe",
  name = "conjure-divination-essence",
  category = "orbs",
  subgroup = "divination",
  energy_required = 1,
  icon = "__orbs__/graphics/divination-essence.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "unstable-orb-beta", amount = 1},
    {type = "item", name = "unstable-orb-gamma", amount = 1}
  },
  results = {
    {type = "item", name = "unstable-orb-alpha", amount = 2},
    {type = "item", name = "divination-essence", amount = 1}
  },
  reset_freshness_on_craft = true,
  enabled = false,
  order = "a[conjure-divination-essence]"
})

-- Stabilize Divination Essence
table.insert(recipes, {
  type = "recipe",
  name = "stabilize-divination-essence",
  category = "orbs",
  subgroup = "divination",
  energy_required = 0.5,
  icon = "__orbs__/graphics/divination-essence.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "divination-essence", amount = 1},
    {type = "item", name = "coal", amount = 1}
  },
  results = {
    {type = "item", name = "divination-essence", amount = 1},
    {type = "item", name = "coal", amount = 1, probability = 0.5}
  },
  reset_freshness_on_craft = true,
  enabled = false,
  order = "b[stabilize-divination-essence]"
})


-- Conjure Luck
table.insert(recipes, {
  type = "recipe",
  name = "conjure-luck",
  category = "orbs",
  subgroup = "divination",
  energy_required = 0.25,
  icon = "__orbs__/graphics/spark-of-luck.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "spark-of-luck", amount = 1, probability = 0.01}
  },
  enabled = true,
  order = "c[conjure-luck]"
})

-- Conjure Serendipity
table.insert(recipes, {
  type = "recipe",
  name = "conjure-serendipity",
  category = "orbs",
  subgroup = "divination",
  energy_required = 3,
  icon = "__orbs__/graphics/dust-of-serendipity.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "stone", amount = 1},
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "dust-of-serendipity", amount = 1}
  },
  enabled = true,
  order = "d[conjure-serendipity]"
})

-- Divination Research Pack
table.insert(recipes, {
  type = "recipe",
  name = "divination-research-pack",
  category = "orbs",
  subgroup = "orbs-research",
  energy_required = 5,
  icon = "__orbs__/graphics/divination-research-pack.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "divination-essence", amount = 1},
    {type = "item", name = "dust-of-serendipity", amount = 1},
    {type = "item", name = "spark-of-luck", amount = 1}
  },
  results = {
    {type = "item", name = "divination-research-pack", amount = 1}
  },
  enabled = true,
  order = "b[divination-research-pack]"
})

-- Magic Grenade Recipe
table.insert(recipes, {
  type = "recipe",
  name = "magic-grenade",
  category = "crafting",
  subgroup = "capsule",
  energy_required = 3,
  icon = "__orbs__/graphics/magic-grenade.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "unstable-orb-alpha", amount = 1},
    {type = "item", name = "iron-plate", amount = 5},
    {type = "item", name = "active-magic-shard", amount = 5}
  },
  results = {
    {type = "item", name = "magic-grenade", amount = 1}
  },
  enabled = false,
  order = "a[grenade]-b[normal]"
})

-- Extract Stability from Magic Orb
table.insert(recipes, {
  type = "recipe",
  name = "extract-stability",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 2,
  icon = "__orbs__/graphics/element-of-stability.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "element-of-stability", amount = 1},
    {type = "item", name = "volatile-orb-2", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-3", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-4", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-5", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-6", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-7", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-8", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-9", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-10", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-11", amount = 1, probability = 1/11},
    {type = "item", name = "volatile-orb-12", amount = 1, probability = 1/11}
  },
  enabled = false,
  order = "l[extract-stability]"
})

-- Generate volatile orb multiplication recipes
-- For each pair of orbs i and j, the result is (i * j) % 13
-- If result is 1, create neutralize recipe that gives 2 magic orbs
-- Note: volatile-orb is treated as volatile-orb-1 for calculations

local function get_orb_name(index)
  return "volatile-orb-" .. index
end

for i = 2, 12 do
  for j = i, 12 do -- Only create recipes for j >= i to avoid duplicates
    local result = (i * j) % 13
    if result == 0 then result = 13 end -- Handle modulo 0 case
    
    local orb_i = get_orb_name(i)
    local orb_j = get_orb_name(j)
    
    -- Create ingredients list - handle case where i = j
    local ingredients = {}
    if i == j then
      table.insert(ingredients, {type = "item", name = orb_i, amount = 2})
    else
      table.insert(ingredients, {type = "item", name = orb_i, amount = 1})
      table.insert(ingredients, {type = "item", name = orb_j, amount = 1})
    end
    
    if result == 1 then
      -- Neutralize recipe - gives 2 magic orbs
      table.insert(recipes, {
        type = "recipe",
        name = "neutralize-volatile-orb-" .. i .. "-" .. j,
        category = "orbs",
        subgroup = "orbs-manifest",
        hide_from_signal_gui = false,
        energy_required = 1,
        icon = "__orbs__/graphics/magic-orb.png",
        icon_size = 1024,
        ingredients = ingredients,
        results = {
          {type = "item", name = "magic-orb", amount = 2}
        },
        enabled = false,
        order = "z[neutralize-volatile-orb-" .. i .. "-" .. j .. "]"
      })
    else
      -- Multiplication recipe
      local result_orb = get_orb_name(result)
      table.insert(recipes, {
        type = "recipe",
        name = "multiply-volatile-orb-" .. i .. "-" .. j,
        category = "orbs",
        subgroup = "orbs-manifest",
        hide_from_signal_gui = false,
        energy_required = 1,
        icon = "__orbs__/graphics/volatile-orb.png",
        icon_size = 1024,
        ingredients = ingredients,
        results = {
          {type = "item", name = result_orb, amount = 1}
        },
        enabled = false,
        order = "y[multiply-volatile-orb-" .. i .. "-" .. j .. "]"
      })
    end
  end
end

-- Generate volatile orb copy recipes
-- Each orb + magic orb = 2 of the same orb
for i = 2, 12 do
  local orb_name = get_orb_name(i)
  table.insert(recipes, {
    type = "recipe",
    name = "copy-volatile-orb-" .. i,
    hide_from_signal_gui = false,
    category = "orbs",
    subgroup = "orbs-manifest",
    energy_required = 1,
    icon = "__orbs__/graphics/volatile-orb.png",
    icon_size = 1024,
    ingredients = {
      {type = "item", name = orb_name, amount = 1},
      {type = "item", name = "magic-orb", amount = 1}
    },
    results = {
      {type = "item", name = orb_name, amount = 2}
    },
    enabled = false,
    order = "x[copy-volatile-orb-" .. string.format("%02d", i) .. "]"
  })
end

-- Extend all recipes
data:extend(recipes)
