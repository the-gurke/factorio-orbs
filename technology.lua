-- technology.lua
-- Define research technologies

data:extend({
  {
    type = "technology",
    name = "orbs-technology",
    icon = "__orbs__/graphics/orb_initial_technology.png",
    icon_size = 1024,
    prerequisites = {"circuit-network"},
    unit = {
      count = 50,
      ingredients = {
        {"automation-science-pack", 1},
        {"logistic-science-pack", 1},
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
        recipe = "conjure-shards-1"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-2"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-4"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-8"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-16"
      },
      {
        type = "unlock-recipe",
        recipe = "conjure-shards-32"
      },
      {
        type = "unlock-recipe",
        recipe = "replicate-shards"
      },
      {
        type = "unlock-recipe",
        recipe = "replicate-shards-2"
      },
      {
        type = "unlock-recipe",
        recipe = "banish-shards"
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
  }
})
