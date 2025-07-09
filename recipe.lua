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
    {type = "item", name = "volatile-orb-Q", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-R", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-S", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-T", amount = 1, probability = 1/5},
    {type = "item", name = "volatile-orb-U", amount = 1, probability = 1/5}
  },
  enabled = false,
  order = "l[extract-stability]"
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

    if result == 1 then
      -- Neutralize recipe - gives 2 magic orbs
      table.insert(recipes, {
        type = "recipe",
        name = "neutralize-volatile-orb-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j],
        category = "orbs",
        subgroup = "orbs-manifest",
        hide_from_signal_gui = false,
        energy_required = 0.5,
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
        subgroup = "orbs-manifest",
        hide_from_signal_gui = false,
        energy_required = 0.5,
        icons = create_manipulation_icon("__orbs__/graphics/volatile-orb.png", 1024, i, j, result),
        ingredients = ingredients,
        results = {
          {type = "item", name = result_orb, amount = 1}
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
    subgroup = "orbs-manifest",
    energy_required = 1,
    icons = create_copy_icon("__orbs__/graphics/volatile-orb.png", 1024, i),
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
    {type = "item", name = "soul", amount = 1}
  },
  results = {
    {type = "item", name = "soul", amount = 1},
    {type = "fluid", name = "rage", amount = 500}
  },
  enabled = false,
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
    {type = "item", name = "magic-orb", amount = 2},
    {type = "fluid", name = "rage", amount = 50}
  },
  results = {
    {type = "item", name = "magic-orb", amount = 1},
    {type = "item", name = "rage-orb", amount = 1}
  },
  enabled = false,
  order = "k[rage-orb]"
})

-- Extend all recipes
data:extend(recipes)
