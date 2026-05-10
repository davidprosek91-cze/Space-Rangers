# Space Rangers - Havirov Coin Edition

**Space Rangers** je太空 obchodní a bojová hra s otevřeným světem postavená v Pythonu s knihovnou Pygame. Hra integruje Havirov Coin pro transakce a nabízí bohatý herní zážitek plný dobrodružství v galaxii.

## O hře

Space Rangers je simulátor kosmického obchodníka a dobrodruha, kde hráči prozkoumávají galaxii, obchodují s různými komoditami, bojují proti pirátům a plní questy. Hra kombinuje prvky obchodní simulace s akčními boji v reálném čase.

## Hlavní rysy

### 🚀 Herní mechaniky
- **Obchodování**: Kupte a prodávejte různé komodity mezi planetami
- **Bojový systém**: Bojujte proti pirátům a ochraňujte své zboží
- **Questy**: Plňte mise pro zisk odměn v Havirov Coinech
- **Vylepšování lodě**: Zvyšte schopnosti své lodi pomocí vylepšení
- **Mapa galaxie**: Prozkoumejte rozsáhlou galaxii s různými planetami

### 💰 Havirov Coin integrace
- **Wallet systém**: Úplná integrace s Havirov Coin walletem
- **Transakce**: Nakupujte zboží, vylepšujte loď a kupujte palivo za Havirov Coiny
- **Uložený postup**: Vaše finance jsou uloženy v wallet.dat souboru

### 🌍 Planety a stanice
- **Různé typy stanic**: Planety, doky, pirátské kluby, hi-tech laboratoře, obchodní stanice
- **Dynamické ceny**: Ceny se mění na základě poptávky a nabídky
- **Speciální nabídky**: Každá stanice nabízí různé typy zboží

### 🎯 Quest systém
- **Dodávky**: Dovážejte zboží mezi planetami
- **Sběr**: Sbírejte suroviny v galaxii
- **Bojové mise**: Zničte pirátské lodě

### 🛠️ Vylepšování lodě
- **Zvýšení života**: Zvyšte odolnost své lodi
- **Štíty**: Vylepšete štítový systém
- **Rychlost**: Zrychlete svou loď
- **Nakladní prostor**: Zvětšete kapacitu nákladu
- **Palivo**: Zvyšte maximální kapacitu paliva
- **Zbraně**: Otevřete si přístup k pokročilejším zbraním

## Ovládání

### Hlavní ovládání
- **WASD/Šipky**: Ovládání lodi
- **Mys**: Kliknutí pro let na pozici
- **Pravé tlačítko myši**: Střílení
- **Mezerník**: Střílení (alternativa)

### Menu a herní stavy
- **ESC**: Návrat do menu/předchozího stavu
- **M**: Otevření mapy galaxie
- **F**: Nákup paliva
- **Q**: Otevření questů
- **U**: Vylepšování lodi
- **T**: Obchodování (při dokování)
- **B**: Otevření walletu
- **C**: Zobrazení kreditů

### Obchodování
- **Čísla 1-6**: Nákup konkrétních položek
- **S**: Prodej nákladu
- **Čísla 7-9**: Prodej konkrétních položek
- **Myš**: Klikání na položky v obchodním rozhraní

### Mapa galaxie
- **Myš**: Posouvání mapy
- **Kolečko myši**: Zoom mapy
- **Šipky**: Posouvání mapy
- **Kliknutí na planetu**: Teleport (za poplatek)

## Instalace a spuštění

### Požadavky
- Python 3.7+
- Pygame knihovna

### Instalace
```bash
# Klonování repozitáře
git clone <repo-url>
cd Space-Rangers

# Instalace závislostí
pip install pygame
```

### Spuštění hry
```bash
python space_rangers.py
```

## Struktura projektu

```
Space-Rangers/
├── space_rangers.py          # Hlavní herní soubor
├── README.md                 # Tento soubor
└── wallet.dat               # Havirov Coin wallet data
```

## Herní ekonomika

### Komodity
- **Minerály**: Ruda, zlato, stříbro, platina, křemík atd.
- **Zbraně**: Lasery, plazmové zbraně, torpéda, ionové blastery
- **Potraviny**: Chléb, maso, ovoce, zelenina, konzervy
- **Technologie**: Čipy, procesory, senzory, AI moduly
- **Léky**: Antibiotika, stimulanty, nanoléky, vakcíny
- **Luxus**: Šperky, umění, víno, kaviár
- **Komponenty**: Motory, převodovky, kabely, filtry

### Ceny a trh
- Ceny se dynamicky mění na základě poptávky a nabídky
- Každá stanice má specifické ceny podle typu
- Pirátské stanice mají vyšší ceny, ale i riziko

## Questy

### Typy questů
1. **Dopravní questy**: Dovážejte zboží mezi planetami
2. **Sběrské questy**: Sbírejte suroviny v galaxii
3. **Bojové questy**: Zničte pirátské lodě

### Odměny
- Každý quest přináší odměny v Havirov Coinech
- Obtížnější questy mají vyšší odměny

## Tipy pro hraní

1. **Obchodování**: Kupujte na levných planetách, prodávejte drahých
2. **Boj**: Vyhněte se konfrontaci s piráty, pokud nejste dobře vyzbrojeni
3. **Palivo**: Sledujete úroveň paliva, doplňujte včas
4. **Questy**: Plnění questů je rychlejší způsob vydělávání peněz
5. **Vylepšování**: Investujte do vylepšení pro snazší hraní

## Technické detaily

### Herní engine
- **Pygame**: Herní engine pro 2D grafiku
- **Real-time combat**: Boj v reálném čase s fyzikou
- **Dynamický svět**: Ceny a zboží se mění v čase

### Ukládání postupu
- Havař Coin wallet se ukládá do `wallet.dat`
- Postup ve hře se ukládá automaticky

## Budoucí vylepšení

Plánovaná vylepšení:
- Více typů lodí
- Multiplayer režim
- Rozšířený quest systém
- Nové typy zbraní a vybavení
- Vylepšená AI nepřátel

## Licence

Tento projekt je vytvořen pro vzdělávací a zábavné účely.

## Autor

Hra vytvořena pro Space Rangers komunitu s integrací Havirov Coin systému.