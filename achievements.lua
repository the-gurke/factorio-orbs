-- achievements.lua
-- Defines custom achievements for the Orbs mod

data:extend({
  {
    type = "kill-achievement",
    name = "fishy-business",
    order = "a[combat]-a[fish]",
    icon = "__orbs__/graphics/achievements/fish-kill.png",
    icon_size = 1024,
    to_kill = "small-biter",
    type_to_kill = "unit",
    damage_type = "fish",
    amount = 1
  }
})
