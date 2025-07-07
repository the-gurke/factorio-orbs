-- categories.lua
-- Define new item groups and subgroups

-- Main item group for Orbs
data:extend({
  {
    type = "item-group",
    name = "orbs",
    order = "z",
    icon = "__orbs__/graphics/orb-initial-technology.png",
    icon_size = 1024
  }
})

-- Subgroups for organizing items within the Orbs group
data:extend({
  {
    type = "item-subgroup",
    name = "orbs-manifest",
    group = "orbs",
    order = "a"
  },
  {
    type = "item-subgroup",
    name = "orbs-conjure",
    group = "orbs",
    order = "b"
  },
  {
    type = "item-subgroup",
    name = "orbs-proliferate",
    group = "orbs",
    order = "c"
  },
  {
    type = "item-subgroup",
    name = "souls",
    group = "orbs",
    order = "d"
  },
  {
    type = "item-subgroup",
    name = "divination",
    group = "orbs",
    order = "e"
  },
  {
    type = "item-subgroup",
    name = "orbs-research",
    group = "orbs",
    order = "f"
  },
  {
    type = "item-subgroup",
    name = "orbs-machines",
    group = "orbs",
    order = "g"
  }
})

-- Recipe categories
data:extend({
  {
    type = "recipe-category",
    name = "orbs"
  }
})

-- Module categories for orb modules
data:extend({
  {
    type = "module-category",
    name = "orb-speed"
  }
})
