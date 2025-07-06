-- entities.lua

-- Create the conjuration machine
local conjuration_machine = util.table.deepcopy(data.raw["assembling-machine"]["assembling-machine-2"])

conjuration_machine.name = "conjuration-machine"
conjuration_machine.minable = {mining_time = 0.2, result = "conjuration-machine"}
conjuration_machine.crafting_categories = {"orbs"} -- ONLY orbs category
conjuration_machine.crafting_speed = 1
conjuration_machine.energy_source = {type = "void"} -- No power required
conjuration_machine.energy_usage = "1W" -- Minimal energy usage
conjuration_machine.allowed_effects = {"speed"} -- Allow speed effects for haste orbs
conjuration_machine.effect_receiver = {
  base_effect = {},
  uses_module_effects = true,
  uses_beacon_effects = false, -- Prevent beacon effects
  uses_surface_effects = true
}
conjuration_machine.module_specification = {
  module_slots = 3,
  module_info_icon_shift = {0, 0.5},
  module_info_multi_row_initial_height_modifier = -0.3
}
conjuration_machine.allowed_module_categories = {"orb-speed"} -- Only allow orb-speed modules (haste orbs)
conjuration_machine.module_slots = 3

-- Create the item for the conjuration machine
data:extend({
  conjuration_machine,
  {
    type = "item",
    name = "conjuration-machine",
    icon = "__base__/graphics/icons/assembling-machine-2.png",
    icon_size = 64,
    subgroup = "orbs-machines", -- New subgroup for machines
    order = "z[conjuration-machine]",
    place_result = "conjuration-machine",
    stack_size = 50
  }
})

-- Recipe to craft the conjuration machine (stays in crafting category)
data:extend({
  {
    type = "recipe",
    name = "craft-conjuration-machine",
    category = "crafting", -- Stays in crafting category so conjuration machine can't craft itself
    energy_required = 5,
    icon = "__base__/graphics/icons/assembling-machine-2.png",
    icon_size = 64,
    ingredients = {
      {type = "item", name = "assembling-machine-1", amount = 1},
      {type = "item", name = "copper-cable", amount = 20},
      {type = "item", name = "iron-plate", amount = 5},
      {type = "item", name = "conjuration-orb", amount = 1}
    },
    results = {
      {type = "item", name = "conjuration-machine", amount = 1}
    },
    enabled = true
  }
})
