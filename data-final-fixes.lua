-- data-final-fixes.lua
-- Override Nanobots2 technologies and items to use magical theming

-- Check if Nanobots2 is loaded
if mods["Nanobots2"] then
  
  -- Override main nanobots technology
  if data.raw.technology["nanobots"] then
    local tech = data.raw.technology["nanobots"]
    tech.icon = "__orbs__/graphics/summoning-technology.png"
    tech.icon_size = 1024
    tech.prerequisites = {"orbs-technology"}
    tech.unit.count = 20
    tech.unit.ingredients = {{"conjuration-research-pack", 1}}
    tech.localised_name = {"technology-name.summon-machines"}
    tech.localised_description = {"technology-description.summon-machines"}
  end
  
  -- Override nanobots cliff technology
  if data.raw.technology["nanobots-cliff"] then
    local tech = data.raw.technology["nanobots-cliff"]
    tech.icon = "__orbs__/graphics/cliff-explosion.png"
    tech.icon_size = 1024
    tech.prerequisites = {"nanobots"}
    tech.unit.count = 50
    tech.unit.ingredients = {{"conjuration-research-pack", 1}}
    tech.localised_name = {"technology-name.mystic-explosives"}
    tech.localised_description = {"technology-description.mystic-explosives"}
  end
  
  -- Override nano range technologies
  for i = 1, 4 do
    if data.raw.technology["nano-range-" .. i] then
      local tech = data.raw.technology["nano-range-" .. i]
      -- Update prerequisites
      if i == 1 then
        tech.prerequisites = {"nanobots"}
      else
        tech.prerequisites = {"nano-range-" .. (i-1)}
      end
      tech.unit.count = 20 * math.pow(2, i-1) -- 20, 40, 80, 160
      tech.unit.ingredients = {{"conjuration-research-pack", 1}}
      tech.localised_name = {"technology-name.summoning-range-" .. i}
      tech.localised_description = {"technology-description.summoning-range-" .. i}
    end
  end
  
  -- Override nano speed technologies
  for i = 1, 4 do
    if data.raw.technology["nano-speed-" .. i] then
      local tech = data.raw.technology["nano-speed-" .. i]
      -- Update prerequisites
      if i == 1 then
        tech.prerequisites = {"nanobots"}
      else
        tech.prerequisites = {"nano-speed-" .. (i-1)}
      end
      tech.unit.count = 20 * math.pow(2, i-1) -- 20, 40, 80, 160
      tech.unit.ingredients = {{"conjuration-research-pack", 1}}
      tech.localised_name = {"technology-name.summoning-speed-" .. i}
      tech.localised_description = {"technology-description.summoning-speed-" .. i}
    end
  end
  
  -- Remove roboport interface technology completely
  if data.raw.technology["roboport-interface"] then
    data.raw.technology["roboport-interface"] = nil
  end
  
  -- Override nano gun item
  if data.raw.gun["gun-nano-emitter"] then
    local gun = data.raw.gun["gun-nano-emitter"]
    gun.icon = "__orbs__/graphics/magic-wand.png"
    gun.icon_size = 1024
    gun.localised_name = {"item-name.magic-wand"}
    gun.localised_description = {"item-description.magic-wand"}
  end
  
  -- Override nano gun recipe
  if data.raw.recipe["gun-nano-emitter"] then
    local recipe = data.raw.recipe["gun-nano-emitter"]
    recipe.icon = "__orbs__/graphics/magic-wand.png"
    recipe.icon_size = 1024
    recipe.localised_name = {"item-name.magic-wand"}
    recipe.localised_description = {"item-description.magic-wand"}
    -- Update recipe to use magical ingredients
    recipe.ingredients = {
      {type = "item", name = "wood", amount = 1},
      {type = "item", name = "active-magic-shard", amount = 10}
    }
  end
  
  -- Override ammo category
  if data.raw["ammo-category"]["nano-ammo"] then
    local ammo_cat = data.raw["ammo-category"]["nano-ammo"]
    ammo_cat.localised_name = {"ammo-category-name.spirit-ammo"}
    ammo_cat.localised_description = {"ammo-category-description.spirit-ammo"}
  end
  
  -- Update all ammo items to use spirit theming
  local ammo_items = {
    ["ammo-nano-termites"] = "tree-conflagration-essence",
    ["ammo-nano-scrappers"] = "summoning-essence", 
    ["ammo-nano-constructors"] = "summoning-essence",
    ["ammo-nano-deconstructors"] = "summoning-essence"
  }
  
  for old_name, new_name in pairs(ammo_items) do
    if data.raw.ammo[old_name] then
      local ammo = data.raw.ammo[old_name]
      ammo.localised_name = {"item-name." .. new_name}
      ammo.localised_description = {"item-description." .. new_name}
      if old_name == "ammo-nano-termites" then
        ammo.icon = "__orbs__/graphics/tree-conflagration-essence.png"
        ammo.icon_size = 1024
      else
        ammo.icon = "__orbs__/graphics/summoning-essence.png"
        ammo.icon_size = 1024
      end
    end
  end
  
  -- Update ammo recipes to use magical ingredients
  local ammo_recipes = {
    "ammo-nano-termites",
    "ammo-nano-scrappers", 
    "ammo-nano-constructors",
    "ammo-nano-deconstructors"
  }
  
  for _, recipe_name in pairs(ammo_recipes) do
    if data.raw.recipe[recipe_name] then
      local recipe = data.raw.recipe[recipe_name]
      recipe.ingredients = {
        {type = "item", name = "active-magic-shard", amount = 1},
        {type = "item", name = "iron-stick", amount = 1}
      }
      -- Update the localized names for recipes too
      if recipe_name == "ammo-nano-termites" then
        recipe.localised_name = {"item-name.tree-conflagration-essence"}
        recipe.icon = "__orbs__/graphics/tree-conflagration-essence.png"
        recipe.icon_size = 1024
        recipe.localised_description = {"item-description.tree-conflagration-essence"}
      else
        recipe.localised_name = {"item-name.summoning-essence"}
        recipe.icon = "__orbs__/graphics/summoning-essence.png"
        recipe.icon_size = 1024
        recipe.localised_description = {"item-description.summoning-essence"}
      end
    end
  end
  
end
