-- data.lua
-- Main data file that includes all other data files

require("categories")
require("entities")  -- Load entities before items so cloud entities exist when ammo references them
require("item")
require("recipe")
require("technology")
require("achievements")
