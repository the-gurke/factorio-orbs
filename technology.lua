-- technology.lua
-- Define research technologies

data:extend({
  {
    type = "technology",
    name = "orbs-technology",
    icon = "__orbs__/graphics/orb_initial_technology.png",
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
  }
})

-- Override circuit network technology to make it cheaper
data.raw["technology"]["circuit-network"].unit = {
  count = 10,
  ingredients = {
    {"automation-science-pack", 1}
  },
  time = 30
}
data.raw["technology"]["circuit-network"].prerequisites = {"automation"}
