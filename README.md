# Space Rangers - Havirov Coin Edition

Space Rangers je česká vesmírná obchodní a bojová hra s otevřeným světem postavená v Pythonu s knihovnou Pygame. Hra integruje reálný Havirov Coin mining přes CPUMiner.

## O hře

Space Rangers je simulátor kosmického obchodníka a dobrodruha. Hráči prozkoumávají galaxii, obchodují s komoditami, bojují proti pirátům, těží Havirov Coin přímo v reálném čase a plní questy.

## Hlavní rysy

### Herní mechaniky
- **Obchodování**: Nákup a prodej komodit mezi planetami v přehledném dvousloupcovém rozhraní
- **Bojový systém**: Bojujte proti pirátům, kteří po smrti pouští náhodné předměty k sebrání
- **Loot systém**: Klávesou J seberte předměty po pirátech přímo do nákladového prostoru
- **Questy**: Plňte mise pro zisk odměn v Havirov Coinech
- **Vylepšování lodě**: Zvyšte schopnosti své lodi pomocí vylepšení
- **Mapa galaxie**: Prozkoumejte rozsáhlou galaxii s různými planetami a stanicemi

### Reálný CPU Mining
- Integrace s reálným **HVR-RandomHash** algoritmem z Havirov-Coin mineru
- Těžba probíhá na pozadí v samostatném vlákně, hash rate se zobrazuje živě
- **PPS (Pay-Per-Share)**: Každý nalezený share se okamžitě připisuje k balanci
- Dynamické přizpůsobování difficulty podle výkonu sítě
- Těžba běží 1 vlákno, aby nezatěžovala celé CPU
- Wallet balance se aktualizuje v reálném čase při každém shareu

### Planety a stanice
- **Různé typy stanic**: Planety, doky, pirátské kluby, hi-tech laboratoře, obchodní stanice
- **Dynamické ceny**: Ceny se mění na základě poptávky a nabídky
- **500+ položek**: Každá stanice nabízí jiné zboží podle svého typu

### Quest systém
- **Dodávky**: Dovážejte zboží mezi planetami
- **Sběr**: Sbírejte suroviny v galaxii
- **Bojové mise**: Zničte pirátské lodě

## Ovládání

### Ve vesmíru
| Klávesa | Akce |
|---------|------|
| `WASD` / `Šipky` | Ovládání lodi |
| `Levý klik` | Let na pozici |
| `Pravý klik` | Střelba |
| `Mezerník` | Střelba (alternativa) |
| `M` | Otevření mapy galaxie |
| `F` | Nákup paliva |
| `Q` | Otevření questů |
| `U` | Vylepšování lodi |
| `K` | Start / Stop mining |
| `J` | Sebrání předmětů z vesmíru do nákladu |
| `L` | Mining statistika a historie |
| `B` | Otevření walletu |
| `C` | Kredity |
| `ESC` | Menu |

### Při dokování
| Klávesa | Akce |
|---------|------|
| `T` | Obchodování |
| `F` | Nákup paliva |
| `Q` | Questy |
| `U` | Vylepšení |
| `K` | Mining |
| `ESC` | Odlet |

### Obchodování
- **Kliknutím** na položku v levém sloupci koupíte, v pravém prodáte
- Položky bez skladových zásob jsou zobrazeny šedě

### Mapa
- **Kolečko myši** — Zoom
- **Levý klik + tažení** — Posun mapy
- **Klik na planetu** — Teleport (za poplatek v HVC)

## Instalace a spuštění

### Požadavky
- Python 3.7+
- Pygame
- Havirov-Coin miner (součástí je CPUMiner)

### Instalace

```bash
git clone https://github.com/davidprosek91-cze/Space-Rangers.git
cd Space-Rangers

pip install pygame
```

Hra vyžaduje Havirov-Coin miner ve složce `~/Downloads/Havirov-Coin-master/` s walletem `wallet.dat`.

### Spuštění

```bash
python space_rangers.py
```

Hlavní menu nabízí:
- **[1] Nová hra** — vytvoří nový wallet a začnete jako Ranger
- **[2] Načíst hru** — načte existující wallet
- **[4] Start Mining** — rovnou spustí těžbu

## Herní ekonomika

### Komodity (500+ položek)
- **Minerály**: Ruda, zlato, stříbro, platina, křemík, atd.
- **Zbraně**: Lasery, plazmové zbraně, torpéda, ionové blastery
- **Potraviny**: Chléb, maso, ovoce, zelenina, konzervy
- **Technologie**: Čipy, procesory, senzory, AI moduly
- **Léky**: Antibiotika, stimulanty, nanoléky, vakcíny
- **Luxus**: Šperky, umění, víno, kaviár
- **Komponenty**: Motory, převodovky, kabely, filtry

### Mining
- Těžba používá **CPUMiner** s algoritmem HVR-RandomHash
- Share reward: `0.0001 × (difficulty / 6_000_000)` HVC
- Block reward: `19.5 / 2^halving` HVC (halving každých 525 600 bloků)
- Auto-přizpůsobení difficulty každých 10 sekund podle výkonu sítě

## Struktura projektu

```
Space-Rangers/
├── space_rangers.py       # Hlavní herní soubor
├── README.md              # Tento soubor
├── .gitignore
└── wallet.dat             # Havirov Coin wallet data
```

## Technické detaily

- **Pygame**: Herní engine pro 2D grafiku
- **CPUMiner**: Reálný mining algoritmus HVR-RandomHash (SHA256 → SHA512 → SHA256×3)
- **Multi-threading**: Těžba běží v samostatném vlákně, herní smyčka zůstává plynulá
- **Dynamický svět**: Ceny a zboží se mění v čase
- **Radar**: Dosah 1500 jednotek s detekcí planet, nepřátel i lootu

## Autor

Hra vytvořena pro Space Rangers komunitu s integrací Havirov Coin systému.
