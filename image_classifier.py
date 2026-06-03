"""
image_classifier.py — AI Image Classification for Animal Expert System v2

Uses torchvision pre-trained MobileNetV2 (lightweight, fast) for image recognition.
Maps ImageNet class labels to our taxonomy database for species-level results.

If PyTorch is not installed, gracefully degrades with an informative message.
"""

import os
import json
import io
import warnings
from PIL import Image
import numpy as np

# ── Try to import torch / torchvision ──────────────────────────────
try:
    import torch
    import torchvision.transforms as T
    from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not installed. Image AI disabled. Run: pip install torch torchvision")

# ── ImageNet → Our Taxonomy mapping (selected animals) ─────────────
# ImageNet 1k class indices mapped to (species_id, confidence_factor)
IMAGENET_TO_TAXONOMY = {
    # Mammals
    282: (1, 0.95),    # tiger
    281: (1, 0.92),    # tabby cat → map to tiger (closest felid)
    283: (2, 0.95),    # lion
    288: (3, 0.92),    # wolf
    289: (3, 0.88),    # timber wolf
    290: (3, 0.88),    # white wolf
    291: (4, 0.90),    # polar bear
    295: (4, 0.88),    # American black bear
    296: (4, 0.88),    # ice bear
    297: (4, 0.88),    # sloth bear
    386: (10, 0.92),   # African elephant
    385: (10, 0.90),   # Indian elephant
    343: (6, 0.88),    # chimpanzee
    365: (5, 0.85),    # gorilla (ImageNet has gorilla)
    366: (7, 0.88),    # gorilla → mountain gorilla
    106: (8, 0.90),    # wombat? no — let's map properly
    # We add more direct animals below
}

# Expanded mapping using label strings (more reliable than indices across versions)
LABEL_KEYWORDS = {
    "tiger": (1, 0.96),
    "lion": (2, 0.95),
    "wolf": (3, 0.90),
    "timber_wolf": (3, 0.90),
    "white_wolf": (3, 0.90),
    "polar_bear": (4, 0.94),
    "ice_bear": (4, 0.94),
    "american_black_bear": (4, 0.82),
    "sloth_bear": (4, 0.82),
    "chimpanzee": (6, 0.93),
    "spider_monkey": (6, 0.75),
    "howler_monkey": (6, 0.75),
    "baboon": (6, 0.72),
    "gorilla": (7, 0.92),
    "orangutan": (6, 0.78),
    "gibbon": (6, 0.76),
    "elephant": (10, 0.93),
    "indian_elephant": (10, 0.92),
    "african_elephant": (10, 0.94),
    "dolphin": (8, 0.90),
    "killer_whale": (8, 0.88),
    "great_white_shark": (20, 0.88),
    "tiger_shark": (20, 0.88),
    "hammerhead": (20, 0.88),
    "goldfish": (25, 0.70),
    "stingray": (25, 0.75),
    "penguin": (13, 0.94),
    "king_penguin": (13, 0.95),
    "albatross": (12, 0.80),
    "bald_eagle": (12, 0.90),
    "raptor": (12, 0.85),
    "vulture": (10, 0.82),
    "bee": (18, 0.90),
    "honeybee": (18, 0.92),
    "bumblebee": (18, 0.90),
    "monarch": (17, 0.92),
    "butterfly": (17, 0.85),
    "sulphur_butterfly": (17, 0.85),
    "cabbage_butterfly": (17, 0.85),
    "admiral": (17, 0.85),
    "fly": (17, 0.60),  # fallback insect
    "mosquito": (17, 0.60),
    "ladybug": (20, 0.78),
    "grasshopper": (22, 0.82),
    "cricket": (22, 0.80),
    "beetle": (20, 0.75),
    "turtle": (15, 0.92),
    "sea_turtle": (15, 0.92),
    "loggerhead": (15, 0.90),
    "leatherback_turtle": (15, 0.90),
    "mud_turtle": (15, 0.88),
    "terrapin": (15, 0.88),
    "box_turtle": (15, 0.88),
    "green_lizard": (14, 0.80),
    "iguana": (14, 0.82),
    "agama": (14, 0.80),
    "frilled_lizard": (14, 0.82),
    "alligator_lizard": (14, 0.78),
    "American_chameleon": (14, 0.75),
    "monitor_lizard": (14, 0.80),
    "Komodo_dragon": (14, 0.85),
    "cobra": (14, 0.85),
    "rattlesnake": (14, 0.85),
    "green_snake": (14, 0.82),
    "king_snake": (14, 0.82),
    "garter_snake": (14, 0.80),
    "night_snake": (14, 0.80),
    "boa_constrictor": (14, 0.85),
    "python": (14, 0.86),
    "tailed_frog": (16, 0.85),
    "bullfrog": (16, 0.88),
    "tree_frog": (16, 0.88),
    "spider": (19, 0.88),
    "black_widow": (19, 0.94),
    "tarantula": (19, 0.90),
    "barn_spider": (19, 0.85),
    "garden_spider": (19, 0.85),
    "scorpion": (24, 0.90),
    "crab": (21, 0.92),
    "fiddler_crab": (21, 0.90),
    "rock_crab": (21, 0.90),
    "Dungeness_crab": (21, 0.90),
    "king_crab": (21, 0.88),
    "American_lobster": (28, 0.88),
    "crayfish": (28, 0.82),
    "hermit_crab": (28, 0.82),
    "isopod": (28, 0.70),
    "goldfinch": (11, 0.78),
    "brambling": (11, 0.75),
    "robin": (11, 0.78),
    "bulbul": (11, 0.75),
    "jay": (11, 0.78),
    "magpie": (11, 0.78),
    "chickadee": (11, 0.75),
    "water_ouzel": (11, 0.72),
    "kite": (12, 0.80),
    "eagle": (12, 0.92),
    "vulture": (12, 0.82),
    "great_grey_owl": (11, 0.82),
    "European_fire_salamander": (18, 0.88),
    "common_newt": (18, 0.85),
    "eft": (18, 0.85),
    "axolotl": (18, 0.88),
    "banded_gecko": (14, 0.80),
    "otter": (1, 0.88),
    "sea_otter": (1, 0.88),
    "mink": (1, 0.85),
    "polecat": (1, 0.85),
    "weasel": (1, 0.85),
    "black-footed_ferret": (1, 0.85),
    "mongoose": (1, 0.82),
    "meerkat": (1, 0.82),
    "badger": (1, 0.82),
    "beaver": (3, 0.82),
    "hamster": (3, 0.78),
    "guinea_pig": (3, 0.78),
    "squirrel": (3, 0.78),
    "hare": (3, 0.78),
    "Angora": (3, 0.70),
    "fox_squirrel": (3, 0.78),
    "marmot": (3, 0.78),
    "porcupine": (3, 0.78),
    "coyote": (3, 0.85),
    "dingo": (3, 0.85),
    "dhole": (3, 0.82),
    "African_hunting_dog": (3, 0.85),
    "hyena": (1, 0.85),
    "red_fox": (3, 0.82),
    "kit_fox": (3, 0.80),
    "Arctic_fox": (3, 0.82),
    "grey_fox": (3, 0.80),
    "tabby": (1, 0.70),   # cat → mammal carnivora
    "Persian_cat": (1, 0.70),
    "Egyptian_cat": (1, 0.70),
    "cougar": (1, 0.88),
    "lynx": (1, 0.88),
    "leopard": (1, 0.90),
    "snow_leopard": (1, 0.90),
    "jaguar": (1, 0.90),
    "cheetah": (1, 0.90),
    "lesser_panda": (1, 0.82),
    "giant_panda": (1, 0.85),
    "gazelle": (7, 0.85),
    "impala": (7, 0.85),
    "hartebeest": (7, 0.82),
    "wildebeest": (7, 0.82),
    "ibex": (7, 0.82),
    "hog": (7, 0.80),
    "warthog": (7, 0.82),
    "water_buffalo": (7, 0.82),
    "bison": (7, 0.85),
    "ram": (7, 0.80),
    "bighorn": (7, 0.80),
    "giant_schnauzer": (1, 0.82),  # dog → mammal carnivora-ish
    "Staffordshire_bullterrier": (1, 0.78),
    "Border_collie": (1, 0.78),
    "golden_retriever": (1, 0.78),
    " Labrador_retriever": (1, 0.78),
    "wombat": (3, 0.78),
    "koala": (3, 0.82),
    "jellyfish": (7, 0.60),  # fallback aquatic
    "sea_anemone": (7, 0.60),
    "brain_coral": (7, 0.60),
    "starfish": (7, 0.65),
    "sea_urchin": (7, 0.60),
    "wood_rabbit": (3, 0.78),
    "hare": (3, 0.78),
    "Angora": (3, 0.70),
    "hen": (2, 0.75),    # bird
    "ostrich": (2, 0.88),
    "brambling": (11, 0.75),
    "goldfinch": (11, 0.78),
    "house_finch": (11, 0.78),
    "junco": (11, 0.75),
    "indigo_bunting": (11, 0.75),
    "robin": (11, 0.78),
    "bulbul": (11, 0.75),
    "jay": (11, 0.78),
    "magpie": (11, 0.78),
    "chickadee": (11, 0.75),
    "water_ouzel": (11, 0.72),
    "kite": (12, 0.80),
    "bald_eagle": (12, 0.92),
    "vulture": (12, 0.82),
    "great_grey_owl": (11, 0.82),
    "black_grouse": (2, 0.78),
    "ptarmigan": (2, 0.78),
    "ruffed_grouse": (2, 0.78),
    "prairie_chicken": (2, 0.78),
    "peacock": (2, 0.88),
    "quail": (2, 0.80),
    "partridge": (2, 0.80),
    "African_grey": (2, 0.85),
    "macaw": (2, 0.88),
    "cockatoo": (2, 0.88),
    "lorikeet": (2, 0.85),
    "coucal": (2, 0.75),
    "bee_eater": (2, 0.78),
    "hornbill": (2, 0.78),
    "hummingbird": (2, 0.82),
    "jacamar": (2, 0.75),
    "toucan": (2, 0.85),
    "drake": (13, 0.82),
    "red-breasted_merganser": (13, 0.85),
    "goose": (13, 0.85),
    "black_swan": (13, 0.88),
    "tusker": (10, 0.88),
    "echidna": (1, 0.82),   # egg-laying mammal
    "platypus": (1, 0.85),  # egg-laying mammal
    "wallaby": (3, 0.80),
    "kangaroo": (3, 0.82),
    "koala": (3, 0.82),
}


class ImageClassifier:
    """Wraps torchvision model with our taxonomy mapping."""

    def __init__(self):
        self.model = None
        self.weights = None
        self.preprocess = None
        self.labels = None
        self._ready = False
        if TORCH_AVAILABLE:
            try:
                self.weights = MobileNet_V2_Weights.IMAGENET1K_V1
                self.model = mobilenet_v2(weights=self.weights)
                self.model.eval()
                self.preprocess = self.weights.transforms()
                self.labels = self.weights.meta["categories"]
                self._ready = True
                print("🤖 Image AI loaded: MobileNetV2 (ImageNet 1k)")
            except Exception as e:
                print(f"⚠️ Failed to load image model: {e}")
        else:
            print("⚠️ PyTorch unavailable. Image AI disabled.")

    def ready(self):
        return self._ready

    def classify_image(self, image_bytes):
        """
        Classify a raw image (bytes).
        Returns dict with:
            - species_id (or None)
            - label (ImageNet label)
            - confidence (0-100)
            - taxonomy_match (bool)
            - message
        """
        if not self._ready:
            return {
                "success": False,
                "message": "Image AI not available. Install PyTorch: pip install torch torchvision",
                "species_id": None,
                "label": None,
                "confidence": 0,
            }

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            input_tensor = self.preprocess(img).unsqueeze(0)

            with torch.no_grad():
                output = self.model(input_tensor)
                probs = torch.nn.functional.softmax(output[0], dim=0)

            top_prob, top_idx = torch.topk(probs, 5)
            top_idx = top_idx.tolist()
            top_prob = (top_prob * 100).tolist()

            # Try keyword matching across top-5
            species_id = None
            best_conf = 0
            best_label = ""

            for idx, prob in zip(top_idx, top_prob):
                raw_label = self.labels[idx]
                # Clean label: remove number prefix, spaces to underscores
                clean = raw_label.lower().replace(" ", "_").strip()
                # Try exact keyword match
                for keyword, (sid, factor) in LABEL_KEYWORDS.items():
                    if keyword.lower() in clean or clean in keyword.lower():
                        adj_conf = int(prob * factor)
                        if adj_conf > best_conf:
                            best_conf = adj_conf
                            species_id = sid
                            best_label = raw_label
                        break
                else:
                    # No keyword match — keep as fallback only if high prob
                    if prob > best_conf and best_conf == 0:
                        best_conf = int(prob * 0.5)
                        best_label = raw_label

            # If still no species match, try index map (legacy)
            if species_id is None:
                for idx, prob in zip(top_idx, top_prob):
                    if idx in IMAGENET_TO_TAXONOMY:
                        sid, factor = IMAGENET_TO_TAXONOMY[idx]
                        adj_conf = int(prob * factor)
                        if adj_conf > best_conf:
                            best_conf = adj_conf
                            species_id = sid
                            best_label = self.labels[idx]
                        break

            return {
                "success": True,
                "species_id": species_id,
                "label": best_label or self.labels[top_idx[0]],
                "confidence": min(best_conf, 99),
                "top5": [
                    {"label": self.labels[i], "confidence": round(p, 1)}
                    for i, p in zip(top_idx, top_prob)
                ],
                "taxonomy_match": species_id is not None,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Image processing error: {str(e)}",
                "species_id": None,
                "label": None,
                "confidence": 0,
            }


# Singleton instance
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = ImageClassifier()
    return _classifier


def classify_image(image_bytes):
    """Convenience function."""
    return get_classifier().classify_image(image_bytes)
