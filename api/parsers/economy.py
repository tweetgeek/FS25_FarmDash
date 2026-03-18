import xml.etree.ElementTree as ET
from pathlib import Path

PERIODS = [
    'EARLY_SPRING', 'MID_SPRING', 'LATE_SPRING',
    'EARLY_SUMMER', 'MID_SUMMER', 'LATE_SUMMER',
    'EARLY_AUTUMN', 'MID_AUTUMN', 'LATE_AUTUMN',
    'EARLY_WINTER', 'MID_WINTER', 'LATE_WINTER',
]

# fill_type → (Polish name, emoji, category)
ITEM_INFO: dict[str, tuple[str, str, str]] = {
    # ── Uprawy ──────────────────────────────────────────────────────────────
    'WHEAT':            ('Pszenica',            '🌾', 'crops'),
    'WHEAT_CUT':        ('Pszenica (cięta)',     '🌾', 'crops'),
    'BARLEY':           ('Jęczmień',             '🌾', 'crops'),
    'BARLEY_CUT':       ('Jęczmień (cięty)',     '🌾', 'crops'),
    'OAT':              ('Owies',                '🌾', 'crops'),
    'OAT_CUT':          ('Owies (cięty)',        '🌾', 'crops'),
    'CANOLA':           ('Rzepak',               '🟡', 'crops'),
    'CANOLA_CUT':       ('Rzepak (cięty)',       '🟡', 'crops'),
    'SORGHUM':          ('Sorgo',                '🌾', 'crops'),
    'SUNFLOWER':        ('Słonecznik',           '🌻', 'crops'),
    'SOYBEAN':          ('Soja',                 '🫘', 'crops'),
    'SOYBEAN_CUT':      ('Soja (cięta)',         '🫘', 'crops'),
    'MAIZE':            ('Kukurydza',            '🌽', 'crops'),
    'POTATO':           ('Ziemniaki',            '🥔', 'crops'),
    'SUGARBEET':        ('Buraki cukrowe',       '🟤', 'crops'),
    'SUGARBEET_CUT':    ('Buraki cukrowe (cięte)','🟤','crops'),
    'SUGARCANE':        ('Trzcina cukrowa',      '🎋', 'crops'),
    'BEETROOT':         ('Buraczki',             '🟣', 'crops'),
    'CARROT':           ('Marchew',              '🥕', 'crops'),
    'PARSNIP':          ('Pasternak',            '🥕', 'crops'),
    'ONION':            ('Cebula',               '🧅', 'crops'),
    'ONION_DIRTY':      ('Cebula (brudna)',      '🧅', 'crops'),
    'PEA':              ('Groch',                '🟢', 'crops'),
    'GREENBEAN':        ('Fasolka szparagowa',   '🫘', 'crops'),
    'SPINACH':          ('Szpinak',              '🥬', 'crops'),
    'COTTON':           ('Bawełna',              '⚪', 'crops'),
    'GRASS':            ('Trawa',                '🌿', 'crops'),
    'MEADOW':           ('Łąka',                 '🌿', 'crops'),
    'OILSEEDRADISH':    ('Rzodkiew oleista',     '🌱', 'crops'),
    'LETTUCE':          ('Sałata',               '🥬', 'crops'),
    'CHILLI':           ('Chili',                '🌶️', 'crops'),
    'TOMATO':           ('Pomidor',              '🍅', 'crops'),
    'STRAWBERRY':       ('Truskawka',            '🍓', 'crops'),
    'GARLIC':           ('Czosnek',              '🧄', 'crops'),
    'NAPACABBAGE':      ('Kapusta pekińska',     '🥬', 'crops'),
    'GRAPE':            ('Winogrona',            '🍇', 'crops'),
    'OLIVE':            ('Oliwki',               '🫒', 'crops'),
    'SPRING_ONION':     ('Szczypiorek',          '🌱', 'crops'),
    'RICE':             ('Ryż',                  '🌾', 'crops'),
    'RICELONGGRAIN':    ('Ryż długoziarnisty',   '🌾', 'crops'),
    'RICESAPLINGS':     ('Sadzonki ryżu',        '🌱', 'crops'),
    'POPLAR':           ('Topola',               '🌳', 'crops'),

    # ── Produkty przetworzone ────────────────────────────────────────────────
    'FLOUR':            ('Mąka',                 '🌾', 'processed'),
    'BREAD':            ('Chleb',                '🍞', 'processed'),
    'BUTTER':           ('Masło',                '🧈', 'processed'),
    'SUGAR':            ('Cukier',               '🍬', 'processed'),
    'CANOLA_OIL':       ('Olej rzepakowy',       '🫙', 'processed'),
    'SUNFLOWER_OIL':    ('Olej słonecznikowy',   '🫙', 'processed'),
    'OLIVE_OIL':        ('Oliwa z oliwek',       '🫙', 'processed'),
    'RICE_OIL':         ('Olej ryżowy',          '🫙', 'processed'),
    'GRAPEJUICE':       ('Sok winogronowy',      '🍇', 'processed'),
    'RAISINS':          ('Rodzynki',             '🍇', 'processed'),
    'POTATOCHIPS':      ('Chipsy',               '🥔', 'processed'),
    'CANNED_PEAS':      ('Groch w puszce',       '🥫', 'processed'),
    'JARRED_GREENBEAN': ('Fasolka w słoiku',     '🫙', 'processed'),
    'CEREAL':           ('Płatki zbożowe',       '🥣', 'processed'),
    'CHOCOLATE':        ('Czekolada',            '🍫', 'processed'),
    'CAKE':             ('Ciasto',               '🎂', 'processed'),
    'ONIONBAG':         ('Cebula w worku',       '🧅', 'processed'),
    'ONIONSALT':        ('Sól cebulowa',         '🧂', 'processed'),
    'ONIONSOUP':        ('Zupa cebulowa',        '🍲', 'processed'),
    'FRIEDONION':       ('Smażona cebula',       '🧅', 'processed'),
    'FERMENTEDNAPACABBAGE': ('Kapusta kiszona',  '🥬', 'processed'),
    'NOODLESOUP':       ('Zupa z makaronem',     '🍜', 'processed'),
    'SOUPCANSBEETROOT': ('Zupa buraczana w puszce',  '🥫', 'processed'),
    'SOUPCANSCARROTS':  ('Zupa marchewkowa w puszce','🥫', 'processed'),
    'SOUPCANSMIXED':    ('Zupa mieszana w puszce',   '🥫', 'processed'),
    'SOUPCANSPARSNIP':  ('Zupa pasternaková w puszce','🥫', 'processed'),
    'SOUPCANSPOTATO':   ('Zupa ziemniaczana w puszce','🥫', 'processed'),
    'PRESERVEDBEETROOT':('Przetwory z buraczków','🫙', 'processed'),
    'PRESERVEDCARROTS': ('Przetwory z marchewki','🫙', 'processed'),
    'PRESERVEDPARSNIP': ('Przetwory z pasternaka','🫙', 'processed'),
    'SPINACH_BAGS':     ('Szpinak w workach',    '🥬', 'processed'),
    'RICE_BAGS':        ('Ryż w workach',        '🌾', 'processed'),
    'RICE_BOXES':       ('Ryż w pudełkach',      '📦', 'processed'),
    'RICEFLOUR':        ('Mąka ryżowa',          '🌾', 'processed'),
    'RICEROLLS':        ('Bułki ryżowe',         '🍙', 'processed'),
    'MOLASSES':         ('Melasa',               '🫙', 'processed'),

    # ── Nabiał ──────────────────────────────────────────────────────────────
    'MILK':             ('Mleko',                '🥛', 'dairy'),
    'MILK_BOTTLED':     ('Mleko butelkowane',    '🥛', 'dairy'),
    'BUFFALOMILK':      ('Mleko bawole',         '🥛', 'dairy'),
    'BUFFALOMILK_BOTTLED': ('Mleko bawole butelkowane', '🥛', 'dairy'),
    'BUFFALOMOZZARELLA':('Mozzarella bawola',    '🧀', 'dairy'),
    'CHEESE':           ('Ser',                  '🧀', 'dairy'),
    'GOATMILK':         ('Mleko kozie',          '🥛', 'dairy'),
    'GOATMILK_BOTTLED': ('Mleko kozie butelkowane','🥛','dairy'),
    'GOATCHEESE':       ('Ser kozi',             '🧀', 'dairy'),
    'EGG':              ('Jaja',                 '🥚', 'dairy'),

    # ── Zwierzęta ────────────────────────────────────────────────────────────
    'COW_ANGUS':        ('Krowa Angus',          '🐄', 'animals'),
    'COW_HIGHLAND_CATTLE': ('Krowa Highland',   '🐄', 'animals'),
    'COW_HOLSTEIN':     ('Krowa Holstein',       '🐄', 'animals'),
    'COW_LIMOUSIN':     ('Krowa Limousin',       '🐄', 'animals'),
    'COW_SWISS_BROWN':  ('Krowa Szwajcarska',    '🐄', 'animals'),
    'COW_WATERBUFFALO': ('Bawół wodny',          '🐃', 'animals'),
    'PIG_BERKSHIRE':    ('Świnia Berkshire',     '🐷', 'animals'),
    'PIG_BLACK_PIED':   ('Świnia Black Pied',    '🐷', 'animals'),
    'PIG_LANDRACE':     ('Świnia Landrace',      '🐷', 'animals'),
    'SHEEP_BLACK_WELSH':('Owca Black Welsh',     '🐑', 'animals'),
    'SHEEP_LANDRACE':   ('Owca Landrace',        '🐑', 'animals'),
    'SHEEP_STEINSCHAF': ('Owca Steinschaf',      '🐑', 'animals'),
    'SHEEP_SWISS_MOUNTAIN': ('Owca Swiss Mountain','🐑','animals'),
    'WOOL':             ('Wełna',                '🧶', 'animals'),
    'HONEY':            ('Miód',                 '🍯', 'animals'),

    # ── Ryby i owoce morza ───────────────────────────────────────────────────
    'SALMON':           ('Łosoś',                '🐟', 'fish'),
    'SALMONYOUNG':      ('Młody łosoś',          '🐟', 'fish'),
    'TROUT':            ('Pstrąg',               '🐟', 'fish'),
    'TROUTYOUNG':       ('Młody pstrąg',         '🐟', 'fish'),
    'OYSTER':           ('Ostrygi',              '🦪', 'fish'),
    'FISHFOOD':         ('Pokarm dla ryb',       '🐟', 'fish'),
    'ENOKI':            ('Grzyby enoki',         '🍄', 'fish'),

    # ── Leśnictwo ────────────────────────────────────────────────────────────
    'WOOD':             ('Drewno',               '🪵', 'forestry'),
    'WOODBEAM':         ('Belka drewniana',      '🪵', 'forestry'),
    'WOODCHIPS':        ('Zrębki drzewne',       '🌲', 'forestry'),
    'TREESAPLINGS':     ('Sadzonki drzew',       '🌱', 'forestry'),
    'POPLAR':           ('Topola',               '🌳', 'forestry'),

    # ── Bele ─────────────────────────────────────────────────────────────────
    'ROUNDBALE':        ('Bela okrągła (słoma)', '🟫', 'bales'),
    'SQUAREBALE':       ('Bela kwadratowa (słoma)','🟫','bales'),
    'ROUNDBALE_GRASS':  ('Bela okrągła (trawa)', '🟩', 'bales'),
    'SQUAREBALE_GRASS': ('Bela kwadratowa (trawa)','🟩','bales'),
    'ROUNDBALE_DRYGRASS':('Bela okrągła (siano)','🟨', 'bales'),
    'SQUAREBALE_DRYGRASS':('Bela kwadratowa (siano)','🟨','bales'),
    'ROUNDBALE_COTTON': ('Bela okrągła (bawełna)','⬜','bales'),
    'SQUAREBALE_COTTON':('Bela kwadratowa (bawełna)','⬜','bales'),
    'ROUNDBALE_WOOD':   ('Bela okrągła (drewno)','🟫', 'bales'),
    'SQUAREBALE_WOOD':  ('Bela kwadratowa (drewno)','🟫','bales'),

    # ── Produkty uboczne ─────────────────────────────────────────────────────
    'STRAW':            ('Słoma',                '🌾', 'byproducts'),
    'STRAW_PELLETS':    ('Pellet słomiany',      '🌾', 'byproducts'),
    'HAY_PELLETS':      ('Pellet sianowy',       '🌿', 'byproducts'),
    'CHAFF':            ('Sieczka',              '🌿', 'byproducts'),
    'DRYGRASS':         ('Siano',                '🌾', 'byproducts'),
    'DRYGRASS_WINDROW': ('Siano (pokos)',        '🌾', 'byproducts'),
    'GRASS_WINDROW':    ('Trawa (pokos)',        '🌿', 'byproducts'),
    'SILAGE':           ('Kiszonka',             '🌿', 'byproducts'),
    'SILAGE_ADDITIVE':  ('Dodatek do kiszonki',  '🧴', 'byproducts'),
    'FORAGE':           ('Pasza',                '🌿', 'byproducts'),
    'FORAGE_MIXING':    ('Mieszanka paszowa',    '🌿', 'byproducts'),
    'DIGESTATE':        ('Poferment',            '♻️', 'byproducts'),
    'MANURE':           ('Obornik',              '💩', 'byproducts'),
    'LIQUIDMANURE':     ('Gnojowica',            '💩', 'byproducts'),

    # ── Środki produkcji ─────────────────────────────────────────────────────
    'SEEDS':            ('Nasiona',              '🌱', 'inputs'),
    'FERTILIZER':       ('Nawóz',                '🧴', 'inputs'),
    'LIQUIDFERTILIZER': ('Nawóz płynny',         '🧴', 'inputs'),
    'HERBICIDE':        ('Herbicyd',             '🧴', 'inputs'),
    'LIME':             ('Wapno',                '🪨', 'inputs'),
    'MINERAL_FEED':     ('Pasza mineralna',      '🧴', 'inputs'),
    'PIGFOOD':          ('Karma dla świń',       '🐷', 'inputs'),
    'LIQUIDSEEDTREATMENT': ('Zaprawianie nasion','🧴', 'inputs'),
    'DIESEL':           ('Diesel',               '⛽', 'inputs'),
    'DEF':              ('AdBlue',               '🧴', 'inputs'),
    'METHANE':          ('Metan',                '⚡', 'inputs'),
    'ELECTRICCHARGE':   ('Energia elektryczna',  '⚡', 'inputs'),
    'WATER':            ('Woda',                 '💧', 'inputs'),

    # ── Materiały budowlane ──────────────────────────────────────────────────
    'WOOD':             ('Drewno',               '🪵', 'construction'),
    'BOARDS':           ('Deski',                '🪵', 'construction'),
    'PLANKS':           ('Belki',                '🪵', 'construction'),
    'CEMENT':           ('Cement',               '🧱', 'construction'),
    'CEMENTBRICKS':     ('Cegły cementowe',      '🧱', 'construction'),
    'PREFABWALL':       ('Ściana prefabrykowana','🧱', 'construction'),
    'ROOFPLATES':       ('Płyty dachowe',        '🏗️', 'construction'),
    'SHINGLEROOF':      ('Gonty dachowe',        '🏗️', 'construction'),
    'STONE':            ('Kamień',               '🪨', 'construction'),
    'STONEBIG':         ('Duży kamień',          '🪨', 'construction'),
    'COAL':             ('Węgiel',               '⬛', 'construction'),
    'ROPE':             ('Lina',                 '🪢', 'construction'),
    'CASTLEROCK':       ('Kamień zamkowy',       '🪨', 'construction'),

    # ── Inne ─────────────────────────────────────────────────────────────────
    'BALE_NET':         ('Siatka do bel',        '📦', 'other'),
    'BALE_TWINE':       ('Sznurek do bel',       '📦', 'other'),
    'BALE_WRAP':        ('Folia do bel',         '📦', 'other'),
    'BARREL':           ('Beczka',               '🛢️', 'other'),
    'BATHTUB':          ('Wanna',                '🛁', 'other'),
    'BUCKET':           ('Wiadro',               '🪣', 'other'),
    'CARTONROLL':       ('Rolka kartonu',        '📦', 'other'),
    'CLOTHES':          ('Ubrania',              '👕', 'other'),
    'FABRIC':           ('Tkanina',              '🧵', 'other'),
    'FURNITURE':        ('Meble',                '🪑', 'other'),
    'PAPERROLL':        ('Rolka papieru',        '🧻', 'other'),
}



def _get_current_period_idx(save_path: Path) -> int:
    env_file = save_path / "environment.xml"
    if not env_file.exists():
        return 0
    try:
        tree = ET.parse(env_file)
        root = tree.getroot()
        current_day = int(root.findtext("currentDay", "1"))
        days_per_period = int(root.findtext("daysPerPeriod", "3"))
        year_length = 12 * days_per_period
        return ((current_day - 1) % year_length) // days_per_period
    except Exception:
        return 0


def parse_economy(save_path: Path) -> dict:
    xml_file = save_path / "economy.xml"
    if not xml_file.exists():
        return {"items": [], "currentPeriodIdx": 0, "periods": PERIODS}

    current_period_idx = _get_current_period_idx(save_path)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception:
        return {"items": [], "currentPeriodIdx": current_period_idx, "periods": PERIODS}

    fill_types_el = root.find("fillTypes")
    if fill_types_el is None:
        return {"items": [], "currentPeriodIdx": current_period_idx, "periods": PERIODS}

    items = []
    for ft_el in fill_types_el.findall("fillType"):
        fill_type = ft_el.get("fillType", "")
        if not fill_type:
            continue

        history_el = ft_el.find("history")
        if history_el is None:
            continue

        prices = []
        for period in PERIODS:
            p_el = history_el.find(f"period[@period='{period}']")
            prices.append(int(p_el.text) if p_el is not None and p_el.text else 0)

        if not any(prices):
            continue

        info = ITEM_INFO.get(fill_type)
        emoji    = info[1] if info else '📦'
        category = info[2] if info else 'other'

        current_price = prices[current_period_idx]
        max_price = max(prices)
        min_price = min(prices)
        prev_idx = (current_period_idx - 1) % 12
        next_idx = (current_period_idx + 1) % 12

        if current_price > prices[prev_idx]:
            trend = 'up'
        elif current_price < prices[prev_idx]:
            trend = 'down'
        else:
            trend = 'flat'

        items.append({
            "type":         fill_type,
            "emoji":        emoji,
            "category":     category,
            "prices":       prices,
            "currentPrice": current_price,
            "nextPrice":    prices[next_idx],
            "maxPrice":     max_price,
            "minPrice":     min_price,
            "maxPeriodIdx": prices.index(max_price),
            "trend":        trend,
        })

    items.sort(key=lambda x: x["currentPrice"], reverse=True)

    return {
        "items": items,
        "currentPeriodIdx": current_period_idx,
        "periods": PERIODS,
    }
