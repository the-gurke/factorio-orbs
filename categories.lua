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
    name = "orbs-shards",
    group = "orbs",
    order = "b"
  },
  {
    type = "item-subgroup",
    name = "souls",
    group = "orbs",
    order = "c"
  },
  {
    type = "item-subgroup",
    name = "divination",
    group = "orbs",
    order = "d"
  },
  {
    type = "item-subgroup",
    name = "orbs-volatile",
    group = "orbs",
    order = "e"
  },
  {
    type = "item-subgroup",
    name = "orbs-transmutation",
    group = "orbs",
    order = "f"
  },
  {
    type = "item-subgroup",
    name = "orbs-runes",
    group = "orbs",
    order = "g"
  },
  {
    type = "item-subgroup",
    name = "orbs-research",
    group = "orbs",
    order = "h"
  },
  {
    type = "item-subgroup",
    name = "orbs-machines",
    group = "orbs",
    order = "i"
  }
})

-- Recipe categories
data:extend({
  {
    type = "recipe-category",
    name = "orbs"
  },
  {
    type = "recipe-category",
    name = "runes"
  },
  {
    type = "recipe-category",
    name = "rune-transformation"
  },
  {
    type = "recipe-category",
    name = "crushing"
  },
  {
    type = "recipe-category",
    name = "distilling"
  }
})

-- Module categories for orb modules
data:extend({
  {
    type = "module-category",
    name = "orb-speed"
  },
  {
    type = "module-category",
    name = "orb-productivity"
  },
  {
    type = "module-category",
    name = "orb-pollution"
  }
})
