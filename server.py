"""Space Rangers - Multiplayer Server"""
import socket
import threading
import pickle
import time
import random
import math

SERVER_PORT = 5555
PLAYER_TIMEOUT = 15
BULLET_SPEED = 8
BULLET_LIFE = 60
BULLET_DAMAGE = 25

BULLET_COOLDOWN = {}  # player_id -> last_shot_time

class PlayerData:
    def __init__(self, conn, addr, name, player_id):
        self.conn = conn
        self.addr = addr
        self.name = name
        self.player_id = player_id
        self.x = random.randint(500, 5500)
        self.y = random.randint(500, 4000)
        self.vx = 0.0
        self.vy = 0.0
        self.direction = random.uniform(0, 2 * math.pi)
        self.hp = 100
        self.max_hp = 100
        self.shield = 50
        self.max_shield = 50
        self.last_update = time.time()
        self.alive = True

class ServerBullet:
    def __init__(self, x, y, vx, vy, owner_id):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner_id = owner_id
        self.life = BULLET_LIFE

class GameServer:
    def __init__(self, host="0.0.0.0", port=SERVER_PORT):
        self.host = host
        self.port = port
        self.players = {}
        self.bullets = []
        self.next_id = 1
        self.lock = threading.Lock()
        self.running = True

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(8)
            print(f"[SERVER] Bezi na {self.host}:{self.port}")
            print(f"[SERVER] Max hracu: 8")
        except Exception as e:
            print(f"[CHYBA] Nelze nastartovat server: {e}")
            return

        threading.Thread(target=self.game_loop, daemon=True).start()
        threading.Thread(target=self.cleanup_thread, daemon=True).start()

        while self.running:
            try:
                conn, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except:
                break

    def game_loop(self):
        while self.running:
            time.sleep(0.05)
            with self.lock:
                self.update_bullets()
                self.broadcast_states()

    def broadcast_states(self):
        if not self.players:
            return
        players_data = []
        for pid, p in self.players.items():
            players_data.append({
                "id": pid,
                "name": p.name,
                "x": p.x, "y": p.y,
                "vx": p.vx, "vy": p.vy,
                "direction": p.direction,
                "hp": p.hp,
                "shield": p.shield
            })
        self.broadcast({"type": "state_update", "players": players_data})

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.x += bullet.vx
            bullet.y += bullet.vy
            bullet.life -= 1

            hit = False
            for pid, p in self.players.items():
                if pid == bullet.owner_id:
                    continue
                dist = math.sqrt((bullet.x - p.x)**2 + (bullet.y - p.y)**2)
                if dist < 16 and p.alive:
                    damage = BULLET_DAMAGE
                    if p.shield > 0:
                        shield_dmg = min(p.shield, damage)
                        p.shield -= shield_dmg
                        damage -= shield_dmg
                    p.hp = max(0, p.hp - damage)
                    if p.hp <= 0:
                        p.alive = False
                    hit = True
                    try:
                        p.conn.sendall(pickle.dumps({
                            "type": "damage",
                            "damage": BULLET_DAMAGE,
                            "attacker": bullet.owner_id,
                            "hp": p.hp,
                            "shield": p.shield
                        }))
                    except:
                        pass
                    try:
                        attacker = self.players.get(bullet.owner_id)
                        if attacker:
                            attacker.conn.sendall(pickle.dumps({
                                "type": "hit",
                                "target": pid,
                                "hp": p.hp
                            }))
                    except:
                        pass
                    break

            if hit or bullet.life <= 0:
                self.bullets.remove(bullet)

    def cleanup_thread(self):
        while self.running:
            time.sleep(2)
            with self.lock:
                now = time.time()
                dead = [pid for pid, p in self.players.items()
                        if now - p.last_update > PLAYER_TIMEOUT]
                for pid in dead:
                    print(f"[ODPOJEN] {self.players[pid].name} (timeout)")
                    del self.players[pid]
                    self.broadcast({"type": "player_left", "player_id": pid})
                for pid, p in list(self.players.items()):
                    if not p.alive and now - p.last_update > 5:
                        p.x = random.randint(500, 5500)
                        p.y = random.randint(500, 4000)
                        p.hp = p.max_hp
                        p.shield = p.max_shield
                        p.alive = True
                        try:
                            p.conn.sendall(pickle.dumps({"type": "respawn", "x": p.x, "y": p.y}))
                        except:
                            pass

    def handle_client(self, conn, addr):
        print(f"[PRIPOJEN] {addr}")
        try:
            data = conn.recv(4096)
            if not data:
                return
            msg = pickle.loads(data)
            if msg.get("type") != "join":
                return
            name = msg.get("name", f"Hrac{random.randint(100,999)}")
            with self.lock:
                pid = self.next_id
                self.next_id += 1
                player = PlayerData(conn, addr, name, pid)
                self.players[pid] = player
            conn.sendall(pickle.dumps({
                "type": "welcome",
                "player_id": pid,
                "x": player.x,
                "y": player.y
            }))
            self.broadcast({
                "type": "player_joined",
                "player_id": pid,
                "name": name,
                "x": player.x,
                "y": player.y
            }, exclude=pid)
            print(f"[PRIPOJEN] {name} (ID:{pid}) - Hracu: {len(self.players)}")
        except Exception as e:
            print(f"[CHYBA] {addr}: {e}")
            return

        while self.running:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                msg = pickle.loads(data)
                self.handle_message(pid, msg)
            except:
                break

        with self.lock:
            if pid in self.players:
                name = self.players[pid].name
                print(f"[ODPOJEN] {name} (ID:{pid})")
                del self.players[pid]
                self.broadcast({"type": "player_left", "player_id": pid})
        conn.close()

    def handle_message(self, pid, msg):
        with self.lock:
            p = self.players.get(pid)
            if not p:
                return
            t = msg.get("type")
            if t == "state":
                p.x = msg.get("x", p.x)
                p.y = msg.get("y", p.y)
                p.vx = msg.get("vx", p.vx)
                p.vy = msg.get("vy", p.vy)
                p.direction = msg.get("direction", p.direction)
                p.last_update = time.time()
            elif t == "shoot":
                bx = msg.get("bx", p.x)
                by = msg.get("by", p.y)
                bvx = msg.get("bvx", 0)
                bvy = msg.get("bvy", 0)
                self.bullets.append(ServerBullet(bx, by, bvx, bvy, pid))

    def broadcast(self, data, exclude=None):
        for pid, p in list(self.players.items()):
            if pid == exclude:
                continue
            try:
                p.conn.sendall(pickle.dumps(data))
            except:
                pass

    def stop(self):
        self.running = False
        try:
            self.server.close()
        except:
            pass

if __name__ == "__main__":
    print("=== Space Rangers Multiplayer Server ===")
    print("Zadej port (ENTER pro 5555): ", end="")
    port_input = input().strip()
    port = int(port_input) if port_input else SERVER_PORT
    server = GameServer(port=port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Vypinam...")
        server.stop()
