"""Space Rangers - Havirov Coin Edition"""
import pygame, sys, os, json, random, math, time, threading

HAVIROV_COIN_DIR = os.path.expanduser("~/Downloads/Havirov-Coin-master")
if os.path.exists(HAVIROV_COIN_DIR):
    sys.path.insert(0, HAVIROV_COIN_DIR)
else:
    HAVIROV_COIN_DIR = os.path.join(os.path.dirname(__file__), "..", "Havirov-Coin-master")
    if os.path.exists(HAVIROV_COIN_DIR):
        sys.path.insert(0, HAVIROV_COIN_DIR)

from miner import CPUMiner
from network import NetworkClient, get_random_ship_name
pygame.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
BLACK = (0,0,0)
DARK_BG = (5,5,20)
SPACE_BG = (8,8,25)
WHITE = (200,200,210)
GREEN = (0,180,0)
BRIGHT_GREEN = (0,220,0)
RED = (180,20,20)
BRIGHT_RED = (220,40,40)
BLUE = (0,80,180)
BRIGHT_BLUE = (30,130,255)
YELLOW = (180,180,0)
BRIGHT_YELLOW = (230,230,40)
CYAN = (0,160,180)
PURPLE = (150,0,255)
BRIGHT_PURPLE = (200,100,255)
ORANGE = (255,165,0)
GRAY = (70,70,70)
LIGHT_GRAY = (140,140,140)
DARK_GRAY = (25,25,35)
BORDER_COLOR = (40,140,200)
FUEL_COLOR = (255,150,0)
PANEL_BG = (10,10,30,220)

# Radar settings
RADAR_RANGE = 1500
RADAR_SIZE = 180
RADAR_POS = (SCREEN_WIDTH - RADAR_SIZE - 20, 100)

WALLET_PATH = os.path.join(HAVIROV_COIN_DIR, "wallet.dat")
MINER_CONFIG_PATH = os.path.join(HAVIROV_COIN_DIR, "miner_config.json")
MINER_SHARES_PATH = os.path.join(HAVIROV_COIN_DIR, "valid_shares.log")
SAVE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")

class WalletInterface:
    def __init__(self):
        self.balance = 0.0
        self.address = ""
        self.name = ""
        self.load_wallet()
    
    def create_wallet(self, name="Space Ranger"):
        """Create a new wallet"""
        import string
        address = ''.join(random.choices(string.hexdigits.lower(), k=40))
        
        wallet_data = {
            "address": address,
            "name": name,
            "balance": 0.0,
            "transactions": []
        }
        
        try:
            with open(WALLET_PATH, "w") as f:
                json.dump(wallet_data, f, indent=2)
            self.balance = 0.0
            self.address = address
            self.name = name
            return True
        except Exception as e:
            print(f"Chyba pri vytvareni walletu: {e}")
            return False

    def load_wallet(self):
        try:
            if os.path.exists(WALLET_PATH):
                with open(WALLET_PATH, "r") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", 0.0)
                    self.address = data.get("address", "")
                    self.name = data.get("name", "")
                    return True
        except Exception as e:
            print(f"Chyba: {e}")
        return False

    def get_balance(self):
        self.load_wallet()
        return self.balance

    def add_credits(self, amount):
        try:
            self.load_wallet()
            self.balance += amount
            if os.path.exists(WALLET_PATH):
                with open(WALLET_PATH, "r") as f:
                    data = json.load(f)
                data["balance"] = self.balance
                with open(WALLET_PATH, "w") as f:
                    json.dump(data, f, indent=2)
                return True
        except Exception as e:
            print(f"Chyba: {e}")
        return False

    def subtract_credits(self, amount):
        try:
            self.load_wallet()
            if self.balance >= amount:
                self.balance -= amount
                if os.path.exists(WALLET_PATH):
                    with open(WALLET_PATH, "r") as f:
                        data = json.load(f)
                    data["balance"] = self.balance
                    with open(WALLET_PATH, "w") as f:
                        json.dump(data, f, indent=2)
                    return True
        except Exception as e:
            print(f"Chyba: {e}")
        return False

# Item database - 500+ items
ITEM_CATEGORIES = {
    "Minerály": ["Ruda", "Zlato", "Stribro", "Platina", "Krystaly", "Kremik", "Uhlí", "Síra", "Vzácné kovy", "Měď", "Železo", "Hliník", "Titan", "Lithium", "Kobalt", "Nikl", "Cín", "Zinek", "Olovo", "Cín"],
    "Zbraně": ["Laser I", "Laser II", "Laser III", "Plazmová puška", "Fotonový kanón", "Raketomet", "Torpedo", "Ionový blaster", "Neutronový emitátor", "Pulzní laser", "Gaussovka", "Railgun", "Štítový generátor", "EM pulz", "Disruptor"],
    "Potraviny": ["Chléb", "Maso", "Ovoce", "Zelenina", "Konzervy", "Syntetické jídlo", "Nutri-pasty", "Proteinové tyčinky", "Káva", "Čaj", "Víno", "Pivo", "Voda", "Energetické nápoje"],
    "Technologie": ["Čipy", "Procesory", "Paměti", "Senzoři", "Navigace", "Komunikace", "Šifrování", "AI moduly", "Hologramy", "Nanotechnologie", "Bionika", "Kybernetika", "Robotika", "Drony", "Satelity"],
    "Léky": ["Analgetika", "Antibiotika", "Stimulanty", "Nanoleky", "Regenerace", "Antitoxin", "Vakcíny", "Vitamíny", "Očkování", "Adrenalin", "Sedativa", "Antidepresiva"],
    "Luxus": ["Šperky", "Víno", "Kaviár", "Svatky", "Umění", "Starodávné předměty", "Holografické obrazy", "Virtuální realita", "Hudební nástroje", "Knihy", "Parfémy"],
    "Komponenty": ["Motory", "Převodovky", "Kabely", "Trubky", "Filtry", "Čerpadla", "Ventily", "Těsnění", "Ložiska", "Šrouby", "Matky", "Podložky", "Svařovací hořáky"]
}

# Generate 500+ items
ALL_ITEMS = []
for category, items in ITEM_CATEGORIES.items():
    for item in items:
        ALL_ITEMS.append((item, category))
base_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta", "Iota", "Kappa", "Lambda",
              "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon", "Phi",
              "Chi", "Psi", "Omega", "Nova", "Prime", "Star", "Nebula", "Void", "Crystal", "Shadow"]
for i in range(600 - len(ALL_ITEMS)):
    cat = list(ITEM_CATEGORIES.keys())[i % len(ITEM_CATEGORIES)]
    suffix = base_names[i % len(base_names)]
    ALL_ITEMS.append((f"{cat[:-1]} {suffix} {i}", cat))

# Pre-computed item name -> category map
ITEM_CATEGORY_MAP = {name: cat for name, cat in ALL_ITEMS}

ITEM_PASSIVE_BONUSES = {
    "Štítový generátor": {"max_shield": 10, "shield_regen": 0.05},
    "AI moduly": {"rotation_speed": 0.02},
    "Navigace": {"max_speed": 0.5},
    "Nanotechnologie": {"hp_regen": 0.05},
    "Bionika": {"max_hp": 15},
    "Kybernetika": {"max_hp": 10, "hp_regen": 0.02},
    "Motory": {"thrust_power": 0.02, "max_speed": 0.3},
    "Senzoři": {"radar_range": 100},
    "Komunikace": {"radar_range": 50},
    "Stimulanty": {"max_speed": 0.5},
    "Antibiotika": {"hp_regen": 0.03},
    "Regenerace": {"hp_regen": 0.08},
    "Nanoleky": {"hp_regen": 0.05, "max_hp": 10},
}

SKILL_DEFS = {
    "obchod": {"name": "Obchodování", "icon": "$", "desc": "Sleva pri nákupu a prémiový prodej (+0.2%/lvl)", "max": 100},
    "stity": {"name": "Štíty", "icon": "◈", "desc": "Více štítů (+1/lvl) a rychlejší regenerace", "max": 100},
    "zbrane": {"name": "Zbraně", "icon": "⚔", "desc": "Větší poškození (+1%/lvl) a rychlejší střelba", "max": 100},
    "motor": {"name": "Motor", "icon": "»", "desc": "Vyšší rychlost a tah motoru", "max": 100},
    "naklad": {"name": "Náklad", "icon": "▣", "desc": "Větší nákladový prostor (+2/lvl)", "max": 100},
}

class Planet:
    def __init__(self, name, x, y, station_type="PLANET"):
        self.name = name
        self.x = x
        self.y = y
        self.station_type = station_type
        self.radius = self._get_radius()
        self.color = self._get_color()
        self.goods = self._generate_goods()
        self.prices = self._generate_prices()
        self.available_items = self._get_available_items()
        self.trade_history = {}  # Historie obchodu pro dynamickou cenu
        self.last_update = 0     # Casova znacka pro aktualizaci cen

    def _get_radius(self):
        sizes = {
            "PLANET": 18,
            "DOCKY": 14,
            "PIRATSKY_KLUB": 12,
            "HI_TECH_LAB": 13,
            "OBCHODNI_STANICE": 15
        }
        return sizes.get(self.station_type, 16)

    def _get_color(self):
        colors = {
            "PLANET": (0, 100, 210),
            "DOCKY": (100, 150, 200),
            "PIRATSKY_KLUB": (180, 30, 30),
            "HI_TECH_LAB": (0, 200, 200),
            "OBCHODNI_STANICE": (200, 150, 0)
        }
        return colors.get(self.station_type, (100, 100, 100))

    def _generate_goods(self):
        goods = {}
        item_counts = {
            "PLANET": 8, "DOCKY": 10, "PIRATSKY_KLUB": 6, "HI_TECH_LAB": 12, "OBCHODNI_STANICE": 15
        }
        count = item_counts.get(self.station_type, 8)
        cat_map = {
            "PLANET": ["Minerály", "Potraviny", "Léky"],
            "DOCKY": ["Zbraně", "Technologie", "Komponenty"],
            "PIRATSKY_KLUB": ["Zbraně", "Minerály", "Luxus"],
            "HI_TECH_LAB": ["Technologie", "Léky", "Komponenty"],
            "OBCHODNI_STANICE": ["Minerály", "Potraviny", "Zbraně", "Technologie", "Léky", "Luxus"]
        }
        categories = cat_map.get(self.station_type, ["Minerály", "Potraviny"])
        available = [name for name, cat in ITEM_CATEGORY_MAP.items() if cat in categories]
        for item in random.sample(available, min(count, len(available))):
            goods[item] = random.randint(10, 80)
        return goods

    def _get_available_items(self):
        cat_map = {
            "PLANET": ["Minerály", "Potraviny", "Léky"],
            "DOCKY": ["Zbraně", "Technologie", "Komponenty"],
            "PIRATSKY_KLUB": ["Zbraně", "Minerály", "Luxus"],
            "HI_TECH_LAB": ["Technologie", "Léky", "Komponenty"],
            "OBCHODNI_STANICE": ["Minerály", "Potraviny", "Zbraně", "Technologie", "Léky", "Luxus"]
        }
        categories = cat_map.get(self.station_type, ["Minerály"])
        return [name for name, cat in ITEM_CATEGORY_MAP.items() if cat in categories]
    
    def _generate_new_goods(self):
        """Generovani noveho zbozi pro udrzeni nekonecneho hraní"""
        if len(self.goods) < 50:
            cat_map = {
                "PLANET": ["Minerály", "Potraviny", "Léky"],
                "DOCKY": ["Zbraně", "Technologie", "Komponenty"],
                "PIRATSKY_KLUB": ["Zbraně", "Minerály", "Luxus"],
                "HI_TECH_LAB": ["Technologie", "Léky", "Komponenty"],
                "OBCHODNI_STANICE": ["Minerály", "Potraviny", "Zbraně", "Technologie", "Léky", "Luxus"]
            }
            available_categories = cat_map.get(self.station_type, ["Minerály"])
            selected_category = random.choice(available_categories)
            
            category_items = [name for name, cat in ITEM_CATEGORY_MAP.items() if cat == selected_category]
            
            new_items = [item for item in category_items if item not in self.goods]
            
            if new_items:
                new_item = random.choice(new_items)
                self.goods[new_item] = random.randint(5, 30)

    def _generate_prices(self):
        prices = {}
        base_prices = {
            "Minerály": {"base": 0.5, "variance": 0.3, "multiplier": 1.0},
            "Zbraně": {"base": 2.0, "variance": 1.0, "multiplier": 1.2},
            "Potraviny": {"base": 0.3, "variance": 0.2, "multiplier": 0.8},
            "Technologie": {"base": 3.0, "variance": 1.5, "multiplier": 1.5},
            "Léky": {"base": 1.0, "variance": 0.5, "multiplier": 1.1},
            "Luxus": {"base": 5.0, "variance": 2.5, "multiplier": 2.0},
            "Komponenty": {"base": 0.8, "variance": 0.4, "multiplier": 0.9}
        }
        
        for item, cat in ALL_ITEMS:
            if cat in base_prices:
                price_data = base_prices[cat]
                # Základní cena s náhodnou odchylkou
                base_price = price_data["base"] + random.uniform(-price_data["variance"], price_data["variance"])
                # Multiplikátor podle typu stanice
                station_multiplier = {
                    "PLANET": 1.0,
                    "DOCKY": 1.1,
                    "PIRATSKY_KLUB": 1.8,
                    "HI_TECH_LAB": 1.3,
                    "OBCHODNI_STANICE": 0.9
                }.get(self.station_type, 1.0)
                
                # Výpočet finální ceny
                final_price = base_price * price_data["multiplier"] * station_multiplier
                # Omezení rozumného rozsahu
                final_price = max(0.0001, min(50.0, final_price))
                prices[item] = round(final_price, 4)
            else:
                prices[item] = round(random.uniform(0.1, 2.0), 4)
        
        return prices

    def get_type_name(self):
        names = {
            "PLANET": "Planeta",
            "DOCKY": "Doky",
            "PIRATSKY_KLUB": "Piratsky klub",
            "HI_TECH_LAB": "Hi-Tech Lab",
            "OBCHODNI_STANICE": "Obchodni stanice"
        }
        return names.get(self.station_type, "Nezname")
    
    def update_prices(self):
        """Aktualizace cen na zaklade poptavky a nabidky"""
        current_time = time.time()
        
        # Aktualizace kazdych 30 sekund
        if current_time - self.last_update < 30:
            return
            
        self.last_update = current_time
        
        # Zmena ceny na zaklade historie obchodu
        for item in self.prices:
            if item in self.trade_history:
                # Pokud byl item nedavno koupen, cena stoupla
                if self.trade_history[item] > 0:
                    self.prices[item] = round(self.prices[item] * 1.1, 4)
                # Pokud byl item nedavno prodan, cena klesla
                elif self.trade_history[item] < 0:
                    self.prices[item] = round(self.prices[item] * 0.9, 4)
                
                # Omezeni rozsahu ceny
                base_price = self._get_base_price(item)
                self.prices[item] = max(round(base_price * 0.5, 4), min(round(base_price * 3.0, 4), self.prices[item]))
            
            # Postupne vraceni puvodni ceny
            base_price = self._get_base_price(item)
            if self.prices[item] > base_price:
                self.prices[item] = round(self.prices[item] * 0.99, 4)
            elif self.prices[item] < base_price:
                self.prices[item] = round(self.prices[item] * 1.01, 4)
        
        # Reset historie
        self.trade_history.clear()
    
    def _get_base_price(self, item):
        """Ziskani zakladni ceny polozky"""
        base_prices = {
            "Minerály": 0.5,
            "Zbraně": 2.0,
            "Potraviny": 0.3,
            "Technologie": 3.0,
            "Léky": 1.0,
            "Luxus": 5.0,
            "Komponenty": 0.8
        }
        category = ITEM_CATEGORY_MAP.get(item)
        if category is None:
            category = next((cat for cat, items in ITEM_CATEGORIES.items() if item in items), "Neznámé")
        return base_prices.get(category, 0.1)
    
    def record_trade(self, item, amount):
        """Zaznamenani obchodu pro dynamickou cenu"""
        if item not in self.trade_history:
            self.trade_history[item] = 0
        self.trade_history[item] += amount

    def draw_on_map(self, screen, camera_x, camera_y, zoom, font_tiny):
        screen_x = int((self.x - camera_x) * zoom + SCREEN_WIDTH // 2)
        screen_y = int((self.y - camera_y) * zoom + SCREEN_HEIGHT // 2)
        radius = max(3, int(self.radius * zoom))
        if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), radius)
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), radius, 1)
            if zoom > 0.3:
                name_text = font_tiny.render(self.name, True, WHITE)
                screen.blit(name_text, (screen_x - name_text.get_width() // 2, screen_y + radius + 3))

    def draw_on_radar(self, screen, radar_x, radar_y, radar_scale, player_x, player_y):
        rel_x = self.x - player_x
        rel_y = self.y - player_y
        dist = math.sqrt(rel_x**2 + rel_y**2)
        if dist <= RADAR_RANGE:
            radar_screen_x = radar_x + RADAR_SIZE // 2 + int(rel_x * radar_scale)
            radar_screen_y = radar_y + RADAR_SIZE // 2 + int(rel_y * radar_scale)
            dot_size = 3 if self.station_type == "PLANET" else 2
            pygame.draw.circle(screen, self.color, (radar_screen_x, radar_screen_y), dot_size)

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.direction = 0
        self.hp = 100
        self.max_hp = 100
        self.shield = 50
        self.max_shield = 50
        self.fuel = 100
        self.max_fuel = 100
        self.cargo = {}
        self.max_cargo = 50
        self.weapons = ["Laser I"]
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.skills = {"obchod": 0, "stity": 0, "zbrane": 0, "motor": 0, "naklad": 0}
        self.skill_points = 0
        self.name = get_random_ship_name()
        self.thrust_power = 0.08
        self.max_speed = 4.0
        self.rotation_speed = 0.05
        self.docked_at = None
        self.auto_pilot = False
        self.drag = 0.96
        self.last_shot = 0
        self.shoot_delay = 15
        self._applied_bonuses = {}
        self.radar_bonus = 0

    def apply_thrust(self, direction, amount=1.0):
        self.vx += math.cos(direction) * self.thrust_power * amount
        self.vy += math.sin(direction) * self.thrust_power * amount
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

    def rotate_to(self, target_direction):
        angle_diff = target_direction - self.direction
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        if abs(angle_diff) < self.rotation_speed:
            self.direction = target_direction
        elif angle_diff > 0:
            self.direction += self.rotation_speed
        else:
            self.direction -= self.rotation_speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.drag
        self.vy *= self.drag
        shield_regen = 0.03 + self._applied_bonuses.get("shield_regen", 0)
        if self.shield < self.max_shield:
            self.shield = min(self.shield + shield_regen, self.max_shield)
        hp_regen = self._applied_bonuses.get("hp_regen", 0)
        if hp_regen > 0 and self.hp < self.max_hp:
            self.hp = min(self.hp + hp_regen, self.max_hp)

    def draw_in_space(self, screen, screen_x, screen_y, zoom):
        size = max(4, int(14 * zoom))
        points = [
            (screen_x + size * math.cos(self.direction),
             screen_y + size * math.sin(self.direction)),
            (screen_x + size * 0.6 * math.cos(self.direction + 2.3),
             screen_y + size * 0.6 * math.sin(self.direction + 2.3)),
            (screen_x - size * 0.5 * math.cos(self.direction),
             screen_y - size * 0.5 * math.sin(self.direction)),
            (screen_x + size * 0.6 * math.cos(self.direction - 2.3),
             screen_y + size * 0.6 * math.sin(self.direction - 2.3))
        ]
        pygame.draw.polygon(screen, BRIGHT_GREEN, points)
        pygame.draw.polygon(screen, WHITE, points, 1)
        engine_x = screen_x - size * 0.5 * math.cos(self.direction)
        engine_y = screen_y - size * 0.5 * math.sin(self.direction)
        pygame.draw.circle(screen, (255, 120, 0), (int(engine_x), int(engine_y)), 2)

    def draw_on_radar(self, screen, radar_x, radar_y, radar_scale):
        radar_screen_x = radar_x + RADAR_SIZE // 2
        radar_screen_y = radar_y + RADAR_SIZE // 2
        size = 4
        points = [
            (radar_screen_x + size * math.cos(self.direction),
             radar_screen_y + size * math.sin(self.direction)),
            (radar_screen_x + size * 0.7 * math.cos(self.direction + 2.5),
             radar_screen_y + size * 0.7 * math.sin(self.direction + 2.5)),
            (radar_screen_x + size * 0.7 * math.cos(self.direction - 2.5),
             radar_screen_y + size * 0.7 * math.sin(self.direction - 2.5))
        ]
        pygame.draw.polygon(screen, BRIGHT_GREEN, points)

    def update_passive_bonuses(self):
        bonus_stats = ["max_hp", "max_shield", "max_fuel", "max_cargo", "max_speed", "thrust_power", "rotation_speed", "shoot_delay"]
        for stat in bonus_stats:
            current_val = self._applied_bonuses.get(stat, 0)
            if current_val != 0:
                if stat == "shoot_delay":
                    setattr(self, stat, getattr(self, stat) - current_val)
                else:
                    setattr(self, stat, getattr(self, stat) - current_val)

        new_bonuses = {}
        self.radar_bonus = 0

        se = self.get_skill_effects()
        for stat, val in se.items():
            if stat == "cargo":
                new_bonuses["max_cargo"] = new_bonuses.get("max_cargo", 0) + val
            elif stat == "shield_max":
                new_bonuses["max_shield"] = new_bonuses.get("max_shield", 0) + val
            elif stat == "speed":
                new_bonuses["max_speed"] = new_bonuses.get("max_speed", 0) + val
            elif stat == "thrust":
                new_bonuses["thrust_power"] = new_bonuses.get("thrust_power", 0) + val
            elif stat == "shoot_delay":
                new_bonuses["shoot_delay"] = new_bonuses.get("shoot_delay", 0) + val
            elif stat in ("shield_regen", "damage_pct"):
                new_bonuses[stat] = new_bonuses.get(stat, 0) + val

        for item, count in self.cargo.items():
            if item in ITEM_PASSIVE_BONUSES:
                for stat, val in ITEM_PASSIVE_BONUSES[item].items():
                    if stat == "radar_range":
                        self.radar_bonus += val * count
                    else:
                        new_bonuses[stat] = new_bonuses.get(stat, 0) + val * count

        for stat, val in new_bonuses.items():
            if stat in bonus_stats:
                if stat == "shoot_delay":
                    setattr(self, stat, getattr(self, stat) + val)
                else:
                    setattr(self, stat, getattr(self, stat) + val)

        self._applied_bonuses = new_bonuses

    def get_skill_effects(self):
        s = self.skills
        return {
            "barter_buy": s["obchod"] * 0.002,
            "barter_sell": s["obchod"] * 0.002,
            "shield_max": s["stity"],
            "shield_regen": s["stity"] * 0.01,
            "damage_pct": s["zbrane"] * 0.01,
            "shoot_delay": s["zbrane"] * 0.1,
            "speed": s["motor"] * 0.02,
            "thrust": s["motor"] * 0.001,
            "cargo": s["naklad"] * 2,
        }

    def add_cargo(self, item, amount):
        current = self.cargo.get(item, 0)
        if current + amount <= self.max_cargo:
            self.cargo[item] = current + amount
            self.update_passive_bonuses()
            return True
        return False

    def remove_cargo(self, item, amount):
        current = self.cargo.get(item, 0)
        if current >= amount:
            self.cargo[item] = current - amount
            if self.cargo[item] == 0:
                del self.cargo[item]
            self.update_passive_bonuses()
            return True
        return False

    def get_total_cargo(self):
        return sum(self.cargo.values())

class EnemyShip:
    def __init__(self, x, y, ship_type="Pirate"):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.type = ship_type
        self.hp = 80 if ship_type == "Pirate" else 120
        self.max_hp = self.hp
        self.speed = 1.5
        self.direction = random.uniform(0, 2 * math.pi)
        self.shoot_timer = 0
        self.color = (160, 30, 30) if ship_type == "Pirate" else (110, 30, 30)
        self.size = 12
        self.drag = 0.96
        self.target_direction = random.uniform(0, 2 * math.pi)
        self.direction_change_timer = random.randint(60, 180)
        self.damage = 10 if ship_type == "Pirate" else 20

    def update(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # Nahodny pohyb a omezeny radar videni
        self.direction_change_timer -= 1
        if self.direction_change_timer <= 0:
            self.target_direction = random.uniform(0, 2 * math.pi)
            self.direction_change_timer = random.randint(60, 180)
        
        # Pokud je hrac v radarovem dosahu, trochu inteligentneji se chovej
        if dist <= RADAR_RANGE:
            # 70% nahodny pohyb, 30% sledovani hrace
            if random.random() < 0.7:
                self.direction = self.target_direction
            else:
                target_dir = math.atan2(dy, dx)
                angle_diff = target_dir - self.direction
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                if angle_diff > 0:
                    self.direction += 0.02
                else:
                    self.direction -= 0.02
        else:
            # Pokud je hrac mimo dosah, pouze nahodny pohyb
            self.direction = self.target_direction
        
        self.vx += math.cos(self.direction) * 0.02
        self.vy += math.sin(self.direction) * 0.02
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.speed:
            self.vx = (self.vx / speed) * self.speed
            self.vy = (self.vy / speed) * self.speed
            
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.drag
        self.vy *= self.drag
        self.shoot_timer -= 1
        
        # Strelba pouze pokud je hrac blizko
        if dist < 250 and self.shoot_timer <= 0:
            self.shoot_timer = 50
            return True
        return False

    def draw_in_space(self, screen, screen_x, screen_y, zoom):
        size = max(3, int(self.size * zoom))
        points = [
            (screen_x + size * math.cos(self.direction),
             screen_y + size * math.sin(self.direction)),
            (screen_x + size * 0.6 * math.cos(self.direction + 2.5),
             screen_y + size * 0.6 * math.sin(self.direction + 2.5)),
            (screen_x - size * 0.4 * math.cos(self.direction),
             screen_y - size * 0.4 * math.sin(self.direction)),
            (screen_x + size * 0.6 * math.cos(self.direction - 2.5),
             screen_y + size * 0.6 * math.sin(self.direction - 2.5))
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (180, 80, 80), points, 1)

    def draw_on_radar(self, screen, radar_x, radar_y, radar_scale, player_x, player_y):
        rel_x = self.x - player_x
        rel_y = self.y - player_y
        dist = math.sqrt(rel_x**2 + rel_y**2)
        if dist <= RADAR_RANGE:
            radar_screen_x = radar_x + RADAR_SIZE // 2 + int(rel_x * radar_scale)
            radar_screen_y = radar_y + RADAR_SIZE // 2 + int(rel_y * radar_scale)
            pygame.draw.circle(screen, BRIGHT_RED, (radar_screen_x, radar_screen_y), 2)

class SpaceRangersGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Rangers - Havirov Coin Edition")
        self.clock = pygame.time.Clock()
        self.font_tiny = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 22)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 40)
        self.font_title = pygame.font.Font(None, 60)
        self.wallet = WalletInterface()
        self.state = "MENU"
        self.running = True
        self.message = ""
        self.message_timer = 0
        self.miner = None
        self.cpuminer = None
        self.mining_thread_ref = None
        self.mining_active = False
        self.network = None
        self.multiplayer = False
        self.remote_players = {}
        self.miner_dir = HAVIROV_COIN_DIR
        self.mining_stats = {
            "hash_count": 0,
            "share_count": 0,
            "start_time": 0,
            "hashrate": 0,
            "total_earned": 0,
            "difficulty": 6000000,
            "max_hashrate": 0,
            "mining_sessions": 0
        }
        self.mining_history = []  # Store mining session history
        
        # Ensure wallet exists
        if not os.path.exists(WALLET_PATH):
            self.wallet.create_wallet("Space Ranger")
            self.show_message("New wallet created! Balance: 0.0000 HVC", 180)
        self.camera_x = 1000
        self.camera_y = 1000
        self.zoom = 1.0
        self.planets = self._generate_galaxy()
        self.player_ship = Ship(1000, 1000)
        self.enemies = self._generate_enemies()
        self.floating_items = []
        self.bullets = []
        self.credits = self.wallet.get_balance()
        self.mouse_pos = (0,0)
        self.mouse_world_x = 0
        self.mouse_world_y = 0
        self.quests = self._generate_quests()
        self.current_quest = None
        self.quest_progress = {"kill": 0, "collect": 0}
        self.docked_planet = None
        self.star_field = [(random.randint(0,6000), random.randint(0,6000), random.randint(1,3)) for _ in range(600)]
        self.map_camera_x = 3000
        self.map_camera_y = 2000
        self.map_zoom = 0.15
        self.clickable_buttons = []
        self.trading_scroll = 0
        self.cargo_scroll = 0
        self.autosave_timer = 0
        self.auto_battle = False
        self.auto_battle_target = None
        self.enemy_bullets = []

    def _generate_galaxy(self):
        return [
            Planet("Zeme", 1000, 1000, "PLANET"),
            Planet("Mars", 2500, 800, "PLANET"),
            Planet("Venuse", 1800, 2200, "PLANET"),
            Planet("Malok Prime", 500, 2800, "PLANET"),
            Planet("Pelengia", 3200, 1500, "PLANET"),
            Planet("Faegana", 1500, 3500, "PLANET"),
            Planet("Gaalos", 3800, 2500, "PLANET"),
            Planet("Klissan Alpha", 4200, 1200, "PLANET"),
            Planet("Klissan Beta", 4500, 2000, "PLANET"),
            Planet("Klissan Gamma", 4000, 3000, "PLANET"),
            Planet("Nova Zeme", 800, 1800, "PLANET"),
            Planet("Havirov Prime", 300, 1200, "PLANET"),
            Planet("Hlavni Doky", 2200, 1600, "DOCKY"),
            Planet("Piratsky Klub", 3500, 900, "PIRATSKY_KLUB"),
            Planet("Hi-Tech Lab", 2800, 2800, "HI_TECH_LAB"),
            Planet("Obchodni Stanice", 3000, 3200, "OBCHODNI_STANICE"),
            Planet("Tajna Zakladna", 4200, 1800, "PIRATSKY_KLUB"),
            Planet("Xenon Labs", 4800, 1500, "HI_TECH_LAB"),
            Planet("Nova Terra", 2000, 4000, "PLANET"),
            Planet("Kryton IV", 5000, 2800, "PLANET"),
            Planet("Starbase Omega", 5500, 2000, "DOCKY"),
            Planet("Cerny Trh", 4800, 3500, "PIRATSKY_KLUB"),
        ]

    def _generate_enemies(self):
        enemies = []
        for _ in range(20):
            x = random.randint(500, 5500)
            y = random.randint(500, 4000)
            enemies.append(EnemyShip(x, y, "Pirate"))
        return enemies

    def _generate_quests(self):
        return [
            {"name": "Doruc zbrane na Mars", "type": "deliver", "item": "Zbrane",
             "amount": 5, "from": "Zeme", "to": "Mars", "reward": 5.0},
            {"name": "Sber rudy v sektoru", "type": "collect", "item": "Ruda",
             "amount": 20, "reward": 3.0},
            {"name": "Znic piratske lodi", "type": "kill", "amount": 3, "reward": 8.0},
            {"name": "Doruc potraviny na Faeganu", "type": "deliver", "item": "Potraviny",
             "amount": 10, "from": "Nova Zeme", "to": "Faegana", "reward": 4.0},
            {"name": "Doruc technologie na Pelengii", "type": "deliver", "item": "Technologie",
             "amount": 8, "from": "Hlavni Doky", "to": "Pelengia", "reward": 6.0},
            {"name": "Doruc leky na Gaalos", "type": "deliver", "item": "Leky",
             "amount": 12, "from": "Hi-Tech Lab", "to": "Gaalos", "reward": 5.5},
        ]

    def show_message(self, text, duration=120):
        self.message = text
        self.message_timer = duration

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.state == "MAP":
                    self.mouse_world_x = (event.pos[0] - SCREEN_WIDTH // 2) / self.map_zoom + self.map_camera_x
                    self.mouse_world_y = (event.pos[1] - SCREEN_HEIGHT // 2) / self.map_zoom + self.map_camera_y
                else:
                    self.mouse_world_x = (event.pos[0] - SCREEN_WIDTH // 2) / self.zoom + self.camera_x
                    self.mouse_world_y = (event.pos[1] - SCREEN_HEIGHT // 2) / self.zoom + self.camera_y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "TRADING":
                    self.handle_trading_click(event.pos)
                else:
                    self.handle_mouse_click(event)
            elif event.type == pygame.MOUSEWHEEL:
                if self.state == "MAP":
                    self.map_zoom *= (1.1 if event.y > 0 else 0.9)
                    self.map_zoom = max(0.1, min(2.0, self.map_zoom))
                elif self.state == "TRADING" and self.docked_planet:
                    max_scroll = max(0, len(self.docked_planet.available_items) - 9)
                    max_cargo_scroll = max(0, len(self.player_ship.cargo) - 9)
                    if max_scroll > 0:
                        self.trading_scroll = max(0, min(max_scroll, self.trading_scroll - event.y))
                    if max_cargo_scroll > 0:
                        self.cargo_scroll = max(0, min(max_cargo_scroll, self.cargo_scroll - event.y))
            if self.state == "MENU":
                self.handle_menu_events(event)
            elif self.state == "GAME":
                self.handle_game_events(event)
            elif self.state == "DOCKED":
                self.handle_docked_events(event)
            elif self.state == "TRADING":
                self.handle_trading_events(event)
            elif self.state == "MAP":
                self.handle_map_events(event)
            elif self.state == "QUEST":
                self.handle_quest_events(event)
            elif self.state == "UPGRADE":
                self.handle_upgrade_events(event)
            elif self.state == "BUY_FUEL":
                self.handle_fuel_events(event)
            elif self.state == "CREDITS":
                self.handle_credits_events(event)
            elif self.state == "MINING_LOG":
                self.handle_mining_log_events(event)
            elif self.state == "SKILLS":
                self.handle_skills_events(event)
            elif self.state == "MULTIPLAYER":
                self.handle_multiplayer_events(event)

    def handle_mouse_click(self, event):
        if event.button == 1:
            clicked_button = False
            for btn in self.clickable_buttons:
                if btn['rect'].collidepoint(event.pos):
                    btn['action']()
                    clicked_button = True
                    break
            if not clicked_button:
                if self.state == "MAP":
                    for planet in self.planets:
                        dist = math.sqrt((self.mouse_world_x - planet.x)**2 + (self.mouse_world_y - planet.y)**2)
                        if dist < 40:
                            self.try_teleport_to_planet(planet)
                            break
                elif self.state == "GAME":
                    self.player_ship.auto_pilot = False
                    self.player_ship.vx = 0
                    self.player_ship.vy = 0
                    self.player_ship.direction = math.atan2(self.mouse_world_y - self.player_ship.y, self.mouse_world_x - self.player_ship.x)
                    self.player_ship.apply_thrust(self.player_ship.direction, 2.0)
                    self.player_ship.fuel = max(0, self.player_ship.fuel - 0.02)
                elif self.state == "TRADING" and self.docked_planet:
                    self.handle_trading_click(event.pos)
                elif self.state == "UPGRADE":
                    self.handle_upgrade_click(event.pos)
        elif event.button == 3 and self.state == "GAME":
            self.fire_weapon()

    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.state = "GAME"
                self.show_message("Vitejte, Rangere! Kliknete pro pohyb, M pro mapu", 180)
            elif event.key == pygame.K_2:
                self.wallet.load_wallet()
                self.credits = self.wallet.get_balance()
                if self.load_game():
                    self.show_message(f"Hra nactena! Pozice: [{int(self.player_ship.x)},{int(self.player_ship.y)}]", 180)
                else:
                    self.show_message(f"Wallet nacten! Zustatek: {self.credits} HVC", 180)
                self.state = "GAME"
            elif event.key == pygame.K_3:
                self.state = "CREDITS"
            elif event.key == pygame.K_4:
                self.state = "GAME"
                self.show_message("Stisknete K pro start miningu!", 120)
            elif event.key == pygame.K_5:
                self.state = "MULTIPLAYER"
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.auto_battle and event.key == pygame.K_ESCAPE:
                self.stop_auto_battle()
                self.show_message("Auto-battle ukoncen!", 60)
                return
            if event.key == pygame.K_ESCAPE:
                self.disconnect_multiplayer()
                self.state = "MENU"
            elif event.key == pygame.K_m:
                self.state = "MAP"
            elif event.key == pygame.K_f:
                self.state = "BUY_FUEL"
            elif event.key == pygame.K_q:
                self.state = "QUEST"
            elif event.key == pygame.K_u:
                self.state = "UPGRADE"
            elif event.key == pygame.K_b:
                self.open_wallet()
            elif event.key == pygame.K_c:
                self.state = "CREDITS"
            elif event.key == pygame.K_j:
                self._collect_nearby_items()
            elif event.key == pygame.K_k:
                if not self.mining_active:
                    self.start_mining()
                else:
                    self.stop_mining()
            elif event.key == pygame.K_l:  # L for mining log/stats
                if self.state == "GAME":
                    self.state = "MINING_LOG"
            elif event.key == pygame.K_e:
                if not self.auto_battle:
                    self.start_auto_battle()
                else:
                    self.stop_auto_battle()
                    self.show_message("Auto-battle ukoncen!", 60)
            elif event.key == pygame.K_p:
                self.state = "SKILLS"
            elif event.key == pygame.K_SPACE:
                self.fire_weapon()

    def handle_docked_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.undock()
            elif event.key == pygame.K_t:
                if self.docked_planet:
                    self.state = "TRADING"
                    # Reset scrollu pri vstupu do obchodovani
                    self.trading_scroll = 0
                    self.cargo_scroll = 0
                else:
                    self.show_message("Neni docovany v zadne stanici!")
            elif event.key == pygame.K_q:
                self.state = "QUEST"
            elif event.key == pygame.K_u:
                self.state = "UPGRADE"
            elif event.key == pygame.K_f:
                self.state = "BUY_FUEL"
            elif event.key == pygame.K_k:
                if not self.mining_active:
                    self.start_mining()
                else:
                    self.stop_mining()
            elif event.key == pygame.K_p:
                self.state = "SKILLS"

    def handle_trading_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "DOCKED"
            elif event.key == pygame.K_UP:
                # Scroll nahoru
                self.trading_scroll = max(0, self.trading_scroll - 1)
                self.cargo_scroll = max(0, self.cargo_scroll - 1)
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self.docked_planet.available_items) - 9) if self.docked_planet else 0
                max_cargo_scroll = max(0, len(self.player_ship.cargo) - 9)
                self.trading_scroll = min(max_scroll, self.trading_scroll + 1)
                self.cargo_scroll = min(max_cargo_scroll, self.cargo_scroll + 1)
            elif event.key == pygame.K_1:
                self._quick_buy_category("Minerály")
            elif event.key == pygame.K_2:
                self._quick_buy_category("Zbraně")
            elif event.key == pygame.K_3:
                self._quick_buy_category("Potraviny")
            elif event.key == pygame.K_4:
                self._quick_buy_category("Technologie")
            elif event.key == pygame.K_5:
                self._quick_buy_category("Léky")
            elif event.key == pygame.K_6:
                self._quick_buy_category("Luxus")
            elif event.key == pygame.K_s:
                self.sell_goods()
            elif event.key == pygame.K_7:
                self._quick_sell_first()
            elif event.key == pygame.K_8:
                self._quick_sell_first()
            elif event.key == pygame.K_9:
                self._quick_sell_first()

    def handle_map_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                self.state = "GAME"
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                self.map_zoom = min(2.0, self.map_zoom * 1.2)
            elif event.key == pygame.K_MINUS:
                self.map_zoom = max(0.1, self.map_zoom * 0.8)
            elif event.key == pygame.K_LEFT:
                self.map_camera_x -= 200 / self.map_zoom
            elif event.key == pygame.K_RIGHT:
                self.map_camera_x += 200 / self.map_zoom
            elif event.key == pygame.K_UP:
                self.map_camera_y -= 200 / self.map_zoom
            elif event.key == pygame.K_DOWN:
                self.map_camera_y += 200 / self.map_zoom
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self.map_camera_x -= event.rel[0] / self.map_zoom
            self.map_camera_y -= event.rel[1] / self.map_zoom

    def handle_trading_click(self, pos):
        if not self.docked_planet: return
        x, y = pos

        for btn in self.clickable_buttons:
            if btn['rect'].collidepoint(x, y):
                if 'action' in btn:
                    try:
                        btn['action']()
                    except Exception as e:
                        print(f"Chyba pri kliknuti: {e}")
                        self.show_message("Chyba v obchodovani! Zkuste znovu.")
                return

    def handle_upgrade_click(self, pos):
        x, y = pos
        upgrades = [
            ("hp", "Posileni trupu (+20 HP)", 500),
            ("shield", "Stity (+20)", 400),
            ("speed", "Rychlost (+0.5)", 300),
            ("cargo", "Naklad (+20)", 600),
            ("fuel", "Max palivo (+50)", 350),
            ("weapon", "Laser II", 1000),
            ("weapon2", "Plazma", 2000),
            ("engine", "Motor I", 800),
            ("radar", "Radar+", 1500)
        ]
        for i, (up_type, name, cost) in enumerate(upgrades):
            btn_rect = pygame.Rect(500, 220 + i * 40, 400, 36)
            if btn_rect.collidepoint(x, y):
                if up_type in ["hp", "shield", "speed", "cargo", "fuel"]:
                    self.upgrade_ship(up_type)
                elif up_type == "weapon":
                    self.upgrade_weapon("Laser II", 1000)
                elif up_type == "weapon2":
                    self.upgrade_weapon("Plazmová puška", 2000)
                elif up_type == "engine":
                    self.upgrade_engine()
                elif up_type == "radar":
                    self.upgrade_radar()
                break

    def handle_quest_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "DOCKED" if self.docked_planet else "GAME"
            elif event.key == pygame.K_1 and len(self.quests) > 0:
                self.accept_quest(0)
            elif event.key == pygame.K_2 and len(self.quests) > 1:
                self.accept_quest(1)
            elif event.key == pygame.K_3 and len(self.quests) > 2:
                self.accept_quest(2)
            elif event.key == pygame.K_4 and len(self.quests) > 3:
                self.accept_quest(3)

    def handle_upgrade_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "DOCKED" if self.docked_planet else "GAME"
            elif event.key == pygame.K_1:
                self.upgrade_ship("hp")
            elif event.key == pygame.K_2:
                self.upgrade_ship("shield")
            elif event.key == pygame.K_3:
                self.upgrade_ship("speed")
            elif event.key == pygame.K_4:
                self.upgrade_ship("cargo")
            elif event.key == pygame.K_5:
                self.upgrade_ship("fuel")

    def handle_fuel_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "DOCKED" if self.docked_planet else "GAME"
            elif event.key == pygame.K_1:
                self.buy_fuel(10)
            elif event.key == pygame.K_2:
                self.buy_fuel(25)
            elif event.key == pygame.K_3:
                self.buy_fuel(50)
            elif event.key == pygame.K_4:
                self.buy_fuel(100)

    def handle_credits_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_c:
                self.state = "MENU" if self.state == "CREDITS" else "GAME"
    
    def handle_mining_log_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "GAME"
            elif event.key == pygame.K_l:
                pass

    def handle_skills_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = "GAME"
            for sk_id in SKILL_DEFS:
                idx = list(SKILL_DEFS.keys()).index(sk_id)
                if event.key == getattr(pygame, f"K_{idx + 1}", None):
                    s = self.player_ship
                    if s.skill_points > 0 and s.skills[sk_id] < SKILL_DEFS[sk_id]["max"]:
                        s.skills[sk_id] += 1
                        s.skill_points -= 1
                        s.update_passive_bonuses()
                        self.show_message(f"{SKILL_DEFS[sk_id]['name']}: {s.skills[sk_id]}/{SKILL_DEFS[sk_id]['max']}", 90)
                    elif s.skill_points <= 0:
                        self.show_message("Nemate volne skill body!", 90)
                    else:
                        self.show_message(f"Skill {SKILL_DEFS[sk_id]['name']} je na maximu!", 90)
                    break
    
    def handle_multiplayer_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "MENU"
            elif event.key == pygame.K_1:
                self.host_game()
            elif event.key == pygame.K_2:
                self.join_game()

    def disconnect_multiplayer(self):
        if self.network:
            self.network.disconnect()
            self.network = None
        self.multiplayer = False
        self.remote_players.clear()

    def start_auto_battle(self):
        closest = None
        closest_dist = 350
        for enemy in self.enemies:
            dx = enemy.x - self.player_ship.x
            dy = enemy.y - self.player_ship.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy
        if closest:
            self.auto_battle = True
            self.auto_battle_target = closest
            self.show_message("AUTO-BATTLE: [ESC] ukoncit", 120)
            return True
        self.show_message("Zadny nepritele v dosahu!", 60)
        return False

    def stop_auto_battle(self):
        self.auto_battle = False
        self.auto_battle_target = None
        self.enemy_bullets.clear()
        self.zoom = 1.0

    def update_auto_battle(self):
        enemy = self.auto_battle_target
        if not enemy or enemy not in self.enemies:
            self.stop_auto_battle()
            return
        target_dir = math.atan2(enemy.y - self.player_ship.y, enemy.x - self.player_ship.x)
        self.player_ship.rotate_to(target_dir)
        enemy.direction = math.atan2(self.player_ship.y - enemy.y, self.player_ship.x - enemy.x)
        self.fire_weapon()
        enemy.shoot_timer -= 1
        if enemy.shoot_timer <= 0:
            enemy.shoot_timer = 50
            bx = enemy.x + math.cos(enemy.direction) * 15
            by = enemy.y + math.sin(enemy.direction) * 15
            bvx = math.cos(enemy.direction) * 5
            bvy = math.sin(enemy.direction) * 5
            self.enemy_bullets.append({'x': bx, 'y': by, 'vx': bvx, 'vy': bvy, 'life': 60, 'damage': enemy.damage})
        mid_x = (self.player_ship.x + enemy.x) / 2
        mid_y = (self.player_ship.y + enemy.y) / 2
        self.camera_x = mid_x
        self.camera_y = mid_y
        self.zoom = 0.5
        dx = enemy.x - self.player_ship.x
        dy = enemy.y - self.player_ship.y
        if math.sqrt(dx*dx + dy*dy) > 400:
            self.stop_auto_battle()
            self.show_message("Boji jste se prilis vzdalili!", 90)

    def player_respawn(self):
        self.player_ship.hp = self.player_ship.max_hp
        self.player_ship.shield = self.player_ship.max_shield
        nearest = None
        nearest_dist = float('inf')
        for planet in self.planets:
            if planet.station_type in ("PLANET", "DOCKY", "OBCHODNI_STANICE"):
                dist = math.sqrt((planet.x - self.player_ship.x)**2 + (planet.y - self.player_ship.y)**2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = planet
        if nearest:
            self.player_ship.x = nearest.x + 50
            self.player_ship.y = nearest.y + 50
            self.camera_x = self.player_ship.x
            self.camera_y = self.player_ship.y
        self.show_message("Lod znicena! Obnoveno na nejblizsi stanici.", 180)
        self.stop_auto_battle()

    def host_game(self):
        """Hostovat hru - spustit server + pripojit se"""
        import subprocess
        self.show_message("Spoustim server...")
        import threading as _th
        def run_server():
            try:
                from server import GameServer
                srv = GameServer()
                srv.start()
            except:
                pass
        t = _th.Thread(target=run_server, daemon=True)
        t.start()
        import time
        time.sleep(0.5)
        self.connect_to_server("127.0.0.1")

    def join_game(self):
        self.state = "MENU"
        print("Zadej IP serveru (napr. 192.168.1.100): ", end="")
        try:
            ip = input().strip()
            if ip:
                self.connect_to_server(ip)
            else:
                self.show_message("Neplatna IP adresa!", 90)
        except:
            self.show_message("Chyba pri zadavani IP!", 90)

    def connect_to_server(self, ip):
        self.network = NetworkClient()
        success, result = self.network.connect(ip, 5555)
        if success:
            self.multiplayer = True
            self.player_ship.x = result.get("x", self.player_ship.x)
            self.player_ship.y = result.get("y", self.player_ship.y)
            self.player_ship.name = self.network.name
            self.state = "GAME"
            self.show_message(f"Pripojen k serveru! ID: {self.network.player_id}, Lod: {self.network.name}", 180)
        else:
            self.network = None
            self.show_message(f"Chyba: {result}", 180)
            self.state = "MULTIPLAYER"

    def draw_multiplayer_menu(self):
        self.screen.fill(BLACK)
        title = self.font_large.render("MULTIPLAYER", True, BRIGHT_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        subtitle = self.font_medium.render("Hrajte s ostatnimi hraci po siti!", True, CYAN)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 200))
        options = [
            ("[1] Hostovat hru", "Spustit server a cekat na hrace - port 5555"),
            ("[2] Pripojit se", "Zadat IP serveru a pripojit se"),
            ("[ESC] Zpet", "Navrat do hlavniho menu")
        ]
        for i, (text, desc) in enumerate(options):
            y = 300 + i * 60
            rendered = self.font_medium.render(text, True, WHITE)
            self.screen.blit(rendered, (SCREEN_WIDTH // 2 - 150, y))
            desc_text = self.font_tiny.render(desc, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - 150, y + 25))

    def save_game(self):
        try:
            s = self.player_ship
            data = {
                "x": s.x, "y": s.y,
                "hp": s.hp, "max_hp": s.max_hp,
                "shield": s.shield, "max_shield": s.max_shield,
                "fuel": s.fuel, "max_fuel": s.max_fuel,
                "cargo": s.cargo, "max_cargo": s.max_cargo,
                "weapons": s.weapons,
                "level": s.level, "xp": s.xp, "xp_to_level": s.xp_to_level,
                "name": s.name,
                "thrust_power": s.thrust_power, "max_speed": s.max_speed,
                "rotation_speed": s.rotation_speed,
                "drag": s.drag, "shoot_delay": s.shoot_delay,
                "camera_x": self.camera_x, "camera_y": self.camera_y,
                "zoom": self.zoom,
                "credits": self.credits
            }
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Autosave chyba: {e}")

    def load_game(self):
        try:
            if not os.path.exists(SAVE_PATH):
                return False
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
            s = self.player_ship
            s.x = data.get("x", s.x)
            s.y = data.get("y", s.y)
            s.hp = data.get("hp", s.hp)
            s.max_hp = data.get("max_hp", s.max_hp)
            s.shield = data.get("shield", s.shield)
            s.max_shield = data.get("max_shield", s.max_shield)
            s.fuel = data.get("fuel", s.fuel)
            s.max_fuel = data.get("max_fuel", s.max_fuel)
            s.cargo = data.get("cargo", s.cargo)
            s.max_cargo = data.get("max_cargo", s.max_cargo)
            s.weapons = data.get("weapons", s.weapons)
            s.level = data.get("level", s.level)
            s.xp = data.get("xp", s.xp)
            s.xp_to_level = data.get("xp_to_level", s.xp_to_level)
            s.name = data.get("name", s.name)
            s.thrust_power = data.get("thrust_power", s.thrust_power)
            s.max_speed = data.get("max_speed", s.max_speed)
            s.rotation_speed = data.get("rotation_speed", s.rotation_speed)
            s.drag = data.get("drag", s.drag)
            s.shoot_delay = data.get("shoot_delay", s.shoot_delay)
            self.camera_x = data.get("camera_x", self.camera_x)
            self.camera_y = data.get("camera_y", self.camera_y)
            self.zoom = data.get("zoom", self.zoom)
            self.credits = data.get("credits", self.credits)
            s.update_passive_bonuses()
            return True
        except Exception as e:
            print(f"Load save chyba: {e}")
            return False

    def start_mining(self):
        """Start real mining using Havirov-Coin CPUMiner"""
        try:
            if not os.path.exists(WALLET_PATH):
                self.wallet.create_wallet("Space Ranger")

            if self.cpuminer is not None and self.cpuminer.running:
                self.show_message("Mining already running!", 90)
                return

            self._orig_dir = os.getcwd()
            os.chdir(self.miner_dir)

            wallet_addr = self.wallet.address
            if not wallet_addr:
                self.show_message("No wallet address!", 120)
                return

            self.cpuminer = CPUMiner(wallet_address=wallet_addr, threads=1, intensity=8)

            self.mining_active = True
            self.mining_stats["start_time"] = time.time()
            self.mining_stats["hash_count"] = 0
            self.mining_stats["share_count"] = 0
            self.mining_stats["total_earned"] = 0
            self.mining_stats["last_share_time"] = 0
            self.mining_stats["difficulty"] = 6000000
            self.mining_stats["max_hashrate"] = 0

            self.current_session_hashes = 0
            self.current_session_shares = 0

            def run_cpuminer():
                try:
                    self.cpuminer.mine()
                except Exception as e:
                    print(f"CPUMiner error: {e}")
                finally:
                    self.mining_active = False

            self.mining_thread_ref = threading.Thread(target=run_cpuminer, daemon=True)
            self.mining_thread_ref.start()

            self.mining_stats["start_time"] = time.time()
            self.show_message("Real mining started! Press K to stop.")

        except Exception as e:
            print(f"Error starting mining: {e}")
            self.show_message(f"Error starting mining: {e}")
            self.mining_active = False
            if hasattr(self, '_orig_dir'):
                os.chdir(self._orig_dir)
    
    def stop_mining(self):
        """Stop the real CPUMiner"""
        try:
            was_mining = self.mining_active

            if self.cpuminer is not None:
                self.cpuminer.running = False

            if self.mining_thread_ref is not None and self.mining_thread_ref.is_alive():
                self.mining_thread_ref.join(timeout=3)
                if self.mining_thread_ref.is_alive():
                    print("Warning: Mining thread did not stop cleanly")

            self.mining_active = False

            if hasattr(self, '_orig_dir'):
                os.chdir(self._orig_dir)

            elapsed = time.time() - self.mining_stats.get("start_time", time.time())

            if self.cpuminer is not None:
                self.mining_stats["hash_count"] = getattr(self.cpuminer, 'hash_count', 0)
                self.mining_stats["share_count"] = getattr(self.cpuminer, 'shared_count', 0) + getattr(self.cpuminer, 'accepted', 0)
                self.mining_stats["total_earned"] = getattr(self.cpuminer, 'total_claimed', 0)

            final_hashrate = 0
            final_efficiency = 0
            if elapsed > 0 and self.mining_stats["hash_count"] > 0:
                final_hashrate = self.mining_stats["hash_count"] / elapsed
                final_efficiency = (self.mining_stats["share_count"] / self.mining_stats["hash_count"]) * 100
                if final_hashrate > self.mining_stats["max_hashrate"]:
                    self.mining_stats["max_hashrate"] = final_hashrate

            self.wallet.load_wallet()
            self.credits = self.wallet.get_balance()

            session_data = {
                "timestamp": time.time(),
                "duration": elapsed,
                "hashes": self.mining_stats["hash_count"],
                "shares": self.mining_stats["share_count"],
                "earned": self.mining_stats["total_earned"],
                "efficiency": final_efficiency,
                "avg_hashrate": final_hashrate,
                "max_hashrate": self.mining_stats["max_hashrate"],
                "final_difficulty": self.mining_stats["difficulty"]
            }
            self.mining_history.append(session_data)

            if len(self.mining_history) > 10:
                self.mining_history.pop(0)

            total_mined = sum(s["earned"] for s in self.mining_history)
            total_hashes = sum(s["hashes"] for s in self.mining_history)
            total_shares = sum(s["shares"] for s in self.mining_history)

            summary_lines = [
                "=== MINING SESSION COMPLETED ===",
                f"Status: {'✓ Success' if was_mining else '⚠ Interrupted'}",
                f"Duration: {elapsed:.1f}s",
                f"Total Hashes: {self.mining_stats['hash_count']:,}",
                f"Shares Found: {self.mining_stats['share_count']}",
                f"Efficiency: {final_efficiency:.4f}%",
                f"Avg Hash Rate: {final_hashrate:,.0f} H/s",
                f"Peak Hash Rate: {self.mining_stats['max_hashrate']:,.0f} H/s",
                f"Session Earned: {self.mining_stats['total_earned']:.8f} HVC",
                f"Wallet Balance: {self.credits:.8f} HVC",
                "",
                "=== OVERALL MINING STATS ===",
                f"Total Sessions: {len(self.mining_history)}",
                f"Total Mined: {total_mined:.8f} HVC",
                f"Total Hashes: {total_hashes:,}",
                f"Total Shares: {total_shares}",
                f"Average Efficiency: {sum(s['efficiency'] for s in self.mining_history)/len(self.mining_history):.4f}%",
                "=============================="
            ]

            summary = "\n".join(summary_lines)
            self.show_message(summary, 600)

        except Exception as e:
            print(f"Error stopping mining: {e}")
            self.show_message(f"Error stopping mining: {e}")

        finally:
            self.mining_active = False
            self.cpuminer = None
            self.mining_thread_ref = None

    def update(self):
        if self.state == "GAME":
            self.update_game()
        elif self.state == "DOCKED" and self.docked_planet:
            # Regenerace zbozi na stanici
            self.docked_planet.update_prices()
            # Postupne doplnovani zbozi
            for item in self.docked_planet.goods:
                if self.docked_planet.goods[item] < 20:
                    self.docked_planet.goods[item] += 1
        elif self.state == "TRADING" and self.docked_planet:
            # Aktualizace cen pri obchodovani
            self.docked_planet.update_prices()
        elif self.state == "TRADING" and not self.docked_planet:
            self.state = "DOCKED"

        if self.mining_active and self.cpuminer is not None:
            cm = self.cpuminer
            self.mining_stats["hash_count"] = getattr(cm, 'hash_count', 0)
            self.mining_stats["share_count"] = getattr(cm, 'shared_count', 0) + getattr(cm, 'accepted', 0)
            self.mining_stats["total_earned"] = getattr(cm, 'total_claimed', 0)
            self.mining_stats["difficulty"] = getattr(cm, 'current_difficulty', self.mining_stats.get("difficulty", 6000000))

            current_hashrate = getattr(cm, '_get_hashrate', lambda: 0)()
            self.mining_stats["hashrate"] = current_hashrate

            if not hasattr(self, 'displayed_hashrate'):
                self.displayed_hashrate = current_hashrate
            else:
                alpha = 0.1
                self.displayed_hashrate = (alpha * current_hashrate +
                                         (1 - alpha) * self.displayed_hashrate)

            if current_hashrate > self.mining_stats["max_hashrate"]:
                self.mining_stats["max_hashrate"] = current_hashrate

            if cm.shared_count > 0:
                prev = getattr(self, '_last_shown_shares', 0)
                if cm.shared_count > prev:
                    self.mining_stats["last_share_time"] = time.time()
                    self._last_shown_shares = cm.shared_count
                    self.wallet.load_wallet()
                    self.credits = self.wallet.get_balance()
        
        self.effective_radar_range = RADAR_RANGE + self.player_ship.radar_bonus

        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""

    def update_game(self):
        keys = pygame.key.get_pressed()
        if self.auto_battle:
            self.update_auto_battle()
        else:
            dx, dy = 0, 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1
            if dx != 0 or dy != 0:
                target_dir = math.atan2(dy, dx)
                self.player_ship.rotate_to(target_dir)
                self.player_ship.apply_thrust(self.player_ship.direction)
                self.player_ship.fuel = max(0, self.player_ship.fuel - 0.008)
            self.camera_x = self.player_ship.x
            self.camera_y = self.player_ship.y
        self.player_ship.update()
        self.player_ship.last_shot -= 1
        for planet in self.planets:
            dist = math.sqrt((self.player_ship.x - planet.x)**2 + (self.player_ship.y - planet.y)**2)
            if dist < 80 and not self.player_ship.docked_at:
                self.dock_at_planet(planet)
                break
        if self.player_ship.docked_at:
            docked = None
            for p in self.planets:
                if p.name == self.player_ship.docked_at:
                    docked = p
                    break
            if docked:
                dist = math.sqrt((self.player_ship.x - docked.x)**2 + (self.player_ship.y - docked.y)**2)
                if dist > 100:
                    self.undock()
        for enemy in self.enemies[:]:
            if self.auto_battle and enemy is self.auto_battle_target:
                continue
            will_shoot = enemy.update(self.player_ship.x, self.player_ship.y)
            if will_shoot:
                bx = enemy.x + math.cos(enemy.direction) * 15
                by = enemy.y + math.sin(enemy.direction) * 15
                bvx = math.cos(enemy.direction) * 5
                bvy = math.sin(enemy.direction) * 5
                self.enemy_bullets.append({'x': bx, 'y': by, 'vx': bvx, 'vy': bvy, 'life': 60, 'damage': enemy.damage})
            if hasattr(enemy, 'should_remove') and enemy.should_remove:
                self.enemies.remove(enemy)
        
        # Generovani novych piratu - vzdy nahodna sance
        if random.random() < 0.015:
            if len(self.enemies) < 10 + self.player_ship.level * 2:
                if random.random() < 0.4:
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.randint(300, 600)
                    x = self.player_ship.x + dist * math.cos(angle)
                    y = self.player_ship.y + dist * math.sin(angle)
                else:
                    x = random.randint(200, 5800)
                    y = random.randint(200, 4500)
                ship_type = "Pirate"
                if self.player_ship.level >= 3 and random.random() < 0.2:
                    ship_type = "Elite"
                enemy = EnemyShip(x, y, ship_type)
                if ship_type == "Elite":
                    enemy.hp = 150
                    enemy.max_hp = 150
                    enemy.speed = 2.0
                self.enemies.append(enemy)
        
        self.update_bullets()
        for bullet in self.enemy_bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['life'] -= 1
            if bullet['life'] <= 0:
                self.enemy_bullets.remove(bullet)
                continue
            dx = bullet['x'] - self.player_ship.x
            dy = bullet['y'] - self.player_ship.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 14:
                damage = bullet['damage']
                if self.player_ship.shield > 0:
                    if self.player_ship.shield >= damage:
                        self.player_ship.shield -= damage
                        damage = 0
                    else:
                        damage -= self.player_ship.shield
                        self.player_ship.shield = 0
                self.player_ship.hp -= damage
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                if self.player_ship.hp <= 0:
                    self.player_respawn()
        now = time.time()
        self.floating_items = [it for it in self.floating_items if now - it["time"] < 300]

        if self.multiplayer:
            if self.network and self.network.connected:
                s = self.player_ship
                self.network.send_state(s.x, s.y, s.vx, s.vy, s.direction, s.hp, s.shield)
                remote = self.network.get_remote_players()
                for pid, rp in remote.items():
                    if pid not in self.remote_players:
                        self.remote_players[pid] = rp
                dead_pids = [pid for pid in self.remote_players if pid not in remote]
                for pid in dead_pids:
                    self.remote_players.pop(pid, None)
                for pid, rp in remote.items():
                    self.remote_players[pid] = rp
                for etype, data in self.network.get_events():
                    if etype == "damage":
                        self.player_ship.hp = data.get("hp", self.player_ship.hp)
                        self.player_ship.shield = data.get("shield", self.player_ship.shield)
                        self.show_message(f"Zasah od {data.get('attacker', 'neznama')}!", 60)
                    elif etype == "respawn":
                        self.player_ship.x = data["x"]
                        self.player_ship.y = data["y"]
                        self.player_ship.hp = self.player_ship.max_hp
                        self.player_ship.shield = self.player_ship.max_shield
                        self.show_message("Respawn!", 60)
            else:
                self.disconnect_multiplayer()
                self.show_message("Spojeni se serverem ztraceno!", 180)
                self.state = "MENU"
        else:
            self.remote_players.clear()

        self.autosave_timer += 1
        if self.autosave_timer >= 600:
            self.autosave_timer = 0
            self.save_game()

    def dock_at_planet(self, planet):
        self.player_ship.docked_at = planet.name
        self.docked_planet = planet
        self.state = "DOCKED"
        self.show_message(f"Automatické dokovani u: {planet.name} ({planet.get_type_name()})")
        self.check_quest_completion(planet)
        self.save_game()

    def undock(self):
        if not self.docked_planet: return
        planet_x = self.docked_planet.x
        planet_y = self.docked_planet.y
        self.player_ship.docked_at = None
        self.docked_planet = None
        self.state = "GAME"
        angle = random.uniform(0, 2 * math.pi)
        self.player_ship.x = planet_x + 100 * math.cos(angle)
        self.player_ship.y = planet_y + 100 * math.sin(angle)
        self.show_message("Odlet z stanice")
        self.save_game()

    def try_teleport_to_planet(self, planet):
        dx = planet.x - self.player_ship.x
        dy = planet.y - self.player_ship.y
        dist = math.sqrt(dx**2 + dy**2)
        cost = int(dist / 100)
        if self.wallet.subtract_credits(cost):
            self.player_ship.x = planet.x + 50
            self.player_ship.y = planet.y
            self.camera_x = self.player_ship.x
            self.camera_y = self.player_ship.y
            self.credits = self.wallet.get_balance()
            self.show_message(f"Teleport na {planet.name} za {cost} HVC")
        else:
            self.show_message(f"Nedostatek kreditu! Potreba: {cost} HVC")

    def buy_fuel(self, amount):
        cost = amount * 2
        if self.wallet.subtract_credits(cost):
            self.player_ship.fuel = min(self.player_ship.max_fuel, self.player_ship.fuel + amount)
            self.credits = self.wallet.get_balance()
            self.show_message(f"Nakoupeno {amount} paliva za {cost} HVC")
            self.save_game()
        else:
            self.show_message("Nedostatek kreditu!")

    def buy_specific_item(self, item):
        if not self.docked_planet: 
            self.show_message("Neni vybrana zadna stanice!")
            return

        try:
            self.docked_planet.update_prices()
            price = self.docked_planet.prices.get(item, 0.1)
            stock = self.docked_planet.goods.get(item, 0)

            se = self.player_ship.get_skill_effects()
            price = max(0.0001, round(price * (1 - se["barter_buy"]), 4))

            if price <= 0.0001 or stock <= 0:
                self.show_message(f"{item} neni skladem!")
                return

            if item not in self.docked_planet.available_items:
                self.show_message(f"{item} neni v nabidce!")
                return

            if self.wallet.subtract_credits(price):
                if self.player_ship.add_cargo(item, 1):
                    self.docked_planet.goods[item] = stock - 1
                    self.credits = self.wallet.get_balance()
                    self.docked_planet.record_trade(item, 1)
                    self.show_message(f"Koupeno {item} za {price} HVC")

                    self.save_game()
                    if random.random() < 0.3:
                        self.docked_planet._generate_new_goods()
                else:
                    self.wallet.add_credits(price)
                    self.show_message("Nedostatek mista v nakladu!")
            else:
                self.show_message(f"Nedostatek kreditu! Potreba: {price} HVC")
        except Exception as e:
            print(f"Chyba pri nakupu {item}: {e}")
            self.show_message("Chyba pri nakupe!")

    def _quick_buy_category(self, category):
        if not self.docked_planet:
            self.show_message("Neni vybrana zadna stanice!")
            return
        available = [item for item in self.docked_planet.available_items
                     if ITEM_CATEGORY_MAP.get(item) == category
                     and self.docked_planet.goods.get(item, 0) > 0]
        if available:
            self.buy_specific_item(available[0])
        else:
            self.show_message(f"Zadne {category} neni skladem!", 90)

    def _quick_sell_first(self):
        if not self.player_ship.cargo:
            self.show_message("Nemate zadny naklad k prodeji!", 90)
            return
        item = list(self.player_ship.cargo.keys())[0]
        self.sell_goods(item)

    def sell_goods(self, item=None):
        if not self.docked_planet:
            self.show_message("Neni vybrana zadna stanice!")
            return
        if not self.player_ship.cargo:
            self.show_message("Nemate zadny naklad k prodeji!")
            return
        
        if item is None:
            if self.player_ship.cargo:
                item = list(self.player_ship.cargo.keys())[0]
            else:
                self.show_message("Nemate zadny naklad!")
                return
        
        if item in self.player_ship.cargo:
            try:
                self.docked_planet.update_prices()
                price = self.docked_planet.prices.get(item, 0.1)

                se = self.player_ship.get_skill_effects()
                price = max(0.0001, round(price * (1 + se["barter_sell"]), 4))

                if price <= 0.0001:
                    self.show_message(f"{item} nema cenu!")
                    return

                if self.player_ship.remove_cargo(item, 1):
                    self.wallet.add_credits(price)
                    self.credits = self.wallet.get_balance()
                    self.docked_planet.goods[item] = self.docked_planet.goods.get(item, 0) + 1
                    self.docked_planet.record_trade(item, -1)
                    self.show_message(f"Prodano {item} za {price} HVC")

                    self.save_game()
                    if random.random() < 0.2:
                        self.docked_planet._generate_new_goods()
                else:
                    self.show_message("Chyba pri odstranovani nakladu!")
            except Exception as e:
                print(f"Chyba pri prodeji {item}: {e}")
                self.show_message("Chyba pri prodeji!")
        else:
            self.show_message(f"{item} neni ve vasem nakladu!")

    def accept_quest(self, index):
        if 0 <= index < len(self.quests):
            self.current_quest = self.quests.pop(index)
            self.show_message(f"Prijat ukol: {self.current_quest['name']}")
            
            # Zobrazeni detailu ukolu podle typu
            if self.current_quest['type'] == 'deliver':
                from_planet = self.current_quest.get('from', 'neurceno')
                to_planet = self.current_quest['to']
                item = self.current_quest['item']
                amount = self.current_quest['amount']
                self.show_message(f"Doruc {amount}x {item} z {from_planet} na {to_planet}", 180)
            elif self.current_quest['type'] == 'collect':
                item = self.current_quest['item']
                amount = self.current_quest['amount']
                self.show_message(f"Seber {amount}x {item} v galaxii", 180)
            elif self.current_quest['type'] == 'kill':
                amount = self.current_quest['amount']
                self.show_message(f"Znic {amount} piratskych lodi", 180)
                self.quest_progress['kill'] = 0

    def check_quest_completion(self, planet):
        if not self.current_quest: return
        quest = self.current_quest
        completed = False
        
        if quest['type'] == 'deliver':
            # Kontrola, zda je hrac na spravne cilove planete
            if planet.name == quest['to']:
                # Zkontroluje, zda ma dostatek zbozi v nakladu
                if self.player_ship.cargo.get(quest['item'], 0) >= quest['amount']:
                    # Odecte zbozi z nakladu
                    for _ in range(quest['amount']):
                        self.player_ship.remove_cargo(quest['item'], 1)
                    completed = True
                    self.show_message(f"Doruceni {quest['item']} na {quest['to']} uspesne!")
            else:
                # Pokud neni na cilove planete, zobrazi zpravu
                self.show_message(f"Musite letet na {quest['to']} pro dokonceni ukolu!", 120)
        
        elif quest['type'] == 'collect':
            # Kontrola, zda ma hrac dostatek zbozi
            if self.player_ship.cargo.get(quest['item'], 0) >= quest['amount']:
                completed = True
                self.show_message(f"Sber {quest['item']} dokoncen!")
        
        elif quest['type'] == 'kill':
            # Ulozeni pokroku se kontroluje jinde (pri zabiti lodi)
            if self.quest_progress['kill'] >= quest['amount']:
                completed = True
                self.show_message(f"Vsechny piratske lodi zniceny!")
        
        if completed:
            self.wallet.add_credits(quest['reward'])
            self.credits = self.wallet.get_balance()
            self.show_message(f"Ukol splnen! Ziskani: {quest['reward']} HVC")
            self.current_quest = None
            self.quest_progress = {"kill": 0, "collect": 0}

    def upgrade_ship(self, upgrade_type):
        costs = {"hp": 5.0, "shield": 4.0, "speed": 3.0, "cargo": 6.0, "fuel": 3.5}
        cost = costs.get(upgrade_type, 10.0)
        if self.wallet.subtract_credits(cost):
            if upgrade_type == "hp":
                self.player_ship.max_hp += 20
                self.player_ship.hp = self.player_ship.max_hp
            elif upgrade_type == "shield":
                self.player_ship.max_shield += 20
                self.player_ship.shield = self.player_ship.max_shield
            elif upgrade_type == "speed":
                self.player_ship.max_speed += 0.5
            elif upgrade_type == "cargo":
                self.player_ship.max_cargo += 20
            elif upgrade_type == "fuel":
                self.player_ship.max_fuel += 50
                self.player_ship.fuel = self.player_ship.max_fuel
            self.credits = self.wallet.get_balance()
            self.show_message(f"Vylepseni zakoupeno za {cost} HVC")
            self.save_game()
        else:
            self.show_message("Nedostatek kreditu!")

    def upgrade_weapon(self, weapon_name, cost):
        if self.wallet.subtract_credits(cost):
            if weapon_name not in self.player_ship.weapons:
                self.player_ship.weapons.append(weapon_name)
                self.player_ship.shoot_delay = max(5, self.player_ship.shoot_delay - 2)
                self.credits = self.wallet.get_balance()
                self.show_message(f"Zbran {weapon_name} zakoupena!")
                self.save_game()
        else:
            self.show_message("Nedostatek kreditu!")

    def upgrade_engine(self):
        cost = 800
        if self.wallet.subtract_credits(cost):
            self.player_ship.thrust_power += 0.02
            self.player_ship.max_speed += 0.5
            self.credits = self.wallet.get_balance()
            self.show_message("Motor vylepsen!")
            self.save_game()

    def upgrade_radar(self):
        global RADAR_RANGE
        cost = 1500
        if self.wallet.subtract_credits(cost):
            RADAR_RANGE = min(3000, RADAR_RANGE + 500)
            self.credits = self.wallet.get_balance()
            self.show_message(f"Radar vylepsen! Rozsah: {RADAR_RANGE}u")
            self.save_game()

    def open_wallet(self):
        self.wallet.load_wallet()
        self.credits = self.wallet.get_balance()
        self.show_message(f"Havirov Coin Wallet: {self.credits:.4f} HVC")

    def fire_weapon(self):
        if self.player_ship.last_shot > 0: return
        self.player_ship.last_shot = self.player_ship.shoot_delay
        bx = self.player_ship.x + math.cos(self.player_ship.direction) * 20
        by = self.player_ship.y + math.sin(self.player_ship.direction) * 20
        bvx = math.cos(self.player_ship.direction) * 8
        bvy = math.sin(self.player_ship.direction) * 8
        bullet = {
            'x': bx, 'y': by,
            'vx': bvx, 'vy': bvy,
            'life': 60
        }
        self.bullets.append(bullet)
        if self.multiplayer and self.network and self.network.connected:
            self.network.send_shoot(bx, by, bvx, bvy)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['life'] -= 1
            if bullet['life'] <= 0:
                self.bullets.remove(bullet)
                continue
            hit_remote = False
            if self.multiplayer:
                for pid, rp in list(self.remote_players.items()):
                    dist = math.sqrt((bullet['x'] - rp.x)**2 + (bullet['y'] - rp.y)**2)
                    if dist < 14:
                        hit_remote = True
                        break
            if hit_remote:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            for enemy in self.enemies[:]:
                dist = math.sqrt((bullet['x'] - enemy.x)**2 + (bullet['y'] - enemy.y)**2)
                if dist < enemy.size:
                    se = self.player_ship.get_skill_effects()
                    damage = int(25 * (1 + se["damage_pct"]))
                    enemy.hp -= damage
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        if self.auto_battle and enemy is self.auto_battle_target:
                            self.stop_auto_battle()
                            self.show_message("Vitezstvi! Nepritel znicen!", 120)
                        self.player_ship.xp += 50
                        self._spawn_floating_item(enemy.x, enemy.y)
                        while self.player_ship.xp >= self.player_ship.xp_to_level:
                            self.player_ship.xp -= self.player_ship.xp_to_level
                            self.player_ship.level += 1
                            self.player_ship.skill_points += 1
                            self.player_ship.xp_to_level = 100 + (self.player_ship.level - 1) * 25
                            self.show_message(f"Level up! Nyni level {self.player_ship.level} (+1 skill bod)", 120)
                        if self.current_quest and self.current_quest['type'] == 'kill':
                            self.quest_progress['kill'] += 1
                            # Zobrazi aktualni progress
                            remaining = self.current_quest['amount'] - self.quest_progress['kill']
                            if remaining > 0:
                                self.show_message(f"Zbyva {remaining} piratskych lodi", 60)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def _spawn_floating_item(self, x, y):
        cat = random.choice(list(ITEM_CATEGORIES.keys()))
        item = random.choice(ITEM_CATEGORIES[cat])
        self.floating_items.append({
            "name": item, "category": cat, "x": x, "y": y,
            "time": time.time()
        })

    def _collect_nearby_items(self):
        collected = 0
        for item in self.floating_items[:]:
            dx = self.player_ship.x - item["x"]
            dy = self.player_ship.y - item["y"]
            if math.sqrt(dx*dx + dy*dy) < 60:
                if self.player_ship.add_cargo(item["name"], 1):
                    self.floating_items.remove(item)
                    collected += 1
                else:
                    self.show_message("Naklad je plny!", 60)
                    break
        if collected > 0:
            self.show_message(f"Sebrano {collected}x predmetu", 90)
            self.save_game()

    def draw(self):
        self.screen.fill(SPACE_BG)
        if self.state == "MENU": self.draw_menu()
        elif self.state == "GAME": self.draw_game()
        elif self.state == "DOCKED": self.draw_docked()
        elif self.state == "TRADING": self.draw_trading()
        elif self.state == "MAP": self.draw_map()
        elif self.state == "QUEST": self.draw_quest()
        elif self.state == "UPGRADE": self.draw_upgrade()
        elif self.state == "BUY_FUEL": self.draw_buy_fuel()
        elif self.state == "CREDITS": self.draw_credits()
        elif self.state == "MINING_LOG": self.draw_mining_log()
        elif self.state == "SKILLS": self.draw_skills()
        elif self.state == "MULTIPLAYER": self.draw_multiplayer_menu()
        if self.message:
            self.draw_message()
        pygame.display.flip()

    def draw_message(self):
        text = self.font_medium.render(self.message, True, BRIGHT_YELLOW)
        bg_w = text.get_width() + 30
        bg_h = text.get_height() + 10
        bg_x = SCREEN_WIDTH // 2 - bg_w // 2
        bg_y = 45
        bg_surface = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(bg_surface, (bg_x, bg_y))
        pygame.draw.rect(self.screen, BORDER_COLOR, (bg_x, bg_y, bg_w, bg_h), 2)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))

    def draw_radar(self):
        radar_x, radar_y = RADAR_POS
        radar_surface = pygame.Surface((RADAR_SIZE, RADAR_SIZE), pygame.SRCALPHA)
        radar_surface.fill((5,5,20,200))
        self.screen.blit(radar_surface, (radar_x, radar_y))
        pygame.draw.rect(self.screen, BORDER_COLOR, (radar_x, radar_y, RADAR_SIZE, RADAR_SIZE), 2)
        title = self.font_tiny.render("RADAR 1500u", True, CYAN)
        self.screen.blit(title, (radar_x + 5, radar_y + 5))
        radar_scale = (RADAR_SIZE // 2) / self.effective_radar_range
        for r in [250, 500, 750, 1000, 1500]:
            scaled_r = int(r * radar_scale)
            pygame.draw.circle(self.screen, (30,30,50), (radar_x + RADAR_SIZE // 2, radar_y + RADAR_SIZE // 2), scaled_r, 1)
        for planet in self.planets:
            planet.draw_on_radar(self.screen, radar_x, radar_y, radar_scale, self.player_ship.x, self.player_ship.y)
        for enemy in self.enemies:
            enemy.draw_on_radar(self.screen, radar_x, radar_y, radar_scale, self.player_ship.x, self.player_ship.y)
        for rp in self.remote_players.values():
            rel_x = rp.x - self.player_ship.x
            rel_y = rp.y - self.player_ship.y
            dist = math.sqrt(rel_x**2 + rel_y**2)
            if dist <= RADAR_RANGE:
                rx = radar_x + RADAR_SIZE // 2 + int(rel_x * radar_scale)
                ry = radar_y + RADAR_SIZE // 2 + int(rel_y * radar_scale)
                pygame.draw.circle(self.screen, CYAN, (rx, ry), 3)
        for item in self.floating_items:
            rel_x = item["x"] - self.player_ship.x
            rel_y = item["y"] - self.player_ship.y
            dist = math.sqrt(rel_x**2 + rel_y**2)
            if dist <= self.effective_radar_range:
                rx = radar_x + RADAR_SIZE // 2 + int(rel_x * radar_scale)
                ry = radar_y + RADAR_SIZE // 2 + int(rel_y * radar_scale)
                pygame.draw.circle(self.screen, (255, 255, 100), (rx, ry), 2)
        self.player_ship.draw_on_radar(self.screen, radar_x, radar_y, radar_scale)

    def draw_mining_hud_and_legend(self):
        radar_x, radar_y = RADAR_POS
        panel_x = radar_x
        panel_y = radar_y + RADAR_SIZE + 8
        panel_w = RADAR_SIZE
        panel_h = 214

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((5, 5, 20, 200))
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(self.screen, BORDER_COLOR, (panel_x, panel_y, panel_w, panel_h), 1)

        y_offset = panel_y + 4
        if self.mining_active:
            elapsed = time.time() - self.mining_stats.get("start_time", time.time())
            elapsed_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
            hash_rate = self.displayed_hashrate if hasattr(self, 'displayed_hashrate') else 0

            mining_lines = [
                ("MINING", BRIGHT_GREEN),
                (f"Hash: {hash_rate:,.0f} H/s", GREEN),
                (f"Shares: {self.mining_stats['share_count']}", YELLOW),
                (f"Earned: {self.mining_stats['total_earned']:.4f} HVC", CYAN),
                (f"Time: {elapsed_str}", LIGHT_GRAY),
                ("", WHITE),
            ]
        else:
            mining_lines = [
                ("MINING [K]", GRAY),
                ("stopped", GRAY),
                ("", WHITE),
            ]

        for label, color in mining_lines:
            rendered = self.font_tiny.render(label, True, color)
            self.screen.blit(rendered, (panel_x + 6, y_offset))
            y_offset += 14

        y_offset += 2
        legend_items = [
            ("[M] Mapa", BRIGHT_YELLOW),
            ("[F] Palivo", FUEL_COLOR),
            ("[K] Mining", BRIGHT_GREEN),
            ("[L] Mining Log", CYAN),
            ("[Q] Ukoly", CYAN),
            ("[U] Upgrade", BRIGHT_BLUE),
            ("[J] Seber item", GREEN),
            ("[E] Auto-battle", ORANGE),
            ("[SPACE] Strelba", BRIGHT_RED),
        ]
        for text, color in legend_items:
            rendered = self.font_tiny.render(text, True, color)
            self.screen.blit(rendered, (panel_x + 6, y_offset))
            y_offset += 14

    def draw_auto_battle(self):
        if not self.auto_battle or not self.auto_battle_target:
            return
        enemy = self.auto_battle_target
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        bar_w = 400
        bar_h = 30
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        enemy_bar_y = SCREEN_HEIGHT - 80
        enemy_name = self.font_medium.render(f"ENEMY: {enemy.type}", True, BRIGHT_RED)
        self.screen.blit(enemy_name, (bar_x, enemy_bar_y - 25))
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, enemy_bar_y, bar_w, bar_h))
        hp_pct = max(0, enemy.hp / enemy.max_hp)
        hp_color = GREEN if hp_pct > 0.5 else YELLOW if hp_pct > 0.25 else RED
        pygame.draw.rect(self.screen, hp_color, (bar_x, enemy_bar_y, int(bar_w * hp_pct), bar_h))
        pygame.draw.rect(self.screen, WHITE, (bar_x, enemy_bar_y, bar_w, bar_h), 2)
        hp_text = self.font_small.render(f"{max(0, int(enemy.hp))}/{int(enemy.max_hp)}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2, enemy_bar_y + 5))
        player_bar_y = enemy_bar_y - 60
        player_name = self.font_medium.render(f"PLAYER: {self.player_ship.name}", True, BRIGHT_GREEN)
        self.screen.blit(player_name, (bar_x, player_bar_y - 25))
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, player_bar_y, bar_w, bar_h))
        hp_pct = max(0, self.player_ship.hp / self.player_ship.max_hp)
        hp_color = GREEN if hp_pct > 0.5 else YELLOW if hp_pct > 0.25 else RED
        pygame.draw.rect(self.screen, hp_color, (bar_x, player_bar_y, int(bar_w * hp_pct), bar_h))
        pygame.draw.rect(self.screen, WHITE, (bar_x, player_bar_y, bar_w, bar_h), 2)
        hp_text = self.font_small.render(f"{max(0, int(self.player_ship.hp))}/{int(self.player_ship.max_hp)}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2, player_bar_y + 5))
        shield_bar_y = player_bar_y - 25
        shield_pct = max(0, self.player_ship.shield / self.player_ship.max_shield)
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, shield_bar_y, bar_w, 12))
        pygame.draw.rect(self.screen, BRIGHT_BLUE, (bar_x, shield_bar_y, int(bar_w * shield_pct), 12))
        pygame.draw.rect(self.screen, WHITE, (bar_x, shield_bar_y, bar_w, 12), 1)
        status_text = self.font_medium.render("AUTO-BATTLE", True, BRIGHT_RED)
        self.screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, 20))
        status_hint = self.font_tiny.render("[ESC] Exit | [E] Stop", True, GRAY)
        self.screen.blit(status_hint, (SCREEN_WIDTH // 2 - status_hint.get_width() // 2, 45))

    def draw_menu(self):
        # Animovane pozadi
        for sx, sy, size in self.star_field[:150]:
            screen_x = int(sx * 0.3) % SCREEN_WIDTH
            screen_y = int(sy * 0.3) % SCREEN_HEIGHT
            
            # Rotujici hvezdy
            angle = pygame.time.get_ticks() * 0.0001 + sx * 0.01
            offset_x = math.cos(angle) * 2
            offset_y = math.sin(angle) * 2
            final_x = int(screen_x + offset_x)
            final_y = int(screen_y + offset_y)
            
            color = (100, 100, 160) if size > 2 else (60, 60, 100)
            pygame.draw.circle(self.screen, color, (final_x, final_y), size//2)
        
        # Titulni animace
        title_pulse = math.sin(pygame.time.get_ticks() * 0.003) * 0.1 + 1.0
        title = self.font_title.render("SPACE RANGERS", True, BRIGHT_BLUE)
        scaled_title = pygame.transform.scale(title, (int(title.get_width() * title_pulse), int(title.get_height() * title_pulse)))
        self.screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 140))
        
        subtitle = self.font_large.render("Havirov Coin Edition", True, BRIGHT_YELLOW)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 220))
        
        # Wallet informace
        wallet_balance = self.wallet.get_balance()
        wallet_color = GREEN if wallet_balance > 0 else RED
        wallet_text = self.font_medium.render(f"Wallet: {wallet_balance:.4f} HVC", True, wallet_color)
        self.screen.blit(wallet_text, (SCREEN_WIDTH // 2 - wallet_text.get_width() // 2, 290))
        
        # Dekorativni elementy
        pygame.draw.line(self.screen, BORDER_COLOR, (SCREEN_WIDTH // 2 - 250, 340), (SCREEN_WIDTH // 2 + 250, 340), 3)
        
        # Menu tlacitka s hover efektem
        menu_options = [
            ("[1] Nová hra", BRIGHT_GREEN, "Zacnete jako novy ranger v galaxii"),
            ("[2] Nacist hru (Wallet)", BRIGHT_BLUE, "Nactete ulozenou hru z walletu"),
            ("[3] Kredity", YELLOW, "Informace o hre a tvurcich"),
            ("[4] Start Mining", PURPLE, "Zacnete mined Havirov Coins"),
            ("[5] Multiplayer", CYAN, "Hrajte s ostatnimi hraci po siti"),
            ("[ESC] Konec", BRIGHT_RED, "Ukonceni hry")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        for i, (text, color, description) in enumerate(menu_options):
            y_pos = 370 + i * 60
            
            # Tlacidko
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, y_pos - 5, 400, 45)
            is_hover = btn_rect.collidepoint(mouse_pos)
            
            # Pozadi tlacidka
            btn_color = (40, 40, 60) if is_hover else (20, 20, 40)
            pygame.draw.rect(self.screen, btn_color, btn_rect)
            pygame.draw.rect(self.screen, color, btn_rect, 2)
            
            # Text tlacidka
            rendered = self.font_medium.render(text, True, color)
            self.screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, y_pos))
            
            # Popisek
            desc_text = self.font_tiny.render(description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, y_pos + 25))
        
        # Verze a copyright
        version_text = self.font_tiny.render("Version 2.0 - Enhanced Edition", True, GRAY)
        self.screen.blit(version_text, (SCREEN_WIDTH // 2 - version_text.get_width() // 2, SCREEN_HEIGHT - 30))

    def draw_game(self):
        # Pozadi s animovanymi hvezdami
        for sx, sy, size in self.star_field:
            screen_x = int((sx - self.camera_x) * 0.3 + SCREEN_WIDTH // 2) % SCREEN_WIDTH
            screen_y = int((sy - self.camera_y) * 0.3 + SCREEN_HEIGHT // 2) % SCREEN_HEIGHT
            
            # Animace hvezd
            twinkle = math.sin(pygame.time.get_ticks() * 0.001 + sx * 0.01) * 0.5 + 0.5
            color_intensity = int((140 if size > 2 else 70) * twinkle)
            color = (color_intensity, color_intensity, int(color_intensity * 1.3))
            
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), max(1, int(size * 0.5)))
        
        # Planety s efektem svetla
        for planet in self.planets:
            screen_x = int((planet.x - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((planet.y - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                # Efekt svetla okolo planety
                if self.zoom > 0.5:
                    glow_size = int(planet.radius * self.zoom * 2)
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    for i in range(glow_size):
                        alpha = int(50 * (1 - i / glow_size))
                        color = (*planet.color, alpha)
                        pygame.draw.circle(glow_surface, color, (glow_size, glow_size), glow_size - i)
                    self.screen.blit(glow_surface, (screen_x - glow_size, screen_y - glow_size))
                
                planet.draw_on_map(self.screen, self.camera_x, self.camera_y, self.zoom, self.font_tiny)
        
        # Nepritele s efektem nebezpeci
        for enemy in self.enemies:
            screen_x = int((enemy.x - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((enemy.y - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                # Varovny efekt
                dist_to_player = math.sqrt((enemy.x - self.player_ship.x)**2 + (enemy.y - self.player_ship.y)**2)
                if dist_to_player < 300:
                    warning_alpha = int(100 * (1 - dist_to_player / 300))
                    warning_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(warning_surface, (255, 0, 0, warning_alpha), (20, 20), 20)
                    self.screen.blit(warning_surface, (screen_x - 20, screen_y - 20))
                
                enemy.draw_in_space(self.screen, screen_x, screen_y, self.zoom)

        # Ostatni hraci (multiplayer)
        for pid, rp in list(self.remote_players.items()):
            dist_to_player = math.sqrt((rp.x - self.player_ship.x)**2 + (rp.y - self.player_ship.y)**2)
            if dist_to_player > 3000:
                continue
            screen_x = int((rp.x - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((rp.y - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                size = max(4, int(14 * self.zoom))
                hue = (pid * 60) % 360
                rp_color = (
                    int(128 + 127 * math.sin(hue * 0.01745)),
                    int(128 + 127 * math.sin((hue + 120) * 0.01745)),
                    int(128 + 127 * math.sin((hue + 240) * 0.01745))
                )
                points = [
                    (screen_x + size * math.cos(rp.direction),
                     screen_y + size * math.sin(rp.direction)),
                    (screen_x + size * 0.6 * math.cos(rp.direction + 2.3),
                     screen_y + size * 0.6 * math.sin(rp.direction + 2.3)),
                    (screen_x - size * 0.5 * math.cos(rp.direction),
                     screen_y - size * 0.5 * math.sin(rp.direction)),
                    (screen_x + size * 0.6 * math.cos(rp.direction - 2.3),
                     screen_y + size * 0.6 * math.sin(rp.direction - 2.3))
                ]
                pygame.draw.polygon(self.screen, rp_color, points)
                pygame.draw.polygon(self.screen, WHITE, points, 1)
                name_tag = self.font_tiny.render(rp.name, True, CYAN)
                self.screen.blit(name_tag, (screen_x - name_tag.get_width() // 2, screen_y - size - 14))
                hp_pct = rp.hp / max(1, rp.max_hp)
                hp_color = GREEN if hp_pct > 0.5 else YELLOW if hp_pct > 0.25 else RED
                bar_w = max(10, int(30 * self.zoom))
                pygame.draw.rect(self.screen, DARK_GRAY, (screen_x - bar_w//2, screen_y - size - 5, bar_w, 4))
                pygame.draw.rect(self.screen, hp_color, (screen_x - bar_w//2, screen_y - size - 5, int(bar_w * hp_pct), 4))
        
        # Floating items (loot from pirates)
        for item in self.floating_items:
            screen_x = int((item["x"] - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((item["y"] - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                pulse = math.sin(pygame.time.get_ticks() * 0.004 + item["x"]) * 0.3 + 0.7
                color = (int(200 * pulse), int(200 * pulse), 50)
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), max(3, int(5 * self.zoom)))
                pygame.draw.circle(self.screen, (255, 255, 100), (screen_x, screen_y), max(1, int(3 * self.zoom)), 1)
                if self.zoom > 0.3:
                    label = self.font_tiny.render(item["name"], True, (255, 255, 100))
                    self.screen.blit(label, (screen_x - label.get_width() // 2, screen_y + 8))
        
        # Strelby s efektem
        for bullet in self.bullets:
            screen_x = int((bullet['x'] - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((bullet['y'] - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                # Efekt strelby
                bullet_trail = int(5 * self.zoom)
                pygame.draw.circle(self.screen, (255, 255, 100), (screen_x, screen_y), max(2, int(3 * self.zoom)))
                pygame.draw.circle(self.screen, (255, 255, 200), (screen_x, screen_y), max(1, int(2 * self.zoom)))
        
        # Enemy strelby
        for bullet in self.enemy_bullets:
            screen_x = int((bullet['x'] - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((bullet['y'] - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                pygame.draw.circle(self.screen, BRIGHT_RED, (screen_x, screen_y), max(2, int(3 * self.zoom)))
                pygame.draw.circle(self.screen, (255, 100, 100), (screen_x, screen_y), max(1, int(2 * self.zoom)))
        
        # Hracova lod
        self.player_ship.draw_in_space(self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.zoom)
        
        # Shield efekt
        if self.player_ship.shield > 0:
            shield_alpha = int(50 * (self.player_ship.shield / self.player_ship.max_shield))
            shield_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha), (30, 30), 25)
            self.screen.blit(shield_surface, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30))
        
        # UI panely
        if not self.auto_battle:
            self.draw_top_panel()
            self.draw_game_controls()
            self.draw_radar()
            self.draw_mining_hud_and_legend()
        
        # Strelba cooldown
        if self.player_ship.last_shot > 0:
            cd_text = self.font_tiny.render(f"Cooldown: {self.player_ship.last_shot}", True, YELLOW)
            self.screen.blit(cd_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30))
        
        # Blizke planety
        for planet in self.planets:
            dist = math.sqrt((self.player_ship.x - planet.x)**2 + (self.player_ship.y - planet.y)**2)
            if dist < 100:
                # Animovany text
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
                text_color = (int(CYAN[0] * pulse), int(CYAN[1] * pulse), int(CYAN[2] * pulse))
                text = self.font_small.render(f"Blizite se k {planet.name} ({planet.get_type_name()}) - dojde k dokovani", True, text_color)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 40))
        
        # Auto-pilot indikator
        if self.player_ship.auto_pilot:
            auto_text = self.font_tiny.render("AUTO-PILOT ACTIVE", True, BRIGHT_GREEN)
            self.screen.blit(auto_text, (SCREEN_WIDTH // 2 - auto_text.get_width() // 2, 100))

        if self.auto_battle:
            self.draw_auto_battle()

    def draw_docked(self):
        if not self.docked_planet: return
        self.screen.fill(DARK_BG)
        center_x = SCREEN_WIDTH // 2
        center_y = 200
        pygame.draw.circle(self.screen, self.docked_planet.color, (center_x, center_y), 60)
        pygame.draw.circle(self.screen, (100,150,220), (center_x, center_y), 62, 2)
        name_text = self.font_large.render(self.docked_planet.name, True, BRIGHT_GREEN)
        self.screen.blit(name_text, (center_x - name_text.get_width() // 2, center_y - 80))
        type_text = self.font_medium.render(self.docked_planet.get_type_name(), True, YELLOW)
        self.screen.blit(type_text, (center_x - type_text.get_width() // 2, center_y - 50))
        info = [f"Zbozi: {sum(self.docked_planet.goods.values())} jednotek"]
        for i, line in enumerate(info):
            text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (center_x - 100, center_y + 80 + i * 25))
        docked_text = self.font_large.render(f"DOKOVANO U: {self.docked_planet.name}", True, BRIGHT_GREEN)
        self.screen.blit(docked_text, (SCREEN_WIDTH // 2 - docked_text.get_width() // 2, 50))
        options = ["[T] Obchodovani", "[Q] Ukoly", "[U] Vylepseni lode", "[F] Nakup paliva", "[K] Mining", "[ESC] Odlet"]
        for i, text in enumerate(options):
            rendered = self.font_medium.render(text, True, BRIGHT_YELLOW)
            self.screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, 400 + i * 40))
        credits_text = self.font_medium.render(f"HVC: {self.credits:.4f}", True, BRIGHT_GREEN)
        self.screen.blit(credits_text, (50, 50))
        ship_info = [f"HP: {self.player_ship.hp}/{self.player_ship.max_hp}", f"Shield: {self.player_ship.shield}/{self.player_ship.max_shield}", f"Palivo: {int(self.player_ship.fuel)}/{self.player_ship.max_fuel}", f"Naklad: {self.player_ship.get_total_cargo()}/{self.player_ship.max_cargo}"]
        for i, info in enumerate(ship_info):
            text = self.font_small.render(info, True, WHITE)
            self.screen.blit(text, (50, 100 + i * 25))

    def draw_map(self):
        self.screen.fill(BLACK)
        
        # Animovane pozadi
        for sx, sy, size in self.star_field:
            screen_x = int((sx - self.map_camera_x) * self.map_zoom + SCREEN_WIDTH // 2) % SCREEN_WIDTH
            screen_y = int((sy - self.map_camera_y) * self.map_zoom + SCREEN_HEIGHT // 2) % SCREEN_HEIGHT
            
            # Pulzujici hvezdy
            pulse = math.sin(pygame.time.get_ticks() * 0.001 + sx * 0.01) * 0.3 + 0.7
            color_intensity = int(50 * pulse)
            color = (color_intensity, color_intensity, int(color_intensity * 1.6))
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 1)
        
        # Planety s efektem
        for planet in self.planets:
            planet.draw_on_map(self.screen, self.map_camera_x, self.map_camera_y, self.map_zoom, self.font_tiny)
            
            # Efekt pro blizke planety
            dist_to_player = math.sqrt((planet.x - self.player_ship.x)**2 + (planet.y - self.player_ship.y)**2)
            if dist_to_player < 500:
                alpha = int(100 * (1 - dist_to_player / 500))
                screen_x = int((planet.x - self.map_camera_x) * self.map_zoom + SCREEN_WIDTH // 2)
                screen_y = int((planet.y - self.map_camera_y) * self.map_zoom + SCREEN_HEIGHT // 2)
                glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*planet.color, alpha), (10, 10), 10)
                self.screen.blit(glow_surface, (screen_x - 10, screen_y - 10))
        
        # Hracova pozice
        player_x = int((self.player_ship.x - self.map_camera_x) * self.map_zoom + SCREEN_WIDTH // 2)
        player_y = int((self.player_ship.y - self.map_camera_y) * self.map_zoom + SCREEN_HEIGHT // 2)
        if 0 <= player_x <= SCREEN_WIDTH and 0 <= player_y <= SCREEN_HEIGHT:
            # Kruhovy efekt kolem hrace
            for i in range(3):
                alpha = int(100 - i * 30)
                radius = 4 + i * 2
                pygame.draw.circle(self.screen, (*BRIGHT_GREEN, alpha), (player_x, player_y), radius, 1)
            pygame.draw.circle(self.screen, BRIGHT_GREEN, (player_x, player_y), 4)
        
        # Titulek
        title = self.font_large.render("GALAXIE - MAPA", True, BRIGHT_BLUE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Informace
        info = self.font_small.render("Klik na planetu/stanici pro teleport za HVC", True, CYAN)
        self.screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 60))
        
        # Legenda
        legend_y = 100
        legend_items = [
            ((0,100,210), "Planeta", "Zakladni planety s surovinami"),
            ((100,150,200), "Doky", "Lodni doky a opravny"),
            ((180,30,30), "Piratsky klub", "Nebezpecna piratska stanice"),
            ((0,200,200), "Hi-Tech Lab", "Vysokotechnologicke centrum"),
            ((200,150,0), "Obchodni stanice", "Obchodni centrum")
        ]
        legend_title = self.font_small.render("LEGENDA:", True, CYAN)
        self.screen.blit(legend_title, (20, legend_y))
        for i, (color, name, description) in enumerate(legend_items):
            y = legend_y + 25 + i * 22
            pygame.draw.circle(self.screen, color, (30, y + 5), 5)
            text = self.font_tiny.render(f"{name}", True, WHITE)
            self.screen.blit(text, (40, y))
            desc_text = self.font_tiny.render(description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (40, y + 12))
        
        # Ovladani
        controls = [
            f"Zoom: {self.map_zoom:.2f} [+/-]",
            f"Pozice: [{int(self.player_ship.x)}, {int(self.player_ship.y)}]",
            f"Planet: {len(self.planets)} | Pirati: {len(self.enemies)}"
        ]
        for i, control in enumerate(controls):
            control_text = self.font_tiny.render(control, True, GRAY)
            self.screen.blit(control_text, (10, 10 + i * 20))
        
        # Zpet tlacidlo
        back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 40)
        pygame.draw.rect(self.screen, (60,60,60), back_btn_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, back_btn_rect, 2)
        back_text = self.font_medium.render("[ESC/M] Zpet do hry", True, WHITE)
        self.screen.blit(back_text, (back_btn_rect.x + 40, back_btn_rect.y + 8))
        
        # Mini radar
        radar_mini_x = 50
        radar_mini_y = SCREEN_HEIGHT - 150
        radar_mini_size = 100
        pygame.draw.rect(self.screen, (20,20,40), (radar_mini_x, radar_mini_y, radar_mini_size, radar_mini_size))
        pygame.draw.rect(self.screen, BORDER_COLOR, (radar_mini_x, radar_mini_y, radar_mini_size, radar_mini_size), 1)
        
        mini_radar_scale = radar_mini_size / (2 * self.effective_radar_range)
        for enemy in self.enemies:
            rel_x = enemy.x - self.player_ship.x
            rel_y = enemy.y - self.player_ship.y
            dist = math.sqrt(rel_x**2 + rel_y**2)
            if dist <= self.effective_radar_range:
                mini_x = radar_mini_x + radar_mini_size // 2 + int(rel_x * mini_radar_scale)
                mini_y = radar_mini_y + radar_mini_size // 2 + int(rel_y * mini_radar_scale)
                pygame.draw.circle(self.screen, BRIGHT_RED, (mini_x, mini_y), 1)

    def draw_trading(self):
        if not self.docked_planet:
            self.state = "DOCKED"
            return

        self.draw_docked()
        self.clickable_buttons = []

        if not hasattr(self, 'trading_scroll'):
            self.trading_scroll = 0
        if not hasattr(self, 'cargo_scroll'):
            self.cargo_scroll = 0

        ow = 920
        oh = 560
        ox = SCREEN_WIDTH // 2 - ow // 2
        oy = SCREEN_HEIGHT // 2 - oh // 2

        overlay = pygame.Surface((ow, oh), pygame.SRCALPHA)
        overlay.fill((10, 10, 40, 245))
        self.screen.blit(overlay, (ox, oy))
        pygame.draw.rect(self.screen, BORDER_COLOR, (ox, oy, ow, oh), 3)

        title = self.font_large.render(f"OBCHODNI CENTRUM - {self.docked_planet.name}", True, BRIGHT_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, oy + 10))

        station_type = self.docked_planet.get_type_name()
        type_colors = {"Planeta": GREEN, "Doky": BLUE, "Piratsky klub": RED, "Hi-Tech Lab": CYAN, "Obchodni stanice": YELLOW}
        type_color = type_colors.get(station_type, WHITE)
        type_text = self.font_small.render(f"Typ: {station_type}  |  Kredity: {self.credits:.2f} HVC", True, type_color)
        self.screen.blit(type_text, (ox + 20, oy + 45))

        pygame.draw.line(self.screen, BORDER_COLOR, (ox + 20, oy + 70), (ox + ow - 20, oy + 70), 2)

        mid_x = ox + ow // 2
        buy_title = self.font_medium.render("NAKUP", True, BRIGHT_GREEN)
        self.screen.blit(buy_title, (ox + 30, oy + 80))
        sell_title = self.font_medium.render("PRODEJ", True, BRIGHT_RED)
        self.screen.blit(sell_title, (mid_x + 20, oy + 80))

        scroll_offset = getattr(self, 'trading_scroll', 0)
        max_scroll = max(0, len(self.docked_planet.available_items) - 9) if self.docked_planet else 0
        col_w = ow // 2 - 50

        # ---- BUY COLUMN ----
        if self.docked_planet:
            visible_items = self.docked_planet.available_items[scroll_offset:scroll_offset + 9]
            for i, item in enumerate(visible_items):
                price = self.docked_planet.prices.get(item, 100)
                stock = self.docked_planet.goods.get(item, 0)
                in_stock = stock > 0

                btn_rect = pygame.Rect(ox + 20, oy + 110 + i * 38, col_w, 34)
                bg_color = (25, 25, 50) if any(b['rect'] == btn_rect for b in self.clickable_buttons) else (15, 15, 35)
                pygame.draw.rect(self.screen, bg_color, btn_rect)
                border_color = (100, 100, 100) if in_stock else (60, 30, 30)
                pygame.draw.rect(self.screen, border_color, btn_rect, 1)

                item_text = self.font_tiny.render(f"{item}", True, WHITE if in_stock else GRAY)
                self.screen.blit(item_text, (btn_rect.x + 6, btn_rect.y + 8))

                price_color = GREEN if price < 1.0 else YELLOW if price < 3.0 else RED
                price_text = self.font_tiny.render(f"{price} HVC", True, price_color if in_stock else GRAY)
                self.screen.blit(price_text, (btn_rect.x + col_w - 80, btn_rect.y + 8))

                if in_stock:
                    def buy_action(item=item):
                        self.buy_specific_item(item)
                    self.clickable_buttons.append({'rect': btn_rect, 'action': buy_action})

            if max_scroll > 0:
                bar_y = oy + 110
                bar_h = 9 * 38
                bar_rect = pygame.Rect(ox + col_w + 35, bar_y, 6, bar_h)
                pygame.draw.rect(self.screen, (60, 60, 60), bar_rect)
                handle_y = bar_y + int((scroll_offset / max_scroll) * (bar_h - 12))
                pygame.draw.rect(self.screen, type_color, (ox + col_w + 35, handle_y, 6, 12))

        # ---- SELL COLUMN ----
        cargo_scroll = getattr(self, 'cargo_scroll', 0)
        max_cargo_scroll = max(0, len(self.player_ship.cargo) - 9)
        visible_cargo = list(self.player_ship.cargo.items())[cargo_scroll:cargo_scroll + 9]

        if visible_cargo:
            for i, (item, amount) in enumerate(visible_cargo):
                price = self.docked_planet.prices.get(item, 100)
                btn_rect = pygame.Rect(mid_x + 10, oy + 110 + i * 38, col_w, 34)
                bg_color = (45, 20, 20) if any(b['rect'] == btn_rect for b in self.clickable_buttons) else (35, 15, 15)
                pygame.draw.rect(self.screen, bg_color, btn_rect)
                pygame.draw.rect(self.screen, (150, 80, 80), btn_rect, 1)

                item_text = self.font_tiny.render(f"{item} ({amount}x)", True, WHITE)
                self.screen.blit(item_text, (btn_rect.x + 6, btn_rect.y + 8))

                price_color = GREEN if price < 1.0 else YELLOW if price < 3.0 else RED
                price_text = self.font_tiny.render(f"{price} HVC", True, price_color)
                self.screen.blit(price_text, (btn_rect.x + col_w - 70, btn_rect.y + 8))

                def sell_action(item=item):
                    self.sell_goods(item)
                self.clickable_buttons.append({'rect': btn_rect, 'action': sell_action})

            if max_cargo_scroll > 0:
                bar_y = oy + 110
                bar_h = 9 * 38
                bar_rect = pygame.Rect(mid_x + col_w + 20, bar_y, 6, bar_h)
                pygame.draw.rect(self.screen, (60, 60, 60), bar_rect)
                handle_y = bar_y + int((cargo_scroll / max_cargo_scroll) * (bar_h - 12))
                pygame.draw.rect(self.screen, RED, (mid_x + col_w + 20, handle_y, 6, 12))
        else:
            no_cargo = self.font_small.render("Zadny naklad", True, GRAY)
            self.screen.blit(no_cargo, (mid_x + 20, oy + 120))

        # Bottom bar
        pygame.draw.line(self.screen, BORDER_COLOR, (ox + 20, oy + oh - 50), (ox + ow - 20, oy + oh - 50), 2)

        back_btn = pygame.Rect(ox + ow - 160, oy + oh - 42, 140, 34)
        pygame.draw.rect(self.screen, (80, 80, 80), back_btn)
        pygame.draw.rect(self.screen, BORDER_COLOR, back_btn, 2)
        back_text = self.font_medium.render("[ESC] Zpet", True, WHITE)
        self.screen.blit(back_text, (back_btn.x + 30, back_btn.y + 6))
        self.clickable_buttons.append({'rect': back_btn, 'action': lambda: setattr(self, 'state', 'DOCKED')})

        help_text = self.font_tiny.render("Klikni na polozku pro koupi/prodej", True, LIGHT_GRAY)
        self.screen.blit(help_text, (ox + 20, oy + oh - 40))

    def draw_quest(self):
        self.screen.fill(DARK_BG)
        
        # Titulek s animaci
        title_pulse = math.sin(pygame.time.get_ticks() * 0.002) * 0.1 + 1.0
        title = self.font_large.render("UKOLY RANGERA", True, BRIGHT_YELLOW)
        scaled_title = pygame.transform.scale(title, (int(title.get_width() * title_pulse), int(title.get_height() * title_pulse)))
        self.screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 40))
        
        # Statistiky hrace
        stats_bg = pygame.Rect(50, 80, 200, 80)
        pygame.draw.rect(self.screen, (20, 20, 40, 150), stats_bg)
        pygame.draw.rect(self.screen, BORDER_COLOR, stats_bg, 1)
        
        stats_title = self.font_small.render("STATISTIKY", True, CYAN)
        self.screen.blit(stats_title, (60, 90))
        
        player_stats = [
            f"Level: {self.player_ship.level}",
            f"XP: {int(self.player_ship.xp)}/{int(self.player_ship.xp_to_level)}",
            f"Lodi zniceno: {self.quest_progress.get('kill', 0)}",
            f"Ukol splnen: {6 - len(self.quests)}"
        ]
        
        for i, stat in enumerate(player_stats):
            text = self.font_tiny.render(stat, True, WHITE)
            self.screen.blit(text, (60, 110 + i * 15))
        
        # Aktualni ukol
        if self.current_quest:
            current_panel = pygame.Surface((850, 160), pygame.SRCALPHA)
            current_panel.fill((10, 30, 10, 200))
            self.screen.blit(current_panel, (75, 120))
            pygame.draw.rect(self.screen, GREEN, (75, 120, 850, 160), 2)
            
            current_title = self.font_medium.render("AKTUALNI UKOL", True, BRIGHT_GREEN)
            self.screen.blit(current_title, (95, 130))
            
            quest_text = self.font_small.render(f"{self.current_quest['name']}", True, WHITE)
            self.screen.blit(quest_text, (95, 155))
            
            reward_text = self.font_tiny.render(f"Odmena: {self.current_quest['reward']} HVC", True, BRIGHT_YELLOW)
            self.screen.blit(reward_text, (95, 175))
            
            # Progress bar
            progress_bg = pygame.Rect(95, 195, 800, 20)
            pygame.draw.rect(self.screen, DARK_GRAY, progress_bg)
            pygame.draw.rect(self.screen, GREEN, progress_bg, 1)
            
            # Progress podle typu ukolu
            if self.current_quest['type'] == 'kill':
                progress = self.quest_progress['kill'] / self.current_quest['amount']
                progress_text = f"{self.quest_progress['kill']}/{self.current_quest['amount']} piratskych lodi"
            elif self.current_quest['type'] == 'deliver':
                has = self.player_ship.cargo.get(self.current_quest['item'], 0)
                progress = has / self.current_quest['amount']
                progress_text = f"{has}/{self.current_quest['amount']} {self.current_quest['item']}"
            elif self.current_quest['type'] == 'collect':
                has = self.player_ship.cargo.get(self.current_quest['item'], 0)
                progress = has / self.current_quest['amount']
                progress_text = f"{has}/{self.current_quest['amount']} {self.current_quest['item']}"
            
            progress_width = int(800 * progress)
            progress_color = GREEN if progress > 0.7 else YELLOW if progress > 0.3 else RED
            pygame.draw.rect(self.screen, progress_color, (95, 195, progress_width, 20))
            
            progress_label = self.font_tiny.render(progress_text, True, WHITE)
            self.screen.blit(progress_label, (100, 200))
            
            # Detailni informace
            if self.current_quest['type'] == 'kill':
                remaining = self.current_quest['amount'] - self.quest_progress['kill']
                if remaining > 0:
                    hint = self.font_tiny.render(f"Zbyva znicit {remaining} piratskych lodi", True, YELLOW)
                    self.screen.blit(hint, (95, 225))
            
            elif self.current_quest['type'] == 'deliver':
                from_planet = self.current_quest.get('from', 'neurceno')
                to_planet = self.current_quest['to']
                planet_info = self.font_tiny.render(f"Doruc z {from_planet} na {to_planet}", True, CYAN)
                self.screen.blit(planet_info, (95, 225))
                
                # Pokud je hrac na cilove planete
                if self.docked_planet and self.docked_planet.name == to_planet:
                    has = self.player_ship.cargo.get(self.current_quest['item'], 0)
                    if has >= self.current_quest['amount']:
                        complete_text = self.font_tiny.render("UKOL MUZE BYT DOKONCEN!", True, BRIGHT_GREEN)
                        self.screen.blit(complete_text, (95, 245))
                    else:
                        need_text = self.font_tiny.render(f"Potreba jeste {self.current_quest['amount'] - has} {self.current_quest['item']}", True, BRIGHT_RED)
                        self.screen.blit(need_text, (95, 245))
            
            elif self.current_quest['type'] == 'collect':
                has = self.player_ship.cargo.get(self.current_quest['item'], 0)
                remaining = self.current_quest['amount'] - has
                if remaining > 0:
                    hint = self.font_tiny.render(f"Zbyva sebrat {remaining} {self.current_quest['item']}", True, YELLOW)
                    self.screen.blit(hint, (95, 225))
        
        # Dostupne ukoly
        available_title = self.font_medium.render("DOSTUPNE UKOLY", True, CYAN)
        self.screen.blit(available_title, (75, 320))
        
        self.clickable_buttons = []
        for i, quest in enumerate(self.quests):
            quest_panel = pygame.Surface((850, 65), pygame.SRCALPHA)
            quest_panel.fill((5, 5, 25, 200))
            self.screen.blit(quest_panel, (75, 360 + i * 75))
            pygame.draw.rect(self.screen, BORDER_COLOR, (75, 360 + i * 75, 850, 65), 1)
            
            # Typ ukolu s ikonkou
            quest_type = quest['type'].upper()
            type_colors = {
                "DELIVER": GREEN,
                "COLLECT": YELLOW,
                "KILL": RED
            }
            type_color = type_colors.get(quest_type, WHITE)
            
            # Ikonka
            icon_x = 95
            icon_y = 390 + i * 75
            pygame.draw.circle(self.screen, type_color, (icon_x, icon_y), 8)
            
            # Informace
            quest_info = self.font_small.render(f"[{i+1}] {quest['name']}", True, WHITE)
            self.screen.blit(quest_info, (115, 375 + i * 75))
            
            reward_info = self.font_tiny.render(f"Odmena: {quest['reward']} HVC", True, BRIGHT_GREEN)
            self.screen.blit(reward_info, (115, 395 + i * 75))
            
            # Typ ukolu
            type_text = self.font_tiny.render(f"Typ: {quest_type}", True, type_color)
            self.screen.blit(type_text, (600, 385 + i * 75))
            
            # Progress pro dorucovaci ukoly
            if quest['type'] == 'deliver':
                progress_text = f"Cil: {quest['to']}"
                progress_info = self.font_tiny.render(progress_text, True, LIGHT_GRAY)
                self.screen.blit(progress_info, (600, 400 + i * 75))
            
            btn_rect = pygame.Rect(75, 360 + i * 75, 850, 65)
            self.clickable_buttons.append({'rect': btn_rect, 'action': lambda idx=i: self.accept_quest(idx)})
        
        # Zpet tlacidlo
        back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, 160, 40)
        pygame.draw.rect(self.screen, (80,80,80), back_btn_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, back_btn_rect, 2)
        back_text = self.font_medium.render("[ESC] Zpet", True, WHITE)
        self.screen.blit(back_text, (back_btn_rect.x + 40, back_btn_rect.y + 8))
        self.clickable_buttons.append({'rect': back_btn_rect, 'action': lambda: setattr(self, 'state', 'DOCKED' if self.docked_planet else 'GAME')})

    def draw_upgrade(self):
        self.screen.fill(DARK_BG)
        self.clickable_buttons = []
        
        # Titulek s animaci
        title_pulse = math.sin(pygame.time.get_ticks() * 0.002) * 0.1 + 1.0
        title = self.font_large.render("VYLEPSENI LODI", True, BRIGHT_YELLOW)
        scaled_title = pygame.transform.scale(title, (int(title.get_width() * title_pulse), int(title.get_height() * title_pulse)))
        self.screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 40))
        
        # Kredit informace
        credits_bg = pygame.Rect(50, 80, 300, 60)
        pygame.draw.rect(self.screen, (0, 50, 0, 150), credits_bg)
        pygame.draw.rect(self.screen, GREEN, credits_bg, 2)
        credits = self.font_medium.render(f"HVC: {self.credits:.2f}", True, BRIGHT_GREEN)
        self.screen.blit(credits, (70, 95))
        
        # Lodni statistiky
        stats_bg = pygame.Rect(50, 160, 380, 200)
        pygame.draw.rect(self.screen, (20, 20, 40, 200), stats_bg)
        pygame.draw.rect(self.screen, BORDER_COLOR, stats_bg, 2)
        
        stats_title = self.font_medium.render("STATISTIKY LODI", True, CYAN)
        self.screen.blit(stats_title, (70, 170))
        
        ship_info = [
            f"Jmeno: {self.player_ship.name}",
            f"Level: {self.player_ship.level}",
            f"HP: {self.player_ship.hp}/{self.player_ship.max_hp}",
            f"Shield: {self.player_ship.shield}/{self.player_ship.max_shield}",
            f"Rychlost: {self.player_ship.max_speed:.1f}",
            f"Naklad: {self.player_ship.get_total_cargo()}/{self.player_ship.max_cargo}",
            f"Palivo: {int(self.player_ship.fuel)}/{self.player_ship.max_fuel}",
            f"Zbrane: {', '.join(self.player_ship.weapons)}"
        ]
        
        for i, info in enumerate(ship_info):
            color = BRIGHT_GREEN if i == 0 else CYAN if i == 1 else WHITE
            text = self.font_small.render(info, True, color)
            self.screen.blit(text, (70, 200 + i * 22))

        # Pasivni bonusy z nakladu
        s = self.player_ship
        if s._applied_bonuses or s.radar_bonus:
            bonus_bg = pygame.Rect(50, 380, 380, 90)
            pygame.draw.rect(self.screen, (20, 40, 20, 200), bonus_bg)
            pygame.draw.rect(self.screen, GREEN, bonus_bg, 2)
            bonus_title = self.font_small.render("PASIVNI BONUSY (z nakladu)", True, BRIGHT_GREEN)
            self.screen.blit(bonus_title, (70, 385))
            bonus_lines = []
            for stat, val in s._applied_bonuses.items():
                if val != 0:
                    sign = "+"
                    bonus_lines.append(f"{stat}: {sign}{val:.2f}")
            if s.radar_bonus:
                bonus_lines.append(f"radar: +{s.radar_bonus}")
            for i, line in enumerate(bonus_lines):
                text = self.font_tiny.render(line, True, GREEN)
                self.screen.blit(text, (70, 405 + i * 16))

        # Dostupna vylepseni
        upgrades_title = self.font_medium.render("VYLEPSENI", True, BRIGHT_YELLOW)
        self.screen.blit(upgrades_title, (500, 120))
        
        upgrades = [
            ("Posileni trupu (+20 HP)", 500, "hp", "Zvysi maximalni HP o 20 bodu"),
            ("Stity (+20)", 400, "shield", "Zvysi maximalni stity o 20 bodu"),
            ("Rychlost (+0.5)", 300, "speed", "Zvysi maximalni rychlost o 0.5"),
            ("Naklad (+20)", 600, "cargo", "Zvysi maximalni naklad o 20 jednotek"),
            ("Max palivo (+50)", 350, "fuel", "Zvysi maximalni palivo o 50 jednotek"),
            ("Laser II", 1000, "weapon", "Nova zbran - rychlejsi strelba"),
            ("Plazmová puška", 2000, "weapon2", "Silna zbran s velkym dosahem"),
            ("Motor vylepseni", 800, "engine", "Vylepseny motor - vetsi tah a rychlost"),
            ("Radar+ (+" + str(self.effective_radar_range) + ")", 1500, "radar", "Zvysi radarovy dosah")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        for i, (name, cost, up_type, description) in enumerate(upgrades):
            y_pos = 160 + i * 45
            
            # Tlacidko
            btn_rect = pygame.Rect(500, y_pos, 450, 40)
            is_hover = btn_rect.collidepoint(mouse_pos)
            can_afford = self.credits >= cost
            
            # Pozadi tlacidka
            if not can_afford:
                btn_color = (60, 20, 20)
                border_color = RED
            elif is_hover:
                btn_color = (30, 30, 50)
                border_color = BRIGHT_YELLOW
            else:
                btn_color = (20, 20, 40)
                border_color = BORDER_COLOR
            
            pygame.draw.rect(self.screen, btn_color, btn_rect)
            pygame.draw.rect(self.screen, border_color, btn_rect, 2)
            
            # Text informace
            name_color = WHITE if can_afford else GRAY
            text = self.font_small.render(f"{name} - {cost} HVC", True, name_color)
            self.screen.blit(text, (510, y_pos + 8))
            
            # Popisek
            desc_text = self.font_tiny.render(description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (510, y_pos + 22))
            
            # Stav koupeni
            if up_type in ["hp", "shield", "speed", "cargo", "fuel"]:
                current_value = getattr(self.player_ship, f"max_{up_type}")
                status_text = self.font_tiny.render(f"Aktualne: {current_value}", True, GREEN)
                self.screen.blit(status_text, (850, y_pos + 12))
            
            self.clickable_buttons.append({'rect': btn_rect, 'action': lambda t=up_type, c=cost: self._do_upgrade(t, c)})
        
        # Zpet tlacidlo
        back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, 160, 40)
        pygame.draw.rect(self.screen, (80,80,80), back_btn_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, back_btn_rect, 2)
        back_text = self.font_medium.render("[ESC] Zpet", True, WHITE)
        self.screen.blit(back_text, (back_btn_rect.x + 40, back_btn_rect.y + 8))
        self.clickable_buttons.append({'rect': back_btn_rect, 'action': lambda: setattr(self, 'state', 'DOCKED' if self.docked_planet else 'GAME')})

    def _do_upgrade(self, up_type, cost):
        if up_type in ["hp", "shield", "speed", "cargo", "fuel"]:
            self.upgrade_ship(up_type)
        elif up_type == "weapon":
            self.upgrade_weapon("Laser II", 1000)
        elif up_type == "weapon2":
            self.upgrade_weapon("Plazmová puška", 2000)
        elif up_type == "engine":
            self.upgrade_engine()
        elif up_type == "radar":
            self.upgrade_radar()

    def draw_buy_fuel(self):
        self.draw_docked()
        overlay = pygame.Surface((500,350), pygame.SRCALPHA)
        overlay.fill((5,5,30,230))
        self.screen.blit(overlay, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 175))
        pygame.draw.rect(self.screen, BORDER_COLOR, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 175, 500, 350), 3)
        title = self.font_large.render("NAKUP PALIVA", True, BRIGHT_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 155))
        fuel_info = self.font_medium.render(f"Aktualni palivo: {int(self.player_ship.fuel)}/{self.player_ship.max_fuel}", True, FUEL_COLOR)
        self.screen.blit(fuel_info, (SCREEN_WIDTH // 2 - fuel_info.get_width() // 2, SCREEN_HEIGHT // 2 - 110))
        options = [("[1] 10 jednotek (20 HVC)", 10), ("[2] 25 jednotek (50 HVC)", 25), ("[3] 50 jednotek (100 HVC)", 50), ("[4] 100 jednotek (200 HVC)", 100)]
        for i, (text, amount) in enumerate(options):
            rendered = self.font_medium.render(text, True, WHITE)
            self.screen.blit(rendered, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 60 + i * 40))

    def draw_credits(self):
        self.screen.fill(BLACK)
        title = self.font_large.render("KREDITY", True, BRIGHT_BLUE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        credits_text = ["", "SPACE RANGERS - HAVIROV COIN EDITION", "", "Puvodni hra: Elemental Games (2002)", "Inspirovano: Space Rangers, X3, Escape Velocity", "", "Vsechny texty jsou v cestine.", "Kredity (HVC) jsou integrovany s Havirov Coin walletem.", "", "[ESC] Zpet"]
        for i, text in enumerate(credits_text):
            color = BRIGHT_YELLOW if i == 1 else WHITE
            rendered = self.font_small.render(text, True, color)
            self.screen.blit(rendered, (SCREEN_WIDTH // 2 - 250, 180 + i * 25))

    def draw_mining_log(self):
        """Draw the mining statistics and history screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("MINING STATISTICS", True, BRIGHT_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Overall stats
        if self.mining_history:
            total_mined = sum(session["earned"] for session in self.mining_history)
            total_hashes = sum(session["hashes"] for session in self.mining_history)
            total_shares = sum(session["shares"] for session in self.mining_history)
            avg_efficiency = sum(session["efficiency"] for session in self.mining_history) / len(self.mining_history)
            
            # Overall stats panel
            overall_panel = pygame.Surface((600, 200), pygame.SRCALPHA)
            overall_panel.fill((10, 10, 30, 200))
            self.screen.blit(overall_panel, (SCREEN_WIDTH // 2 - 300, 80))
            pygame.draw.rect(self.screen, BORDER_COLOR, (SCREEN_WIDTH // 2 - 300, 80, 600, 200), 3)
            
            overall_stats = [
                ("Total Sessions", f"{len(self.mining_history)}", CYAN),
                ("Total Mined", f"{total_mined:.8f} HVC", BRIGHT_GREEN),
                ("Total Hashes", f"{total_hashes:,}", BRIGHT_BLUE),
                ("Total Shares", f"{total_shares}", YELLOW),
                ("Avg Efficiency", f"{avg_efficiency:.4f}%", PURPLE)
            ]
            
            for i, (label, value, color) in enumerate(overall_stats):
                y_pos = 100 + i * 30
                label_text = self.font_small.render(f"{label}:", True, WHITE)
                value_text = self.font_medium.render(str(value), True, color)
                self.screen.blit(label_text, (SCREEN_WIDTH // 2 - 280, y_pos))
                self.screen.blit(value_text, (SCREEN_WIDTH // 2 + 50, y_pos))
        
        # Session history
        history_title = self.font_medium.render("RECENT SESSIONS", True, CYAN)
        self.screen.blit(history_title, (50, 320))
        
        # Draw recent sessions
        for i, session in enumerate(self.mining_history[-5:]):  # Show last 5 sessions
            y_pos = 360 + i * 80
            
            # Session panel
            session_panel = pygame.Surface((SCREEN_WIDTH - 100, 70), pygame.SRCALPHA)
            session_panel.fill((5, 5, 20, 150))
            self.screen.blit(session_panel, (50, y_pos))
            pygame.draw.rect(self.screen, BORDER_COLOR, (50, y_pos, SCREEN_WIDTH - 100, 70), 1)
            
            # Session info
            session_time = time.strftime("%H:%M", time.localtime(session["timestamp"]))
            session_info = [
                f"Time: {session_time}",
                f"Duration: {session['duration']:.1f}s",
                f"Hashes: {session['hashes']:,}",
                f"Shares: {session['shares']}",
                f"Earned: {session['earned']:.8f} HVC",
                f"Efficiency: {session['efficiency']:.4f}%"
            ]
            
            for j, info in enumerate(session_info):
                x_pos = 70 + j * 140
                info_text = self.font_tiny.render(info, True, WHITE)
                self.screen.blit(info_text, (x_pos, y_pos + 20))
        
        # Controls
        controls = [
            "[L] Refresh",
            "[ESC] Back to Game"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, BRIGHT_YELLOW)
            self.screen.blit(control_text, (50, SCREEN_HEIGHT - 80 + i * 25))
        
        # Best performance indicator
        if self.mining_history:
            best_session = max(self.mining_history, key=lambda x: x["max_hashrate"])
            best_text = self.font_small.render(f"Best Hash Rate: {best_session['max_hashrate']:,.0f} H/s", True, GREEN)
            self.screen.blit(best_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60))

    def draw_top_panel(self):
        panel = pygame.Surface((SCREEN_WIDTH,90), pygame.SRCALPHA)
        panel.fill((0,0,0,200))
        self.screen.blit(panel, (0,0))
        
        # Titulek
        title_text = self.font_medium.render("SPACE RANGERS - HAVIROV COIN EDITION", True, BRIGHT_BLUE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 5))
        
        # HP s progress barem
        hp_pct = self.player_ship.hp / self.player_ship.max_hp
        hp_color = GREEN if hp_pct > 0.5 else (YELLOW if hp_pct > 0.25 else RED)
        pygame.draw.rect(self.screen, DARK_GRAY, (10,30,204,18))
        pygame.draw.rect(self.screen, hp_color, (12,32,200*hp_pct,14))
        hp_text = self.font_tiny.render(f"HP: {int(self.player_ship.hp)}/{self.player_ship.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (220,33))
        
        # Shield s progress barem
        shield_pct = self.player_ship.shield / self.player_ship.max_shield
        pygame.draw.rect(self.screen, DARK_GRAY, (10,55,204,18))
        pygame.draw.rect(self.screen, BLUE, (12,57,200*shield_pct,14))
        shield_text = self.font_tiny.render(f"Shield: {int(self.player_ship.shield)}/{self.player_ship.max_shield}", True, WHITE)
        self.screen.blit(shield_text, (220,58))
        
        # Fuel s progress barem
        fuel_pct = self.player_ship.fuel / self.player_ship.max_fuel
        pygame.draw.rect(self.screen, DARK_GRAY, (10,80,204,18))
        pygame.draw.rect(self.screen, FUEL_COLOR, (12,82,200*fuel_pct,14))
        fuel_text = self.font_tiny.render(f"Fuel: {int(self.player_ship.fuel)}/{self.player_ship.max_fuel}", True, WHITE)
        self.screen.blit(fuel_text, (220,83))
        
        # Informace o kreditu a nakladu
        credits_bg = pygame.Rect(350, 30, 200, 65)
        pygame.draw.rect(self.screen, (0,50,0,150), credits_bg)
        pygame.draw.rect(self.screen, GREEN, credits_bg, 2)
        credits_text = self.font_medium.render(f"HVC: {self.credits:.2f}", True, BRIGHT_GREEN)
        self.screen.blit(credits_text, (360,40))
        
        cargo_text = self.font_small.render(f"Cargo: {self.player_ship.get_total_cargo()}/{self.player_ship.max_cargo}", True, CYAN)
        self.screen.blit(cargo_text, (360,70))
        
        # Level a XP
        level_bg = pygame.Rect(570, 30, 180, 65)
        pygame.draw.rect(self.screen, (50,0,50,150), level_bg)
        pygame.draw.rect(self.screen, PURPLE, level_bg, 2)
        level_text = self.font_medium.render(f"Level: {self.player_ship.level}", True, PURPLE)
        self.screen.blit(level_text, (580,40))
        
        xp_pct = self.player_ship.xp / self.player_ship.xp_to_level
        pygame.draw.rect(self.screen, DARK_GRAY, (580,70,160,12))
        pygame.draw.rect(self.screen, PURPLE, (582,72,156*xp_pct,8))
        xp_text = self.font_tiny.render(f"XP: {int(self.player_ship.xp)}/{int(self.player_ship.xp_to_level)}", True, WHITE)
        self.screen.blit(xp_text, (580,85))
        
        # Status informace
        status_x = 770
        if self.player_ship._applied_bonuses or self.player_ship.radar_bonus:
            bonus_count = len(self.player_ship._applied_bonuses) + (1 if self.player_ship.radar_bonus else 0)
            bonus_text = self.font_tiny.render(f"Bonusy: {bonus_count}x", True, GREEN)
            self.screen.blit(bonus_text, (status_x, 25))
        if self.multiplayer and self.network and self.network.connected:
            mp_text = self.font_tiny.render(f"MP: {len(self.remote_players)} hracu", True, CYAN)
            self.screen.blit(mp_text, (status_x, 40))
            name_text = self.font_tiny.render(self.player_ship.name, True, BRIGHT_GREEN)
            self.screen.blit(name_text, (status_x, 55))
        elif self.player_ship.docked_at:
            docked_text = self.font_tiny.render(f"Docked at: {self.player_ship.docked_at}", True, YELLOW)
            self.screen.blit(docked_text, (status_x, 40))
        else:
            status_text = self.font_tiny.render("In flight", True, GREEN)
            self.screen.blit(status_text, (status_x, 40))

    def draw_game_controls(self):
        controls = ["[C] Kredity", "[B] Wallet", "[ESC] Menu"]
        for i, text in enumerate(controls):
            rendered = self.font_tiny.render(text, True, BRIGHT_YELLOW)
            self.screen.blit(rendered, (SCREEN_WIDTH - 150, 10 + i * 20))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        if self.state != "MENU":
            self.save_game()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SpaceRangersGame()
    game.run()

