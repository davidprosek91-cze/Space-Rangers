"""Space Rangers - Havirov Coin Edition"""
import pygame, sys, os, json, random, math, itertools
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

WALLET_PATH = "/home/davidprosek/Downloads/Havirov-Coin-master/wallet.dat"

class WalletInterface:
    def __init__(self):
        self.balance = 0.0
        self.address = ""
        self.name = ""
        self.load_wallet()

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
# Add generated variations
base_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta", "Iota", "Kappa", "Lambda",
              "Sigma", "Omega", "Phi", "Psi", "Tau", "Mu", "Nu", "Xi", "Pi", "Rho",
              "Chi", "Psi", "Tau", "Upsilon", "Omicron", "Xi", "Pi", "Rho", "Sigma", "Tau"]
for i in range(600 - len(ALL_ITEMS)):
    cat = list(ITEM_CATEGORIES.keys())[i % len(ITEM_CATEGORIES)]
    suffix = base_names[i % len(base_names)]
    ALL_ITEMS.append((f"{cat[:-1]} {suffix} {i}", cat))

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
        available = [item for item, cat in ALL_ITEMS if cat in categories]
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
        return [item for item, cat in ALL_ITEMS if cat in categories]
    
    def _generate_new_goods(self):
        """Generovani noveho zbozi pro udrzeni nekonecneho hraní"""
        if len(self.available_items) < 50:  # Omezeni maximalniho poctu polozek
            # Vyber nahodnou kategorii
            cat_map = {
                "PLANET": ["Minerály", "Potraviny", "Léky"],
                "DOCKY": ["Zbraně", "Technologie", "Komponenty"],
                "PIRATSKY_KLUB": ["Zbraně", "Minerály", "Luxus"],
                "HI_TECH_LAB": ["Technologie", "Léky", "Komponenty"],
                "OBCHODNI_STANICE": ["Minerály", "Potraviny", "Zbraně", "Technologie", "Léky", "Luxus"]
            }
            available_categories = cat_map.get(self.station_type, ["Minerály"])
            selected_category = random.choice(available_categories)
            
            # Najdi vsechny polozky v dane kategorii
            category_items = [item for item, cat in ALL_ITEMS if cat == selected_category]
            
            # Najdi polozky, ktere nejsou v aktualni nabidce
            new_items = [item for item in category_items if item not in self.available_items]
            
            if new_items:
                # Pridej nahodnou novou polozku
                new_item = random.choice(new_items)
                self.available_items.append(new_item)
                self.prices[new_item] = self._get_base_price(new_item) + random.randint(-50, 50)
                self.goods[new_item] = random.randint(5, 30)  # Pocet dostupnych kusu

    def _generate_prices(self):
        prices = {}
        base_prices = {
            "Minerály": {"base": 80, "variance": 40, "multiplier": 1.0},
            "Zbraně": {"base": 400, "variance": 200, "multiplier": 1.2},
            "Potraviny": {"base": 80, "variance": 40, "multiplier": 0.8},
            "Technologie": {"base": 600, "variance": 300, "multiplier": 1.5},
            "Léky": {"base": 200, "variance": 100, "multiplier": 1.1},
            "Luxus": {"base": 800, "variance": 400, "multiplier": 2.0},
            "Komponenty": {"base": 120, "variance": 60, "multiplier": 0.9}
        }
        
        for item, cat in ALL_ITEMS:
            if cat in base_prices:
                price_data = base_prices[cat]
                # Základní cena s náhodnou odchylkou
                base_price = price_data["base"] + random.randint(-price_data["variance"], price_data["variance"])
                # Multiplikátor podle typu stanice
                station_multiplier = {
                    "PLANET": 1.0,
                    "DOCKY": 1.1,
                    "PIRATSKY_KLUB": 1.8,
                    "HI_TECH_LAB": 1.3,
                    "OBCHODNI_STANICE": 0.9
                }.get(self.station_type, 1.0)
                
                # Výpočet finální ceny
                final_price = int(base_price * price_data["multiplier"] * station_multiplier)
                # Omezení rozumného rozsahu
                final_price = max(20, min(10000, final_price))
                prices[item] = final_price
            else:
                prices[item] = random.randint(100, 1000)
        
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
        import time
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
                    self.prices[item] = int(self.prices[item] * 1.1)
                # Pokud byl item nedavno prodan, cena klesla
                elif self.trade_history[item] < 0:
                    self.prices[item] = int(self.prices[item] * 0.9)
                
                # Omezeni rozsahu ceny
                base_price = self._get_base_price(item)
                self.prices[item] = max(int(base_price * 0.5), min(int(base_price * 3.0), self.prices[item]))
            
            # Postupne vraceni puvodni ceny
            base_price = self._get_base_price(item)
            if self.prices[item] > base_price:
                self.prices[item] = int(self.prices[item] * 0.99)
            elif self.prices[item] < base_price:
                self.prices[item] = int(self.prices[item] * 1.01)
        
        # Reset historie
        self.trade_history.clear()
    
    def _get_base_price(self, item):
        """Ziskani zakladni ceny polozky"""
        base_prices = {
            "Minerály": 80,
            "Zbraně": 400,
            "Potraviny": 80,
            "Technologie": 600,
            "Léky": 200,
            "Luxus": 800,
            "Komponenty": 120
        }
        category = next((cat for cat, items in ITEM_CATEGORIES.items() if item in items), "Neznámé")
        return base_prices.get(category, 100)
    
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
        self.name = "Havirov Ranger"
        self.thrust_power = 0.08
        self.max_speed = 4.0
        self.rotation_speed = 0.05
        self.docked_at = None
        self.auto_pilot = False
        self.drag = 0.96
        self.last_shot = 0
        self.shoot_delay = 15

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
        if self.shield < self.max_shield:
            self.shield = min(self.shield + 0.03, self.max_shield)

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

    def add_cargo(self, item, amount):
        current = self.cargo.get(item, 0)
        if current + amount <= self.max_cargo:
            self.cargo[item] = current + amount
            return True
        return False

    def remove_cargo(self, item, amount):
        current = self.cargo.get(item, 0)
        if current >= amount:
            self.cargo[item] = current - amount
            if self.cargo[item] == 0:
                del self.cargo[item]
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
        self.radar_range = 500  # Omezeny radar videni
        self.target_direction = random.uniform(0, 2 * math.pi)
        self.direction_change_timer = random.randint(60, 180)

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
        if dist <= self.radar_range:
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
        
        # Strelba pouze pokud je hrac blizko a v radarovem dosahu
        if dist < 250 and dist <= self.radar_range and self.shoot_timer <= 0:
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
        if dist <= self.radar_range:  # Zobrazeni pouze v omezenem radarovem dosahu
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
        self.camera_x = 1000
        self.camera_y = 1000
        self.zoom = 1.0
        self.planets = self._generate_galaxy()
        self.player_ship = Ship(1000, 1000)
        self.enemies = self._generate_enemies()
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
             "amount": 5, "from": "Zeme", "to": "Mars", "reward": 500},
            {"name": "Sber rudy v sektoru", "type": "collect", "item": "Ruda",
             "amount": 20, "reward": 300},
            {"name": "Znic piratske lodi", "type": "kill", "amount": 3, "reward": 800},
            {"name": "Doruc potraviny na Faeganu", "type": "deliver", "item": "Potraviny",
             "amount": 10, "from": "Nova Zeme", "to": "Faegana", "reward": 400},
            {"name": "Doruc technologie na Pelengii", "type": "deliver", "item": "Technologie",
             "amount": 8, "from": "Hlavni Doky", "to": "Pelengia", "reward": 600},
            {"name": "Doruc leky na Gaalos", "type": "deliver", "item": "Leky",
             "amount": 12, "from": "Hi-Tech Lab", "to": "Gaalos", "reward": 550},
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
                if self.state == "TRADING" and self.docked_planet:
                    # Scrollovani v obchodovani
                    max_scroll = max(0, len(self.docked_planet.available_items) - 10)
                    max_cargo_scroll = max(0, len(self.player_ship.cargo) - 8)
                    
                    # Scrollovani pro nákup
                    if max_scroll > 0:
                        self.trading_scroll = max(0, min(max_scroll, self.trading_scroll - event.y))
                    
                    # Scrollovani pro prodej
                    if max_cargo_scroll > 0:
                        self.cargo_scroll = max(0, min(max_cargo_scroll, self.cargo_scroll - event.y))
            elif event.type == pygame.MOUSEWHEEL:
                if self.state == "MAP":
                    self.map_zoom *= (1.1 if event.y > 0 else 0.9)
                    self.map_zoom = max(0.1, min(2.0, self.map_zoom))
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
                    self.player_ship.fuel = max(0, self.player_ship.fuel - 0.05)
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
                self.show_message(f"Wallet nacten! Zustatek: {self.credits} HVC", 180)
                self.state = "GAME"
            elif event.key == pygame.K_3:
                self.state = "CREDITS"
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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

    def handle_trading_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "DOCKED"
            elif event.key == pygame.K_UP:
                # Scroll nahoru
                self.trading_scroll = max(0, self.trading_scroll - 1)
                self.cargo_scroll = max(0, self.cargo_scroll - 1)
            elif event.key == pygame.K_DOWN:
                # Scroll dolu
                max_scroll = max(0, len(self.docked_planet.available_items) - 10) if self.docked_planet else 0
                max_cargo_scroll = max(0, len(self.player_ship.cargo) - 8)
                self.trading_scroll = min(max_scroll, self.trading_scroll + 1)
                self.cargo_scroll = min(max_cargo_scroll, self.cargo_scroll + 1)
            elif event.key == pygame.K_1:
                self.buy_specific_item("Ruda")
            elif event.key == pygame.K_2:
                self.buy_specific_item("Zbrane")
            elif event.key == pygame.K_3:
                self.buy_specific_item("Potraviny")
            elif event.key == pygame.K_4:
                self.buy_specific_item("Technologie")
            elif event.key == pygame.K_5:
                self.buy_specific_item("Léky")
            elif event.key == pygame.K_6:
                self.buy_specific_item("Krystaly")
            elif event.key == pygame.K_s:
                self.sell_goods()
            elif event.key == pygame.K_7 and "Ruda" in self.player_ship.cargo:
                self.sell_goods("Ruda")
            elif event.key == pygame.K_8 and "Zbrane" in self.player_ship.cargo:
                self.sell_goods("Zbrane")
            elif event.key == pygame.K_9 and "Potraviny" in self.player_ship.cargo:
                self.sell_goods("Potraviny")

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
        
        # Kontrola vsech tlacitek v obchodovani
        for btn in self.clickable_buttons:
            if btn['rect'].collidepoint(x, y):
                if hasattr(btn, 'action'):
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
            # Pokud neni docovany, vratit se do DOCKED modu
            self.state = "DOCKED"
            
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""

    def update_game(self):
        keys = pygame.key.get_pressed()
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
            self.player_ship.fuel = max(0, self.player_ship.fuel - 0.02)
        self.player_ship.update()
        self.camera_x = self.player_ship.x
        self.camera_y = self.player_ship.y
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
            enemy.update(self.player_ship.x, self.player_ship.y)
            if hasattr(enemy, 'should_remove') and enemy.should_remove:
                self.enemies.remove(enemy)
        
        # Generovani novych piratu pro udrzeni hratelnosti
        if len(self.enemies) < 15 and random.random() < 0.01:  # 1% sansa kazdy frame
            x = random.randint(500, 5500)
            y = random.randint(500, 4000)
            self.enemies.append(EnemyShip(x, y, "Pirate"))
        
        self.update_bullets()

    def dock_at_planet(self, planet):
        self.player_ship.docked_at = planet.name
        self.docked_planet = planet
        self.state = "DOCKED"
        self.show_message(f"Automatické dokovani u: {planet.name} ({planet.get_type_name()})")
        self.check_quest_completion(planet)

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
        else:
            self.show_message("Nedostatek kreditu!")

    def buy_specific_item(self, item):
        if not self.docked_planet: 
            self.show_message("Neni vybrana zadna stanice!")
            return
        
        try:
            # Aktualizace pred nakupem
            self.docked_planet.update_prices()
            price = self.docked_planet.prices.get(item, 100)
            
            if price <= 0:
                self.show_message(f"{item} neni k dispozici!")
                return
            
            # Kontrola dostupnosti zbozi
            if item not in self.docked_planet.available_items:
                self.show_message(f"{item} neni v nabidce!")
                return
            
            if self.wallet.subtract_credits(price):
                if self.player_ship.add_cargo(item, 1):
                    self.credits = self.wallet.get_balance()
                    self.docked_planet.record_trade(item, 1)  # Zaznamenani naku
                    self.show_message(f"Koupeno {item} za {price} HVC")
                    
                    # Generovani noveho zbozi pro udrzeni nekonecneho hraní
                    if random.random() < 0.3:  # 30% sansa na nove zbozi
                        self._generate_new_goods()
                else:
                    self.wallet.add_credits(price)
                    self.show_message("Nedostatek mista v nakladu!")
            else:
                self.show_message(f"Nedostatek kreditu! Potreba: {price} HVC")
        except Exception as e:
            print(f"Chyba pri nakupu {item}: {e}")
            self.show_message("Chyba pri nakupe!")

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
                # Aktualizace pred prodejem
                self.docked_planet.update_prices()
                price = self.docked_planet.prices.get(item, 100)
                
                if price <= 0:
                    self.show_message(f"{item} nema cenu!")
                    return
                
                if self.player_ship.remove_cargo(item, 1):
                    self.wallet.add_credits(price)
                    self.credits = self.wallet.get_balance()
                    self.docked_planet.record_trade(item, -1)  # Zaznamenani prodeje
                    self.show_message(f"Prodano {item} za {price} HVC")
                    
                    # Generovani noveho zbozi pro udrzeni nekoncecneho hraní
                    if random.random() < 0.2:  # 20% sansa na nove zbozi
                        self._generate_new_goods()
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
        costs = {"hp": 500, "shield": 400, "speed": 300, "cargo": 600, "fuel": 350}
        cost = costs.get(upgrade_type, 1000)
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
        else:
            self.show_message("Nedostatek kreditu!")

    def upgrade_weapon(self, weapon_name, cost):
        if self.wallet.subtract_credits(cost):
            if weapon_name not in self.player_ship.weapons:
                self.player_ship.weapons.append(weapon_name)
                self.player_ship.shoot_delay = max(5, self.player_ship.shoot_delay - 2)
                self.credits = self.wallet.get_balance()
                self.show_message(f"Zbran {weapon_name} zakoupena!")
        else:
            self.show_message("Nedostatek kreditu!")

    def upgrade_engine(self):
        cost = 800
        if self.wallet.subtract_credits(cost):
            self.player_ship.thrust_power += 0.02
            self.player_ship.max_speed += 0.5
            self.credits = self.wallet.get_balance()
            self.show_message("Motor vylepsen!")

    def upgrade_radar(self):
        global RADAR_RANGE
        cost = 1500
        if self.wallet.subtract_credits(cost):
            RADAR_RANGE = min(3000, RADAR_RANGE + 500)
            self.credits = self.wallet.get_balance()
            self.show_message(f"Radar vylepsen! Rozsah: {RADAR_RANGE}u")

    def open_wallet(self):
        self.wallet.load_wallet()
        self.credits = self.wallet.get_balance()
        self.show_message(f"Havirov Coin Wallet: {self.credits:.4f} HVC")

    def fire_weapon(self):
        if self.player_ship.last_shot > 0: return
        self.player_ship.last_shot = self.player_ship.shoot_delay
        bullet = {
            'x': self.player_ship.x + math.cos(self.player_ship.direction) * 20,
            'y': self.player_ship.y + math.sin(self.player_ship.direction) * 20,
            'vx': math.cos(self.player_ship.direction) * 8,
            'vy': math.sin(self.player_ship.direction) * 8,
            'life': 60
        }
        self.bullets.append(bullet)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['life'] -= 1
            if bullet['life'] <= 0:
                self.bullets.remove(bullet)
                continue
            for enemy in self.enemies[:]:
                dist = math.sqrt((bullet['x'] - enemy.x)**2 + (bullet['y'] - enemy.y)**2)
                if dist < enemy.size:
                    enemy.hp -= 25
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        self.player_ship.xp += 50
                        if self.player_ship.xp >= self.player_ship.xp_to_level:
                            self.player_ship.level += 1
                            self.player_ship.xp = 0
                            self.player_ship.xp_to_level *= 1.5
                            self.show_message(f"Level up! Nyni level {self.player_ship.level}")
                        if self.current_quest and self.current_quest['type'] == 'kill':
                            self.quest_progress['kill'] += 1
                            # Zobrazi aktualni progress
                            remaining = self.current_quest['amount'] - self.quest_progress['kill']
                            if remaining > 0:
                                self.show_message(f"Zbyva {remaining} piratskych lodi", 60)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

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
        if self.message:
            self.draw_message()
        pygame.display.flip()

    def draw_message(self):
        text = self.font_medium.render(self.message, True, BRIGHT_YELLOW)
        bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - text.get_width() // 2 - 15, 45, text.get_width() + 30, text.get_height() + 10)
        pygame.draw.rect(self.screen, (0,0,0,200), bg_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, bg_rect, 2)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))

    def draw_radar(self):
        radar_x, radar_y = RADAR_POS
        radar_surface = pygame.Surface((RADAR_SIZE, RADAR_SIZE), pygame.SRCALPHA)
        radar_surface.fill((5,5,20,200))
        self.screen.blit(radar_surface, (radar_x, radar_y))
        pygame.draw.rect(self.screen, BORDER_COLOR, (radar_x, radar_y, RADAR_SIZE, RADAR_SIZE), 2)
        title = self.font_tiny.render("RADAR 1500u", True, CYAN)
        self.screen.blit(title, (radar_x + 5, radar_y + 5))
        radar_scale = (RADAR_SIZE // 2) / RADAR_RANGE
        for r in [250, 500, 750, 1000, 1500]:
            scaled_r = int(r * radar_scale)
            pygame.draw.circle(self.screen, (30,30,50), (radar_x + RADAR_SIZE // 2, radar_y + RADAR_SIZE // 2), scaled_r, 1)
        for planet in self.planets:
            planet.draw_on_radar(self.screen, radar_x, radar_y, radar_scale, self.player_ship.x, self.player_ship.y)
        for enemy in self.enemies:
            enemy.draw_on_radar(self.screen, radar_x, radar_y, radar_scale, self.player_ship.x, self.player_ship.y)
        self.player_ship.draw_on_radar(self.screen, radar_x, radar_y, radar_scale)
        legend_y = radar_y + RADAR_SIZE + 10
        legend_items = [
            ("[M] Mapa", BRIGHT_YELLOW),
            ("[F] Palivo", FUEL_COLOR),
            ("[Q] Ukoly", CYAN),
            ("[U] Upgrade", BRIGHT_BLUE),
            ("[SPACE] Strelba", BRIGHT_RED),
            ("[Klik] Pohyb", GREEN)
        ]
        for i, (text, color) in enumerate(legend_items):
            rendered = self.font_tiny.render(text, True, color)
            self.screen.blit(rendered, (radar_x, legend_y + i * 16))

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
        
        # Strelby s efektem
        for bullet in self.bullets:
            screen_x = int((bullet['x'] - self.camera_x) * self.zoom + SCREEN_WIDTH // 2)
            screen_y = int((bullet['y'] - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2)
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                # Efekt strelby
                bullet_trail = int(5 * self.zoom)
                pygame.draw.circle(self.screen, (255, 255, 100), (screen_x, screen_y), max(2, int(3 * self.zoom)))
                pygame.draw.circle(self.screen, (255, 255, 200), (screen_x, screen_y), max(1, int(2 * self.zoom)))
        
        # Hracova lod
        self.player_ship.draw_in_space(self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.zoom)
        
        # Shield efekt
        if self.player_ship.shield > 0:
            shield_alpha = int(50 * (self.player_ship.shield / self.player_ship.max_shield))
            shield_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha), (30, 30), 25)
            self.screen.blit(shield_surface, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30))
        
        # UI panely
        self.draw_top_panel()
        self.draw_game_controls()
        self.draw_radar()
        
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
        options = ["[T] Obchodovani", "[Q] Ukoly", "[U] Vylepseni lode", "[F] Nakup paliva", "[ESC] Odlet"]
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
        
        mini_radar_scale = radar_mini_size / (2 * RADAR_RANGE)
        for enemy in self.enemies:
            rel_x = enemy.x - self.player_ship.x
            rel_y = enemy.y - self.player_ship.y
            dist = math.sqrt(rel_x**2 + rel_y**2)
            if dist <= RADAR_RANGE:
                mini_x = radar_mini_x + radar_mini_size // 2 + int(rel_x * mini_radar_scale)
                mini_y = radar_mini_y + radar_mini_size // 2 + int(rel_y * mini_radar_scale)
                pygame.draw.circle(self.screen, BRIGHT_RED, (mini_x, mini_y), 1)

    def draw_trading(self):
        # Kontrola zda je hrac opravdu docovany
        if not self.docked_planet:
            self.state = "DOCKED"
            return
            
        self.draw_docked()
        self.clickable_buttons = []
        
        # Inicializace scrollu
        if not hasattr(self, 'trading_scroll'):
            self.trading_scroll = 0
        if not hasattr(self, 'cargo_scroll'):
            self.cargo_scroll = 0
        
        # Vylepsene okno obchodovani
        overlay_width = 900
        overlay_height = 650
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((10,10,40,245))
        self.screen.blit(overlay, (SCREEN_WIDTH // 2 - overlay_width // 2, SCREEN_HEIGHT // 2 - overlay_height // 2))
        pygame.draw.rect(self.screen, BORDER_COLOR, (SCREEN_WIDTH // 2 - overlay_width // 2, SCREEN_HEIGHT // 2 - overlay_height // 2, overlay_width, overlay_height), 3)
        
        # Titulek s informacemi o planete
        title = self.font_large.render(f"OBCHODNI CENTRUM - {self.docked_planet.name}", True, BRIGHT_YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - overlay_height // 2 + 15))
        
        # Typ stanice s ikonkou
        station_type = self.docked_planet.get_type_name()
        type_colors = {
            "Planeta": GREEN,
            "Doky": BLUE,
            "Piratsky klub": RED,
            "Hi-Tech Lab": CYAN,
            "Obchodni stanice": YELLOW
        }
        type_color = type_colors.get(station_type, WHITE)
        
        # Ikonka stanice
        icon_size = 20
        icon_x = SCREEN_WIDTH // 2 - overlay_width // 2 + 25
        icon_y = SCREEN_HEIGHT // 2 - overlay_height // 2 + 55
        pygame.draw.circle(self.screen, type_color, (icon_x, icon_y), icon_size // 2)
        
        type_text = self.font_small.render(f"Typ: {station_type}", True, type_color)
        self.screen.blit(type_text, (icon_x + 15, icon_y - 8))
        
        # Obchodni informace
        info_texts = {
            "Piratsky klub": "Ceny vyssi, ale ruzne zbrane a luxusni zbozi",
            "Hi-Tech Lab": "Vysokotechnologicke zbozi a specialni predmety",
            "Obchodni stanice": "Vsechno mozne, dobre ceny",
            "Planeta": "Standardni nabidka planetarnich surovin",
            "Doky": "Lodni vybaveni a technologicke komponenty"
        }
        info_text = self.font_tiny.render(info_texts.get(station_type, "Standardni nabidka"), True, type_color)
        self.screen.blit(info_text, (SCREEN_WIDTH // 2 - overlay_width // 2 + 25, icon_y + 15))
        
        # Oddelovaci cara
        pygame.draw.line(self.screen, BORDER_COLOR, 
                        (SCREEN_WIDTH // 2 - overlay_width // 2 + 20, SCREEN_HEIGHT // 2 - overlay_height // 2 + 100),
                        (SCREEN_WIDTH // 2 + overlay_width // 2 - 20, SCREEN_HEIGHT // 2 - overlay_height // 2 + 100), 2)
        
        # NAKUPNI CAST
        buy_title = self.font_medium.render("NAKUP", True, BRIGHT_GREEN)
        self.screen.blit(buy_title, (SCREEN_WIDTH // 2 - overlay_width // 2 + 30, SCREEN_HEIGHT // 2 - overlay_height // 2 + 120))
        
        # Scroll pro nákup
        scroll_offset = getattr(self, 'trading_scroll', 0)
        max_scroll = max(0, len(self.docked_planet.available_items) - 10) if self.docked_planet else 0
        
        if self.docked_planet:
            # Zobrazeni pouze polozek v okne s scroll
            visible_items = self.docked_planet.available_items[scroll_offset:scroll_offset + 10]
            
            for i, item in enumerate(visible_items):
                actual_index = scroll_offset + i
                price = self.docked_planet.prices.get(item, 100)
                category = next((cat for cat, items in ITEM_CATEGORIES.items() if item in items), "Neznámé")
                available = self.docked_planet.goods.get(item, 0)
                
                # Barva podle kategorie
                category_colors = {
                    "Minerály": (150, 120, 80),
                    "Zbraně": (200, 80, 80),
                    "Potraviny": (80, 180, 80),
                    "Technologie": (80, 120, 200),
                    "Léky": (80, 180, 180),
                    "Luxus": (200, 150, 80),
                    "Komponenty": (120, 120, 120)
                }
                category_color = category_colors.get(category, (120, 120, 120))
                
                # Pozadi polozky
                btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - overlay_width // 2 + 30, 
                                     SCREEN_HEIGHT // 2 - overlay_height // 2 + 150 + i * 40, 
                                     overlay_width - 120, 36)
                
                # Stav pozadi (hover efekt)
                mouse_over = any(btn['rect'] == btn_rect for btn in self.clickable_buttons if hasattr(btn, 'hover'))
                bg_color = (30, 30, 50) if mouse_over else (20, 20, 40)
                pygame.draw.rect(self.screen, bg_color, btn_rect)
                pygame.draw.rect(self.screen, category_color, btn_rect, 1)
                
                # Text informace
                item_text = self.font_small.render(f"{item}", True, WHITE)
                self.screen.blit(item_text, (btn_rect.x + 12, btn_rect.y + 8))
                
                # Kategorie a dostupnost
                cat_text = self.font_tiny.render(f"[{category}] {available}ks", True, category_color)
                self.screen.blit(cat_text, (btn_rect.x + 220, btn_rect.y + 10))
                
                # Cena s trendem
                price_color = GREEN if price < 500 else YELLOW if price < 1000 else RED
                price_text = self.font_small.render(f"{price} HVC", True, price_color)
                self.screen.blit(price_text, (btn_rect.x + 380, btn_rect.y + 8))
                
                # Tlacidlo pro koupi
                buy_btn_rect = pygame.Rect(btn_rect.x + btn_rect.width - 90, btn_rect.y, 85, 32)
                btn_bg_color = (0, 120, 0) if mouse_over else (0, 100, 0)
                pygame.draw.rect(self.screen, btn_bg_color, buy_btn_rect)
                pygame.draw.rect(self.screen, GREEN, buy_btn_rect, 1)
                buy_text = self.font_tiny.render("Koupit", True, WHITE)
                self.screen.blit(buy_text, (buy_btn_rect.x + 25, buy_btn_rect.y + 6))
                
                # Vytvoreni akce pro koupi
                def buy_action(item=item):
                    self.buy_specific_item(item)
                
                self.clickable_buttons.append({
                    'rect': buy_btn_rect, 
                    'action': buy_action,
                    'hover': btn_rect
                })
            
            # Scroll bar pro nabidku
            if max_scroll > 0:
                scroll_bar_height = 400
                scroll_bar_y = SCREEN_HEIGHT // 2 - overlay_height // 2 + 150
                scroll_bar_rect = pygame.Rect(SCREEN_WIDTH // 2 + overlay_width // 2 - 25, scroll_bar_y, 10, scroll_bar_height)
                pygame.draw.rect(self.screen, (60,60,60), scroll_bar_rect)
                scroll_pos = int((scroll_offset / max_scroll) * scroll_bar_height)
                scroll_handle_rect = pygame.Rect(SCREEN_WIDTH // 2 + overlay_width // 2 - 25, scroll_bar_y + scroll_pos - 5, 10, 10)
                pygame.draw.rect(self.screen, type_color, scroll_handle_rect)
        
        # PRODEJNI CAST
        sell_title = self.font_medium.render("PRODEJ", True, BRIGHT_RED)
        self.screen.blit(sell_title, (SCREEN_WIDTH // 2 - overlay_width // 2 + 30, SCREEN_HEIGHT // 2 - overlay_height // 2 + 380))
        
        # Scroll pro prodej
        cargo_scroll = getattr(self, 'cargo_scroll', 0)
        max_cargo_scroll = max(0, len(self.player_ship.cargo) - 8)
        visible_cargo = list(self.player_ship.cargo.items())[cargo_scroll:cargo_scroll + 8]
        
        if visible_cargo:
            for i, (item, amount) in enumerate(visible_cargo):
                actual_index = cargo_scroll + i
                price = self.docked_planet.prices.get(item, 100)
                category = next((cat for cat, items in ITEM_CATEGORIES.items() if item in items), "Neznámé")
                
                # Pozadi polozky
                btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - overlay_width // 2 + 30, 
                                     SCREEN_HEIGHT // 2 - overlay_height // 2 + 410 + i * 40, 
                                     overlay_width - 120, 36)
                
                # Stav pozadi (hover efekt)
                mouse_over = any(btn['rect'] == btn_rect for btn in self.clickable_buttons if hasattr(btn, 'hover'))
                bg_color = (50, 30, 30) if mouse_over else (40, 20, 20)
                pygame.draw.rect(self.screen, bg_color, btn_rect)
                pygame.draw.rect(self.screen, (150, 80, 80), btn_rect, 1)
                
                # Text informace
                item_text = self.font_small.render(f"{item} ({amount}x)", True, WHITE)
                self.screen.blit(item_text, (btn_rect.x + 12, btn_rect.y + 8))
                
                # Kategorie
                cat_text = self.font_tiny.render(f"[{category}]", True, (150, 100, 100))
                self.screen.blit(cat_text, (btn_rect.x + 220, btn_rect.y + 10))
                
                # Cena
                total_price = price * amount
                price_color = GREEN if total_price < 1000 else YELLOW if total_price < 3000 else RED
                price_text = self.font_small.render(f"{total_price} HVC", True, price_color)
                self.screen.blit(price_text, (btn_rect.x + 380, btn_rect.y + 8))
                
                # Tlacidlo pro prodej
                sell_btn_rect = pygame.Rect(btn_rect.x + btn_rect.width - 90, btn_rect.y, 85, 32)
                btn_bg_color = (120, 0, 0) if mouse_over else (100, 0, 0)
                pygame.draw.rect(self.screen, btn_bg_color, sell_btn_rect)
                pygame.draw.rect(self.screen, RED, sell_btn_rect, 1)
                sell_text = self.font_tiny.render("Prodat", True, WHITE)
                self.screen.blit(sell_text, (sell_btn_rect.x + 25, sell_btn_rect.y + 6))
                
                # Vytvoreni akce pro prodej
                def sell_action(item=item):
                    self.sell_goods(item)
                
                self.clickable_buttons.append({
                    'rect': sell_btn_rect, 
                    'action': sell_action,
                    'hover': btn_rect
                })
            
            # Scroll bar pro naklad
            if max_cargo_scroll > 0:
                cargo_scroll_bar_height = 320
                cargo_scroll_bar_y = SCREEN_HEIGHT // 2 - overlay_height // 2 + 410
                cargo_scroll_bar_rect = pygame.Rect(SCREEN_WIDTH // 2 + overlay_width // 2 - 25, cargo_scroll_bar_y, 10, cargo_scroll_bar_height)
                pygame.draw.rect(self.screen, (60,60,60), cargo_scroll_bar_rect)
                cargo_scroll_pos = int((cargo_scroll / max_cargo_scroll) * cargo_scroll_bar_height)
                cargo_scroll_handle_rect = pygame.Rect(SCREEN_WIDTH // 2 + overlay_width // 2 - 25, cargo_scroll_bar_y + cargo_scroll_pos - 5, 10, 10)
                pygame.draw.rect(self.screen, RED, cargo_scroll_handle_rect)
        else:
            no_cargo_text = self.font_small.render("Nemate zadny naklad", True, GRAY)
            self.screen.blit(no_cargo_text, (SCREEN_WIDTH // 2 - overlay_width // 2 + 30, SCREEN_HEIGHT // 2 - overlay_height // 2 + 420))
        
        # Zpet tlacidlo
        back_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + overlay_height // 2 - 60, 140, 40)
        pygame.draw.rect(self.screen, (80,80,80), back_btn_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, back_btn_rect, 2)
        back_text = self.font_medium.render("[ESC] Zpet do stanice", True, WHITE)
        self.screen.blit(back_text, (back_btn_rect.x + 15, back_btn_rect.y + 8))
        self.clickable_buttons.append({'rect': back_btn_rect, 'action': lambda: setattr(self, 'state', 'DOCKED')})
        
        # Informace o kreditu
        credits_text = self.font_medium.render(f"Vase kredity: {self.credits:.2f} HVC", True, BRIGHT_GREEN)
        self.screen.blit(credits_text, (SCREEN_WIDTH // 2 - overlay_width // 2 + 30, SCREEN_HEIGHT // 2 + overlay_height // 2 - 90))

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
            ("Radar+ (+" + str(RADAR_RANGE) + ")", 1500, "radar", "Zvysi radarovy dosah")
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
        if self.player_ship.docked_at:
            docked_text = self.font_tiny.render(f"Docked at: {self.player_ship.docked_at}", True, YELLOW)
            self.screen.blit(docked_text, (770,40))
        else:
            status_text = self.font_tiny.render("In flight", True, GREEN)
            self.screen.blit(status_text, (770,40))

    def draw_game_controls(self):
        controls = ["[M] Mapa", "[F] Palivo", "[Q] Ukoly", "[U] Vylepseni", "[SPACE] Strelba", "[ESC] Menu"]
        for i, text in enumerate(controls):
            rendered = self.font_tiny.render(text, True, BRIGHT_YELLOW)
            self.screen.blit(rendered, (SCREEN_WIDTH - 150, 10 + i * 20))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SpaceRangersGame()
    game.run()

