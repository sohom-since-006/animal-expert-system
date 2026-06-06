"""
app.py — Animal Classification Expert System v2 (Portfolio Edition)

Features:
  • Wizard trait-based classification
  • AI Image classification (with PyTorch)
  • Voice-to-text trait parsing (text endpoint)
  • Hybrid Rule + ML classification
  • Explainable reasoning chains
  • Interactive taxonomy tree API
  • Species encyclopedia module
  • Classification history / audit log

Run:  python app.py
"""

import os
import sys
import json
import io
import warnings
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory

# ── Local modules ──────────────────────────────────────────────────
from database import init_db, get_classes, get_orders, get_species, get_species_by_id
from database import get_taxonomy_tree, log_classification, get_history, DB_PATH
from rule_engine import classify_with_ml
from ml_engine import predict as ml_predict

# Image AI (optional)
from image_classifier import classify_image, TRANSFORMERS_AVAILABLE, TORCH_AVAILABLE

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# ── Init DB ────────────────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    print("🔧 First run — initialising database...")
    init_db()

# ── Helper: safe JSON ──────────────────────────────────────────────
def to_bool(val):
    if val is None or val == "":
        return None
    return int(val)


# ════════════════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the single-page application."""
    return render_template("index.html",
                           torch_available=TORCH_AVAILABLE,
                           transformers_available=TRANSFORMERS_AVAILABLE,
                           build_date=datetime.now().strftime("%Y-%m-%d"))


@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Hybrid Wizard Classification
    Body JSON: trait facts
    """
    data = request.get_json(force=True)

    facts = {
        "has_backbone":  to_bool(data.get("has_backbone")),
        "body_covering": data.get("body_covering") or None,
        "reproduction":  data.get("reproduction") or None,
        "warm_blooded":  to_bool(data.get("warm_blooded")),
        "diet":          data.get("diet") or None,
        "has_wings":     to_bool(data.get("has_wings")),
        "aquatic":       to_bool(data.get("aquatic")),
    }

    # ML layer
    ml_res = ml_predict(facts)
    ml_conf = ml_res.get("confidence")

    # Hybrid fusion
    result = classify_with_ml(facts, ml_confidence=ml_conf)

    # Enrich with species if we have an order
    if result.get("success") and result.get("taxon_order") and result["taxon_order"].get("id"):
        species = get_species(order_id=result["taxon_order"]["id"])
        result["species"] = species[:6]
        # Pick best species by name heuristic if available
        if species:
            result["best_species"] = species[0]
        else:
            result["best_species"] = None
    elif result.get("success") and result.get("taxon_class"):
        species = get_species(class_id=result["taxon_class"]["id"])
        result["species"] = species[:6]
        result["best_species"] = species[0] if species else None
    else:
        result["species"] = []
        result["best_species"] = None

    # Log to history
    if result.get("success"):
        log_classification(
            input_type="wizard",
            input_summary=json.dumps(facts),
            result_class_id=result["taxon_class"]["id"] if result["taxon_class"] else None,
            result_order_id=result["taxon_order"]["id"] if result.get("taxon_order") else None,
            result_species_id=result["best_species"]["id"] if result.get("best_species") else None,
            confidence=result.get("hybrid_confidence", result.get("confidence", 0)),
            ml_confidence=ml_conf,
            reasoning="\n".join(result.get("reasoning", []))
        )

    return jsonify(result)


@app.route("/api/classify_image", methods=["POST"])
def api_classify_image():
    """
    Image-based animal identification.
    Accepts: multipart/form-data with 'image' file.
    """
    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image uploaded."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "message": "Empty filename."}), 400

    image_bytes = file.read()
    img_result = classify_image(image_bytes)

    if not img_result["success"]:
        return jsonify(img_result), 503

    # Enrich with DB species if mapped
    species_data = None
    if img_result.get("species_id"):
        species_data = get_species_by_id(img_result["species_id"])
        if species_data:
            img_result["species"] = species_data
            img_result["class_name"] = species_data.get("class_name")
            img_result["order_name"] = species_data.get("order_common")

    # Log
    if img_result.get("species_id"):
        log_classification(
            input_type="image",
            input_summary=f"Image: {file.filename}",
            result_class_id=species_data.get("class_id") if species_data else None,
            result_order_id=species_data.get("order_id") if species_data else None,
            result_species_id=img_result["species_id"],
            confidence=img_result["confidence"],
            ml_confidence=img_result["confidence"],
            reasoning=f"Image AI: predicted {img_result.get('label')}"
        )

    return jsonify(img_result)


@app.route("/api/voice_classify", methods=["POST"])
def api_voice_classify():
    """
    Voice text classification.
    Receives transcribed text, parses traits heuristically.
    """
    data = request.get_json(force=True)
    text = (data.get("text") or "").lower()

    if not text:
        return jsonify({"success": False, "message": "No text received."}), 400

    # Simple heuristic parser
    facts = {
        "has_backbone": None,
        "body_covering": None,
        "reproduction": None,
        "warm_blooded": None,
        "diet": None,
        "has_wings": None,
        "aquatic": None,
    }

    # Keywords mapping
    if any(w in text for w in ["backbone", "spine", "vertebrate", "skeleton", "bone", "mammal", "bird", "fish", "reptile", "amphibian", "lion", "tiger", "elephant", "wolf", "snake", "turtle", "frog", "shark", "whale", "dolphin", "penguin", "eagle"]):
        facts["has_backbone"] = 1
    if any(w in text for w in ["invertebrate", "worm", "insect", "spider", "crab", "jellyfish", "snail", "ant", "bee", "butterfly", "shell", "exoskeleton"]):
        facts["has_backbone"] = 0

    if any(w in text for w in ["warm-blooded", "warm blooded", "endotherm", "mammal", "bird"]):
        facts["warm_blooded"] = 1
    if any(w in text for w in ["cold-blooded", "cold blooded", "ectotherm", "reptile", "fish", "amphibian", "insect", "spider"]):
        facts["warm_blooded"] = 0

    if any(w in text for w in ["fur", "hair", "furry", "hairy", "mammal", "lion", "tiger", "wolf", "bear", "dog", "cat", "elephant"]):
        facts["body_covering"] = "fur"
    if any(w in text for w in ["feather", "feathers", "bird", "eagle", "parrot", "penguin", "wing"]):
        facts["body_covering"] = "feathers"
        facts["has_wings"] = 1
    if any(w in text for w in ["scale", "scales", "scaly", "reptile", "snake", "lizard", "fish", "shark"]):
        facts["body_covering"] = "scales"
    if any(w in text for w in ["moist skin", "wet skin", "slimy", "amphibian", "frog", "salamander", "newt"]):
        facts["body_covering"] = "moist_skin"
    if any(w in text for w in ["shell", "hard shell", "carapace", "turtle", "crab", "lobster", "exoskeleton"]):
        facts["body_covering"] = "shell"
    if any(w in text for w in ["chitin", "insect", "spider", "ant", "bee", "butterfly", "bare"]):
        facts["body_covering"] = "none"

    if any(w in text for w in ["live birth", "gives birth", "viviparous", "mammal", "bear live young", "whale", "dolphin", "elephant", "lion"]):
        facts["reproduction"] = "live_birth"
    if any(w in text for w in ["egg", "eggs", "lay eggs", "oviparous", "bird", "reptile", "snake", "turtle", "insect", "crocodile"]):
        facts["reproduction"] = "eggs_land"
    if any(w in text for w in ["spawn", "spawn eggs", "fish eggs", "amphibian eggs", "frog spawn"]):
        facts["reproduction"] = "eggs_water"
    if any(w in text for w in ["metamorphosis", "caterpillar", "tadpole", "larva", "pupa", "chrysalis", "butterfly", "frog life cycle"]):
        facts["reproduction"] = "metamorphosis"

    if any(w in text for w in ["carnivore", "meat", "meat-eater", "predator", "hunt", "eats meat", "lion", "tiger", "wolf", "shark", "eagle", "snake"]):
        facts["diet"] = "carnivore"
    if any(w in text for w in ["herbivore", "plant", "grass", "leaves", "eats plants", "elephant", "deer", "cow", "horse", "rabbit"]):
        facts["diet"] = "herbivore"
    if any(w in text for w in ["omnivore", "everything", "plants and meat", "human", "bear", "pig", "crow", "raven"]):
        facts["diet"] = "omnivore"
    if any(w in text for w in ["insectivore", "eats insects", "ants", "termites", "aardvark"]):
        facts["diet"] = "insectivore"

    if any(w in text for w in ["wing", "wings", "fly", "flying", "bird", "bat", "insect", "butterfly", "eagle", "bee"]):
        facts["has_wings"] = 1
    if any(w in text for w in ["no wing", "flightless", "penguin", "ostrich", "kiwi", "wingless", "cannot fly"]):
        facts["has_wings"] = 0

    if any(w in text for w in ["water", "ocean", "sea", "aquatic", "marine", "river", "lake", "pond", "fish", "shark", "whale", "dolphin", "crab", "penguin", "frog", "turtle", "crocodile"]):
        facts["aquatic"] = 1
    if any(w in text for w in ["land", "terrestrial", "savanna", "forest", "desert", "mountain", "tree", "ground"]):
        facts["aquatic"] = 0

    # Filter out None values for cleaner summary
    parsed = {k: v for k, v in facts.items() if v is not None}

    if not parsed:
        return jsonify({
            "success": False,
            "message": "Could not extract animal traits from voice text. Try describing: body covering, diet, backbone, habitat, wings.",
            "parsed": {}
        }), 422

    # Run hybrid classification with parsed facts
    ml_res = ml_predict(facts)
    ml_conf = ml_res.get("confidence")
    result = classify_with_ml(facts, ml_confidence=ml_conf)

    # Enrich
    if result.get("success") and result.get("taxon_order") and result["taxon_order"].get("id"):
        species = get_species(order_id=result["taxon_order"]["id"])
        result["species"] = species[:6]
        result["best_species"] = species[0] if species else None
    elif result.get("success") and result.get("taxon_class"):
        species = get_species(class_id=result["taxon_class"]["id"])
        result["species"] = species[:6]
        result["best_species"] = species[0] if species else None
    else:
        result["species"] = []
        result["best_species"] = None

    result["voice_parsed"] = parsed

    # Log
    if result.get("success"):
        log_classification(
            input_type="voice",
            input_summary=text[:200],
            result_class_id=result["taxon_class"]["id"] if result["taxon_class"] else None,
            result_order_id=result["taxon_order"]["id"] if result.get("taxon_order") else None,
            result_species_id=result["best_species"]["id"] if result.get("best_species") else None,
            confidence=result.get("hybrid_confidence", result.get("confidence", 0)),
            ml_confidence=ml_conf,
            reasoning="Voice parsed: " + json.dumps(parsed) + "\n" + "\n".join(result.get("reasoning", []))
        )

    return jsonify(result)


@app.route("/api/species/<int:sid>")
def api_species(sid):
    """Get detailed info about a species (encyclopedia module)."""
    s = get_species_by_id(sid)
    if not s:
        return jsonify({"success": False, "message": "Species not found"}), 404
    return jsonify({"success": True, "data": s})


@app.route("/api/taxonomy")
def api_taxonomy():
    """Return full nested taxonomy tree for visualization."""
    return jsonify({"success": True, "tree": get_taxonomy_tree()})


@app.route("/api/search")
def api_search():
    """Search species by name."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "results": []})
    results = get_species(search=q)
    return jsonify({"success": True, "results": results[:20]})


@app.route("/api/history")
def api_history():
    """Return recent classification history."""
    limit = request.args.get("limit", 50, type=int)
    return jsonify({"success": True, "history": get_history(limit=limit)})


@app.route("/api/stats")
def api_stats():
    """Dashboard stats."""
    from database import get_conn
    conn = get_conn()
    c = conn.cursor()
    stats = {
        "classes": c.execute("SELECT COUNT(*) FROM taxonomy_classes").fetchone()[0],
        "orders": c.execute("SELECT COUNT(*) FROM taxonomy_orders").fetchone()[0],
        "species": c.execute("SELECT COUNT(*) FROM species").fetchone()[0],
        "classifications": c.execute("SELECT COUNT(*) FROM classification_history").fetchone()[0],
        "image_ai_available": TRANSFORMERS_AVAILABLE or TORCH_AVAILABLE,
    }
    conn.close()
    return jsonify({"success": True, "stats": stats})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset database and re-seed."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    return jsonify({"status": "Database reset successfully"})


# ── Static file serving (fallback) ─────────────────────────────────
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("="*60)
    print("🦁 Animal Classification Expert System v2")
    print("   Portfolio Edition — AI + ML + Explainable + Image + Voice")
    print("="*60)
    print("📡 Local:   http://127.0.0.1:5000")
    print("🤖 Image AI:", "ENABLED" if TORCH_AVAILABLE else "DISABLED (install torch)")
    print("="*60)
    app.run(debug=True, host="0.0.0.0", port=5000)
