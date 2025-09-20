-- recipe.lua
-- Define all the new recipes

local recipes = {}

-- Conjure Shards recipes (conjure-shards subgroup)
-- Start with conjure-shards-0 for the 1:1 ratio with 5% chance
table.insert(recipes, {
  type = "recipe",
  name = "conjure-shards-0",
  category = "orbs",
  subgroup = "orbs-shards",
  energy_required = 1,
  hide_from_signal_gui = false,
  icon = "__orbs__/graphics/conjure-shards.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "item", name = "active-magic-shard", amount = 1, probability = 0.05}
  },
  enabled = false,
  allow_productivity = true,
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
    subgroup = "orbs-shards",
    energy_required = n,
    icon = "__orbs__/graphics/conjure-shards.png",
    hide_from_signal_gui = false,
    icon_size = 1024,
    ingredients = {
      {type = "item", name = "magic-orb", amount = n + 1, ignored_by_stats = 1}
    },
    results = {
      {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
      {type = "item", name = "active-magic-shard", amount = n * n}
    },
    enabled = false,
    allow_productivity = true,
    main_product = "",
    order = "d[conjure-shards]-" .. string.char(97 + i) .. "[" .. n .. "]"
  })
end

-- Shard Proliferation recipes
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards",
  category = "orbs",
  subgroup = "orbs-shards",
  energy_required = 1,
  hide_from_signal_gui = false,
  icon = "__orbs__/graphics/active-magic-shard.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1},
    {type = "item", name = "active-magic-shard", amount = 1, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "item", name = "active-magic-shard", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "item", name = "active-magic-shard", amount = 1, probability = 0.5}
  },
  enabled = false,
  allow_productivity = true,
  main_product = "",
  order = "a[replicate-shards]"
})

-- Shard Proliferation II
table.insert(recipes, {
  type = "recipe",
  name = "replicate-shards-2",
  category = "orbs",
  subgroup = "orbs-shards",
  energy_required = 3,
  hide_from_signal_gui = false,
  icon = "__orbs__/graphics/active-magic-shard.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 2, ignored_by_stats = 2},
    {type = "item", name = "active-magic-shard", amount = 10, ignored_by_stats = 10}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 2, ignored_by_stats = 2, ignored_by_productivity = 2},
    {type = "item", name = "active-magic-shard", amount = 10, ignored_by_stats = 10, ignored_by_productivity = 10},
    {type = "item", name = "active-magic-shard", amount_min = 2, amount_max = 4}
  },
  enabled = false,
  allow_productivity = true,
  main_product = "",
  order = "b[replicate-shards-2]"
})

-- Banish Shards
table.insert(recipes, {
  type = "recipe",
  name = "banish-shards",
  category = "orbs",
  subgroup = "orbs-shards",
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
  allow_productivity = true,
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
    {type = "item", name = "conjuration-orb", amount = 1},
    {type = "item", name = "magic-orb", amount = 1}
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
  energy_required = 4,
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
  allow_productivity = true,
  order = "a[conjuration-research-pack]"
})

-- Magic Science Pack
table.insert(recipes, {
  type = "recipe",
  name = "magic-science-pack",
  category = "orbs",
  subgroup = "orbs-research",
  energy_required = 3,
  icon = "__orbs__/graphics/magic-science-pack.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 2}
  },
  results = {
    {type = "item", name = "magic-science-pack", amount = 1},
    {type = "item", name = "magic-orb", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "a[magic-science-pack]"
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
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
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

-- Conjure Productivity Orb
table.insert(recipes, {
  type = "recipe",
  name = "conjure-productivity-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 5,
  icon = "__orbs__/graphics/productivity-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "gold-plate", amount = 4},
    {type = "item", name = "copper-cable", amount = 2},
    {type = "item", name = "dust-of-serendipity", amount = 1}
  },
  results = {
    {type = "item", name = "productivity-orb", amount = 1}
  },
  enabled = false,
  order = "f[conjure-productivity-orb]"
})

-- Conjure Cleansing Orb
table.insert(recipes, {
  type = "recipe",
  name = "conjure-cleansing-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 3,
  icon = "__orbs__/graphics/cleansing-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "fluid", name = "water", amount = 50},
    {type = "item", name = "dust-of-serendipity", amount = 1}
  },
  results = {
    {type = "item", name = "cleansing-orb", amount = 1}
  },
  enabled = false,
  order = "g[conjure-cleansing-orb]"
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
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1},
    {type = "item", name = "active-magic-shard", amount = 50}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "item", name = "unstable-orb-alpha", amount = 10, probability = 0.05}
  },
  enabled = false,
  allow_productivity = true,
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
    {type = "item", name = "unstable-orb-alpha", amount = 2, ignored_by_productivity = 2},
    {type = "item", name = "divination-essence", amount = 1}
  },
  reset_freshness_on_craft = true,
  allow_productivity = true,
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
    {type = "item", name = "divination-essence", amount = 2, ignored_by_stats = 2},
    {type = "item", name = "coal", amount = 1}
  },
  results = {
    {type = "item", name = "divination-essence", amount = 2, ignored_by_stats = 2},
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
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "item", name = "spark-of-luck", amount = 1, probability = 0.01}
  },
  enabled = false,
  allow_productivity = true,
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
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1},
    {type = "item", name = "dust-of-serendipity", amount = 1}
  },
  enabled = false,
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
  enabled = false,
  allow_productivity = true,
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
  subgroup = "divination",
  energy_required = 60,
  icon = "__orbs__/graphics/element-of-stability.png",
  icon_size = 1024,
  reset_freshness_on_craft = true,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1}
  },
  results = {
    {type = "item", name = "element-of-stability", amount = 1},
    {type = "item", name = "volatile-orb-Q", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-R", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-S", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-T", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-U", amount = 1, probability = 1/5}
  },
  enabled = false,
  order = "l[extract-stability]"
})

-- Liquify Stability Element
table.insert(recipes, {
  type = "recipe",
  name = "liquify-stability",
  category = "orbs",
  subgroup = "divination",
  energy_required = 3,
  icon = "__orbs__/graphics/stability-liquid.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "element-of-stability", amount = 1}
  },
  results = {
    {type = "fluid", name = "stability", amount = 225}
  },
  enabled = false,
  allow_productivity = true,
  order = "m[liquify-stability]"
})

-- Generate volatile orb manipulation recipes
-- For each pair of orbs i and j, the result is (i * j) % 7
-- If result is 1, create neutralize recipe that gives 2 magic orbs

local volatile_orb_names = {
  [2] = "Q",
  [3] = "R",
  [4] = "S",
  [5] = "T",
  [6] = "U"
}

local function get_orb_name(index)
  return "volatile-orb-" .. volatile_orb_names[index]
end

-- Helper function to create manipulation recipe icons showing "A × B" at top and result at bottom
local function create_manipulation_icon(base_icon, base_icon_size, input_a, input_b, result)
  local icons = {
    {
      icon = base_icon,
      icon_size = base_icon_size
    }
  }

  -- Add input A (top left)
  table.insert(icons, {
    icon = "__base__/graphics/icons/signal/signal_" .. volatile_orb_names[input_a] .. ".png",
    icon_size = 64,
    scale = 0.35,
    shift = {-12, -16}
  })

  -- Add × symbol (top center) - use signal-X
  table.insert(icons, {
    icon = "__base__/graphics/icons/signal/signal_X.png",
    icon_size = 64,
    scale = 0.25,
    shift = {0, -16}
  })

  -- Add input B (top right)
  table.insert(icons, {
    icon = "__base__/graphics/icons/signal/signal_" .. volatile_orb_names[input_b] .. ".png",
    icon_size = 64,
    scale = 0.35,
    shift = {12, -16}
  })

  -- Add result (bottom center)
  if result == 1 then
    -- For neutralization, show magic orb icon at bottom
    table.insert(icons, {
      icon = "__orbs__/graphics/magic-orb.png",
      icon_size = 1024,
      scale = 0.08,
      shift = {0, 16}
    })
  else
    -- For manipulation, show result letter
    table.insert(icons, {
      icon = "__base__/graphics/icons/signal/signal_" .. volatile_orb_names[result] .. ".png",
      icon_size = 64,
      scale = 0.4,
      shift = {0, 16}
    })
  end

  return icons
end

-- Helper function to create copy recipe icons showing magic orb + volatile orb + letter
local function create_copy_icon(base_icon, base_icon_size, letter_index)
  local icons = {
    {
      icon = base_icon,
      icon_size = base_icon_size
    }
  }

  -- Add magic orb (top left)
  table.insert(icons, {
    icon = "__orbs__/graphics/magic-orb.png",
    icon_size = 1024,
    scale = 0.08,
    shift = {-8, -16}
  })

  -- Add volatile orb (top right)
  table.insert(icons, {
    icon = "__orbs__/graphics/volatile-orb.png",
    icon_size = 1024,
    scale = 0.1,
    shift = {8, -16}
  })

  -- Add letter (bottom center)
  table.insert(icons, {
    icon = "__base__/graphics/icons/signal/signal_" .. volatile_orb_names[letter_index] .. ".png",
    icon_size = 64,
    scale = 0.5,
    shift = {0, 16}
  })

  return icons
end

for i = 2, 6 do
  for j = i, 6 do -- Only create recipes for j >= i to avoid duplicates
    local result = (i * j) % 7
    if result == 0 then result = 7 end -- Handle modulo 0 case but won't happen in 2-6 range

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
    -- Add stability liquid requirement
    table.insert(ingredients, {type = "fluid", name = "stability", amount = 50})

    if result == 1 then
      -- Neutralize recipe - gives 2 magic orbs
      table.insert(recipes, {
        type = "recipe",
        name = "neutralize-volatile-orb-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j],
        category = "orbs",
        subgroup = "orbs-volatile",
        hide_from_signal_gui = false,
        energy_required = 4.,
        icons = create_manipulation_icon("__orbs__/graphics/volatile-orb.png", 1024, i, j, 1),
        ingredients = ingredients,
        results = {
          {type = "item", name = "magic-orb", amount = 2}
        },
        enabled = false,
        order = "z[neutralize-volatile-orb-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j] .. "]"
      })
    else
      -- Manipulation recipe
      local result_orb = get_orb_name(result)
      table.insert(recipes, {
        type = "recipe",
        name = "volatile-orb-manipulation-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j],
        category = "orbs",
        subgroup = "orbs-volatile",
        hide_from_signal_gui = false,
        energy_required = 4.,
        icons = create_manipulation_icon("__orbs__/graphics/volatile-orb.png", 1024, i, j, result),
        ingredients = ingredients,
        results = {
          {type = "item", name = result_orb, amount = 1},
          {type = "item", name = "magic-orb", amount = 1}
        },
        enabled = false,
        order = "y[volatile-orb-manipulation-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j] .. "]"
      })
    end
  end
end

-- Generate volatile orb copy recipes
-- Each orb + magic orb = 2 of the same orb
for i = 2, 6 do
  local orb_name = get_orb_name(i)
  local letter_name = volatile_orb_names[i]
  table.insert(recipes, {
    type = "recipe",
    name = "copy-volatile-orb-" .. letter_name,
    hide_from_signal_gui = false,
    category = "orbs",
    subgroup = "orbs-volatile",
    energy_required = 2,
    icons = create_copy_icon("__orbs__/graphics/volatile-orb.png", 1024, i),
    ingredients = {
      {type = "item", name = orb_name, amount = 1},
      {type = "item", name = "magic-orb", amount = 1},
      {type = "fluid", name = "stability", amount = 50}
    },
    results = {
      {type = "item", name = orb_name, amount = 2}
    },
    enabled = false,
    order = "x[copy-volatile-orb-" .. string.format("%02d", i) .. "]"
  })
end

-- Magical Experience Recipe
table.insert(recipes, {
  type = "recipe",
  name = "magical-experience",
  category = "orbs",
  subgroup = "souls",
  energy_required = 60,
  icon = "__orbs__/graphics/soul.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "soul", amount = 1, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "soul", amount = 1, ignored_by_stats = 1, ignored_by_productivity = 1},
    {type = "fluid", name = "rage", amount = 500}
  },
  enabled = false,
  allow_productivity = true,
  order = "b[magical-experience]"
})

-- Rage Orb Recipe
table.insert(recipes, {
  type = "recipe",
  name = "rage-orb",
  category = "orbs",
  subgroup = "orbs-manifest",
  energy_required = 5,
  icon = "__orbs__/graphics/rage-orb.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "fluid", name = "rage", amount = 50}
  },
  results = {
    {type = "item", name = "rage-orb", amount = 1}
  },
  enabled = false,
  order = "k[rage-orb]"
})


-- Light Wood on Fire in Furnace (1 second)
table.insert(recipes, {
  type = "recipe",
  name = "light-wood",
  ingredients = {
    {type = "item", name = "wood", amount = 1}
  },
  results = {
    {type = "item", name = "burning-wood", amount = 1}
  },
  energy_required = 1,
  enabled = true,
  category = "smelting"
})

-- Light Coal on Fire in Furnace (1 second)
table.insert(recipes, {
  type = "recipe",
  name = "light-coal",
  ingredients = {
    {type = "item", name = "coal", amount = 1}
  },
  results = {
    {type = "item", name = "burning-coal", amount = 1}
  },
  energy_required = 1,
  enabled = true,
  category = "smelting"
})

-- Fire through Friction (assembler 1 only)
table.insert(recipes, {
  type = "recipe",
  name = "fire-through-friction",
  icon = "__orbs__/graphics/burning-wood.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "stick", amount = 1},
    {type = "item", name = "wood", amount = 1}
  },
  results = {
    {type = "item", name = "wood", amount = 1, probability=0.9},
    {type = "item", name = "burning-wood", amount = 1, probability = 0.1}
  },
  energy_required = 5,
  enabled = true,
  category = "crafting"
})

-- Stick Recipe
table.insert(recipes, {
  type = "recipe",
  name = "stick",
  ingredients = {
    {
      type = "item",
      name = "wood",
      amount = 1
    }
  },
  results = {
    {
      type = "item",
      name = "stick",
      amount = 8
    }
  },
  energy_required = 0.5,
  enabled = true,
  allow_productivity = true,
  category = "crafting"
})

-- Override assembling-machine-1 recipe
if data.raw.recipe["assembling-machine-1"] then
  data.raw.recipe["assembling-machine-1"].ingredients = {
    {type = "item", name = "iron-plate", amount = 9},
    {type = "item", name = "iron-gear-wheel", amount = 5},
    {type = "item", name = "copper-cable", amount = 6}
  }
end

-- Override offshore-pump recipe
if data.raw.recipe["offshore-pump"] then
  data.raw.recipe["offshore-pump"].ingredients = {
    {type = "item", name = "iron-gear-wheel", amount = 2},
    {type = "item", name = "iron-plate", amount = 1}
  }
end

-- Lock base recipes at start
local recipes_to_lock = {
  "burner-mining-drill",
  "iron-chest",
  "light-armor",
  "iron-gear-wheel"
}

for _, recipe_name in pairs(recipes_to_lock) do
  if data.raw.recipe[recipe_name] then
    data.raw.recipe[recipe_name].enabled = false
  end
end


-- Update fast inserter recipe to use new burner inserter
if data.raw.recipe["fast-inserter"] then
  data.raw.recipe["fast-inserter"].ingredients = {
    {type = "item", name = "burner-inserter", amount = 1},
    {type = "item", name = "copper-cable", amount = 8},
    {type = "item", name = "iron-plate", amount = 1}
  }
end

-- Update long-handed inserter recipe to use burner inserter
if data.raw.recipe["long-handed-inserter"] then
  data.raw.recipe["long-handed-inserter"].ingredients = {
    {type = "item", name = "burner-inserter", amount = 1},
    {type = "item", name = "iron-stick", amount = 1}
  }
end

-- Magic inserter recipes
table.insert(recipes, {
  type = "recipe",
  name = "magic-inserter",
  category = "crafting",
  subgroup = "inserter",
  energy_required = 3,
  icon = "__base__/graphics/icons/fast-inserter.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "burner-inserter", amount = 1},
    {type = "item", name = "magic-orb", amount = 2, ignored_by_stats = 1}
  },
  results = {
    {type = "item", name = "magic-inserter", amount = 1},
    {type = "item", name = "magic-orb", amount = 1, ignored_by_stats = 1}
  },
  enabled = false,
  order = "d[fast-inserter]"
})


-- Rune Word Recipes
table.insert(recipes, {
  type = "recipe",
  name = "conjure-rune-word-aqua",
  category = "orbs",
  subgroup = "orbs-runes",
  energy_required = 2,
  icon = "__base__/graphics/icons/signal/signal_A.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "active-magic-shard", amount = 1},
    {type = "item", name = "element-of-stability", amount = 1},
    {type = "fluid", name = "water", amount = 100}
  },
  results = {
    {type = "item", name = "rune-word-aqua", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "s[conjure-rune-word-aqua]"
})

table.insert(recipes, {
  type = "recipe",
  name = "conjure-rune-word-spiritus",
  category = "orbs",
  subgroup = "orbs-runes",
  energy_required = 2,
  icon = "__base__/graphics/icons/signal/signal_S.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "active-magic-shard", amount = 1},
    {type = "item", name = "element-of-stability", amount = 1}
  },
  results = {
    {type = "item", name = "rune-word-spiritus", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "s[conjure-rune-word-spiritus]"
})

-- Rune Research Pack recipe (requires 6 specific runes)
table.insert(recipes, {
  type = "recipe",
  name = "rune-research-pack",
  category = "runes",
  subgroup = "orbs-research",
  energy_required = 20,
  icon = "__base__/graphics/icons/utility-science-pack.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "rune-word-vitae", amount = 1},
    {type = "item", name = "rune-word-ignis", amount = 1},
    {type = "item", name = "rune-word-tempus", amount = 1},
    {type = "item", name = "rune-word-terra", amount = 1},
    {type = "item", name = "rune-word-umbra", amount = 1},
    {type = "item", name = "rune-word-mortis", amount = 1}
  },
  results = {
    {type = "item", name = "rune-research-pack", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  hidden = false,
  order = "d[rune-research-pack]"
})

-- Load the rune transformation chains
local rune_transformation_chains = require("rune-chains")

-- Create all transformation recipes
-- Each rune can transform into 5 different runes in sequence
local rune_recipes = {}
for source_rune, target_chain in pairs(rune_transformation_chains) do
  for i, target_rune in ipairs(target_chain) do
    local recipe_name = "transform-" .. source_rune .. "-to-" .. target_rune .. "-" .. i

    -- Get the target rune item's icon properties
    local target_item = data.raw.item[target_rune]
    local recipe_icon = target_item and target_item.icon or "__base__/graphics/icons/signal/signal_R.png"
    local recipe_icon_size = target_item and target_item.icon_size or 64

    table.insert(rune_recipes, {
      type = "recipe",
      name = recipe_name,
      category = "rune-transformation",
      energy_required = 0.2,
      icon = recipe_icon,
      icon_size = recipe_icon_size,
      ingredients = {
        {type = "item", name = source_rune, amount = 1}
      },
      results = {
        {type = "item", name = target_rune, amount = 1}
      },
      enabled = true,
      hidden = true -- Hide from player recipe list
    })
  end
end

-- Add all rune transformation recipes
for _, recipe in pairs(rune_recipes) do
  table.insert(recipes, recipe)
end

-- Transmutation recipes
table.insert(recipes, {
  type = "recipe",
  name = "transmute-copper-to-iron",
  category = "orbs",
  subgroup = "orbs-transmutation",
  energy_required = 1,
  icon = "__base__/graphics/icons/iron-plate.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "copper-plate", amount = 2}
  },
  results = {
    {type = "item", name = "iron-plate", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "t[transmute-copper-to-iron]"
})

table.insert(recipes, {
  type = "recipe",
  name = "transmute-iron-to-copper",
  category = "orbs",
  subgroup = "orbs-transmutation",
  energy_required = 1,
  icon = "__base__/graphics/icons/copper-plate.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "iron-plate", amount = 2}
  },
  results = {
    {type = "item", name = "copper-plate", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "t[transmute-iron-to-copper]"
})

table.insert(recipes, {
  type = "recipe",
  name = "transmute-copper-to-gold",
  category = "orbs",
  subgroup = "orbs-transmutation",
  energy_required = 2,
  icon = "__orbs__/graphics/gold-plate.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "copper-plate", amount = 3}
  },
  results = {
    {type = "item", name = "gold-plate", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "u[transmute-copper-to-gold]"
})

table.insert(recipes, {
  type = "recipe",
  name = "transmute-gold-to-copper",
  category = "orbs",
  subgroup = "orbs-transmutation",
  energy_required = 2,
  icon = "__base__/graphics/icons/copper-plate.png",
  icon_size = 64,
  ingredients = {
    {type = "item", name = "gold-plate", amount = 2}
  },
  results = {
    {type = "item", name = "copper-plate", amount = 1}
  },
  enabled = false,
  allow_productivity = true,
  order = "u[transmute-gold-to-copper]"
})

-- Stone to Sand recipe (for crusher)
table.insert(recipes, {
  type = "recipe",
  name = "stone-to-sand",
  category = "crushing",
  energy_required = 2,
  icon = "__orbs__/graphics/sand.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "stone", amount = 1}
  },
  results = {
    {type = "item", name = "sand", amount = 2}
  },
  enabled = false
})

-- Sand to Glass recipe (for furnace)
table.insert(recipes, {
  type = "recipe",
  name = "sand-to-glass",
  category = "smelting",
  energy_required = 3,
  icon = "__orbs__/graphics/glass.png",
  icon_size = 1024,
  ingredients = {
    {type = "item", name = "sand", amount = 1}
  },
  results = {
    {type = "item", name = "glass", amount = 1}
  },
  enabled = false
})

-- Extend all recipes
data:extend(recipes)
