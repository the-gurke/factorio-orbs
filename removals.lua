-- removals.lua
-- Remove unwanted items and technologies from the base game

-- Remove specific technologies
local technologies_to_remove = {
  "logistic-science-pack",
  "radar",
  "gun-turret",
  "steel-processing",
  "military",
  "fast-inserter",
  "steam-power",
  "electronics"
}

-- Remove all technologies that require logistic-science-pack
for tech_name, tech in pairs(data.raw.technology) do
  if tech.unit and tech.unit.ingredients then
    for _, ingredient in pairs(tech.unit.ingredients) do
      if ingredient[1] == "logistic-science-pack" or ingredient.name == "logistic-science-pack" then
        table.insert(technologies_to_remove, tech_name)
        break
      end
    end
  end
end

-- Remove the specified technologies
for _, tech_name in pairs(technologies_to_remove) do
  if data.raw.technology[tech_name] then
    data.raw.technology[tech_name] = nil
  end
end

-- Hide unwanted items instead of removing them to avoid reference errors
local items_to_hide = {
  "small-electric-pole",
  "biolab"
}

for _, item_name in pairs(items_to_hide) do
  if data.raw.item[item_name] then
    data.raw.item[item_name].hidden = true
  end
  if data.raw.recipe[item_name] then
    data.raw.recipe[item_name].enabled = false
    data.raw.recipe[item_name].hidden = true
  end
end

-- Clean up broken references (iteratively remove dependent items)
-- Technologies that depend on removed technologies
local removed_any = true
while removed_any do
  removed_any = false
  for tech_name, tech in pairs(data.raw.technology) do
    if tech.prerequisites then
      for _, prereq in pairs(tech.prerequisites) do
        if not data.raw.technology[prereq] then
          data.raw.technology[tech_name] = nil
          removed_any = true
          break
        end
      end
    end
  end
end

-- Function to recursively check triggers for deleted technologies
local function has_deleted_tech(trigger_obj)
  if not trigger_obj then return false end
  if trigger_obj.technology and not data.raw.technology[trigger_obj.technology] then
    return true
  end
  if trigger_obj.triggers then
    for _, nested_trigger in pairs(trigger_obj.triggers) do
      if has_deleted_tech(nested_trigger) then return true end
    end
  end
  return false
end

-- Clean up UI elements that reference deleted content
local ui_types = {
  ["tips-and-tricks-item"] = function(item)
    return has_deleted_tech(item.trigger) or has_deleted_tech(item.skip_trigger)
  end,
  ["research-achievement"] = function(item)
    return item.technology and not data.raw.technology[item.technology]
  end,
  ["shortcut"] = function(item)
    return item.technology_to_unlock and not data.raw.technology[item.technology_to_unlock]
  end
}

for ui_type, check_func in pairs(ui_types) do
  for item_name, item in pairs(data.raw[ui_type] or {}) do
    if check_func(item) then
      data.raw[ui_type][item_name] = nil
    end
  end
end

-- Clean up tips-and-tricks dependencies (iteratively)
local tips_removed_any = true
while tips_removed_any do
  tips_removed_any = false
  for tip_name, tip in pairs(data.raw["tips-and-tricks-item"] or {}) do
    if tip.dependencies then
      for _, dep in pairs(tip.dependencies) do
        if not data.raw["tips-and-tricks-item"][dep] then
          data.raw["tips-and-tricks-item"][tip_name] = nil
          tips_removed_any = true
          break
        end
      end
    end
  end
end
