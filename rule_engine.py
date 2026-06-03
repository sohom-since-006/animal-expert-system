"""
rule_engine.py — Forward-chaining expert system with EXPLAINABILITY.

Returns:
  • taxon_class, taxon_order  (or None)
  • confidence_score          (0-100)
  • reasoning_chain           (human-readable rule trace)
  • alternatives              (other possible matches with scores)
"""

from database import get_classes, get_orders, get_species


RULES = [
    # Class-level rules
    {
        "name": "Mammal Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "fur"},
        "class_id": 1, "order_id": None,
        "confidence": 85,
        "explain": "IF Vertebrate AND Warm-blooded AND Fur/Hair THEN Class = Mammalia"
    },
    {
        "name": "Bird Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "feathers"},
        "class_id": 2, "order_id": None,
        "confidence": 98,
        "explain": "IF Vertebrate AND Warm-blooded AND Feathers THEN Class = Aves"
    },
    {
        "name": "Reptile Rule (scales)",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "scales"},
        "class_id": 3, "order_id": None,
        "confidence": 90,
        "explain": "IF Vertebrate AND Cold-blooded AND Scales THEN Class = Reptilia"
    },
    {
        "name": "Amphibian Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "moist_skin"},
        "class_id": 4, "order_id": None,
        "confidence": 92,
        "explain": "IF Vertebrate AND Cold-blooded AND Moist Skin THEN Class = Amphibia"
    },
    {
        "name": "Fish Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "scales", "aquatic": 1},
        "class_id": 7, "order_id": None,
        "confidence": 88,
        "explain": "IF Vertebrate AND Cold-blooded AND Scales AND Aquatic THEN Class = Pisces"
    },
    {
        "name": "Insect Rule",
        "conditions": {"has_backbone": 0, "body_covering": "none"},
        "class_id": 5, "order_id": None,
        "confidence": 75,
        "explain": "IF Invertebrate AND Bare/Chitin THEN Class = Insecta"
    },
    {
        "name": "Arachnid Rule",
        "conditions": {"has_backbone": 0, "body_covering": "shell"},
        "class_id": 6, "order_id": None,
        "confidence": 70,
        "explain": "IF Invertebrate AND Shell/Exoskeleton THEN Class = Arachnida / Crustacea"
    },
    {
        "name": "Crustacean Rule",
        "conditions": {"has_backbone": 0, "body_covering": "shell", "aquatic": 1},
        "class_id": 8, "order_id": None,
        "confidence": 78,
        "explain": "IF Invertebrate AND Shell AND Aquatic THEN Class = Crustacea"
    },
    # Order-level rules (examples)
    {
        "name": "Carnivora Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "fur", "diet": "carnivore"},
        "class_id": 1, "order_id": 1,
        "confidence": 88,
        "explain": "IF Mammal AND Carnivorous Diet THEN Order = Carnivora"
    },
    {
        "name": "Primate Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "fur", "diet": "omnivore"},
        "class_id": 1, "order_id": 2,
        "confidence": 72,
        "explain": "IF Mammal AND Omnivorous Diet THEN Order = Primates (possible)"
    },
    {
        "name": "Bird of Prey Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "feathers", "diet": "carnivore", "has_wings": 1},
        "class_id": 2, "order_id": 10,
        "confidence": 90,
        "explain": "IF Bird AND Carnivore AND Wings THEN Order = Falconiformes (Birds of Prey)"
    },
    {
        "name": "Waterfowl Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "feathers", "aquatic": 1, "has_wings": 1},
        "class_id": 2, "order_id": 13,
        "confidence": 85,
        "explain": "IF Bird AND Aquatic AND Wings THEN Order = Anseriformes (Waterfowl)"
    },
    {
        "name": "Penguin Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "feathers", "aquatic": 1, "has_wings": 0},
        "class_id": 2, "order_id": 12,
        "confidence": 94,
        "explain": "IF Bird AND Aquatic AND Flightless THEN Order = Sphenisciformes (Penguins)"
    },
    {
        "name": "Bat Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "fur", "has_wings": 1, "diet": "insectivore"},
        "class_id": 1, "order_id": 8,
        "confidence": 92,
        "explain": "IF Mammal AND Fur AND Wings AND Insectivore THEN Order = Chiroptera (Bats)"
    },
    {
        "name": "Cetacean Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 1, "body_covering": "fur", "aquatic": 1, "has_wings": 0, "diet": "carnivore"},
        "class_id": 1, "order_id": 4,
        "confidence": 90,
        "explain": "IF Mammal AND Aquatic AND Fur AND Carnivore THEN Order = Cetacea (Whales/Dolphins)"
    },
    {
        "name": "Snake Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "scales", "reproduction": "eggs_land", "diet": "carnivore"},
        "class_id": 3, "order_id": 14,
        "confidence": 82,
        "explain": "IF Reptile AND Scales AND Eggs(Land) AND Carnivore THEN Order = Squamata (Snakes/Lizards)"
    },
    {
        "name": "Turtle Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "shell", "diet": "herbivore"},
        "class_id": 3, "order_id": 15,
        "confidence": 88,
        "explain": "IF Reptile AND Shell AND Herbivore THEN Order = Testudines (Turtles)"
    },
    {
        "name": "Frog Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "moist_skin", "reproduction": "eggs_water", "diet": "carnivore", "aquatic": 1},
        "class_id": 4, "order_id": 17,
        "confidence": 86,
        "explain": "IF Amphibian AND Moist Skin AND Eggs(Water) AND Aquatic THEN Order = Anura (Frogs)"
    },
    {
        "name": "Butterfly Rule",
        "conditions": {"has_backbone": 0, "body_covering": "none", "reproduction": "metamorphosis", "has_wings": 1, "diet": "herbivore"},
        "class_id": 5, "order_id": 19,
        "confidence": 84,
        "explain": "IF Invertebrate AND Metamorphosis AND Wings THEN Order = Lepidoptera (Butterflies/Moths)"
    },
    {
        "name": "Bee Rule",
        "conditions": {"has_backbone": 0, "body_covering": "none", "reproduction": "metamorphosis", "has_wings": 1, "diet": "herbivore"},
        "class_id": 5, "order_id": 21,
        "confidence": 76,
        "explain": "IF Invertebrate AND Metamorphosis AND Wings THEN Order = Hymenoptera (Bees/Ants/Wasps)"
    },
    {
        "name": "Spider Rule",
        "conditions": {"has_backbone": 0, "body_covering": "shell", "diet": "carnivore", "has_wings": 0, "aquatic": 0},
        "class_id": 6, "order_id": 23,
        "confidence": 80,
        "explain": "IF Invertebrate AND Shell AND Carnivore AND Terrestrial THEN Order = Araneae (Spiders)"
    },
    {
        "name": "Shark Rule",
        "conditions": {"has_backbone": 1, "warm_blooded": 0, "body_covering": "scales", "aquatic": 1, "diet": "carnivore"},
        "class_id": 7, "order_id": 26,
        "confidence": 87,
        "explain": "IF Fish AND Scales AND Aquatic AND Carnivore THEN Order = Carcharhiniformes (Ground Sharks)"
    },
    {
        "name": "Crab Rule",
        "conditions": {"has_backbone": 0, "body_covering": "shell", "aquatic": 1, "diet": "omnivore"},
        "class_id": 8, "order_id": 28,
        "confidence": 83,
        "explain": "IF Invertebrate AND Shell AND Aquatic AND Omnivore THEN Order = Decapoda (Crabs/Lobsters)"
    },
]


def _match_score(rule_conditions, facts):
    """Calculate how many conditions match. Returns (matches, total, score_pct)."""
    total = len(rule_conditions)
    matches = 0
    for key, expected in rule_conditions.items():
        actual = facts.get(key)
        if actual is not None and actual == expected:
            matches += 1
    # Weighted: direct match = 1.0, missing fact = 0.0
    score = (matches / total) if total else 0
    return matches, total, score


def classify(facts):
    """
    Forward-chaining classification with full explainability.
    Returns dict ready for JSON serialization.
    """
    reasoning = []
    reasoning.append("🔍 Starting forward-chaining inference...")
    reasoning.append(f"📥 Received facts: {facts}")

    # Score every rule
    scored = []
    for r in RULES:
        m, t, s = _match_score(r["conditions"], facts)
        weighted = s * r["confidence"]  # rule confidence weighting
        scored.append({
            "rule": r,
            "matches": m,
            "total": t,
            "score": round(s, 2),
            "weighted": round(weighted, 2),
        })
        if s > 0:
            status = "✅ FULL MATCH" if s == 1 else f"⚠️ Partial match ({m}/{t})"
            reasoning.append(f"{status}: [{r['name']}] {r['explain']} → weighted={weighted:.1f}")

    scored.sort(key=lambda x: x["weighted"], reverse=True)

    if not scored or scored[0]["weighted"] == 0:
        reasoning.append("❌ No matching rules found. Insufficient data.")
        return {
            "success": False,
            "message": "Could not classify with given traits. Try providing more information.",
            "reasoning": reasoning,
            "alternatives": []
        }

    winner = scored[0]
    rule = winner["rule"]

    # Fetch DB records
    cls_row = None
    ord_row = None
    species_list = []

    classes = {c["id"]: c for c in get_classes()}
    orders = {o["id"]: o for o in get_orders()}

    cls_row = classes.get(rule["class_id"])
    if rule["order_id"]:
        ord_row = orders.get(rule["order_id"])

    # Species-level: try to find exact species from DB for this order
    if ord_row:
        species_list = get_species(order_id=rule["order_id"])
    elif cls_row:
        # fallback: get all species in class
        species_list = get_species(class_id=rule["class_id"])

    confidence = int(min(winner["weighted"], 100))

    # Build alternatives (next 3 best matches with different outcomes)
    alts = []
    seen = set()
    seen.add((rule.get("class_id"), rule.get("order_id")))
    for entry in scored[1:]:
        key = (entry["rule"].get("class_id"), entry["rule"].get("order_id"))
        if key not in seen and entry["weighted"] > 20:
            seen.add(key)
            alt_cls = classes.get(entry["rule"]["class_id"])
            alt_ord = orders.get(entry["rule"]["order_id"]) if entry["rule"]["order_id"] else None
            alts.append({
                "name": entry["rule"]["name"],
                "class_name": alt_cls["common_name"] if alt_cls else "Unknown",
                "order_name": alt_ord["common_name"] if alt_ord else None,
                "emoji": alt_cls["emoji"] if alt_cls else "❓",
                "confidence": int(min(entry["weighted"], 100)),
            })
        if len(alts) >= 3:
            break

    # Format result
    result = {
        "success": True,
        "confidence": confidence,
        "taxon_class": {
            "id": cls_row["id"] if cls_row else None,
            "name": cls_row["name"] if cls_row else "Unknown",
            "common_name": cls_row["common_name"] if cls_row else "Unknown",
            "emoji": cls_row["emoji"] if cls_row else "❓",
            "description": cls_row["description"] if cls_row else "",
            "characteristics": cls_row["characteristics"] if cls_row else "",
        },
        "taxon_order": {
            "id": ord_row["id"] if ord_row else None,
            "name": ord_row["name"] if ord_row else None,
            "common_name": ord_row["common_name"] if ord_row else None,
            "description": ord_row["description"] if ord_row else None,
        } if ord_row else None,
        "species": species_list[:6] if species_list else [],
        "examples": [s["common_name"] for s in species_list[:6]],
        "reasoning": reasoning,
        "alternatives": alts,
        "match_details": {
            "rule_name": rule["name"],
            "rule_explain": rule["explain"],
            "facts_matched": winner["matches"],
            "facts_total": winner["total"],
        }
    }

    return result


def classify_with_ml(facts, ml_confidence=None):
    """
    Hybrid wrapper: runs rule engine + overlays optional ML confidence.
    Returns enriched result with hybrid_confidence.
    """
    result = classify(facts)
    if not result["success"]:
        return result

    rule_conf = result["confidence"]
    if ml_confidence is not None:
        # Simple hybrid: weighted average (70% rule, 30% ML)
        hybrid = int(0.7 * rule_conf + 0.3 * ml_confidence)
        result["hybrid_confidence"] = hybrid
        result["ml_confidence"] = int(ml_confidence)
        result["reasoning"].append(
            f"🤖 ML Model confidence = {ml_confidence}%. "
            f"Hybrid score (70% rule + 30% ML) = {hybrid}%"
        )
    else:
        result["hybrid_confidence"] = rule_conf
        result["ml_confidence"] = None

    return result
