"""
database.py — Animal Classification Expert System v2
EXPANDED DATABASE: 50+ species, rich educational data, global coverage.
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
    """Create tables and seed MASSIVE taxonomy data."""
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
    print("✅ Database initialised with 50+ species at", DB_PATH)


def _seed_taxonomy(c):
    """Populate classes and orders."""
    classes = [
        (1, 'Mammalia', 'Mammals', 'Vertebrates with fur/hair, warm-blooded, mammary glands, neocortex, and three middle ear bones.', '🦁', 'Fur or hair, warm-blooded (endothermic), four-chambered heart, neocortex, mammary glands, three middle ear bones, single lower jaw bone.'),
        (2, 'Aves', 'Birds', 'Warm-blooded vertebrates with feathers, beaks, and lightweight skeletons adapted for flight.', '🦅', 'Feathers, beak, hollow bones, high metabolism, four-chambered heart, lightweight skeleton, egg-laying with hard shells.'),
        (3, 'Reptilia', 'Reptiles', 'Cold-blooded vertebrates with scales or scutes, most lay leathery or hard-shelled eggs on land.', '🐍', 'Dry scaly skin or scutes, ectothermic, lungs, amniotic eggs, most are oviparous, internal fertilization.'),
        (4, 'Amphibia', 'Amphibians', 'Cold-blooded vertebrates with moist permeable skin, dual aquatic-terrestrial life cycle.', '🐸', 'Moist permeable skin, ectothermic, metamorphosis from larval to adult, aquatic larvae with gills, cutaneous respiration, webbed feet.'),
        (5, 'Insecta', 'Insects', 'Invertebrates with exoskeletons, three body segments (head, thorax, abdomen), six legs, often wings.', '🦋', 'Chitinous exoskeleton, three body segments (head, thorax, abdomen), six jointed legs, compound eyes, one pair of antennae, often wings.'),
        (6, 'Arachnida', 'Arachnids', 'Invertebrates with two body segments (cephalothorax and abdomen), eight legs, no antennae or wings.', '🕷️', 'Two body segments (cephalothorax, abdomen), eight legs, no antennae, no wings, chelicerae mouthparts, simple eyes.'),
        (7, 'Pisces', 'Fish', 'Aquatic vertebrates with scales, gills, and fins. Most are ectothermic and use lateral line for sensing.', '🐟', 'Scales, gills, fins, ectothermic, two-chambered heart, lateral line system, swim bladder (most), external fertilization (many).'),
        (8, 'Crustacea', 'Crustaceans', 'Aquatic (mostly) arthropods with hard calcified exoskeletons, two pairs of antennae, and biramous appendages.', '🦀', 'Two pairs of antennae, biramous appendages, calcified exoskeleton, gills, compound eyes on stalks, cephalothorax covered by carapace.'),
    ]
    c.executemany('''INSERT OR IGNORE INTO taxonomy_classes (id,name,common_name,description,emoji,characteristics) VALUES (?,?,?,?,?,?)''', classes)

    orders = [
        # Mammalia
        (1, 1, 'Carnivora', 'Carnivores', 'Meat-eating mammals with sharp teeth, strong jaws, and claws. Includes cats, dogs, bears, weasels, and hyenas.', '🐯'),
        (2, 1, 'Primates', 'Primates', 'Intelligent mammals with forward-facing eyes, grasping hands with nails, and complex social structures. Includes monkeys, apes, and humans.', '🐵'),
        (3, 1, 'Rodentia', 'Rodents', 'Gnawing mammals with a single pair of continuously growing incisors in each jaw. Largest order of mammals.', '🐭'),
        (4, 1, 'Cetacea', 'Cetaceans', 'Fully aquatic mammals with streamlined bodies, blowholes, and echolocation. Includes whales, dolphins, and porpoises.', '🐋'),
        (5, 1, 'Proboscidea', 'Proboscideans', 'Large mammals with long muscular trunks (proboscis), tusks, and pillar-like legs. Only elephants survive today.', '🐘'),
        (6, 1, 'Perissodactyla', 'Odd-toed Ungulates', 'Hoofed mammals with an odd number of weight-bearing toes (1 or 3). Includes horses, rhinos, and tapirs.', '🦏'),
        (7, 1, 'Artiodactyla', 'Even-toed Ungulates', 'Hoofed mammals with an even number of toes (2 or 4). Includes deer, cows, pigs, camels, and hippos.', '🦌'),
        (8, 1, 'Chiroptera', 'Bats', 'Flying mammals with wings formed by a membrane stretched between elongated fingers. Use echolocation for navigation.', '🦇'),
        # Aves
        (9, 2, 'Passeriformes', 'Perching Birds', 'Songbirds with feet adapted for perching (3 toes forward, 1 back). Over half of all bird species.', '🐦'),
        (10, 2, 'Falconiformes', 'Birds of Prey', 'Diurnal raptors with keen eyesight, sharp hooked beaks, and powerful talons. Includes eagles, hawks, and falcons.', '🦅'),
        (11, 2, 'Strigiformes', 'Owls', 'Nocturnal raptors with facial discs, large forward-facing eyes, and silent flight feathers. Exceptional hearing.', '🦉'),
        (12, 2, 'Sphenisciformes', 'Penguins', 'Flightless aquatic birds of the Southern Hemisphere. Streamlined bodies, flipper-like wings, dense waterproof feathers.', '🐧'),
        (13, 2, 'Anseriformes', 'Waterfowl', 'Aquatic birds with webbed feet, broad flat bills, and waterproof plumage. Ducks, geese, swans.', '🦆'),
        # Reptilia
        (14, 3, 'Squamata', 'Scaled Reptiles', 'Lizards and snakes with overlapping scales, movable quadrate bones, and flexible jaws. Largest reptile order.', '🦎'),
        (15, 3, 'Testudines', 'Turtles & Tortoises', 'Reptiles with bony or cartilaginous shells developed from ribs. Includes sea turtles, freshwater turtles, and land tortoises.', '🐢'),
        (16, 3, 'Crocodilia', 'Crocodilians', 'Large semi-aquatic reptiles with powerful jaws, armor-like scales, and four-chambered hearts. Includes crocodiles, alligators, and caimans.', '🐊'),
        # Amphibia
        (17, 4, 'Anura', 'Frogs & Toads', 'Tailless amphibians with long hind legs adapted for jumping, webbed feet, and bulging eyes. Frogs, toads, tree frogs.', '🐸'),
        (18, 4, 'Urodela', 'Salamanders', 'Tailed amphibians with lizard-like bodies, four legs of equal size, and the ability to regenerate limbs. Newts, salamanders, axolotls.', '🦎'),
        # Insecta
        (19, 5, 'Lepidoptera', 'Butterflies & Moths', 'Winged insects with scaled wings and a coiled proboscis for feeding. Complete metamorphosis (caterpillar → pupa → adult).', '🦋'),
        (20, 5, 'Coleoptera', 'Beetles', 'Hard-shelled insects with forewings modified into protective elytra. Largest order of animals with ~400,000 species.', '🪲'),
        (21, 5, 'Hymenoptera', 'Ants, Bees & Wasps', 'Social insects with membranous wings, elbowed antennae, and complex colony behaviors. Many are important pollinators.', '🐝'),
        (22, 5, 'Orthoptera', 'Grasshoppers & Crickets', 'Jumping insects with enlarged hind legs, leathery forewings, and sound-producing organs (stridulation).', '🦗'),
        # Arachnida
        (23, 6, 'Araneae', 'Spiders', 'Eight-legged silk-spinning predators with venomous fangs (chelicerae). Over 50,000 species worldwide.', '🕷️'),
        (24, 6, 'Scorpiones', 'Scorpions', 'Arachnids with pincers (pedipalps) and a segmented tail with a venomous stinger. Glow under UV light.', '🦂'),
        # Pisces
        (25, 7, 'Perciformes', 'Perch-like Fish', 'Largest order of fish (~10,000 species) with spiny rays in dorsal fins. Includes perch, bass, tuna, and wrasses.', '🐠'),
        (26, 7, 'Carcharhiniformes', 'Ground Sharks', 'Requiem sharks, tiger sharks, hammerheads, and catsharks. Five to seven gill slits, dorsal fin with spines.', '🦈'),
        (27, 7, 'Anguilliformes', 'Eels', 'Snake-like fish with elongated bodies, fused fins, and no pelvic fins. Some migrate thousands of km to spawn.', '🐍'),
        # Crustacea
        (28, 8, 'Decapoda', 'Decapods', 'Ten-legged crustaceans including crabs, lobsters, shrimp, and crayfish. Carapace covers fused cephalothorax.', '🦀'),
        (29, 8, 'Stomatopoda', 'Mantis Shrimp', 'Marine crustaceans with powerful raptorial claws that strike with the speed of a bullet. Exceptional vision (12-16 photoreceptors).', '🦐'),
    ]
    c.executemany('''INSERT OR IGNORE INTO taxonomy_orders (id,class_id,name,common_name,description,emoji) VALUES (?,?,?,?,?,?)''', orders)


def _seed_species(c):
    """Populate MASSIVE species dataset with rich educational data."""
    species = [
        # === MAMMALIA: CARNIVORA (1) ===
        (1, 1, 'Panthera tigris', 'Tiger', '🐯', 'The largest living cat species, apex predator of Asian forests. Solitary hunters with powerful limbs and striped camouflage.', 'Tropical forests, mangroves, grasslands, swamps', 'Hypercarnivore: deer, wild boar, buffalo, gaur', '8-10 years in wild', 'India, Southeast Asia, Russian Far East, China', 'Endangered', 'Tiger stripes are unique like fingerprints. A tiger can eat up to 40 kg (88 lbs) in one sitting.'),
        (2, 1, 'Panthera leo', 'Lion', '🦁', 'Social big cats living in prides on African savannas. The only cats with manes (males). Females do most of the hunting.', 'Savanna, grassland, open woodland, scrubland', 'Carnivore: zebras, wildebeest, buffalo, warthog', '10-14 years in wild', 'Sub-Saharan Africa, Gir Forest (India)', 'Vulnerable', 'A lion’s roar can be heard from 8 km (5 miles) away. Lions sleep up to 20 hours a day.'),
        (3, 1, 'Canis lupus', 'Gray Wolf', '🐺', 'The largest wild member of the dog family. Highly social pack hunters with complex hierarchies and cooperative hunting strategies.', 'Forests, tundra, grasslands, mountains, taiga', 'Carnivore: elk, deer, moose, bison, caribou', '6-8 years in wild', 'North America, Europe, Asia, Middle East', 'Least Concern', 'Wolf packs are typically family units led by a breeding pair (alpha male and female).'),
        (4, 1, 'Ursus maritimus', 'Polar Bear', '🐻‍❄️', 'The largest land carnivore, perfectly adapted to Arctic life. Seals are their primary prey.', 'Arctic sea ice, coastal islands, tundra', 'Hypercarnivore: ringed seals, bearded seals, walrus calves', '25-30 years', 'Circumpolar Arctic (Alaska, Canada, Greenland, Norway, Russia)', 'Vulnerable', 'Polar bear skin is black under transparent fur to absorb heat. They can swim for days at a time.'),
        (5, 1, 'Ailuropoda melanoleuca', 'Giant Panda', '🐼', 'Bear native to central China, famous for its black-and-white coat. Bamboo specialist with a modified wrist bone acting as a thumb.', 'Temperate broadleaf and mixed forests of Sichuan, Shaanxi, Gansu', 'Herbivore (99% bamboo): shoots, leaves, stems', '20 years in wild', 'South-central China (Sichuan, Shaanxi, Gansu)', 'Vulnerable', 'Pandas spend 10-16 hours a day eating bamboo and defecate 40 times daily. They are born blind and pink.'),
        (6, 1, 'Acinonyx jubatus', 'Cheetah', '🐆', 'Fastest land mammal, reaching 112 km/h (70 mph) in short bursts. Non-retractable claws act like cleats for traction.', 'Savanna, grassland, open plains, semi-desert', 'Carnivore: small to medium antelopes (gazelle, impala)', '10-12 years in wild', 'Sub-Saharan Africa, Iran (critically endangered Asiatic cheetah)', 'Vulnerable', 'Cheetahs can accelerate from 0 to 100 km/h in 3 seconds — faster than most sports cars. They chirp like birds rather than roar.'),
        (7, 1, 'Hyaena hyaena', 'Striped Hyena', '🐺', 'Nocturnal scavenger with powerful jaws capable of crushing bone. Distinctive striped coat and mane.', 'Semi-desert, scrub forest, savanna, grassland', 'Omnivore/Scavenger: carrion, insects, fruit, small mammals', '12-15 years', 'North Africa, East Africa, Middle East, India, Central Asia', 'Near Threatened', 'Hyena jaws are so powerful they can crush elephant bones. Their laugh-like vocalizations are communication, not emotion.'),
        (8, 1, 'Meles meles', 'European Badger', '🦡', 'Stout nocturnal mammals with distinctive black-and-white facial stripes. Excellent diggers with powerful claws.', 'Woodland, farmland, grassland, suburban areas', 'Omnivore: earthworms, insects, fruit, small mammals, carrion', '5-8 years', 'Europe, British Isles, Scandinavia, Russia, parts of Middle East and China', 'Least Concern', 'Badgers live in underground burrow systems called setts that can be centuries old and passed down through generations.'),

        # === MAMMALIA: PRIMATES (2) ===
        (9, 2, 'Homo sapiens', 'Human', '🧑', 'Highly intelligent primates with complex language, tool use, abstract thought, and global civilization. Only species to develop technology and space travel.', 'All terrestrial habitats (cities, forests, deserts, tundra, mountains)', 'Omnivore', '70-85 years global average', 'Global (every continent and habitat)', 'Least Concern', 'Humans share 98.8% of DNA with chimpanzees. The human brain uses 20% of the body’s energy despite being only 2% of body weight.'),
        (10, 2, 'Pan troglodytes', 'Chimpanzee', '🐒', 'Great ape native to African forests. Closest living human relative. Uses tools, has complex social structures, and can learn sign language.', 'Tropical rainforest, savanna-woodland, montane forest', 'Omnivore: fruits, leaves, seeds, insects, meat (hunts colobus monkeys)', '40-50 years', 'Central & West Africa (Gabon, Congo, Uganda, Tanzania)', 'Endangered', 'Chimps make tools from sticks to fish termites and use stones to crack nuts. They mourn their dead and have been observed embracing to comfort each other.'),
        (11, 2, 'Gorilla beringei', 'Mountain Gorilla', '🦍', 'Largest living primate. Inhabits high-altitude cloud forests. Gentle herbivores despite formidable size. Led by a dominant silverback male.', 'Montane rainforest, bamboo forest (1,800-3,900 m elevation)', 'Herbivore: leaves, shoots, stems, bark, fruit, bamboo', '35-40 years', 'Rwanda, Uganda, Democratic Republic of Congo (Virunga Mountains, Bwindi)', 'Endangered', 'Mountain gorillas share 98% of human DNA. Infants suck their thumbs and gorillas build new nests to sleep in every night.'),
        (12, 2, 'Macaca mulatta', 'Rhesus Macaque', '🐵', 'Old World monkey native to South, Central, and Southeast Asia. Highly adaptable, often found in urban areas and temples.', 'Tropical forest, grassland, urban areas, mountains', 'Omnivore: fruit, seeds, roots, insects, small vertebrates, human food', '25-30 years', 'India, Nepal, Bangladesh, Pakistan, Thailand, China, Afghanistan', 'Least Concern', 'Rhesus monkeys were the first primates in space (Albert II in 1949). They are highly social with strict dominance hierarchies.'),
        (13, 2, 'Pongo pygmaeus', 'Bornean Orangutan', '🦧', 'Great ape with long reddish-brown hair and exceptionally long arms (span up to 2.3 m). Solitary and arboreal.', 'Tropical rainforest, peat swamp forest, mangrove', 'Frugivore/Herbivore: fruit, bark, leaves, insects, honey', '35-45 years', 'Borneo (Indonesia, Malaysia)', 'Critically Endangered', 'Orangutans are the only great apes found in Asia. They build elaborate nests high in trees with roofs made of leaves during rain.'),

        # === MAMMALIA: RODENTIA (3) ===
        (14, 3, 'Rattus norvegicus', 'Brown Rat', '🐀', 'Highly adaptable commensal rodent found worldwide. Excellent swimmer, climber, and burrower. Highly intelligent with good memory.', 'Urban areas, sewers, farms, forests, grasslands', 'Omnivore: grains, fruit, meat, eggs, garbage', '1-3 years', 'Global (native to northern China, now worldwide)', 'Least Concern', 'Rats can laugh when tickled (ultrasonic giggles). They can hold their breath for 3 minutes and tread water for 3 days. Rats are used in rescue operations for their small size and trainability.'),
        (15, 3, 'Castor canadensis', 'North American Beaver', '🦫', 'Large aquatic rodent known for building dams and lodges. Second-largest rodent in the world after capybara.', 'Rivers, streams, lakes, ponds, wetlands', 'Herbivore: bark, leaves, twigs, aquatic plants (aspen, willow, birch)', '10-15 years', 'North America (USA, Canada, Mexico)', 'Least Concern', 'Beavers have transparent eyelids for swimming underwater. Their dams create wetlands that benefit hundreds of other species. They slap their tails on water to warn of danger.'),
        (16, 3, 'Cavia porcellus', 'Guinea Pig', '🐹', 'Domesticated South American rodent kept as pets and used in research. Highly social, vocal, and unable to synthesize vitamin C.', 'Grassland, domestic (native to Andes)', 'Herbivore: grass, hay, vegetables, fruit (requires vitamin C supplements)', '4-8 years', 'Global (domestic); native to Andes (Colombia, Ecuador, Peru, Bolivia)', 'Domesticated', 'Guinea pigs are not from Guinea and are not pigs. They were domesticated by the Incas over 3,000 years ago. They purr when happy and squeak loudly when hungry.'),
        (17, 3, 'Hystrix cristata', 'Crested Porcupine', '🐿️', 'Large terrestrial rodent covered in long quills (modified hairs) that raise when threatened. Nocturnal herbivore.', 'Forest, grassland, rocky hills, semi-desert', 'Herbivore: roots, bark, tubers, fruit, cultivated crops', '12-15 years', 'Italy, North Africa, Sub-Saharan Africa', 'Least Concern', 'Porcupines cannot shoot their quills, but quills detach easily when touched. They rattle their hollow quills as a warning. Their quills have been found buried in lions and leopards.'),

        # === MAMMALIA: CETACEA (4) ===
        (18, 4, 'Tursiops truncatus', 'Bottlenose Dolphin', '🐬', 'Highly intelligent marine mammal known for echolocation, complex social bonds, and problem-solving. Famous for their "smile".', 'Coastal and offshore temperate/tropical waters, estuaries', 'Carnivore: fish, squid, crustaceans', '40-60 years', 'Worldwide temperate and tropical oceans', 'Least Concern', 'Dolphins sleep with one hemisphere of their brain awake to keep breathing. They use echolocation clicks to "see" with sound. Each dolphin has a signature whistle like a name.'),
        (19, 4, 'Balaenoptera musculus', 'Blue Whale', '🐋', 'Largest animal ever known to have lived on Earth. Heart the size of a small car. Feeds almost exclusively on tiny krill.', 'Open ocean, pelagic zones, deep waters', 'Carnivore: krill (euphausiids) — up to 4 tonnes per day', '80-90 years', 'All oceans except Arctic (Antarctic, North Atlantic, North Pacific, Indian Ocean)', 'Endangered', 'A blue whale’s tongue weighs as much as an elephant. Its heart beats so loud it can be detected from 3 km away. They are louder than a jet engine (188 decibels).'),
        (20, 4, 'Orcinus orca', 'Killer Whale (Orca)', '🐳', 'Apex predator of the ocean, highly social and matriarchal. Not a true whale but the largest dolphin species. Hunts in pods.', 'Coastal and open ocean, polar to tropical waters', 'Hypercarnivore: fish, seals, sea lions, penguins, whales, sharks', '30-50 years (males), 50-80 years (females)', 'Global — all oceans from Arctic to Antarctic', 'Data Deficient', 'Orcas have distinct cultures: different pods use different dialects, hunting techniques, and food preferences. Some pods only eat fish, others hunt mammals. Grandmothers lead pods and help raise calves.'),
        (21, 4, 'Physeter macrocephalus', 'Sperm Whale', '🐋', 'Largest toothed predator with the largest brain on Earth (5 times heavier than a human brain). Dives deeper than any other mammal.', 'Deep offshore waters, continental slopes, canyons', 'Carnivore: giant squid, colossal squid, octopus, fish, sharks', '60-70 years', 'Worldwide in deep waters between 60°N and 60°S', 'Vulnerable', 'Sperm whales can dive to 2,250 meters (7,400 ft) and hold their breath for 90 minutes. Ambergris (a valuable perfume ingredient) is produced in their digestive system.'),

        # === MAMMALIA: PROBOSCIDEA (5) ===
        (22, 5, 'Loxodonta africana', 'African Elephant', '🐘', 'Largest land animal, keystone species of African savannas. Ecosystem engineers that shape landscapes by uprooting trees and digging water holes.', 'Savanna, forest, grassland, desert, woodland', 'Herbivore: grasses, bark, leaves, fruit, branches (up to 150 kg/day)', '60-70 years', 'Sub-Saharan Africa (Kenya, Tanzania, Botswana, Zimbabwe, South Africa)', 'Endangered', 'Elephants have 40,000 muscles in their trunk. They can recognize themselves in mirrors (rare in animals). They mourn their dead and return to bones years later. They communicate through seismic vibrations in their feet.'),
        (23, 5, 'Elephas maximus', 'Asian Elephant', '🐘', 'Smaller than African cousins with smaller ears, one finger-like appendage on trunk tip, and convex backs. Vital to Asian forest ecosystems.', 'Tropical forest, grassland, scrubland', 'Herbivore: grasses, leaves, bark, fruit, sugarcane, rice (crop-raider)', '48-80 years', 'South Asia, Southeast Asia (India, Sri Lanka, Thailand, Myanmar, Indonesia)', 'Endangered', 'Asian elephants have been domesticated for 4,000 years for logging, warfare, and ceremonies. Only males have tusks (some have none). They can cry emotional tears.'),

        # === MAMMALIA: PERISSODACTYLA (6) ===
        (24, 6, 'Equus ferus caballus', 'Horse', '🐴', 'Domesticated odd-toed ungulate with one functional toe (hoof). One of the most economically important domestic animals in human history.', 'Grassland, steppe, farmland, domestic (stables, pastures)', 'Herbivore: grass, hay, oats, grains, carrots', '25-30 years', 'Global (domestic); wild ancestors from Central Asia', 'Domesticated', 'Horses can sleep both standing and lying down. They have nearly 360-degree vision (eyes on sides of head). A horse’s teeth take up more space in its head than its brain. They can gallop at 70 km/h (44 mph).'),
        (25, 6, 'Diceros bicornis', 'Black Rhinoceros', '🦏', 'Hook-lipped rhino adapted for browsing leaves and branches. Despite poor eyesight, has excellent hearing and smell. Solitary and aggressive when threatened.', 'Savanna, grassland, scrubland, tropical bushland', 'Browser herbivore: leaves, branches, fruit, bark, shoots', '35-50 years', 'Eastern and Southern Africa (Kenya, Tanzania, Zimbabwe, South Africa, Namibia)', 'Critically Endangered', 'Rhinos are illegally poached for their horns (made of keratin, same as human nails). A rhino horn can sell for $60,000/kg on black markets. Black rhinos have a prehensile upper lip for grasping leaves.'),

        # === MAMMALIA: ARTIODACTYLA (7) ===
        (26, 7, 'Cervus elaphus', 'Red Deer / Elk', '🦌', 'Large even-toed ungulate with impressive antlers (males). Adaptable to forests, mountains, and grasslands. Herd animal.', 'Forest, grassland, moorland, mountains, open woodland', 'Herbivore: grass, heather, shoots, bark, leaves, berries', '10-15 years in wild', 'Europe, Asia, North Africa; introduced to New Zealand, Argentina, Chile', 'Least Concern', 'Stags grow and shed antlers every year (one of the fastest-growing tissues). They bellow loudly during the "rut" (mating season). Only males have antlers.'),
        (27, 7, 'Hippopotamus amphibius', 'Hippopotamus', '🦛', 'Large semi-aquatic even-toed ungulate. Spends daytime in water to prevent skin drying. One of the most dangerous animals in Africa.', 'Rivers, lakes, swamps, wetlands (sub-Saharan Africa)', 'Herbivore: grass, aquatic plants, reeds (eats ~40 kg at night)', '40-50 years', 'Sub-Saharan Africa (rivers and lakes from Senegal to South Africa)', 'Vulnerable', 'Hippos secrete a natural sunscreen ("blood sweat") that is red and acidic. They can hold their breath underwater for 5 minutes. Despite their bulk, they can run at 30 km/h (19 mph). They kill more humans in Africa than any other large animal.'),
        (28, 7, 'Sus scrofa domesticus', 'Domestic Pig', '🐖', 'Even-toed ungulate domesticated 9,000 years ago. Highly intelligent, social, and cleaner than their reputation suggests.', 'Farmland, barns, pastures, domestic', 'Omnivore: grains, vegetables, fruit, roots, insects, small vertebrates', '10-15 years', 'Global (domestic); wild boar native to Europe, Asia, North Africa', 'Domesticated', 'Pigs are as smart as dogs and can play video games with joysticks. They have excellent long-term memory and can navigate mazes faster than children. They are one of the few animals that can recognize themselves in a mirror.'),
        (29, 7, 'Giraffa camelopardalis', 'Giraffe', '🦒', 'Tallest living terrestrial animal and largest ruminant. Unique coat patterns like fingerprints. Long neck for browsing acacia canopies.', 'Savanna, open woodland, grassland (sub-Saharan Africa)', 'Browser herbivore: acacia leaves, twigs, bark, fruit, grass', '20-25 years in wild', 'Sub-Saharan Africa (Kenya, Tanzania, South Africa, Botswana, Namibia)', 'Vulnerable', 'Giraffes have the same number of neck vertebrae as humans (7). Their tongues are bluish-purple to prevent sunburn. They only sleep 30 minutes a day, usually standing up. A giraffe’s kick can kill a lion.'),

        # === MAMMALIA: CHIROPTERA (8) ===
        (30, 8, 'Pteropus vampyrus', 'Large Flying Fox', '🦇', 'One of the largest bat species with a wingspan up to 1.7 meters. Does not use echolocation; relies on vision and smell. Fruit-eating.', 'Tropical rainforest, mangroves, coastal islands', 'Frugivore: figs, bananas, mangoes, nectar, flowers', '15-30 years', 'Southeast Asia (Philippines, Indonesia, Malaysia, Thailand, Myanmar, India)', 'Near Threatened', 'Flying foxes are vital pollinators and seed dispersers. They can fly 50 km in a single night foraging. They drink by swooping down to rivers and lapping water while flying.'),
        (31, 8, 'Myotis lucifugus', 'Little Brown Bat', '🦇', 'Small insectivorous bat common in North America. Uses sophisticated echolocation to hunt mosquitoes and moths.', 'Forests, caves, mines, buildings, attics', 'Insectivore: mosquitoes, moths, beetles, midges (eats up to 1,000/hour)', '6-7 years', 'North America (USA, Canada, Alaska)', 'Endangered', 'Little brown bats can eat 1,000 mosquitoes in a single hour. They hibernate in caves for up to 6 months. White-nose syndrome (a fungal disease) has killed millions in North America.'),

        # === AVES: PASSERIFORMES (9) ===
        (32, 9, 'Corvus corax', 'Common Raven', '🐦‍⬛', 'Large all-black passerine with remarkable problem-solving intelligence. Can mimic human speech, use tools, and plan for future events.', 'Forests, coasts, deserts, tundra, grasslands, cities, mountains', 'Omnivore: carrion, insects, fruit, eggs, small mammals, garbage', '10-15 years', 'Northern Hemisphere (North America, Europe, Asia, North Africa)', 'Least Concern', 'Ravens can mimic human speech better than parrots. They use sticks to get food and have been observed calling wolves to carcasses to tear open tough hides for them. They can remember human faces for years.'),
        (33, 9, 'Passer domesticus', 'House Sparrow', '🐦', 'Small, adaptable passerine found in most human settlements worldwide. Social, noisy, and opportunistic feeder.', 'Urban areas, farmland, grassland, suburbs, villages', 'Omnivore: seeds, insects, breadcrumbs, garbage, fruit', '3-5 years', 'Global (native to Eurasia, introduced worldwide)', 'Least Concern', 'House sparrows are one of the most widespread wild birds. They bathe in dust to keep their feathers clean. Males have black bibs; larger bibs indicate higher status.'),
        (34, 9, 'Parus major', 'Great Tit', '🐦', 'Small, colorful passerine with a black head, white cheeks, and yellow belly. Highly adaptable and intelligent songbird.', 'Woodland, gardens, parks, scrubland', 'Insectivore/Omnivore: caterpillars, spiders, seeds, nuts, suet', '3-5 years', 'Europe, Asia, North Africa, Middle East', 'Least Concern', 'Great tits have been observed using tools to get food. They can open milk bottles (historically in Britain). They cache thousands of seeds in autumn and remember each location.'),

        # === AVES: FALCONIFORMES (10) ===
        (35, 10, 'Aquila chrysaetos', 'Golden Eagle', '🦅', 'Large bird of prey with powerful build and keen eyesight. Hunts mammals as large as foxes and young deer. Monogamous, pairs mate for life.', 'Mountains, hills, cliffs, open country, tundra', 'Carnivore: rabbits, marmots, foxes, birds, young deer, carrion', '15-20 years', 'Northern Hemisphere (North America, Europe, Asia, North Africa)', 'Least Concern', 'Golden eagles can dive at speeds over 240 km/h (150 mph). Their nests (eyries) can be 2 meters wide and used for decades. They have been known to hunt in pairs — one flushes prey while the other ambushes.'),
        (36, 10, 'Falco peregrinus', 'Peregrine Falcon', '🦅', 'Fastest bird in the world, reaching 390 km/h (240 mph) in a hunting stoop. Hunts medium-sized birds in mid-air.', 'Coastal cliffs, skyscrapers, mountains, tundra, urban areas', 'Carnivore: pigeons, ducks, songbirds, bats (catches in flight)', '15-20 years', 'Global (every continent except Antarctica)', 'Least Concern', 'Peregrine falcons were nearly wiped out by DDT pesticide in the 1960s but recovered thanks to conservation. They are popular in falconry and have been used for 3,000 years. They have a tomial tooth on their beak for killing prey instantly.'),

        # === AVES: STRIGIFORMES (11) ===
        (37, 11, 'Bubo virginianus', 'Great Horned Owl', '🦉', 'Powerful, adaptable owl with prominent ear tufts. Hunts mammals larger than itself. Has incredible low-light vision and silent flight feathers.', 'Forest, desert, tundra, urban parks, swamps, grassland', 'Carnivore: rabbits, skunks, geese, cats, foxes, snakes, rodents', '13-15 years', 'North and South America (USA, Canada, Mexico, Brazil, Argentina)', 'Least Concern', 'Great horned owls can carry prey weighing 3 times their own body weight. Their eyes are tube-shaped and cannot move, so they rotate their heads up to 270 degrees. They have no sense of smell, so they are one of the few predators that regularly eats skunks.'),
        (38, 11, 'Tyto alba', 'Barn Owl', '🦉', 'Pale, heart-faced owl with exceptional hearing. Hunts rodents almost exclusively. Silent flight and long legs for snatching prey.', 'Farmland, grassland, open woodland, marshes, barns, churches', 'Carnivore: voles, mice, rats, shrews, small birds', '4-5 years', 'Global (every continent except Antarctica)', 'Least Concern', 'Barn owls can hunt in complete darkness using sound alone. Their heart-shaped face acts as a sound funnel. One barn owl family can eat 3,000 rodents in a single breeding season. They do not hoot — they screech.'),

        # === AVES: SPHENISCIFORMES (12) ===
        (39, 12, 'Aptenodytes forsteri', 'Emperor Penguin', '🐧', 'Largest penguin species, breeds in Antarctic winter. Males incubate eggs on their feet for 64 days without eating, surviving temperatures of -60°C and winds of 200 km/h.', 'Antarctic ice shelves, coastal waters, open sea', 'Carnivore: fish, squid, krill', '15-20 years', 'Antarctica', 'Near Threatened', 'Emperor penguins can dive to 535 meters (1,755 ft) and hold their breath for 20 minutes. Chicks huddle in crèches to stay warm. They toboggan on their bellies to travel quickly over ice.'),
        (40, 12, 'Spheniscus demersus', 'African Penguin', '🐧', 'Endangered penguin native to South African coast. Has distinctive black band and spotted belly pattern. Donkey-like braying call.', 'Coastal islands, rocky shores, beaches (South Africa, Namibia)', 'Carnivore: anchovies, sardines, squid, crustaceans', '10-15 years', 'Southern Africa (South Africa, Namibia)', 'Endangered', 'African penguins are also called jackass penguins for their loud braying call. They can swim at 20 km/h (12 mph) and travel 110 km per day. They have been declining due to overfishing and oil spills.'),

        # === AVES: ANSERIFORMES (13) ===
        (41, 13, 'Anas platyrhynchos', 'Mallard Duck', '🦆', 'Common wild duck found in wetlands worldwide. Male has iridescent green head, female is mottled brown. Ancestor of most domestic duck breeds.', 'Wetlands, ponds, lakes, rivers, parks, urban waterways', 'Omnivore: aquatic plants, insects, seeds, small fish, bread', '5-10 years', 'Northern Hemisphere (North America, Europe, Asia); introduced globally', 'Least Concern', 'Mallards are the ancestors of nearly all domestic ducks except Muscovy. Ducklings imprint on their mother within hours of hatching. They can sleep with one eye open and half their brain awake.'),
        (42, 13, 'Cygnus olor', 'Mute Swan', '🦢', 'Elegant white swan with an orange bill and black knob. Aggressive defender of territory. Can hiss, snort, and flap wings loudly.', 'Lakes, ponds, rivers, marshes, coastal lagoons', 'Herbivore: aquatic plants, grass, algae, grain', '10-20 years', 'Europe, Central Asia, North Africa; introduced to North America, Australia, New Zealand', 'Least Concern', 'Mute swans form monogamous pairs that mate for life. They can weigh up to 15 kg (33 lbs) and are one of the heaviest flying birds. Their wingspan reaches 2.4 meters (8 ft). They are called "mute" because they are less vocal than other swans.'),

        # === REPTILIA: SQUAMATA (14) ===
        (43, 14, 'Python bivittatus', 'Burmese Python', '🐍', 'One of the largest snake species, non-venomous constrictor. Excellent swimmer, often found near water. Invasive in Florida Everglades.', 'Tropical forests, marshes, grasslands, riversides, caves', 'Carnivore: mammals, birds, reptiles (constricts prey)', '20-25 years', 'Southeast Asia (Myanmar, Thailand, Vietnam, Indonesia); invasive in Florida', 'Vulnerable', 'Burmese pythons can grow over 7 meters (23 ft) and weigh 90 kg. They have heat-sensing pits on their lips to detect prey in darkness. They can go months without eating after a large meal.'),
        (44, 14, 'Varanus komodoensis', 'Komodo Dragon', '🐉', 'World’s largest lizard, reaching 3 meters and 70 kg. Venomous bite with toxic proteins and bacteria. Apex predator of Komodo islands.', 'Dry savanna, tropical dry forest, grassland, beaches', 'Carnivore: deer, pigs, water buffalo, birds, eggs, carrion, humans (rarely)', '30+ years', 'Indonesia (Komodo, Rinca, Flores, Gili Motang)', 'Endangered', 'Komodo dragons can consume 80% of their body weight in one meal. Their venom causes shock, blood loss, and paralysis. Females can reproduce via parthenogenesis (without males). They can smell carrion from 9 km away.'),
        (45, 14, 'Chamaeleo chamaeleon', 'Common Chameleon', '🦎', 'Old World lizard famous for color-changing skin, independently moving eyes, and long sticky tongue. Arboreal and slow-moving.', 'Mediterranean forest, scrubland, plantations, gardens', 'Insectivore: flies, grasshoppers, crickets, spiders (catches with ballistic tongue)', '2-3 years', 'Southern Europe, North Africa, Middle East, India, Sri Lanka', 'Least Concern', 'Chameleon tongues are twice their body length and hit prey in 0.07 seconds. They can move each eye independently (360-degree vision). They change color for temperature regulation and communication, not just camouflage.'),
        (46, 14, 'Naja naja', 'Indian Cobra', '🐍', 'Highly venomous snake with a distinctive hood bearing a spectacle pattern. Sacred in Hindu culture and used by snake charmers.', 'Grassland, forests, agricultural areas, wetlands, urban areas', 'Carnivore: rodents, frogs, birds, other snakes, lizards', '15-20 years', 'Indian subcontinent (India, Pakistan, Bangladesh, Sri Lanka, Nepal)', 'Least Concern', 'Cobra venom is neurotoxic and can kill an elephant. They can rise up to one-third of their body length and "stand" to look a human in the eye. Snake charmers remove their fangs (painful and illegal).'),

        # === REPTILIA: TESTUDINES (15) ===
        (47, 15, 'Chelonia mydas', 'Green Sea Turtle', '🐢', 'Large sea turtle named for green fat under its shell (from vegetarian diet). Travels thousands of km to return to the same beach where it hatched.', 'Tropical and subtropical oceans, beaches, coral reefs, seagrass beds', 'Herbivore (adult): seagrass, algae; Carnivore (juvenile): jellyfish, invertebrates', '60-80 years', 'Tropical and subtropical oceans worldwide (Atlantic, Pacific, Indian)', 'Endangered', 'Green sea turtles can hold their breath for 5 hours while resting. Only 1 in 1,000 hatchlings survives to adulthood. They use Earth’s magnetic field to navigate thousands of km back to their birth beach.'),
        (48, 15, 'Testudo graeca', 'Spur-thighed Tortoise', '🐢', 'Small to medium terrestrial tortoise with distinctive spurs on thighs. Hibernates in winter and aestivates in summer. Long-lived pet.', 'Mediterranean scrubland, grassland, forests, farmlands, rocky hills', 'Herbivore: grass, leaves, flowers, fruit, vegetables', '50-100+ years', 'North Africa, Southern Europe, Middle East, Central Asia', 'Vulnerable', 'Tortoises can live over 100 years. They absorb water through their skin and shell. They have a third "eye" (parietal eye) on top of their head to sense light and shadows.'),

        # === REPTILIA: CROCODILIA (16) ===
        (49, 16, 'Crocodylus niloticus', 'Nile Crocodile', '🐊', 'Africa’s largest crocodile and apex freshwater predator. Ambush hunter that takes prey as large as buffalo and zebras. Females fiercely guard nests.', 'Rivers, lakes, swamps, marshes, estuaries (sub-Saharan Africa)', 'Carnivore: fish, amphibians, birds, mammals (antelope, buffalo, humans)', '70-100 years', 'Sub-Saharan Africa, Madagascar', 'Least Concern', 'Nile crocodiles have the strongest bite force ever measured (5,000 psi). They can hold their breath underwater for 2 hours. They swallow stones to help grind food and aid buoyancy. They are more dangerous to humans than any other crocodile species.'),
        (50, 16, 'Alligator mississippiensis', 'American Alligator', '🐊', 'Large crocodilian found in the southeastern United States. Can survive freezing temperatures by sticking its snout above ice to breathe.', 'Freshwater swamps, marshes, rivers, lakes, bayous (Florida, Louisiana, Georgia, Texas)', 'Carnivore: fish, turtles, mammals, birds, carrion', '35-50 years', 'Southeastern United States (Florida, Louisiana, Alabama, Georgia, Texas, Carolinas)', 'Least Concern', 'Alligators can regrow lost teeth up to 50 times. They are farmed for meat and leather. They were saved from extinction by conservation — a rare success story. They bellow loudly during mating season, creating water "dances" on their backs.'),

        # === AMPHIBIA: ANURA (17) ===
        (51, 17, 'Rana temporaria', 'Common Frog', '🐸', 'Widespread European frog with smooth skin and long jumping legs. First frog to return to ponds after winter. Indicator species for healthy wetlands.', 'Ponds, lakes, marshes, damp woodlands, gardens', 'Carnivore: insects, slugs, worms, spiders, small fish (tadpoles are herbivores)', '5-10 years', 'Europe, northwest Asia (UK, France, Germany, Scandinavia, Russia)', 'Least Concern', 'Common frogs can change color to camouflage. They hibernate at the bottom of ponds in winter. They absorb water through their skin rather than drinking. Tadpoles are herbivores; metamorphosis transforms their digestive system to carnivore.'),
        (52, 17, 'Dendrobates tinctorius', 'Dyeing Poison Dart Frog', '🐸', 'Brilliantly colored frog with aposematic (warning) coloration. Toxic skin secretions used by indigenous people to poison blowgun darts.', 'Tropical rainforest floor, near streams, humid microhabitats', 'Insectivore: ants, termites, mites, beetles, small spiders', '4-6 years', 'Guiana Shield (Suriname, Guyana, French Guiana, Brazil)', 'Least Concern', 'Poison dart frogs are not toxic in captivity — their toxins come from wild ants and mites. They are popular in the pet trade. They lay eggs in leaf litter and carry tadpoles on their backs to water pools.'),
        (53, 17, 'Lithobates catesbeianus', 'American Bullfrog', '🐸', 'Large, aggressive frog native to North America. Invasive in many countries. Eats anything that fits in its mouth. Deep jug-o-rum call.', 'Lakes, ponds, marshes, slow rivers, artificial reservoirs', 'Carnivore: insects, spiders, crayfish, small mammals, snakes, birds, other frogs', '8-10 years', 'North America (eastern USA, Canada); invasive in Europe, Asia, South America', 'Least Concern', 'Bullfrogs are invasive in over 40 countries and eat native species. They have no natural predators outside their native range. They are the largest frog in North America. Males are highly territorial and fight violently.'),

        # === AMPHIBIA: URODELA (18) ===
        (54, 18, 'Ambystoma mexicanum', 'Axolotl', '🦎', 'Neotenic salamander that retains juvenile features (gills, fins) throughout life. Can regenerate limbs, heart, spinal cord, and parts of its brain.', 'Lake Xochimilco and Lake Chalco (Mexico City freshwater canals)', 'Carnivore: worms, insects, small fish, crustaceans (suction feeding)', '10-15 years', 'Mexico (Lake Xochimilco, Mexico City — critically endangered in wild)', 'Critically Endangered', 'Axolotls can regenerate their entire limbs, spinal cord, heart, and parts of their brain without scarring. They are popular in research and as pets. In the wild, they are nearly extinct due to pollution and invasive fish. They come in wild-type brown, leucistic (pink), and albino forms.'),
        (55, 18, 'Salamandra salamandra', 'Fire Salamander', '🦎', 'Striking black-and-yellow amphibian. Secretes potent neurotoxin from skin glands when threatened. Gives birth to live larvae in water.', 'Deciduous forest, moist woodlands, rocky hills, near streams', 'Insectivore: beetles, spiders, slugs, worms, millipedes', '10-15 years', 'Central and Southern Europe (Germany, France, Italy, Spain, Balkans)', 'Least Concern', 'Fire salamanders are one of the few salamanders that give birth to live young (most lay eggs). Their bright yellow warns predators of toxicity. Their skin secretions contain samandarine, which can cause convulsions and death in predators.'),

        # === INSECTA: LEPIDOPTERA (19) ===
        (56, 19, 'Danaus plexippus', 'Monarch Butterfly', '🦋', 'Famous migratory butterfly traveling up to 4,800 km (3,000 miles) from Canada to Mexico. Four generations complete the round trip. Milkweed specialist.', 'Meadows, fields, gardens, roadsides, forests, prairies', 'Herbivore: milkweed nectar and leaves (larvae only eat milkweed)', '6 months (migratory generation)', 'North & Central America (USA, Canada, Mexico); introduced to Australia, Spain, New Zealand', 'Endangered', 'Monarchs are poisonous to predators because milkweed toxins accumulate in their bodies. They navigate using a circadian clock and a sun compass. The fourth generation lives 8 times longer than the others to make the migration.'),
        (57, 19, 'Actias luna', 'Luna Moth', '🦋', 'Large pale-green moth with long hindwing tails and dramatic eyespots. Adults do not eat — they have no mouths and live only to reproduce.', 'Deciduous forests, woodlands, suburban areas', 'Larvae: herbivore (leaves of birch, walnut, hickory, sumac); Adults: no mouth, do not eat', '1 week (adult), 2-3 months (larva)', 'Eastern North America (USA, Canada)', 'Least Concern', 'Luna moth adults live only about 7 days and never eat. Their long tails spin like a propeller to confuse bat echolocation. They are one of the largest moths in North America with a 12 cm wingspan. They emerge from cocoons only in the morning.'),
        (58, 19, 'Papilio machaon', 'Old World Swallowtail', '🦋', 'Large yellow-and-black butterfly with distinctive tail-like extensions on hindwings. Strong flier, often seen gliding over meadows.', 'Meadows, fields, gardens, coastal cliffs, fens', 'Herbivore: nectar (adult); leaves of carrot, fennel, parsley, rue (larvae)', '1-2 months (adult stage)', 'Europe, Asia, North Africa', 'Least Concern', 'Swallowtail caterpillars have a retractable organ called an osmeterium that emits a foul smell to deter predators. They are one of the largest butterflies in Europe with a wingspan up to 10 cm.'),

        # === INSECTA: COLEOPTERA (20) ===
        (59, 20, 'Lucanus cervus', 'Stag Beetle', '🪲', 'Large beetle with oversized antler-like mandibles (males) used for fighting. Despite fearsome appearance, they are harmless and cannot bite humans.', 'Deciduous woodland, parks, gardens, hedgerows, orchards', 'Larvae: detritivore (decaying wood); Adults: tree sap, fruit, nectar', '3-7 years (mostly as larvae), 2-5 months as adult', 'Europe, Asia (UK, France, Germany, Scandinavia, Russia, Japan)', 'Least Concern', 'Stag beetles spend 3-7 years as larvae inside rotting wood, then emerge as adults for only a few weeks to mate. Males fight by locking antlers and trying to throw each other. Their jaws are too weak to bite humans.'),
        (60, 20, 'Coccinella septempunctata', 'Seven-spotted Ladybug', '🐞', 'Most recognizable ladybug with seven black spots on red elytra. Aphid predator, widely used in biological pest control.', 'Gardens, meadows, fields, forests, agricultural areas', 'Carnivore: aphids, mites, scale insects, mealybugs (larvae eat 400 aphids before pupating)', '1-2 years', 'Europe, Asia, North Africa; introduced to North America', 'Least Concern', 'Ladybugs can play dead and secrete foul-tasting yellow fluid from their legs when threatened. They hibernate in clusters of thousands. A single ladybug can eat 5,000 aphids in its lifetime.'),

        # === INSECTA: HYMENOPTERA (21) ===
        (61, 21, 'Apis mellifera', 'Western Honey Bee', '🐝', 'Primary pollinator of crops worldwide. Lives in complex hives with a single queen, thousands of workers, and hundreds of drones. Performs waggle dance to communicate food locations.', 'Meadows, gardens, agricultural areas, orchards, forests', 'Herbivore: nectar, pollen, honeydew (honey is stored food for winter)', '5-6 weeks (summer worker), 4-6 months (winter worker), 2-5 years (queen)', 'Worldwide (human-introduced and domesticated)', 'Least Concern (species), but populations declining globally', 'Honey bees perform a "waggle dance" that encodes the direction, distance, and quality of food sources. They are responsible for pollinating one-third of the food we eat. A hive contains 20,000-80,000 bees. They flap their wings 230 times per second.'),
        (62, 21, 'Vespa mandarinia', 'Asian Giant Hornet', '🐝', 'World’s largest hornet (5 cm long). Known as "murder hornet" for its ability to destroy honey bee colonies. Powerful venom and aggressive defense of nests.', 'Forests, low mountains, rural areas (nests in tree hollows or underground)', 'Carnivore: honey bees, other insects, tree sap, honey (feeds larvae with chewed prey)', '3-5 months (workers), 1 year (queen)', 'East Asia, Southeast Asia (Japan, China, Korea, Taiwan, Nepal, India)', 'Least Concern', 'Asian giant hornets can kill 40 honey bees per minute. Their sting is painful but not deadly to humans unless allergic or stung many times. A small team of hornets can destroy a hive of 30,000 bees in hours. They are a delicacy in Japan.'),
        (63, 21, 'Formica rufa', 'Southern Wood Ant', '🐜', 'Large red-and-black ant that builds massive dome-shaped mounds from pine needles. Highly territorial and aggressive defenders. Important forest predator.', 'Coniferous and mixed forests, woodlands, heathlands', 'Carnivore/Omnivore: insects, honeydew from aphids, seeds, small vertebrates', '6-10 years (queen), 2-3 months (workers)', 'Europe, Asia (UK, Scandinavia, Germany, France, Russia, Japan)', 'Least Concern', 'Wood ant mounds can be 1 meter tall and contain 500,000 ants. They spray formic acid from their abdomens as a defense. They herd aphids like cattle and "milk" them for honeydew. They are apex predators of the forest floor.'),
        (64, 21, 'Bombus terrestris', 'Buff-tailed Bumblebee', '🐝', 'Large, fuzzy bee with a distinctive buff-colored tail. Important pollinator for tomatoes, peppers, and berries. Can fly in cold weather.', 'Gardens, meadows, farmland, woodlands, hedgerows', 'Herbivore: nectar, pollen (especially legumes, foxgloves, raspberry)', '2-6 months (workers), 1 year (queen)', 'Europe, North Africa, Middle East; introduced to New Zealand, Tasmania, Chile', 'Least Concern', 'Bumblebees can fly in temperatures as low as 5°C and are vital early-spring pollinators. They buzz-pollinate by shaking flowers to release pollen. A queen can lay up to 2,000 eggs. They are less aggressive than honey bees and rarely sting.'),

        # === INSECTA: ORTHOPTERA (22) ===
        (65, 22, 'Gryllus campestris', 'Field Cricket', '🦗', 'Black cricket famous for its loud chirping song produced by rubbing wings together (stridulation). Male song attracts females and warns rivals.', 'Grassland, meadows, forest edges, heathland, farmland', 'Omnivore: grass, seeds, insects, fruit, decaying matter', '2-3 months (adult), 1 year total lifecycle', 'Europe, North Africa, Asia (UK, France, Germany, Spain, Russia, Turkey)', 'Least Concern', 'Crickets chirp faster in warmer weather. You can estimate temperature by counting chirps: (chirps in 14 seconds + 40) = °F. They have ears on their front legs. In many cultures, crickets are kept as pets for good luck.'),
        (66, 22, 'Locusta migratoria', 'Migratory Locust', '🦗', 'Swarming grasshopper that undergoes density-dependent phase change — solitary green insects become gregarious black-and-yellow swarm members.', 'Grassland, savanna, semi-desert, agricultural areas', 'Herbivore: grasses, cereals, crops, bamboo, leaves (eats own weight daily)', '3-6 months', 'Africa, Asia, Australia, Europe (migratory swarms cross continents)', 'Least Concern', 'A single locust swarm can contain billions of individuals and cover 1,200 km². They eat 200,000 tonnes of vegetation per day. Swarms can travel 150 km per day. Locusts are edible and a good source of protein.'),

        # === ARACHNIDA: ARANEAE (23) ===
        (67, 23, 'Latrodectus mactans', 'Black Widow', '🕷️', 'Venomous spider famous for the red hourglass marking on its abdomen. Shiny black, web-building. Bite is rarely fatal to humans but causes severe pain.', 'Dark sheltered areas: woodpiles, sheds, caves, basements, garages, under rocks', 'Carnivore: insects, scorpions, centipedes, other spiders (ensnares in tangled webs)', '1-3 years', 'North & South America, Caribbean (USA, Mexico, Brazil, Argentina)', 'Least Concern', 'Black widow venom is 15 times stronger than rattlesnake venom, but bites are rarely fatal because they inject little venom. Females sometimes eat males after mating (hence the name). They are shy and bite only when disturbed.'),
        (68, 23, 'Araneus diadematus', 'European Garden Spider', '🕷️', 'Common orb-weaver with a white cross pattern on its abdomen. Builds beautiful spiral webs and sits head-down in the center.', 'Gardens, meadows, hedgerows, woodlands, parks, fields', 'Carnivore: flies, mosquitoes, moths, butterflies, beetles (caught in orb web)', '1-2 years', 'Europe, North America (introduced)', 'Least Concern', 'Garden spiders eat their webs each night and recycle the silk to build a new one. They vibrate the web to identify prey vs. debris. The cross pattern is thought to attract insects by reflecting UV light. They wrap prey in silk faster than you can blink.'),

        # === ARACHNIDA: SCORPIONES (24) ===
        (69, 24, 'Androctonus australis', 'Fat-tailed Scorpion', '🦂', 'One of the most dangerous scorpions in the world. Thick, powerful tail with a large venom bulb. Yellow to orange coloration.', 'Desert, semi-desert, arid rocky areas, sandy scrubland', 'Carnivore: insects, spiders, centipedes, small lizards, other scorpions (cannibalistic)', '4-6 years', 'North Africa, Middle East (Morocco, Algeria, Tunisia, Libya, Egypt, Israel, Saudi Arabia)', 'Not Evaluated', 'Fat-tailed scorpion venom is highly neurotoxic and can kill a human in hours without antivenom. They glow bright blue-green under UV light (blacklight). They are nocturnal and hide under rocks during the day. They can survive months without food.'),
        (70, 24, 'Hadrurus arizonensis', 'Giant Hairy Scorpion', '🦂', 'Largest scorpion in North America, reaching 14 cm. Hairy body helps detect vibrations in sand. Burrows deep in desert soil.', 'Desert, sandy washes, arid grassland, rocky slopes', 'Carnivore: insects, spiders, small lizards, centipedes, other scorpions', '15-20 years', 'Southwestern USA (Arizona, California, Nevada, Utah), Northwestern Mexico', 'Least Concern', 'Despite their size and fearsome appearance, their sting is relatively mild — like a bee sting. They are popular in the exotic pet trade. They can sense vibrations through the ground and ambush prey at burrow entrances. They are the largest scorpion in North America.'),

        # === PISCES: PERCIFORMES (25) ===
        (71, 25, 'Thunnus thynnus', 'Atlantic Bluefin Tuna', '🐟', 'Warm-blooded fish capable of speeds up to 75 km/h. Highly migratory, crossing entire oceans. Prized for sushi, severely overfished.', 'Open ocean, pelagic, coastal waters (temperate and cold seas)', 'Carnivore: herring, mackerel, squid, crustaceans, other fish', '15-30 years', 'Atlantic Ocean (Mediterranean, Gulf of Mexico, North Atlantic)', 'Near Threatened', 'Bluefin tuna are warm-blooded (endothermic) — rare for fish. They can cross the Atlantic in 60 days. A single fish can sell for $3 million at Tokyo auctions. They can swim at 75 km/h and dive to 1,000 meters. Their body temperature can be 20°C above water temperature.'),
        (72, 25, 'Amphiprion ocellaris', 'Clownfish', '🐠', 'Famous reef fish that lives symbiotically with sea anemones. Immune to anemone stings. All clownfish are born male; dominant one becomes female.', 'Tropical coral reefs, lagoons, rocky reefs, sea anemones', 'Omnivore: algae, zooplankton, small crustaceans, leftovers from anemone meals', '6-10 years', 'Indo-Pacific (Red Sea, Indian Ocean, Southeast Asia, Australia, Western Pacific)', 'Least Concern', 'Clownfish have a mucus layer that makes them immune to anemone stings. They are sequential hermaphrodites: all start as male and the dominant one becomes female. They defend their anemone territory aggressively. They were popularized by the movie "Finding Nemo."'),
        (73, 25, 'Perca fluviatilis', 'European Perch', '🐟', 'Freshwater fish with distinctive dark vertical bars and red lower fins. Popular sport fish and food fish in Europe.', 'Lakes, ponds, rivers, canals, reservoirs, brackish waters', 'Carnivore: zooplankton (juveniles), insects, crustaceans, small fish (adults)', '6-8 years', 'Europe, Northern Asia (UK, Scandinavia, Germany, Russia, China)', 'Least Concern', 'Perch are one of the most widely distributed freshwater fish in Europe. They school in open water but hunt alone near the bottom. They have spiny dorsal fins that can injure predators. They are popular in aquaculture and recreational fishing.'),

        # === PISCES: CARCHARHINIFORMES (26) ===
        (74, 26, 'Carcharhinus leucas', 'Bull Shark', '🦈', 'Aggressive shark known for entering freshwater rivers and lakes. Responsible for many near-shore attacks. Can tolerate brackish and fresh water.', 'Coastal marine, estuaries, rivers, lakes (can enter freshwater hundreds of km inland)', 'Carnivore: fish, dolphins, turtles, birds, stingrays, other sharks, mammals', '12-16 years', 'Worldwide tropical and subtropical waters (Atlantic, Pacific, Indian Ocean)', 'Near Threatened', 'Bull sharks can survive in freshwater and have been found 4,200 km up the Amazon River. They have been found in the Mississippi River as far north as Illinois. They give birth in freshwater to protect pups from predators. They are one of the "Big Three" sharks responsible for attacks on humans.'),
        (75, 26, 'Carcharodon carcharias', 'Great White Shark', '🦈', 'Apex predator of the ocean, up to 6 meters long. Can detect a drop of blood from 5 km away. Warm-blooded fish (endothermic).', 'Coastal and offshore temperate waters, island shelves, continental shelves', 'Carnivore: seals, sea lions, fish, dolphins, whales, sea turtles, carrion', '70+ years', 'Coastal waters of all major oceans (USA, South Africa, Australia, Mexico, Japan, Mediterranean)', 'Vulnerable', 'Great whites can breach (jump) 3 meters out of the water to catch seals. They have 300 serrated teeth arranged in rows and can lose 20,000 teeth in a lifetime. They are warm-blooded, maintaining body temperature above water. They are not man-eaters — humans are too bony.'),
        (76, 26, 'Sphyrna mokarran', 'Great Hammerhead', '🦈', 'Largest hammerhead species with cephalofoil (hammer-shaped head) that provides 360-degree vision and enhanced electroreception. Solitary hunter.', 'Coastal warm waters, continental shelves, coral reefs, deep waters', 'Carnivore: stingrays, fish, squid, crustaceans, other sharks (specializes in hunting stingrays)', '20-30 years', 'Tropical waters worldwide (Atlantic, Pacific, Indian Ocean, Caribbean, Red Sea)', 'Critically Endangered', 'Hammerhead sharks have a 360-degree field of vision because their eyes are placed at the ends of the hammer. Their heads are packed with electroreceptors that detect stingrays buried in sand. They are critically endangered due to finning and bycatch. They give birth to live pups.'),

        # === PISCES: ANGUILLIFORMES (27) ===
        (77, 27, 'Anguilla anguilla', 'European Eel', '🐍', 'Snake-like fish that migrates 6,000 km to the Sargasso Sea to spawn. Catadromous (lives in freshwater, spawns in saltwater). Critically endangered.', 'Rivers, streams, lakes, ponds, estuaries (freshwater and brackish)', 'Carnivore: insects, crustaceans, worms, small fish, mollusks, carrion', '15-20 years (some up to 85 years)', 'Europe, North Africa, Mediterranean (spawns in Sargasso Sea, Atlantic)', 'Critically Endangered', 'European eels are born in the Sargasso Sea and drift as larvae for a year to reach Europe. They can live over 80 years. They can survive on damp land for hours, crossing between ponds. Their population has declined by 90% since the 1970s. They are a delicacy in Europe (jellied eels, unagi).'),
        (78, 27, 'Gymnothorax javanicus', 'Giant Moray Eel', '🐍', 'Largest moray eel, reaching 3 meters. Hides in reef crevices with mouth open (for breathing, not aggression). Sharp teeth, poor eyesight.', 'Coral reefs, rocky reefs, lagoons, drop-offs (tropical Indo-Pacific)', 'Carnivore: fish, octopus, squid, crustaceans (hunts by smell, ambushes from caves)', '30+ years', 'Indo-Pacific (Red Sea, East Africa, Japan, Australia, Polynesia)', 'Least Concern', 'Moray eels have a second set of jaws (pharyngeal jaws) that shoot forward to pull prey down their throat. They are not aggressive but have poor eyesight and may bite if cornered. They partner with grouper fish to hunt — grouper point to prey, eels flush it out.'),

        # === CRUSTACEA: DECAPODA (28) ===
        (79, 28, 'Cancer pagurus', 'Edible Crab / Brown Crab', '🦀', 'Large brown crab common in the North Sea. Powerful claws for crushing shells. Important commercial seafood species.', 'Rocky seabed, sandy/muddy bottoms, kelp beds (5-50 m depth)', 'Omnivore: molluscs, worms, algae, carrion, small crustaceans', '20-30 years', 'Northeast Atlantic, North Sea, Baltic Sea, Mediterranean (UK, Norway, France, Spain)', 'Least Concern', 'Edible crabs can crush shells with claws exerting pressure over 500 N. They are right-handed or left-handed (one claw is larger). They walk sideways because their legs are jointed that way. They molt their shell to grow.'),
        (80, 28, 'Homarus americanus', 'American Lobster', '🦞', 'Large marine crustacean with heavy claws and muscular tail. Changes color from blue-green to bright red when cooked. Long-lived benthic predator.', 'Rocky seabed, coastal waters, continental shelf (1-700 m depth)', 'Omnivore: fish, mollusks, worms, crustaceans, sea urchins, carrion', '50+ years (some over 100 years)', 'Northwestern Atlantic (Canada, Maine, Massachusetts, North Carolina)', 'Least Concern', 'Lobsters can live over 100 years and never stop growing. They have blue blood (hemocyanin) like spiders. They have a dominant claw (crusher) and a slender one (cutter). They molt up to 25 times in their first 5 years. They taste with their legs and chew with their stomachs.'),
        (81, 28, 'Callinectes sapidus', 'Blue Crab', '🦀', 'Atlantic crab named for blue claws. Fast swimmer with paddle-shaped rear legs. Iconic seafood in Chesapeake Bay and Gulf of Mexico.', 'Estuaries, bays, seagrass beds, coastal waters, rivers', 'Omnivore: fish, mollusks, worms, plants, detritus, carrion', '2-3 years', 'Western Atlantic (Chesapeake Bay, Gulf of Mexico, Caribbean, South America)', 'Not Evaluated', 'Blue crabs are cannibalistic and aggressive. They can swim sideways and backward using their paddle legs. Their scientific name means "savory beautiful swimmer." They are one of the most valuable fisheries in the USA. They molt 20+ times before reaching adulthood.'),

        # === CRUSTACEA: STOMATOPODA (29) ===
        (82, 29, 'Odontodactylus scyllarus', 'Peacock Mantis Shrimp', '🦐', 'Marine crustacean with the most complex eyes in the animal kingdom (12-16 photoreceptors). Clubs strike with the acceleration of a .22 caliber bullet.', 'Coral reefs, rocky crevices, burrows in rubble (tropical Indo-Pacific)', 'Carnivore: gastropods, crabs, mollusks, shrimp, fish (smashes or spears prey)', '4-6 years', 'Indo-Pacific (Red Sea, East Africa, Australia, Japan, Hawaii, Polynesia)', 'Least Concern', 'Mantis shrimp punches reach 23 m/s with 1,500 N of force — enough to break aquarium glass. They see ultraviolet, infrared, and polarized light. Their strike is so fast it creates cavitation bubbles that flash with light and heat (sonoluminescence). They are highly aggressive and solitary.'),
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
    print("Database created with 8 classes, 29 orders, and 82 species!")