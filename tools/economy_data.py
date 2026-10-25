"""Economy tables for The Croods 1.3.1, rebuilt for the offline server.

The original tables lived on Rovio's servers and are gone. Everything here is a
reconstruction: the values that could be recovered from the game itself (object
definitions, bytecode constants, formulas) are used as-is, and the gaps are
filled with values that follow the same rules so that the game stays playable
and internally consistent. See the "Balance" section of README.md for what is
confirmed and what is estimated.

Units, as the game reads them:
  constructTime, upgrade2Time, upgrade3Time, defaultTrapTime, productionTime
      -> minutes (the engine multiplies them by 60)
  creatureEvents.spawnFrequency
      -> minutes
  trapChance0..3, decorationBoost1..3, productionTimeDecrease, playBoosts[],
  cleanBoosts[]
      -> fractions (0..1), not percentages
"""

MISC = {
    # minutes; the sample save shipped with the game (BeltsMap.lua) has renewTotalTime = 300 s
    'SINK_QUEST_RENEW_TIMER': 5,
    'INITIAL_RESOURCE_CURRENCY_CARROT': 20,
    'INITIAL_RESOURCE_CURRENCY_STICK': 20,
    'INITIAL_RESOURCE_CURRENCY_SOUP': 10,
    'INITIAL_RESOURCE_CURRENCY_MUD': 10,
    'INITIAL_RESOURCE_CURRENCY_STONE': 10,
    'INITIAL_RESOURCE_CURRENCY_FEATHER': 10,
    'INITIAL_RESOURCE_CURRENCY_BONE': 10,
    'INITIAL_RESOURCE_CURRENCY_FISH': 10,
    'INITIAL_RESOURCE_CURRENCY_LEAF': 10,
    'INITIAL_RESOURCE_CURRENCY_COIN': 500,
    'INITIAL_RESOURCE_CURRENCY_ROVIO': 50,
    'INITIAL_RESOURCE_CURRENCY_BERRY': 20,
    'INITIAL_RESOURCE_CURRENCY_FRUIT': 10,
    'INITIAL_RESOURCE_CURRENCY_XP': 0,
    'CLEAN_CREATURE_XP_REWARD': 5,
    'PLAY_WITH_CREATURE_XP_REWARD': 5,
    'PLAY_WITH_CREATURE_XP_REWARD_FULL': 10,
    # seconds until a neighbour's gift boxes refill (the game calls them 'daily treasures');
    # without it the second visit crashed (GameManager.loadFriendsMapAndVisitWithID)
    'FRIENDWORLD_REWARD_COOLDOWN': 24 * 60 * 60,
    # Thunk asks for a few resources and pays crystals, then comes back after a random
    # time in seconds (Thunk.setRespawn / respawnCheat). Missing values crashed claiming his
    # reward (math.random(nil, nil) and 'for' limit nil in Thunk.claimReward/setRespawn).
    'THUNK_REWARD_ROVIOS': 3,
    'THUNK_RESPAWN_TIME_MIN': 4 * 60 * 60,
    'THUNK_RESPAWN_TIME_MAX': 8 * 60 * 60,
}

CAVE_RESOURCES = ['Carrots', 'Sticks', 'Mud', 'Stones', 'Feathers', 'Bones', 'Fish', 'Leaves',
                  'Berries', 'Soup', 'Eggs', 'Fruit']

MAX_LEVEL = 30


# ---------------------------------------------------------------------------
# creatures
# ---------------------------------------------------------------------------
# Food-chain order: every creature eats what an earlier one produces, so the
# player can always feed the next habitat from the previous one. The pair is
# (habitat suffix, trap suffix) - exactly the names used in GameObjects.lua.
CREATURES = [
    ('MOLERBEAR', 'Molerbear'),
    ('GIRELEPHANT', 'Girelephant'),
    ('BUNNY_BEAST', 'Bunny_Beast'),
    ('CROCOPUP', 'Crocopup'),
    ('RAMU', 'Ramu'),
    ('ALBATROCEROS', 'Albatroceros'),
    ('BEAROWL', 'Bearowl'),
    ('SHARKODILE', 'Sharkodile'),
    ('FISHCAT', 'FishCat'),
    ('ZEAVER', 'Zeaver'),
    ('LIYOTE', 'Liyote'),
    ('WALKING_WHALE', 'WalkingWhale'),
]

CREATURE_IDS = ['Molerbear', 'Girelephant', 'BunnyBeast', 'Crocopup', 'Ramu', 'Albatroceros',
                'Bearowl', 'Sharkodile', 'FishCat', 'Zeaver', 'Liyote', 'WalkingWhale']

# feedCurrency / outputResource, taken verbatim from the GameObjects dump
CREATURE_FOOD = ['Berries', 'Carrots', 'Carrots', 'Carrots', 'Bones', 'Berries',
                 'Berries', 'Bones', 'Fish', 'Berries', 'Eggs', 'Carrots']
CREATURE_PRODUCE = ['Carrots', 'Leaves', 'Stones', 'Bones', 'Eggs', 'Feathers',
                    'Coins', 'Fish', 'Mud', 'Sticks', 'Fruit', 'Coins']

# Creatures that produce Coins are the coin faucet of the game, so their
# habitats store more (and the Land Whale, the last one, the most).
COIN_PRODUCERS = ('Bearowl', 'WalkingWhale')

DECORATIONS = [
    'ROCK_DECORATION_01', 'WOODEN_LOG_01', 'PURCHASE_WOODEN_FENCE_01', 'PURCHASE_WOODEN_POLE_01',
    'PURCHASE_BOULDER_01', 'PURCHASE_PUDDLE_01', 'STONE_WALL_01', 'SKULL_01', 'PURCHASE_BONES_01',
    'PURCHASE_BONES_02', 'PURCHASE_FISHBONES_01', 'PURCHASE_FLAGPOLE_01', 'PURCHASE_MEAT_01',
    'PURCHASE_EGG_01', 'PURCHASE_TAILS_01', 'PURCHASE_TUSKS_01', 'PURCHASE_KRISPY_01',
    'MEDIUM_POND_01', 'PURCHASE_DUCKPOND_01', 'PURCHASE_DREAMCATCHER_01',
]
# the object dump says every creature favours the same three skulls
FAVOURITE_DECORATION = 'SKULL_01'


def creature_unlock_level(index):
    """Player level at which a creature's habitat and trap appear in the build menu."""
    return 1 + 2 * index


# ---------------------------------------------------------------------------
# habitats
# ---------------------------------------------------------------------------
# (creature, build price, construct minutes, caps per level, output per cycle,
#  food per cycle, level-2 upgrade, level-3 upgrade)
#
# Prices follow the pattern found in the 2013 tables: round coin values times
# powers of three (300 = 100x3, 900 = 100x9, 2700 = 100x27, 8100 = 100x81,
# 24300 = 300x81, 32400 = 400x81). The Bear Owl is the premium (Rovios) home,
# the Land Whale keeps its odd 1000/7875 price point.
HABITAT_ROWS = [
    dict(creature='Molerbear', cost=('Coins', 100), build=1, caps=(16, 24, 32), cycle=3, feed=3,
         lvl2=('Coins', 300), lvl3=('Coins', 900)),
    dict(creature='Girelephant', cost=('Coins', 300), build=10, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 900), lvl3=('Coins', 2700)),
    dict(creature='BunnyBeast', cost=('Coins', 900), build=30, caps=(16, 24, 32), cycle=3, feed=6,
         lvl2=('Coins', 2700), lvl3=('Coins', 8100)),
    dict(creature='Crocopup', cost=('Coins', 2700), build=60, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 8100), lvl3=('Coins', 24300)),
    dict(creature='Ramu', cost=('Coins', 8100), build=120, caps=(16, 24, 32), cycle=3, feed=6,
         lvl2=('Coins', 24300), lvl3=('Coins', 72900)),
    dict(creature='Albatroceros', cost=('Coins', 8100), build=150, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 24300), lvl3=('Coins', 72900)),
    # 1 h 45 min build time, paid in crystals only (2013 player reports)
    dict(creature='Bearowl', cost=('Rovios', 20), build=105, caps=(50, 75, 100), cycle=5, feed=2,
         lvl2=('Rovios', 30), lvl3=('Rovios', 50)),
    dict(creature='Sharkodile', cost=('Coins', 24300), build=240, caps=(16, 24, 32), cycle=3, feed=6,
         lvl2=('Coins', 72900), lvl3=('Coins', 218700)),
    dict(creature='FishCat', cost=('Coins', 8100), build=180, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 24300), lvl3=('Coins', 72900)),
    # 32 400 coins and 192 hours (691 200 s) - both confirmed by the 2013 reports
    dict(creature='Zeaver', cost=('Coins', 32400), build=11520, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 97200), lvl3=('Coins', 291600)),
    dict(creature='Liyote', cost=('Coins', 24300), build=240, caps=(16, 24, 32), cycle=3, feed=9,
         lvl2=('Coins', 72900), lvl3=('Coins', 218700)),
    # "1000 coins and 5 sticks and 7875 coins" for the second evolution
    dict(creature='WalkingWhale', cost=('Coins', 1000), build=60, caps=(50, 75, 100), cycle=10, feed=4,
         lvl2=('Coins', 3000), lvl3=('Coins', 7875, 'Sticks', 5)),
]

HABITAT_BY_CREATURE = {row['creature']: row for row in HABITAT_ROWS}


def _cost_fields(prefix, cost):
    """Turn ('Coins', 100) / ('Coins', 7875, 'Sticks', 5) into itemType_*/itemCost_* columns."""
    pairs = [(cost[i], cost[i + 1]) for i in range(0, len(cost), 2)]
    out = {}
    for n in range(1, 4):
        kind, amount = pairs[n - 1] if n <= len(pairs) else ('-', 0)
        out[f'{prefix}itemType_{n}'] = kind
        out[f'{prefix}itemCost_{n}'] = amount
    return out


def habitats():
    rows = []
    for i, data in enumerate(HABITAT_ROWS):
        tier = i + 1
        caps = data['caps']
        feed = data['feed']
        row = {'Habitat': f"HABITAT_{CREATURES[i][0]}"}
        row.update(_cost_fields('', data['cost']))
        row.update({
            'constructTime': data['build'],
            'productionTime': 5,  # every habitat works in 5-minute cycles
            'coinsLvl1': 5 * tier, 'coinsLvl2': 8 * tier, 'coinsLvl3': 12 * tier,
            'ConstructionXP': 20 * tier, 'ProductionXP': 2 * tier,
        })
        row.update(_cost_fields('level2_', data['lvl2']))
        row.update(_cost_fields('level3_', data['lvl3']))
        for n in range(1, 4):
            row[f'level{n}_productionCap'] = caps[n - 1]
            row[f'level{n}_productionPerCycle'] = data['cycle']
            row[f'level{n}_feedAmount'] = feed
        row.update({
            'upgrade2Time': max(5, data['build'] // 2),
            'upgrade3Time': max(5, data['build']),
            'removePrice': 10, 'removeTime': 0,
        })
        rows.append(row)
    return rows


def habitat_coin_value(creature):
    """Coin price of a habitat (Rovios homes are converted at the conversion rate)."""
    cost = HABITAT_BY_CREATURE[creature]['cost']
    return cost[1] if cost[0] == 'Coins' else cost[1] * COIN_VALUE['Rovios']


# ---------------------------------------------------------------------------
# traps
# ---------------------------------------------------------------------------
# A trap costs coins to build; levelling it up costs the creature's food plus
# sticks and raises the catch chance (TrapObject builds levelingCosts from
# levelUpResource1/2 + resourceCountNLvlM).
TRAP_COINS = {
    'Molerbear': 50, 'Girelephant': 150, 'BunnyBeast': 450, 'Crocopup': 1350,
    'Ramu': 4050, 'Albatroceros': 4050, 'Bearowl': 500, 'Sharkodile': 12150,
    'FishCat': 4050, 'Zeaver': 16200, 'Liyote': 12150, 'WalkingWhale': 500,
}
TRAP_CHANCES = (0.25, 0.5, 0.75, 1.0)


def traps():
    rows = []
    for i, (_, trap) in enumerate(CREATURES):
        tier = i + 1
        mult = 1 + (tier - 1) // 4
        rows.append({
            'Trap': f'Trap_{trap}',
            'itemType_1': 'Coins', 'itemCost_1': TRAP_COINS[CREATURE_IDS[i]],
            'itemType_2': '-', 'itemCost_2': 0,
            'levelUpResource1': CREATURE_FOOD[i], 'levelUpResource2': 'Sticks', 'levels': 3,
            'currencies': 2,
            'resourceCount1Lvl1': 4 * mult, 'resourceCount2Lvl1': 2 * mult,
            'resourceCount1Lvl2': 10 * mult, 'resourceCount2Lvl2': 5 * mult,
            'resourceCount1Lvl3': 20 * mult, 'resourceCount2Lvl3': 10 * mult,
            'trappedCreature': CREATURE_IDS[i], 'trappingXP': 10 * tier, 'ConstructionXP': 10 * tier,
            'trapChance0': TRAP_CHANCES[0], 'trapChance1': TRAP_CHANCES[1],
            'trapChance2': TRAP_CHANCES[2], 'trapChance3': TRAP_CHANCES[3],
            'defaultTrapTime': min(30, 5 + 2 * (tier - 1)),
            # the tutorial opens the first trap's menu right after placing it and needs the
            # 'evolve' button, which only a finished trap has -> the tutorial trap builds instantly
            'constructTime': 0 if tier == 1 else 4,
            'releaseInterest': 1,
        })
    return rows


# ---------------------------------------------------------------------------
# creature levelling
# ---------------------------------------------------------------------------
# XP needed for creature level N is feedingSessions * sum(feedPerSession1..N)
# (CreatureXPManager), and taming needs 3 feedings - the 2013 reports agree.
FEED_PER_SESSION = [3, 5, 8, 12, 18, 26]


def creature_levelup():
    rows = []
    for i, cid in enumerate(CREATURE_IDS):
        tier = i + 1
        mult = 1 + (tier - 1) // 4
        row = {
            'Creature': cid,
            'feedCurrency': CREATURE_FOOD[i],
            'feedingSessions': 3,
            'eatingTime': 5,
            # fractions: getHabitatProductionTimeDecrease = (level-2)*this + boosts
            'productionTimeDecrease': 0.05,
            'favorableDecoration1': FAVOURITE_DECORATION, 'decorationBoost1': 0.05,
            'favorableDecoration2': FAVOURITE_DECORATION, 'decorationBoost2': 0.05,
            'favorableDecoration3': FAVOURITE_DECORATION, 'decorationBoost3': 0.05,
            # ratio gained per minute; 0.05 -> a creature gets dirty/bored in ~20 minutes
            'dirtinessIncreaseRatio': 0.05,
            'boredomIncreaseRatio': 0.05,
            # fractions of the production cycle removed by playing / cleaning.
            # The engine derives happinessTheresholds from the length of cleanBoosts,
            # so both arrays must have the same, non-zero length.
            'playBoosts1': 0.05, 'cleanBoosts1': 0.05,
            # boredom after a mini-play is capped at this value (must stay <= 1)
            'miniPlayCap': 0.2,
            'boredomeResource': CREATURE_PRODUCE[i],
        }
        for lvl in range(1, 7):
            row[f'feedPerSession{lvl}'] = FEED_PER_SESSION[lvl - 1] * mult
            row[f'creaturelevelupXP{lvl}'] = 10 * lvl * tier
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# decorations
# ---------------------------------------------------------------------------
PURCHASABLE = DECORATIONS + [
    'ALBATROCEROS_TOTEM_01', 'BEAROWL_TOTEM_01', 'BUNNYBEAST_TOTEM_01', 'CROCOPUP_TOTEM_01', 'FISHCAT_TOTEM_01',
    'GIRELEPHANT_TOTEM_01', 'LANDWHALE_TOTEM_01', 'LIYOTE_TOTEM_01', 'MOLARBEAR_TOTEM_01', 'RAMU_TOTEM_01',
    'SHARKODILE_TOTEM_01', 'ZEAVER_TOTEM_01',
] + [f'dynamic_group_0{i}' for i in range(2, 9)]


def decos():
    rows = []
    for i, name in enumerate(PURCHASABLE):
        totem = 'TOTEM' in name
        if name == FAVOURITE_DECORATION:
            price = 100  # every creature likes skulls, so keep them cheap enough to buy three
        elif totem:
            price = 300
        else:
            price = 25 + 10 * i
        rows.append({'Decorations': name, 'itemType_1': 'Coins', 'itemCost_1': price,
                     'itemType_2': '-', 'itemCost_2': 0, 'constructTime': 0, 'removePrice': 5, 'removeTime': 0,
                     'decorationNearbyRadius': 3})
    return rows


# ---------------------------------------------------------------------------
# removable map objects (rocks and trees)
# ---------------------------------------------------------------------------
# XP and crystals per object come from the 2013 screenshots (big tree 20 XP +
# 3 crystals, big rock 40 XP + 4 crystals); smaller objects are scaled down.
DYNAMIC_OBJECTS = {
    'area1_h_dyn_4': (5, 1, 5),
    'superbait': (5, 1, 5),
    **{f'{base}{suffix}': reward for base, reward in (
        ('big_rock_01', (40, 4, 20)),
        ('small_rock_02', (10, 2, 10)),
        ('small_rock_03', (5, 1, 5)),
        ('big_tree_00', (20, 3, 20)),
        ('small_tree_01', (10, 2, 10)),
        ('small_tree_02', (5, 1, 5)),
    ) for suffix in ('', '_A2', '_A3')},
}


def dynamic_objects():
    rows = []
    for name, (xp, rovios, price) in DYNAMIC_OBJECTS.items():
        rows.append({'ObjectID': name, 'removePrice': price, 'removeTime': 0, 'removeXP': xp,
                     'removeRewardType': 'Rovios', 'removeRewardAmount': rovios})
    return rows


# ---------------------------------------------------------------------------
# factories (berry bushes)
# ---------------------------------------------------------------------------
# Capacity 24 at level 2, 38 at level 3 and 50/100 crystal upgrade prices are
# confirmed; the bushes' 120-second cycle comes from the object definition.
def factories():
    rows = []
    for name in ('BERRY_BUSH', 'BERRY_BUSH_2'):
        row = {'Factory': name, 'levels': 4, 'outputResource': 'Berries',
               'outputAmount': 16, 'outputAmount2': 24, 'outputAmount3': 38, 'outputAmount4': 54,
               'productionTime': 2, 'ProductionXP': 3}
        for lvl, price in ((2, 50), (3, 100), (4, 200)):
            row.update(_cost_fields(f'level{lvl}_', ('Rovios', price)))
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# cave storage
# ---------------------------------------------------------------------------
# Level 1 holds 50 of every resource and level 2 holds 75 (2013 review), so the
# rest of the progression simply keeps adding 25.
def cave_levels(count=6):
    rows = []
    for lvl in range(1, count + 1):
        row = {'CaveLevel': f'CaveLevel{lvl}',
               'UpgradeCostCoins': 500 * 3 ** (lvl - 1),
               'UpgradeCostRovio': 5 * lvl,
               'RewardXP': 50 * lvl}
        row.update({res: 25 * (lvl + 1) for res in CAVE_RESOURCES})
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# resources
# ---------------------------------------------------------------------------
CURRENCIES = ['Berries', 'Carrots', 'Stones', 'Leaves', 'Feathers', 'Sticks', 'Mud', 'Bones', 'Fish', 'Soup',
              'Eggs', 'Fruit']

# Relative worth, anchored on the confirmed production chain
# "54 Berries -> 54 Carrots -> 18 Leaves -> 6 Bones -> 3 Fish -> 1 Stick".
# Berries 1 / Carrots 3 are confirmed by Ugga's orders in BeltsMap.lua: Ugga pays
# quantity x ConvertCoin, and "Give 4 Carrots" pays 12 coins, "Give 5 Berries" pays 5.
COIN_VALUE = {'Berries': 1, 'Carrots': 3, 'Leaves': 3, 'Bones': 9, 'Fish': 18, 'Sticks': 54,
              'Stones': 2, 'Feathers': 4, 'Mud': 6, 'Eggs': 12, 'Fruit': 20, 'Soup': 30,
              'Coins': 1, 'Rovios': 100, 'XP': 0}


def conversion_table():
    rows = [{'ResourceName': res, 'ConvertCoin': COIN_VALUE[res],
             'ConvertRovio': max(1, COIN_VALUE[res] // 20) if COIN_VALUE[res] else 0}
            for res in CURRENCIES + ['Coins', 'Rovios', 'XP']]
    # 'Time' (TweakValues.CURRENCY_TIME) is priced in minutes: skipping the wait for Ugga's
    # next soup order costs ceil(minutes * ConvertRovio) crystals (QuestSink.getSpeedCost).
    # Without this row tapping Ugga crashed (ResourceManager.getRovioAmountForResources).
    rows.append({'ResourceName': 'Time', 'ConvertCoin': 1, 'ConvertRovio': 0.1})
    return rows


# ---------------------------------------------------------------------------
# player levels
# ---------------------------------------------------------------------------
def xp_levels():
    return [{'Level': f'LEVEL_{lvl}', 'Points': 25 * lvl * (lvl + 1)} for lvl in range(1, MAX_LEVEL + 1)]


HOME_EVERY = 3
MAX_HOMES = 8


def level_rewards():
    rows = [{'Levels': lvl, 'RewardType': 'Coins', 'Quantity': 50 * lvl} for lvl in range(1, MAX_LEVEL + 1)]
    # crystals: there is no shop in the offline build, so the only way to get
    # them is levelling up (plus clearing rocks/trees)
    for lvl in range(5, MAX_LEVEL + 1, 5):
        rows.append({'Levels': lvl, 'RewardType': 'Rovios', 'Quantity': 20})
    rows.append({'Levels': 21, 'RewardType': 'Rovios', 'Quantity': 100})  # confirmed: 100 crystals
    for i, (hab, trap) in enumerate(CREATURES):
        lvl = creature_unlock_level(i)
        rows.append({'Levels': lvl, 'RewardType': f'Trap_{trap}', 'Quantity': 1})
        # How many homes of a kind may be built is the sum of these rewards up to the player's
        # level (PlayerXPManager.getUnlockableObjectsTillLevel). The sample save in BeltsMap.lua
        # (level 18) owns up to 8 Molerbear and 5 Bunny Beast homes, so hand out one more home
        # every 3 levels after the unlock, at most 8. Rows of one level must not repeat a
        # RewardType: the game keeps only the last one.
        for n, home_lvl in enumerate(range(lvl, MAX_LEVEL + 1, HOME_EVERY)):
            if n == MAX_HOMES:
                break
            rows.append({'Levels': home_lvl, 'RewardType': f'HABITAT_{hab}', 'Quantity': 1})
    for i, deco in enumerate(DECORATIONS):
        rows.append({'Levels': 1 + i, 'RewardType': deco, 'Quantity': 5})
    totems = [f'{name}_TOTEM_01' for name in ('BUNNYBEAST', 'LIYOTE', 'RAMU', 'CROCOPUP', 'FISHCAT', 'BEAROWL',
                                              'ZEAVER', 'MOLARBEAR', 'GIRELEPHANT', 'SHARKODILE',
                                              'ALBATROCEROS', 'LANDWHALE')]
    for i, totem in enumerate(totems):
        rows.append({'Levels': creature_unlock_level(i) + 1, 'RewardType': totem, 'Quantity': 1})
    # the "unlocks at level N" hint comes from the first row of an item the game reads
    rows.sort(key=lambda row: row['Levels'])
    return rows


# ---------------------------------------------------------------------------
# quests
# ---------------------------------------------------------------------------
def quest(name, order, level, qtype, giver, description, item, count, icon, coins, xp, camera=None):
    row = {'questName': name, 'order': order, 'level': level, 'questType': qtype, 'questGiverType': giver,
           'description': description, 'itemDefinition': item, 'itemCount': count, 'icon': icon,
           'rewardType_1': 'Coins', 'rewardQuantity_1': coins, 'rewardType_2': 'XP', 'rewardQuantity_2': xp}
    if camera:
        row['cameraTarget'] = camera
    return row


QUEST_LEVEL_OFFSET = 2  # no progress quests before level 3 (see progress_quests)


def progress_quests():
    """Granny's (and Ugga's) task chain: for each creature build habitat + trap, catch, tame, feed."""
    rows = []
    order = 1
    for i, (hab, trap) in enumerate(CREATURES):
        cid = CREATURE_IDS[i]
        # Quests are handed out at once for every level <= the player's level. The tutorial
        # itself builds a trap/habitat and catches/tames a creature while it forbids quest-giver
        # indicators, so a quest finished (or offered) then crashes the game
        # (QuestCharacter.showQuestIndicator). The tutorial gives < 150 XP, so start at level 3.
        lvl = creature_unlock_level(i) + QUEST_LEVEL_OFFSET
        nice = cid if cid != 'BunnyBeast' else 'Bunny Beast'
        steps = [
            ('Plant', f'HABITAT_{hab}', 1, 'ICON_BUILD', f'Build a {nice} habitat'),
            ('Plant', f'Trap_{trap}', 1, 'ICON_BUILD', f'Build a {nice} trap'),
            ('Trap', cid, 1, 'ICON_TRAP', f'Catch a {nice}'),
            ('Tame', cid, 1, 'ICON_TAME', f'Tame a {nice}'),
            ('FeedCreature', cid, 2, 'ICON_COLLECT', f'Feed a {nice} twice'),
        ]
        # five steps pay out roughly half of the creature's habitat price in total
        step_coins = max(25, habitat_coin_value(cid) // 10)
        for j, (qtype, item, count, icon, text) in enumerate(steps):
            rows.append(quest(f'{cid}_{j + 1}', order, lvl, qtype, 'CHARACTER_GRANNY', text, item, count, icon,
                              step_coins, 10 * (i + 1)))
            order += 1
    # map clearing and gathering tasks from Ugga
    for lvl in range(1 + QUEST_LEVEL_OFFSET, MAX_LEVEL + 1, 3):
        rows.append(quest(f'Clear_{lvl}', order, lvl, 'Remove', 'CHARACTER_UGGA', 'Clear rocks or trees',
                          '*', 2 + lvl // 3, 'ICON_REMOVE', 30 + 10 * lvl, 10 + 2 * lvl))
        order += 1
        rows.append(quest(f'Gather_{lvl}', order, lvl, 'Resource', 'CHARACTER_UGGA', 'Gather 20 Berries',
                          'Berries', 20, 'ICON_COLLECT', 40 + 10 * lvl, 10 + 2 * lvl))
        order += 1
    return rows


# Achievements are quests of giver ACHIEVEMENT whose only real reward is ('Achievement', id).
# The first six rows are copied from the sample save in BeltsMap.lua; that save also names
# the other twelve (ids 1-3, 5-7, 11-13, 15, 17, 18) but not their goals, so those are made up
# from the names using the same quest types. Descriptions must not contain commas (CSV).
ACHIEVEMENTS = [
    # (name, id, type, itemDefinition, count, description)
    ('Happy Animal', 4, 'LevelCreature', '*', 6, 'Fully level up a creature in one Home'),
    ('Fully Stocked', 8, 'Plant', 'OBJECT_GROUP_DECORATION', 200, 'Plant total of 200 decorations'),
    ('Trapped!', 9, 'Plant', 'OBJECT_GROUP_TRAP', 50, 'Plant total of 50 traps'),
    ('Trapmaster', 10, 'Plant', 'OBJECT_GROUP_TRAP', 200, 'Plant total of 200 traps'),
    ('Hoarder', 14, 'Resource', '-Coins;-Rovios;-XP;+*', 10000, 'Collect total of 10000 resources'),
    ('Lots of Creatures', 16, 'Tame', '*', 30, 'Catch total of 30 creatures'),
    ('Crood Up!', 1, 'WorldLevel', '*', 5, 'Reach level 5'),
    ('Cleanup Process', 2, 'Remove', '*', 10, 'Clear 10 rocks or trees'),
    ('Bunch of Creatures', 3, 'Tame', '*', 10, 'Catch total of 10 creatures'),
    ('Five Sticks', 5, 'Resource', 'Sticks', 5, 'Collect 5 Sticks'),
    ('Exterior Designer', 6, 'Plant', 'OBJECT_GROUP_DECORATION', 20, 'Plant total of 20 decorations'),
    ('Got my mind on money', 7, 'Resource', 'Coins', 1000, 'Collect total of 1000 coins'),
    ('Rocking it Ten', 11, 'WorldLevel', '*', 10, 'Reach level 10'),
    ('Grumpy Collector', 12, 'Resource', '-Coins;-Rovios;-XP;+*', 1000, 'Collect total of 1000 resources'),
    ('Expert Cleaning', 13, 'Remove', '*', 50, 'Clear 50 rocks or trees'),
    ("I'm getting rich", 15, 'Resource', 'Coins', 10000, 'Collect total of 10000 coins'),
    ('Happy Zoo', 17, 'Tame', '*', 60, 'Catch total of 60 creatures'),
    ("Ugga's Dream", 18, 'Resource', 'Soup', 30, 'Get 30 bowls of Soup from Ugga'),
]


def achievements():
    rows = []
    for name, ident, qtype, item, count, text in ACHIEVEMENTS:
        # level 3 like the other quests: nothing may finish while the tutorial runs
        rows.append({'questName': name, 'order': ident, 'level': 1 + QUEST_LEVEL_OFFSET, 'questType': qtype,
                     'questGiverType': 'ACHIEVEMENT', 'description': text, 'itemDefinition': item,
                     'itemCount': count, 'icon': 'BUTTON_ACHIEVEMENTS',
                     'rewardType_1': 'Achievement', 'rewardQuantity_1': ident,
                     'rewardType_2': 'XP', 'rewardQuantity_2': 0})
    return rows


def sink_quests():
    """Ugga's soup ingredients per level. Coins/crystals/XP/soup stay empty on purpose:
    the generator picks ingredients from this row, and those four are not ingredients."""
    rows = []
    for lvl in range(1, MAX_LEVEL + 1):
        row = {'level': lvl, 'Coins': 0, 'Rovios': 0, 'XP': 0, 'Soup': 0}
        row.update({res: 2 + lvl // 2 for res in CURRENCIES if res != 'Soup'})
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# misc tables
# ---------------------------------------------------------------------------
def daily_bonus():
    rewards = [('Coins', 100), ('Berries', 20), ('Carrots', 20), ('Stones', 15), ('Rovios', 5)]
    rows = []
    for prefix in ('Week_', 'Cycle_'):
        for n in range(1, 11):
            row = {'Weeks': f'{prefix}{n}', 'Egg_cost_type': 'Rovios', 'Egg_cost_amount': 5}
            for d, (res, amount) in enumerate(rewards, 1):
                row[f'Day_{d}_reward'] = res
                row[f'Day_{d}_amount'] = amount * n
            rows.append(row)
    return rows


ROWS = {
    'quests.csv': progress_quests(),
    'achievements.csv': achievements(),
    'sinkquestdefinitions.csv': sink_quests(),
    'resourceconversiontable.csv': conversion_table(),
    'dailyBonus.csv': daily_bonus(),
    'thunk.csv': [{'resource': res, 'minamount': 3, 'maxamount': 10} for res in CURRENCIES],
    # speed-up price in Rovios by remaining time (seconds)
    'costcurve.csv': [{'time': t, 'cost': c} for t, c in ((60, 1), (600, 2), (3600, 5), (4 * 3600, 10),
                                                            (24 * 3600, 25), (7 * 24 * 3600, 60))],
    'keys.csv': [{'Key': 'CROODS', 'message': 'Welcome back!', 'itemType1': 'Coins', 'itemType_1': 'Coins',
                  'itemCost_1': 500, 'itemType_2': 'Rovios', 'itemCost_2': 20, 'itemType_3': '-', 'itemCost_3': 0}],
    # forcedResource must stay empty (= nil in the game): any text is used as a resource name,
    # and an unknown one ('-') crashed collecting a neighbour's gift box (BasicTileScene.spawnCollectables)
    'socialpickup.csv': [{'pack': 'pack1', 'probability': 100, 'resourceAmount': 5, 'maxDifferentResource': 2,
                          'forcedResource': ''}],
    'habitats.csv': habitats(),
    'traps.csv': traps(),
    'creatureLevelUp.csv': creature_levelup(),
    'decos.csv': decos(),
    'dynamicobjects.csv': dynamic_objects(),
    'factory.csv': factories(),
    'cave.csv': cave_levels(),
    'xp.csv': xp_levels(),
    'levelrewards.csv': level_rewards(),
    'miscValues.csv': [{'name': k, 'value': v} for k, v in MISC.items()],
    # spawnFrequency is in minutes (ScriptedEventsManager multiplies by 60)
    'creatureEvents.csv': [{'Event': 'Spawn', 'spawnFrequency': 10, 'lifeTime': 600, 'maxCreaturesAtTime': 3}],
}
