"""Run The Croods' decompiled Lua game logic on the desktop with the engine stubbed out.

Used to find which economy-table rows/columns the game needs: Lua errors here come
with file:line in the decompiled sources, unlike on the device (stripped bytecode).

usage: harness.py <decompiled data dir> <assets dir> [steps...]
env BYTECODE_DIR: decrypted original bytecode, used for files whose decompiled
source does not compile (unluac emits goto, which Lua 5.1 lacks).
"""
import os
import sys

sys.path.insert(0, os.environ.get('LUPA_PATH', ''))
from lupa import lua51  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luac_convert import convert  # noqa: E402

SRC, ASSETS = sys.argv[1], sys.argv[2]

L = lua51.LuaRuntime(unpack_returned_tuples=True)
G = L.globals()


def read_script(path):
    p = path.replace('\\', '/')
    while '//' in p:
        p = p.replace('//', '/')
    p = p.lstrip('/')
    for cand in (p, 'data/' + p, 'data/scripts/' + p):
        full = os.path.join(SRC, cand)
        if os.path.isfile(full):
            bc = os.path.join(os.environ.get('BYTECODE_DIR', ''), cand)
            bc = convert(open(bc, 'rb').read()) if os.path.isfile(bc) else None
            return open(full, encoding='latin-1').read(), cand, bc
    raise FileNotFoundError(path)


def read_asset(path):
    full = os.path.join(ASSETS, os.path.basename(path))
    return open(full, encoding='latin-1').read() if os.path.isfile(full) else None


G.py_read_script = read_script
G.py_read_asset = read_asset
G.PREFER_SOURCE = bool(os.environ.get('PREFER_SOURCE'))
G.py_native_names = lambda: open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'native_names.txt')).read()

L.execute(r'''
STUBBED = {}
BYTECODE_FILES = {}
local stubmt = {}
local function newstub(name) return setmetatable({__stubname = name}, stubmt) end
stubmt.__index = function(t, k)
  local s = newstub(rawget(t, "__stubname") .. "." .. tostring(k)); rawset(t, k, s); return s end
stubmt.__call = function(t)
  local name = rawget(t, "__stubname")
  local last = name:match("([%w_]+)$") or ""
  -- native getters return numbers (sizes, positions); predicates return false
  if last:match("^get") and not last:match("Data$") and not last:match("^getAll") then return 64, 64, 64, 64, 64, 64 end
  if last:match("^is") or last:match("^has") then return false end
  -- coordinate conversions (screenToTileWorld, worldAxisToScreenAxis, ...) return x, y
  if last:match("To%u") or last:match("Position$") or last:match("Size$") then return 0, 0 end
  return newstub(name .. "()")
end
stubmt.__concat = function(a, b) return tostring(a) .. tostring(b) end
stubmt.__tostring = function(t) return "<" .. rawget(t, "__stubname") .. ">" end
for _, op in ipairs({"__add", "__sub", "__mul", "__div", "__mod", "__pow", "__unm"}) do
  stubmt[op] = function() return 0 end
end
stubmt.__lt = function() return false end
stubmt.__le = function() return true end
STUB = newstub

-- only names known to come from the native engine become stubs
NATIVE = {}
for name in (py_native_names()):gmatch("%S+") do NATIVE[name] = true end
local function native_index(prefix)
  return function(t, k)
    if type(k) ~= "string" then return nil end
    local full = prefix .. k
    if not NATIVE[full] then MISSING[full] = true return nil end
    STUBBED[full] = true
    local s = newstub(full); rawset(t, k, s); return s end
end
MISSING = {}
setmetatable(_G, {__index = native_index("")})

local function load_into(path, env, chunkname)
  local src, rel, bc = py_read_script(path)
  local f, err
  -- original bytecode by default (decompiled sources mistranslate some calls, e.g. extra nils
  -- to table.insert); PREFER_SOURCE=1 uses decompiled sources to get file:line in errors
  if bc and (rel:match("Utility%.lua$") or not PREFER_SOURCE) then src = nil end
  if src then f, err = loadstring(src, "@" .. rel) end
  if not f and bc then
    BYTECODE_FILES[#BYTECODE_FILES + 1] = rel
    f, err = loadstring(bc, "@" .. rel)
  end
  if not f then error(err) end
  setfenv(f, env)
  f()
end

gamelua = _G  -- on the device the global environment doubles as the gamelua object
rawset(gamelua, "DEV_MODE", false)
rawset(gamelua, "buildType", "distribution")
for k, v in pairs({scriptPath = "/scripts", imagePath = "/images", fontPath = "/fonts", audioPath = "/audio",
                   screenWidth = 1794, screenHeight = 1080}) do rawset(gamelua, k, v) end
screenWidth, screenHeight, buildType, deviceModel = 1794, 1080, "distribution", "emulator"
keyPressed, keyReleased, keyHold = {}, {}, {}
g_time, time = 0, 0
-- native time API, modelled with plain numbers (seconds)
local clock = 1792900000
function getCurrentTime() return clock end
function getTimeDifferenceInSeconds(a, b) return (tonumber(b) or 0) - (tonumber(a) or 0) end
function addTimeToStructure(t, secs) return (tonumber(t) or 0) + (tonumber(secs) or 0) end
function advanceClock(secs) clock = clock + secs end
function getDevice() return "android" end
function getLocale() return "en" end
function getCurrentLocale() return "en" end
GAME_VERSION, BUILD_ID, CUSTOMER_ID, CLOUD_SERVER_URL = "1.3.1", "Croods-1.3.1", "androidmarket", "http://10.0.2.2:8000"
cursor = {x = 0, y = 0, pressed = false, wheelTriggered = false}
function gamelua.loadLuaFileToObject(path, parent, name)
  parent = parent or _G
  if name == nil or name == "" then
    load_into(path, parent)
  else
    local env = rawget(parent, name)
    if type(env) ~= "table" or getmetatable(env) == stubmt then env = {} end
    env.gamelua = gamelua; env._G = _G; env.this = env
    -- native code registers functions into these objects; stub what is missing
    setmetatable(env, {__index = native_index(name .. ".")})
    rawset(parent, name, env)
    load_into(path, env)
  end
end
function gamelua.loadLuaFile(path) load_into(path, _G) end
loadLuaFileToObject = gamelua.loadLuaFileToObject
loadLuaFile = gamelua.loadLuaFile
function gamelua.loadTextFileToString(path, isAsset)
  local s = py_read_asset(path)
  if s == nil then error("asset not found: " .. tostring(path)) end
  return s
end
local raw_print = print
function gamelua.print(...) local t = {} for i = 1, select("#", ...) do t[#t+1] = tostring((select(i, ...))) end raw_print("[game] " .. table.concat(t, " ")) end
function gamelua.showAlert(a, b) raw_print("[alert] " .. tostring(a) .. ": " .. tostring(b)) end
function gamelua.logEvent() end
function gamelua.deepCopy(t, seen)
  if type(t) ~= "table" then return t end
  seen = seen or {}
  if seen[t] then return seen[t] end
  local c = {}
  seen[t] = c
  for k, v in pairs(t) do c[gamelua.deepCopy(k, seen)] = gamelua.deepCopy(v, seen) end
  return setmetatable(c, getmetatable(t))
end
function gamelua.range(a, b, step)
  local out = {}
  if b == nil then a, b = 1, a end
  for i = a, b, step or 1 do out[#out + 1] = i end
  return out
end
function gamelua.contains(t, v) for _, x in pairs(t) do if x == v then return true end end return false end
function gamelua.map(f, t) local out = {} for k, v in pairs(t) do out[k] = f(v) end return out end
function gamelua.split(str, sep)
  local out, start = {}, 1
  while true do
    local i = string.find(str, sep, start, true)
    if not i then out[#out + 1] = string.sub(str, start) break end
    out[#out + 1] = string.sub(str, start, i - 1)
    start = i + #sep
  end
  return out
end
this = _G
scriptPath = "/scripts"
registerClassAsSingleton = nil -- defined by Utility.lua
''')


def run(code, label):
    fn = L.eval('function(code) local f, e = loadstring(code, "=harness") if not f then return false, e end '
                'local ok, e = xpcall(f, debug.traceback) return ok, e end')
    ok, err = fn(code)
    if not ok:
        print(f'### ERROR during {label}:\n{err}')
        stubbed = sorted(k for k in L.globals().STUBBED.keys())
        print('### stubbed:', ' '.join(stubbed)[:3000])
        print('### looked up but nil:', ' '.join(sorted(L.globals().MISSING.keys()))[:3000])
        sys.exit(1)
    print(f'--- {label}: ok')


STEPS = {
    'main': 'loadLuaFile("/scripts/gamelogic.lua")',
    'load': 'loadFiles()',
    'init': 'initialize()',
    'assets': '''
        local names = {}
        for _, n in ipairs(Cloud.g_requiredAssetsFiles or g_requiredAssetsFiles or {}) do names[n] = n end
        Cloud.g_assetFilenames = names
        g_assetFilenames = names
        Cloud.Assets = Cloud.Assets or {}
    ''',
    # what Cloud.getGotoGame does once the save is synced (nil save = new game)
    'newgame': 'gamelua.g_gameManager = g_gameManager; g_gameManager:reallyLoadAssets(); '
               'g_gameManager:loadGameState(nil)',
    'frames': 'Cloud.g_action = nil; g_action = nil; for i = 1, 300 do update(0.033) end',
    # wrap class methods so errors carry a Class.method chain (bytecode files have no line info)
    'trace': open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lua_trace.lua')).read()
             .replace('depth < 2', 'depth < 3')
             .replace('if type(v) == "function" then', 'if type(v) == "function" and debug.getinfo(v, "S").what ~= "C" then'),
}
for step in sys.argv[3:] or ['main', 'load', 'init', 'assets', 'trace', 'newgame', 'frames']:
    run(STEPS.get(step, step), step)
