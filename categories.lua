-- categories.lua
-- Define the new crafting categories and recipe groups

-- Create the orbs recipe category
data:extend({
  {
    type = "recipe-category",
    name = "orbs"
  }
})

-- Create the custom orb-speed module category
data:extend({
  {
    type = "module-category",
    name = "orb-speed"
  }
})

-- Create the orbs item group
data:extend({
  {
    type = "item-group",
    name = "orbs",
    order = "z",
    icon = "__orbs__/graphics/magic-orb.png",
    icon_size = 1024
  }
})

-- Create subgroups for organizing recipes within the orbs tab
data:extend({
  {
    type = "item-subgroup",
    name = "orbs-conjure",
    group = "orbs",
    order = "a"
  },
  {
    type = "item-subgroup",
    name = "orbs-proliferate",
    group = "orbs",
    order = "b"
  },
  {
    type = "item-subgroup",
    name = "orbs-manifest",
    group = "orbs",
    order = "c"
  },
  {
    type = "item-subgroup",
    name = "orbs-research",
    group = "orbs",
    order = "d"
  },
  {
    type = "item-subgroup",
    name = "orbs-machines",
    group = "orbs",
    order = "e"
  }
})
