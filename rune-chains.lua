-- rune-chains.lua
-- Shared rune transformation chains data

local rune_transformation_chains = {
  ["rune-word-aqua"] = {"rune-word-aqua", "rune-word-aqua", "rune-word-aqua", "rune-word-ventus"},
  ["rune-word-ventus"] = {"rune-word-aqua", "rune-word-aqua", "rune-word-ventus", "rune-word-aqua", "rune-word-ignis"},
  ["rune-word-ignis"] = {"rune-word-aqua", "rune-word-ventus", "rune-word-terra", "rune-word-lux"},
  ["rune-word-terra"] = {"rune-word-ventus", "rune-word-ignis", "rune-word-lux", "rune-word-ventus", "rune-word-aqua", "rune-word-umbra"},
  ["rune-word-lux"] = {"rune-word-ventus", "rune-word-ventus", "rune-word-ignis", "rune-word-aqua", "rune-word-ventus"},
  ["rune-word-umbra"] = {"rune-word-mortis", "rune-word-tempus", "rune-word-terra"},
  ["rune-word-tempus"] = {"rune-word-tempus", "rune-word-tempus", "rune-word-tempus", "rune-word-tempus", "rune-word-vitae", "rune-word-tempus", "rune-word-mortis", "rune-word-ventus"},
  ["rune-word-vitae"] = {"rune-word-tempus", "rune-word-vitae"},
  ["rune-word-mortis"] = {"rune-word-ignis", "rune-word-tempus", "rune-word-ventus", "rune-word-umbra", "rune-word-tempus", "rune-word-umbra"}
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
