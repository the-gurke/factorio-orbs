-- technology.lua
-- Define research technologies

data:extend({
  {
    type = "technology",
    name = "orbs-technology",
    icon = "__orbs__/graphics/orb-initial-technology.png",
    icon_size = 1024,
    prerequisites = {"automation"},
    unit = {
      count = 10,
      ingredients = {
        {"automation-science-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-0"
      },
      {
        type = "unlock-recipe",
        recipe = "replicate-shards"
      },
      {
        type = "unlock-recipe",
        recipe = "manifest-orb"
      },
      {
        type = "unlock-recipe",
        recipe = "transfigure-conjuration-orb"
      },
      {
        type = "unlock-recipe",
        recipe = "neutralize-conjuration-orb"
      },
      {
        type = "unlock-recipe",
        recipe = "conjuration-research-pack"
      },
      {
        type = "unlock-recipe",
        recipe = "craft-conjuration-machine"
      },
      {
        type = "unlock-recipe",
        recipe = "craft-conjuration-lab"
      }
    },
    order = "a-h-a"
  },
  {
    type = "technology",
    name = "haste-orb",
    icon = "__orbs__/graphics/haste-orb.png",
    icon_size = 1024,
    prerequisites = {"orbs-technology"},
    unit = {
      count = 100,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "transfigure-haste-orb"
      },
      {
        type = "unlock-recipe",
        recipe = "neutralize-haste-orb"
      }
    },
    order = "a-h-b"
  },
  {
    type = "technology",
    name = "conjure-shards-i",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"orbs-technology"},
    unit = {
      count = 10,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-1"
      }
    },
    order = "a-h-c"
  },
  {
    type = "technology",
    name = "conjure-shards-ii",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-i"},
    unit = {
      count = 20,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-2"
      }
    },
    order = "a-h-d"
  },
  {
    type = "technology",
    name = "conjure-shards-iv",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-ii"},
    unit = {
      count = 40,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-4"
      }
    },
    order = "a-h-e"
  },
  {
    type = "technology",
    name = "conjure-shards-viii",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-iv"},
    unit = {
      count = 80,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-8"
      }
    },
    order = "a-h-f"
  },
  {
    type = "technology",
    name = "conjure-shards-xvi",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-viii"},
    unit = {
      count = 160,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-16"
      }
    },
    order = "a-h-g"
  },
  {
    type = "technology",
    name = "conjure-shards-xxxii",
    icon = "__orbs__/graphics/conjure-shards.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-xvi"},
    unit = {
      count = 320,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-32"
      }
    },
    order = "a-h-h"
  },
  {
    type = "technology",
    name = "replicate-shards-ii",
    icon = "__orbs__/graphics/active-magic-shard.png",
    icon_size = 1024,
    prerequisites = {"conjure-shards-iv"},
    unit = {
      count = 50,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "replicate-shards-2"
      }
    },
    order = "a-h-i"
  },
  {
    type = "technology",
    name = "banish-shards",
    icon = "__orbs__/graphics/inactive-magic-shard.png",
    icon_size = 1024,
    prerequisites = {"orbs-technology"},
    unit = {
      count = 20,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "banish-shards"
      }
    },
    order = "a-h-j"
  },
  {
    type = "technology",
    name = "unstable-orb",
    icon = "__orbs__/graphics/unstable-orb-alpha.png",
    icon_size = 1024,
    prerequisites = {"orbs-technology"},
    unit = {
      count = 100,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-unstable-orb"
      },
      {
        type = "unlock-recipe",
        recipe = "align-unstable-orb"
      }
    },
    order = "a-h-k"
  },
  {
    type = "technology",
    name = "divination-essence",
    icon = "__orbs__/graphics/divination-essence.png",
    icon_size = 1024,
    prerequisites = {"unstable-orb"},
    unit = {
      count = 100,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-divination-essence"
      }
    },
    order = "a-h-l"
  },
  {
    type = "technology",
    name = "stabilize-divination-essence",
    icon = "__orbs__/graphics/divination-essence.png",
    icon_size = 1024,
    prerequisites = {"divination-essence"},
    unit = {
      count = 200,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "stabilize-divination-essence"
      }
    },
    order = "a-h-m"
  },
  {
    type = "technology",
    name = "magic-grenade",
    icon = "__orbs__/graphics/magic-grenade.png",
    icon_size = 1024,
    prerequisites = {"orbs-technology"},
    unit = {
      count = 50,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "magic-grenade"
      }
    },
    order = "a-h-z"
  },
  {
    type = "technology",
    name = "divination",
    icon = "__orbs__/graphics/divination-research-pack.png",
    icon_size = 1024,
    prerequisites = {"divination-essence"},
    unit = {
      count = 200,
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "conjure-serendipity"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-luck"
      },
      {
        type = "unlock-recipe",
        recipe = "divination-research-pack"
      }
    },
    order = "a-h-n"
  },
  {
    type = "technology",
    name = "soul-collection",
    icon_size = 1024,
    icon = "__orbs__/graphics/soul-collector.png",
    effects = {
      {
        type = "unlock-recipe",
        recipe = "craft-soul-collector"
      }
    },
    prerequisites = {"divination"},
    unit = {
      count = 50,
      ingredients = {
        {"conjuration-research-pack", 1},
        {"divination-research-pack", 1}
      },
      time = 30
    },
    order = "z-a[soul-collection]"
  },
  {
    type = "technology",
    name = "stability-extraction",
    icon_size = 1024,
    icon = "__orbs__/graphics/element-of-stability.png",
    effects = {},
    prerequisites = {"divination"},
    unit = {
      count = 100,
      ingredients = {
        {"conjuration-research-pack", 1},
        {"divination-research-pack", 1}
      },
      time = 30
    },
    order = "z-b[stability-extraction]"
  },
  {
    type = "technology",
    name = "rage-orb",
    icon = "__orbs__/graphics/rage-orb.png",
    icon_size = 1024,
    prerequisites = {"divination"},
    unit = {
      count = 100,
      ingredients = {
        {"conjuration-research-pack", 1},
        {"divination-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "magical-experience"
      },
      {
        type = "unlock-recipe",
        recipe = "rage-orb"
      }
    },
    order = "z-b[rage-orb]"
  },
  {
    type = "technology",
    name = "ragethrower",
    icon = "__base__/graphics/technology/flamethrower.png",
    icon_size = 256,
    prerequisites = {"rage-orb"},
    unit = {
      count = 50,
      ingredients = {
        {"conjuration-research-pack", 1},
        {"divination-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "unlock-recipe",
        recipe = "ragethrower-turret"
      }
    },
    order = "z-c[ragethrower]"
  }
})

-- Telekinesis technologies (10 tiers)
local telekinesis_technologies = {}
for i = 1, 10 do
  table.insert(telekinesis_technologies, {
    type = "technology",
    name = "telekinesis-" .. i,
    localised_name = {"technology-name.telekinesis-" .. i},
    localised_description = {"technology-description.telekinesis-" .. i},
    icon = "__orbs__/graphics/telekinesis-technology.png",
    icon_size = 1024,
    prerequisites = i == 1 and {"orbs-technology"} or {"telekinesis-" .. (i-1)},
    unit = {
      count = math.pow(2, i-1), -- 2^(i-1): 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
      ingredients = {
        {"conjuration-research-pack", 1}
      },
      time = 30
    },
    effects = {
      {
        type = "character-build-distance",
        modifier = 9 -- +9 build distance per tier (90 total)
      },
      {
        type = "character-reach-distance",
        modifier = 9 -- +9 reach distance per tier (90 total)
      },
      {
        type = "character-resource-reach-distance",
        modifier = 9 -- +9 resource reach distance per tier (90 total)
      },
      {
        type = "character-item-drop-distance",
        modifier = 9 -- +9 item drop distance per tier (90 total)
      }
    },
    order = "a-h-c-" .. string.format("%02d", i)
  })
end

data:extend(telekinesis_technologies)

-- Add volatile orb recipes to the stability-extraction technology
local volatile_orb_tech = data.raw["technology"]["stability-extraction"]
if volatile_orb_tech then
  local volatile_orb_names = {
    [2] = "Q",
    [3] = "R",
    [4] = "S",
    [5] = "T",
    [6] = "U"
  }

  -- Add extract stability recipe
  table.insert(volatile_orb_tech.effects, {
    type = "unlock-recipe",
    recipe = "extract-stability"
  })
  
  -- Add liquify stability recipe
  table.insert(volatile_orb_tech.effects, {
    type = "unlock-recipe",
    recipe = "liquify-stability"
  })

  -- Add copy recipes for all volatile orbs
  for i = 2, 6 do
    table.insert(volatile_orb_tech.effects, {
      type = "unlock-recipe",
      recipe = "copy-volatile-orb-" .. volatile_orb_names[i]
    })
  end

  -- Add manipulation and neutralization recipes
  for i = 2, 6 do
    for j = i, 6 do
      local result = (i * j) % 7
      if result == 0 then result = 7 end

      if result == 1 then
        -- Neutralization recipe
        table.insert(volatile_orb_tech.effects, {
          type = "unlock-recipe",
          recipe = "neutralize-volatile-orb-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j]
        })
      else
        -- Manipulation recipe
        table.insert(volatile_orb_tech.effects, {
          type = "unlock-recipe",
          recipe = "volatile-orb-manipulation-" .. volatile_orb_names[i] .. "-" .. volatile_orb_names[j]
        })
      end
    end
  end
end

-- Override circuit network technology to make it cheaper
data.raw["technology"]["circuit-network"].unit = {
  count = 10,
  ingredients = {
    {"automation-science-pack", 1}
  },
  time = 30
}
data.raw["technology"]["circuit-network"].prerequisites = {"automation"}
