"""
database.py — Animal Classification Expert System v2

Expanded schema:
  • taxonomy_classes    — Animal classes (Mammalia, Aves, Reptilia, etc.)
  • taxonomy_orders     — Orders within each class
  • species             — Species-level data with rich info (habitat, diet, etc.)
  • classification_history — Audit log of every classification
  • users               — (Optional extension) User accounts
"""

import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'animals.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed rich taxonomy data."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    c = conn.cursor()

    # ── Core taxonomy ─────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS taxonomy_classes (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            common_name TEXT,
            description TEXT,
            emoji TEXT,
            characteristics TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS taxonomy_orders (
            id INTEGER PRIMARY KEY,
            class_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            common_name TEXT,
            description TEXT,
            emoji TEXT,
            FOREIGN KEY (class_id) REFERENCES taxonomy_classes(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            scientific_name TEXT NOT NULL,
            common_name TEXT NOT NULL,
            emoji TEXT,
            description TEXT,
            habitat TEXT,
            diet TEXT,
            lifespan TEXT,
            distribution TEXT,
            conservation_status TEXT,
            image_url TEXT,
            facts TEXT,
            FOREIGN KEY (order_id) REFERENCES taxonomy_orders(id)
        )
    ''')

    # ── Classification audit trail ────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS classification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            input_type TEXT DEFAULT 'wizard',
            input_summary TEXT,
            result_class_id INTEGER,
            result_order_id INTEGER,
            result_species_id INTEGER,
            confidence REAL,
            ml_confidence REAL,
            reasoning TEXT,
            FOREIGN KEY (result_class_id) REFERENCES taxonomy_classes(id),
            FOREIGN KEY (result_order_id) REFERENCES taxonomy_orders(id),
            FOREIGN KEY (result_species_id) REFERENCES species(id)
        )
    ''')

    # ── Seed data ─────────────────────────────────────────────
    _seed_taxonomy(c)
    _seed_species(c)

    conn.commit()
    conn.close()
    print("✅ Database initialised at", DB_PATH)


def _seed_taxonomy(c):
    """Populate classes and orders."""
    classes = [
        (1, 'Mammalia', 'Mammals', 'Vertebrates with fur/hair, warm-blooded, live birth (mostly), mammary glands.', '🦁', 'Fur, warm-blooded, four-chambered heart, neocortex, three middle ear bones.'),
        (2, 'Aves', 'Birds', 'Warm-blooded vertebrates with feathers, beaks, and egg-laying reproduction.', '🦅', 'Feathers, beak, hollow bones, high metabolism, four-chambered heart, lightweight skeleton.'),
        (3, 'Reptilia', 'Reptiles', 'Cold-blooded vertebrates with scales, most lay eggs on land.', '🐍', 'Dry scaly skin, ectothermic, lungs, most oviparous, amniotic eggs.'),
        (4, 'Amphibia', 'Amphibians', 'Cold-blooded vertebrates with moist skin, dual life (water/land).', '🐸', 'Moist permeable skin, ectothermic, metamorphosis, aquatic larvae, cutaneous respiration.'),
        (5, 'Insecta', 'Insects', 'Invertebrates with exoskeletons, six legs, antennae, often wings.', '🦋', 'Chitinous exoskeleton, three body segments, six legs, compound eyes, antennae.'),
        (6, 'Arachnida', 'Arachnids', 'Invertebrates with two body segments, eight legs, no antennae.', '🕷️', 'Two tagmata, eight legs, chelicerae, no antennae, book lungs/tracheae.'),
        (7, 'Pisces', 'Fish', 'Aquatic vertebrates with scales, gills, and fins.', '🐟', 'Scales, gills, fins, ectothermic, two-chambered heart, lateral line.'),
        (8, 'Crustacea', 'Crustaceans', 'Aquatic invertebrates with hard exoskeletons and two pairs of antennae.', '🦀', 'Two pairs of antennae, biramous appendages, calcified exoskeleton, gills.'),
    ]
    c.executemany('''INSERT OR IGNORE INTO taxonomy_classes (id,name,common_name,description,emoji,characteristics) VALUES (?,?,?,?,?,?)''', classes)

    orders = [
        # Mammalia
        (1, 1, 'Carnivora', 'Carnivores', 'Meat-eating mammals with sharp teeth and claws.', '🐯'),
        (2, 1, 'Primates', 'Primates', 'Intelligent mammals with forward-facing eyes and grasping hands.', '🐵'),
        (3, 1, 'Rodentia', 'Rodents', 'Gnawing mammals with continuously growing incisors.', '🐭'),
        (4, 1, 'Cetacea', 'Cetaceans', 'Fully aquatic mammals including whales and dolphins.', '🐋'),
        (5, 1, 'Proboscidea', 'Proboscideans', 'Large mammals with trunks (elephants).', '🐘'),
        (6, 1, 'Perissodactyla', 'Odd-toed Ungulates', 'Hoofed mammals with odd number of toes (horses, rhinos).', '🦏'),
        (7, 1, 'Artiodactyla', 'Even-toed Ungulates', 'Hoofed mammals with even number of toes (deer, cows, pigs).', '🦌'),
        (8, 1, 'Chiroptera', 'Bats', 'Flying mammals with echolocation.', '🦇'),
        # Aves
        (9, 2, 'Passeriformes', 'Perching Birds', 'Songbirds with feet adapted for perching.', '🐦'),
        (10, 2, 'Falconiformes', 'Birds of Prey', 'Diurnal raptors with keen eyesight and sharp talons.', '🦅'),
        (11, 2, 'Strigiformes', 'Owls', 'Nocturnal raptors with facial discs and silent flight.', '🦉'),
        (12, 2, 'Sphenisciformes', 'Penguins', 'Flightless aquatic birds of the Southern Hemisphere.', '🐧'),
        (13, 2, 'Anseriformes', 'Waterfowl', 'Ducks, geese, swans with webbed feet.', '🦆'),
        # Reptilia
        (14, 3, 'Squamata', 'Scaled Reptiles', 'Lizards and snakes with overlapping scales.', '🦎'),
        (15, 3, 'Testudines', 'Turtles & Tortoises', 'Reptiles with bony shells.', '🐢'),
        (16, 3, 'Crocodilia', 'Crocodilians', 'Large aquatic reptiles including crocodiles and alligators.', '🐊'),
        # Amphibia
        (17, 4, 'Anura', 'Frogs & Toads', 'Tailless amphibians with long hind legs for jumping.', '🐸'),
        (18, 4, 'Urodela', 'Salamanders', 'Tailed amphibians with lizard-like bodies.', '🦎'),
        # Insecta
        (19, 5, 'Lepidoptera', 'Butterflies & Moths', 'Winged insects with scaled wings.', '🦋'),
        (20, 5, 'Coleoptera', 'Beetles', 'Hard-shelled insects with elytra.', '🪲'),
        (21, 5, 'Hymenoptera', 'Ants, Bees & Wasps', 'Social insects with membranous wings.', '🐝'),
        (22, 5, 'Orthoptera', 'Grasshoppers & Crickets', 'Jumping insects with enlarged hind legs.', '🦗'),
        # Arachnida
        (23, 6, 'Araneae', 'Spiders', 'Eight-legged silk-spinning predators.', '🕷️'),
        (24, 6, 'Scorpiones', 'Scorpions', 'Arachnids with pincers and venomous stingers.', '🦂'),
        # Pisces
        (25, 7, 'Perciformes', 'Perch-like Fish', 'Largest order of fish with spiny fins.', '🐠'),
        (26, 7, 'Carcharhiniformes', 'Ground Sharks', 'Requiem sharks, tiger sharks, hammerheads.', '🦈'),
        (27, 7, 'Anguilliformes', 'Eels', 'Snake-like fish with elongated bodies.', '🐍'),
        # Crustacea
        (28, 8, 'Decapoda', 'Decapods', 'Ten-legged crustaceans including crabs and lobsters.', '🦀'),
        (29, 8, 'Stomatopoda', 'Mantis Shrimp', 'Marine crustaceans with powerful claws.', '🦐'),
    ]
    c.executemany('''INSERT OR IGNORE INTO taxonomy_orders (id,class_id,name,common_name,description,emoji) VALUES (?,?,?,?,?,?)''', orders)


def _seed_species(c):
    """Populate species with rich educational data."""
    species = [
        # Mammalia - Carnivora
        (1, 1, 'Panthera tigris', 'Tiger', '🐯', 'Largest living cat species, apex predator of Asian forests.',
         'Tropical forests, mangroves, grasslands', 'Carnivore: deer, wild boar, buffalo',
         '8-10 years in wild', 'India, Southeast Asia, Russia, China', 'Endangered',
         'Tigers have striped skin under their fur — no two patterns are alike.'),
        (2, 1, 'Panthera leo', 'Lion', '🦁', 'Social big cats living in prides on African savannas.',
         'Savanna, grassland, open woodland', 'Carnivore: zebras, wildebeest, buffalo',
         '10-14 years in wild', 'Sub-Saharan Africa, Gir Forest (India)', 'Vulnerable',
         'Male lions are the only cats with manes; females do most of the hunting.'),
        (3, 1, 'Canis lupus', 'Gray Wolf', '🐺', 'Largest wild member of the dog family, highly social pack hunter.',
         'Forests, tundra, grasslands, mountains', 'Carnivore: elk, deer, moose, bison',
         '6-8 years in wild', 'North America, Europe, Asia', 'Least Concern',
         'Wolf packs have complex social hierarchies led by an alpha breeding pair.'),
        (4, 1, 'Ursus maritimus', 'Polar Bear', '🐻‍❄️', 'Largest land carnivore, perfectly adapted to Arctic ice.',
         'Arctic sea ice, coastal islands', 'Hypercarnivore: ringed seals, bearded seals',
         '25-30 years', 'Circumpolar Arctic', 'Vulnerable',
         'Polar bear skin is black under transparent fur to absorb heat from the sun.'),
        # Mammalia - Primates
        (5, 2, 'Homo sapiens', 'Human', '🧑', 'Highly intelligent primates with complex language and tool use.',
         'Global terrestrial habitats', 'Omnivore', '70-85 years', 'Worldwide', 'Least Concern',
         'Humans share 98.8% of their DNA with chimpanzees.'),
        (6, 2, 'Pan troglodytes', 'Chimpanzee', '🐒', 'Great ape native to African forests, closest living human relative.',
         'Tropical rainforest, savanna-woodland', 'Omnivore: fruits, leaves, insects, meat',
         '40-50 years', 'Central & West Africa', 'Endangered',
         'Chimps use sticks as tools to fish termites and crack nuts with stones.'),
        (7, 2, 'Gorilla beringei', 'Mountain Gorilla', '🦍', 'Largest living primate, inhabiting high-altitude forests.',
         'Montane rainforest, bamboo forest (1,800-3,900m)', 'Herbivore: leaves, shoots, fruit',
         '35-40 years', 'Rwanda, Uganda, DRC', 'Endangered',
         'Mountain gorillas share 98% of human DNA and live in stable family troops.'),
        # Mammalia - Cetacea
        (8, 4, 'Tursiops truncatus', 'Bottlenose Dolphin', '🐬', 'Highly intelligent marine mammal known for echolocation.',
         'Coastal and offshore temperate/tropical waters', 'Carnivore: fish, squid, crustaceans',
         '40-60 years', 'Worldwide temperate/tropical oceans', 'Least Concern',
         'Dolphins sleep with one hemisphere of their brain awake to keep breathing.'),
        (9, 4, 'Balaenoptera musculus', 'Blue Whale', '🐋', 'Largest animal ever known to have lived on Earth.',
         'Open ocean', 'Carnivore: krill (up to 4 tonnes/day)',
         '80-90 years', 'All oceans except Arctic', 'Endangered',
         'A blue whale\'s tongue can weigh as much as an elephant.'),
        # Mammalia - Proboscidea
        (10, 5, 'Loxodonta africana', 'African Elephant', '🐘', 'Largest land animal, keystone species of African savannas.',
         'Savanna, forest, grassland, desert', 'Herbivore: grasses, bark, fruit, leaves (150kg/day)',
         '60-70 years', 'Sub-Saharan Africa', 'Endangered',
         'Elephants have 40,000 muscles in their trunk and can recognize themselves in mirrors.'),
        # Aves - Passeriformes
        (11, 9, 'Corvus corax', 'Common Raven', '🐦‍⬛', 'Large all-black passerine with remarkable problem-solving intelligence.',
         'Forests, coasts, deserts, tundra, cities', 'Omnivore: carrion, insects, fruit, eggs',
         '10-15 years', 'Northern Hemisphere', 'Least Concern',
         'Ravens can mimic human speech and have been observed using tools in the wild.'),
        # Aves - Falconiformes
        (12, 10, 'Aquila chrysaetos', 'Golden Eagle', '🦅', 'Large bird of prey with powerful build and keen eyesight.',
         'Mountains, hills, cliffs, open country', 'Carnivore: rabbits, marmots, foxes, birds',
         '15-20 years', 'Northern Hemisphere', 'Least Concern',
         'Golden eagles can dive at speeds over 240 km/h (150 mph).'),
        # Aves - Sphenisciformes
        (13, 12, 'Aptenodytes forsteri', 'Emperor Penguin', '🐧', 'Largest penguin species, breeds in Antarctic winter.',
         'Antarctic ice shelves and coastal waters', 'Carnivore: fish, squid, krill',
         '15-20 years', 'Antarctica', 'Near Threatened',
         'Male emperor penguins incubate eggs on their feet for 64 days without eating.'),
        # Reptilia - Squamata
        (14, 14, 'Python bivittatus', 'Burmese Python', '🐍', 'One of the largest snake species, non-venomous constrictor.',
         'Tropical forests, marshes, grasslands', 'Carnivore: mammals, birds, reptiles',
         '20-25 years', 'Southeast Asia (invasive in Florida Everglades)', 'Vulnerable',
         'Burmese pythons can grow over 7 meters (23 ft) and weigh 90 kg.'),
        # Reptilia - Testudines
        (15, 15, 'Chelonia mydas', 'Green Sea Turtle', '🐢', 'Large sea turtle that travels thousands of kilometers to nest.',
         'Tropical and subtropical oceans, beaches', 'Herbivore: seagrass, algae (adults); jellyfish (juveniles)',
         '60-80 years', 'Tropical oceans worldwide', 'Endangered',
         'Green sea turtles can hold their breath for up to 5 hours while resting.'),
        # Amphibia - Anura
        (16, 17, 'Rana temporaria', 'Common Frog', '🐸', 'Widespread European frog with smooth skin and long jumping legs.',
         'Ponds, lakes, marshes, damp woodlands', 'Carnivore: insects, slugs, worms, spiders',
         '5-10 years', 'Europe, northwest Asia', 'Least Concern',
         'Common frogs can change colour to camouflage with their surroundings.'),
        # Insecta - Lepidoptera
        (17, 19, 'Danaus plexippus', 'Monarch Butterfly', '🦋', 'Famous migratory butterfly traveling up to 4,800 km.',
         'Meadows, fields, gardens, forests', 'Herbivore: milkweed nectar and leaves',
         '6 months (migratory generation)', 'North & Central America', 'Endangered',
         'Monarchs are poisonous to predators because milkweed toxins accumulate in their bodies.'),
        # Insecta - Hymenoptera
        (18, 21, 'Apis mellifera', 'Western Honey Bee', '🐝', 'Primary pollinator of crops worldwide, lives in complex hives.',
         'Meadows, gardens, agricultural areas', 'Herbivore: nectar, pollen',
         '5-6 weeks (summer worker)', 'Worldwide (human-introduced)', 'Least Concern',
         'Honey bees perform a \'waggle dance\' to communicate the direction and distance to flowers.'),
        # Arachnida - Araneae
        (19, 23, 'Latrodectus mactans', 'Black Widow', '🕷️', 'Venomous spider known for the red hourglass on its abdomen.',
         'Dark sheltered areas: woodpiles, sheds, caves', 'Carnivore: insects, scorpions, centipedes',
         '1-3 years', 'North & South America, Caribbean', 'Least Concern',
         'Black widow venom is 15 times stronger than rattlesnake venom, but bites are rarely fatal.'),
        # Pisces - Carcharhiniformes
        (20, 26, 'Carcharhinus leucas', 'Bull Shark', '🦈', 'Aggressive shark known for entering freshwater rivers.',
         'Coastal marine, estuaries, rivers, lakes', 'Carnivore: fish, dolphins, turtles, birds',
         '12-16 years', 'Worldwide tropical/subtropical waters', 'Near Threatened',
         'Bull sharks can survive in freshwater and have been found 4,200 km up the Amazon River.'),
        # Crustacea - Decapoda
        (21, 28, 'Cancer pagurus', 'Edible Crab', '🦀', 'Large brown crab common in the North Sea and eastern Atlantic.',
         'Rocky seabed, sandy/muddy bottoms (5-50m depth)', 'Omnivore: molluscs, worms, algae, carrion',
         '20-30 years', 'Northeast Atlantic, North Sea', 'Least Concern',
         'Edible crabs can crush shells with claws exerting pressure over 500 N.'),
    ]
    c.executemany('''INSERT OR IGNORE INTO species
        (id,order_id,scientific_name,common_name,emoji,description,habitat,diet,lifespan,distribution,conservation_status,facts)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', species)


def get_classes():
    conn = get_conn()
    rows = conn.execute('SELECT * FROM taxonomy_classes ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orders(class_id=None):
    conn = get_conn()
    if class_id:
        rows = conn.execute('SELECT * FROM taxonomy_orders WHERE class_id=? ORDER BY id', (class_id,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM taxonomy_orders ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_species(order_id=None, class_id=None, search=None):
    conn = get_conn()
    query = '''SELECT s.*, o.name as order_name, o.common_name as order_common, o.class_id,
                      c.name as class_name, c.common_name as class_common, c.emoji as class_emoji
               FROM species s
               JOIN taxonomy_orders o ON s.order_id = o.id
               JOIN taxonomy_classes c ON o.class_id = c.id
               WHERE 1=1'''
    params = []
    if order_id:
        query += ' AND s.order_id=?'
        params.append(order_id)
    if class_id:
        query += ' AND o.class_id=?'
        params.append(class_id)
    if search:
        query += ' AND (s.common_name LIKE ? OR s.scientific_name LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    query += ' ORDER BY s.common_name'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_species_by_id(sid):
    conn = get_conn()
    row = conn.execute('''SELECT s.*, o.name as order_name, o.common_name as order_common,
                          c.name as class_name, c.common_name as class_common
                          FROM species s
                          JOIN taxonomy_orders o ON s.order_id = o.id
                          JOIN taxonomy_classes c ON o.class_id = c.id
                          WHERE s.id=?''', (sid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_taxonomy_tree():
    """Return nested JSON-like tree: Class -> Order -> [Species]."""
    conn = get_conn()
    classes = conn.execute('SELECT * FROM taxonomy_classes ORDER BY id').fetchall()
    tree = []
    for cls in classes:
        cdict = dict(cls)
        orders = conn.execute('SELECT * FROM taxonomy_orders WHERE class_id=? ORDER BY id', (cls['id'],)).fetchall()
        cdict['orders'] = []
        for order in orders:
            odict = dict(order)
            species = conn.execute('SELECT id,scientific_name,common_name,emoji FROM species WHERE order_id=? ORDER BY common_name', (order['id'],)).fetchall()
            odict['species'] = [dict(s) for s in species]
            cdict['orders'].append(odict)
        tree.append(cdict)
    conn.close()
    return tree


def log_classification(input_type, input_summary, result_class_id, result_order_id,
                         result_species_id, confidence, ml_confidence, reasoning):
    conn = get_conn()
    conn.execute('''INSERT INTO classification_history
        (input_type, input_summary, result_class_id, result_order_id, result_species_id,
         confidence, ml_confidence, reasoning)
        VALUES (?,?,?,?,?,?,?,?)''',
        (input_type, input_summary, result_class_id, result_order_id,
         result_species_id, confidence, ml_confidence, reasoning))
    conn.commit()
    conn.close()


def get_history(limit=50):
    conn = get_conn()
    rows = conn.execute('''SELECT h.*, c.name as class_name, o.name as order_name,
                                  s.common_name as species_name, s.emoji as species_emoji
                           FROM classification_history h
                           LEFT JOIN taxonomy_classes c ON h.result_class_id = c.id
                           LEFT JOIN taxonomy_orders o ON h.result_order_id = o.id
                           LEFT JOIN species s ON h.result_species_id = s.id
                           ORDER BY h.id DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == '__main__':
    init_db()
