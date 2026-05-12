"""Space Rangers - Network Client"""
import socket
import pickle
import threading
import time
import random

SHIP_NAMES = [
    "Kosmický Drak", "Hvězdný Poutník", "Galaktický Běžec",
    "Nebula Runner", "Void Walker", "Star Reaper",
    "Mléčný Střelec", "Orbitální Lovec", "Hyperion",
    "Andromeda", "Sirius", "Vega Star",
    "Temný Korzár", "Vesmírný Šílenec", "Kometa smrti",
    "Hvězda Severu", "Plazmový Duch", "Fotonický Orel",
    "Kosmický Tulák", "Nebula Phantom", "Rychlý Šíp",
    "Havířský Diamant", "Ocelový Jestřáb", "Gravitační Vlk",
    "Světelný Nůž", "Černá Perla", "Solaris",
    "Kvantový Skokan", "Magnetický Střelec", "Pulsar"
]

def get_random_ship_name():
    return random.choice(SHIP_NAMES)

class RemotePlayer:
    def __init__(self, player_id, name, x, y):
        self.player_id = player_id
        self.name = name
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.direction = 0.0
        self.hp = 100
        self.max_hp = 100
        self.shield = 50
        self.max_shield = 50
        self.last_update = time.time()

class NetworkClient:
    def __init__(self):
        self.socket = None
        self.player_id = None
        self.players = {}
        self.name = get_random_ship_name()
        self.server_ip = None
        self.server_port = 5555
        self.connected = False
        self.lock = threading.Lock()
        self.running = False
        self.recv_thread = None
        self.send_thread = None
        self.last_state_send = 0
        self.event_queue = []

    def connect(self, ip, port=5555):
        self.server_ip = ip
        self.server_port = port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((ip, port))
            self.socket.settimeout(None)
            self.socket.sendall(pickle.dumps({
                "type": "join",
                "name": self.name
            }))
            data = self.socket.recv(4096)
            msg = pickle.loads(data)
            if msg.get("type") == "welcome":
                self.player_id = msg["player_id"]
                self.connected = True
                self.running = True
                self.recv_thread = threading.Thread(target=self.receive_loop, daemon=True)
                self.recv_thread.start()
                return True, msg
            return False, "Neocekavana odpoved serveru"
        except socket.timeout:
            return False, "Timeout - server neodpovida"
        except ConnectionRefusedError:
            return False, "Pripojeni odmítnuto - server neni spusten"
        except Exception as e:
            return False, f"Chyba: {e}"

    def receive_loop(self):
        while self.running and self.socket:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.disconnect()
                    break
                msg = pickle.loads(data)
                with self.lock:
                    self.handle_message(msg)
            except:
                if self.running:
                    self.disconnect()
                break

    def handle_message(self, msg):
        t = msg.get("type")
        if t == "player_joined":
            pid = msg["player_id"]
            if pid not in self.players:
                self.players[pid] = RemotePlayer(
                    pid, msg["name"], msg["x"], msg["y"]
                )
        elif t == "player_left":
            self.players.pop(msg["player_id"], None)
        elif t == "state_update":
            for pdata in msg.get("players", []):
                pid = pdata["id"]
                if pid == self.player_id:
                    continue
                if pid in self.players:
                    p = self.players[pid]
                    p.x = pdata["x"]
                    p.y = pdata["y"]
                    p.vx = pdata["vx"]
                    p.vy = pdata["vy"]
                    p.direction = pdata["direction"]
                    p.hp = pdata["hp"]
                    p.shield = pdata["shield"]
                    p.last_update = time.time()
                else:
                    self.players[pid] = RemotePlayer(
                        pid, pdata.get("name", "Neznamy"), pdata["x"], pdata["y"]
                    )
        elif t == "damage":
            self.event_queue.append(("damage", msg))
        elif t == "hit":
            self.event_queue.append(("hit", msg))
        elif t == "respawn":
            self.event_queue.append(("respawn", msg))

    def send_state(self, x, y, vx, vy, direction, hp, shield):
        if not self.connected or not self.socket:
            return
        try:
            msg = {
                "type": "state",
                "x": x, "y": y, "vx": vx, "vy": vy,
                "direction": direction,
                "hp": hp, "shield": shield
            }
            self.socket.sendall(pickle.dumps(msg))
        except:
            pass

    def send_shoot(self, bx, by, bvx, bvy):
        if not self.connected or not self.socket:
            return
        try:
            self.socket.sendall(pickle.dumps({
                "type": "shoot",
                "bx": bx, "by": by,
                "bvx": bvx, "bvy": bvy
            }))
        except:
            pass

    def get_events(self):
        with self.lock:
            events = list(self.event_queue)
            self.event_queue.clear()
            return events

    def get_remote_players(self):
        with self.lock:
            return dict(self.players)

    def disconnect(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
