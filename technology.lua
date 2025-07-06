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
    icon = "__orbs__/graphics/telekinesis_technology.png",
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

-- Override circuit network technology to make it cheaper
data.raw["technology"]["circuit-network"].unit = {
  count = 10,
  ingredients = {
    {"automation-science-pack", 1}
  },
  time = 30
}
data.raw["technology"]["circuit-network"].prerequisites = {"automation"}
