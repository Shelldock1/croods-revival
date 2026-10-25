-- Debug aid appended to the IAP asset (runs in the game's global environment).
-- Wraps global functions and functions in global tables (two levels deep) so a
-- Lua error message carries the chain of calls that led to it (no debug info).
local pairs, pcall, unpack, type, tostring, error, maxn = _G.pairs, _G.pcall, _G.unpack, _G.type, _G.tostring, _G.error, _G.table.maxn
local skip = { _G = true, string = true, table = true, math = true, os = true, io = true,
  debug = true, coroutine = true, package = true, res = true, Tilemap = true }
local seen = {}
local function wrap(path, f)
  return function(...)
    local r = { pcall(f, ...) }
    if r[1] then return unpack(r, 2, maxn(r)) end
    local msg = tostring(r[2])
    if #msg < 1500 then msg = path .. " > " .. msg end
    error(msg)
  end
end
local function wrapTable(prefix, t, depth)
  if seen[t] then return end
  seen[t] = true
  for k, v in pairs(t) do
    if type(k) == "string" and not skip[k] then
      if type(v) == "function" and depth > 0 then  -- top level holds builtins (getfenv...)
        t[k] = wrap(prefix .. k, v)
      elseif type(v) == "table" and depth < 2 then
        wrapTable(prefix .. k .. ".", v, depth + 1)
      end
    end
  end
end
wrapTable("", _G, 0)
-- game classes live in the environment this chunk runs in (the GameManager object)
local env = _G.getfenv(1)
if env ~= _G then wrapTable("GM.", env, 1) end
