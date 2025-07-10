-- rune-chains.lua
-- Shared rune transformation chains data

local rune_transformation_chains = {
  ["rune-word-ignis"] = {"rune-word-aqua", "rune-word-terra", "rune-word-lux", "rune-word-umbra", "rune-word-tempus"},
  ["rune-word-aqua"] = {"rune-word-ventus", "rune-word-ignis", "rune-word-vitae", "rune-word-mortis", "rune-word-terra"},
  ["rune-word-ventus"] = {"rune-word-terra", "rune-word-aqua", "rune-word-tempus", "rune-word-lux", "rune-word-ignis"},
  ["rune-word-terra"] = {"rune-word-lux", "rune-word-ventus", "rune-word-umbra", "rune-word-vitae", "rune-word-aqua"},
  ["rune-word-umbra"] = {"rune-word-mortis", "rune-word-lux", "rune-word-ignis", "rune-word-tempus", "rune-word-vitae"},
  ["rune-word-lux"] = {"rune-word-tempus", "rune-word-umbra", "rune-word-vitae", "rune-word-aqua", "rune-word-mortis"},
  ["rune-word-tempus"] = {"rune-word-vitae", "rune-word-ignis", "rune-word-mortis", "rune-word-ventus", "rune-word-umbra"},
  ["rune-word-vitae"] = {"rune-word-umbra", "rune-word-tempus", "rune-word-aqua", "rune-word-ignis", "rune-word-lux"},
  ["rune-word-mortis"] = {"rune-word-ignis", "rune-word-vitae", "rune-word-ventus", "rune-word-terra", "rune-word-tempus"}
}

return rune_transformation_chains


-- rune word ideas:
-- VITRUM - glass
-- RITUS - rite
-- ASTRUM - star
-- MIRUS - wondrous
-- ULTRA - beyond
-- ATRUM - dark
-- PRIMA - first
-- VIRTUS, VIS - power, force
-- IMPURA - unclean
-- PRISMA - prism
-- SILVA - forest
-- RATUS - calculated / reasoned
