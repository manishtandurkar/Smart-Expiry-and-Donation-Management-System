"""
Enhanced NLP module for category prediction using transformer models.
Combines zero-shot classification with keyword matching for robust predictions.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING
import re
import importlib

if TYPE_CHECKING:
    from transformers import pipeline  # type: ignore
    # import sentence-transformers types for linters/type-checkers
    from sentence_transformers import SentenceTransformer, util  # type: ignore

# transformers detection (runtime)
try:
    from transformers import pipeline  # type: ignore
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Install with: pip install transformers torch")

# sentence-transformers: import at runtime to avoid static linter errors
SENTENCE_TRANSFORMERS_AVAILABLE = False
SentenceTransformer = None
util = None
try:
    st_mod = importlib.import_module("sentence_transformers")
    SentenceTransformer = getattr(st_mod, "SentenceTransformer")
    util = getattr(st_mod, "util")
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")


class EnhancedCategoryPredictor:
    """
    Enhanced NLP-based category predictor using transformer models.
    Falls back to keyword matching if models are unavailable.
    """
    
    # Category keywords and descriptions
    CATEGORIES = {
        'Food': {
            'description': 'Food items, groceries, edible products, beverages, and consumables',
            'keywords': [
                'rice', 'wheat', 'flour', 'grain', 'cereal', 'bread', 'pasta', 'noodle',
                'beans', 'lentils', 'dal', 'pulses', 'milk', 'cheese', 'yogurt', 'butter', 'ghee', 'cream',
                'egg', 'meat', 'chicken', 'mutton', 'beef', 'pork', 'fish', 'seafood', 'prawn', 'crab',
                'vegetable', 'fruit', 'tomato', 'potato', 'onion', 'carrot', 'apple', 'banana', 'orange',
                'oil', 'cooking', 'sugar', 'salt', 'spice', 'masala', 'pepper', 'chilli', 'turmeric',
                'snack', 'biscuit', 'cookie', 'candy', 'chocolate', 'sweet', 'dessert', 'cake',
                'juice', 'water', 'tea', 'coffee', 'beverage', 'drink', 'soda', 'cola',
                'canned', 'frozen', 'fresh', 'packed', 'dry', 'preserved', 'pickle',
                'sauce', 'ketchup', 'jam', 'honey', 'peanut', 'almond', 'cashew', 'nuts',
                'grocery', 'edible', 'food', 'meal', 'ration', 'provision'
            ]
        },
        'Medicine': {
            'description': 'Medicines, drugs, pharmaceuticals, medical supplies, and healthcare products',
            'keywords': [
                'tablet', 'capsule', 'syrup', 'medicine', 'drug', 'pharmaceutical', 'medication',
                'antibiotic', 'painkiller', 'paracetamol', 'aspirin', 'ibuprofen', 'acetaminophen',
                'vitamin', 'supplement', 'multivitamin', 'calcium', 'iron', 'zinc',
                'injection', 'vaccine', 'immunization', 'bandage', 'gauze', 'dressing',
                'antiseptic', 'ointment', 'cream', 'gel', 'lotion', 'balm',
                'prescription', 'medical', 'treatment', 'therapy', 'remedy',
                'inhaler', 'nebulizer', 'drops', 'pill', 'dose',
                'antihistamine', 'antacid', 'laxative', 'probiotic',
                'cough', 'cold', 'fever', 'pain', 'relief',
                'first aid', 'surgical', 'diagnostic', 'test kit',
                'crocin', 'dolo', 'combiflam', 'cetrizine', 'disprin'
            ]
        },
        'Clothing': {
            'description': 'Clothing items, apparel, footwear, and fashion accessories',
            'keywords': [
                'shirt', 'pant', 'trouser', 'dress', 'skirt', 'jacket', 'coat', 'blazer',
                'sweater', 'cardigan', 'hoodie', 't-shirt', 'tshirt', 'top', 'blouse',
                'jeans', 'shorts', 'capri', 'leggings', 'track', 'jogger',
                'underwear', 'innerwear', 'bra', 'panty', 'boxer', 'brief',
                'sock', 'stocking', 'shoe', 'sandal', 'slipper', 'boot', 'sneaker', 'footwear',
                'hat', 'cap', 'scarf', 'shawl', 'muffler', 'glove', 'belt',
                'saree', 'kurta', 'salwar', 'kameez', 'dhoti', 'lungi',
                'fabric', 'textile', 'cloth', 'garment', 'apparel', 'clothing', 'wear', 'attire',
                'cotton', 'silk', 'wool', 'denim', 'leather',
                'uniform', 'suit', 'traditional', 'ethnic', 'formal', 'casual'
            ]
        },
        'Hygiene': {
            'description': 'Personal care products, cleaning supplies, and hygiene items',
            'keywords': [
                'soap', 'shampoo', 'conditioner', 'detergent', 'cleanser', 'cleaner', 'wash',
                'sanitizer', 'disinfectant', 'hand wash', 'handwash', 'body wash', 'bodywash', 'face wash',
                'toothpaste', 'toothbrush', 'dental', 'mouthwash', 'floss',
                'deodorant', 'deo', 'perfume', 'fragrance', 'cologne',
                'lotion', 'moisturizer', 'sunscreen', 'cream', 'oil', 'powder',
                'tissue', 'napkin', 'toilet paper', 'wipe', 'cotton',
                'diaper', 'nappy', 'sanitary', 'pad', 'tampon', 'menstrual',
                'towel', 'cloth', 'sponge', 'scrub', 'brush',
                'shaving', 'razor', 'blade', 'foam', 'aftershave',
                'nail', 'comb', 'hairbrush', 'cosmetic', 'makeup',
                'bathing', 'shower', 'hygiene', 'personal care', 'grooming'
            ]
        },
        'Stationery': {
            'description': 'Office supplies, school items, writing materials, and art supplies',
            'keywords': [
                'pen', 'pencil', 'eraser', 'sharpener', 'notebook', 'copy', 'register',
                'paper', 'sheet', 'book', 'diary', 'journal', 'notepad',
                'marker', 'highlighter', 'sketch', 'crayon', 'color', 'paint', 'watercolor',
                'ruler', 'scale', 'compass', 'protractor', 'geometry',
                'scissors', 'cutter', 'knife', 'blade',
                'glue', 'adhesive', 'tape', 'cellotape', 'fevicol',
                'stapler', 'staple', 'pin', 'clip', 'binder',
                'folder', 'file', 'envelope', 'calculator',
                'ink', 'refill', 'cartridge', 'toner',
                'board', 'chart', 'drawing', 'art', 'craft',
                'office', 'school', 'stationery', 'writing', 'supplies'
            ]
        },
        'Electronics': {
            'description': 'Electronic devices, gadgets, appliances, and technology items',
            'keywords': [
                'phone', 'mobile', 'smartphone', 'tablet', 'ipad', 'laptop', 'computer', 'pc',
                'charger', 'cable', 'wire', 'adapter', 'battery', 'powerbank',
                'headphone', 'earphone', 'earbud', 'speaker', 'bluetooth',
                'tv', 'television', 'monitor', 'screen', 'display',
                'fan', 'cooler', 'ac', 'heater', 'iron', 'appliance',
                'watch', 'smartwatch', 'clock', 'alarm',
                'camera', 'webcam', 'lens', 'tripod',
                'mouse', 'keyboard', 'usb', 'pendrive', 'hard disk', 'ssd',
                'router', 'modem', 'wifi', 'network',
                'electronic', 'gadget', 'device', 'digital', 'tech', 'technology'
            ]
        }
    }
    
    def __init__(self, use_transformers: bool = True, model_name: str = "facebook/bart-large-mnli"):
        """
        Initialize the enhanced predictor with AI models.
        
        Args:
            use_transformers: Whether to use transformer models
            model_name: Name of the zero-shot classification model
        """
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.classifier = None
        self.embedder = None
        self.category_embeddings = None
        self.model_status = {"classifier": False, "embedder": False}
        
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️  WARNING: transformers library not available!")
            print("   Install with: pip install transformers torch")
            self.use_transformers = False
        
        if self.use_transformers:
            try:
                print("\n🤖 Loading AI Models for Category Prediction...")
                print(f"   📦 Zero-shot classifier: {model_name}")
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model=model_name,
                    device=-1  # Use CPU (-1) or 0 for GPU
                )
                self.model_status["classifier"] = True
                print("   ✅ Zero-shot classifier loaded successfully!")
                
                # Try to load sentence transformer for semantic similarity
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    try:
                        print("   📦 Sentence transformer: all-MiniLM-L6-v2")
                        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                        self._compute_category_embeddings()
                        self.model_status["embedder"] = True
                        print("   ✅ Sentence transformer loaded successfully!")
                    except Exception as e:
                        print(f"   ⚠️  Sentence transformer failed: {e}")
                        self.embedder = None
                
                print("\n🎯 AI-powered prediction ACTIVE\n")
                        
            except Exception as e:
                print(f"\n❌ ERROR: Could not load transformer model: {e}")
                print("   Falling back to keyword-based prediction")
                print("   Please check your internet connection and try again\n")
                self.use_transformers = False
    
    def _compute_category_embeddings(self):
        """Precompute embeddings for category descriptions."""
        if self.embedder:
            descriptions = [
                f"{cat}: {info['description']}"
                for cat, info in self.CATEGORIES.items()
            ]
            self.category_embeddings = self.embedder.encode(descriptions, convert_to_tensor=True)
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def _handle_plurals(self, word: str) -> List[str]:
        """Generate common plural/singular variations of a word."""
        variations = [word]
        
        # Handle common plural forms
        if word.endswith('s'):
            variations.append(word[:-1])  # Remove 's'
        else:
            variations.append(word + 's')  # Add 's'
        
        if word.endswith('ies'):
            variations.append(word[:-3] + 'y')  # berry -> berries
        elif word.endswith('es'):
            variations.append(word[:-2])  # box -> boxes
        elif word.endswith('y') and len(word) > 2:
            variations.append(word[:-1] + 'ies')  # berry -> berries
        
        # Handle common variations
        if word.endswith('ing'):
            variations.append(word[:-3])  # cooking -> cook
        
        return list(set(variations))
    
    def _keyword_based_prediction(
        self, 
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Enhanced keyword-based prediction with plural handling and smart fallback."""
        if not description or not description.strip():
            # Return Food as default for empty descriptions (most common donation)
            return ("Food", 0.1)
        
        processed = self.preprocess_text(description)
        tokens = processed.split()
        
        scores = {}
        categories = self.CATEGORIES.keys()
        if available_categories:
            categories = [c for c in categories if c in available_categories]
        
        for category in categories:
            keywords = self.CATEGORIES[category]['keywords']
            category_score = 0
            
            for token in tokens:
                # Generate variations (plurals, etc.)
                token_variations = self._handle_plurals(token)
                
                for keyword in keywords:
                    keyword_variations = self._handle_plurals(keyword)
                    
                    # Exact match (highest score)
                    if token in keyword_variations or keyword in token_variations:
                        category_score += 10
                    # Substring match (medium score)
                    elif any(kw in token for kw in keyword_variations) or any(tv in keyword for tv in token_variations):
                        category_score += 5
                    # Partial overlap (low score)
                    elif len(token) > 3 and len(keyword) > 3:
                        # Check for common characters (for typos)
                        common = sum(1 for c in token if c in keyword)
                        if common >= min(len(token), len(keyword)) * 0.7:
                            category_score += 2
            
            scores[category] = category_score
        
        # Even if no perfect matches, return the best category
        if not scores or max(scores.values()) == 0:
            # Intelligent fallback: check description length and context
            desc_lower = description.lower()
            if any(word in desc_lower for word in ['tablet', 'capsule', 'mg', 'ml', 'dose']):
                return ("Medicine", 0.3)
            elif any(word in desc_lower for word in ['shirt', 'pant', 'wear', 'cloth']):
                return ("Clothing", 0.3)
            elif any(word in desc_lower for word in ['clean', 'wash', 'hygien']):
                return ("Hygiene", 0.3)
            elif any(word in desc_lower for word in ['write', 'draw', 'office', 'school']):
                return ("Stationery", 0.3)
            elif any(word in desc_lower for word in ['device', 'electronic', 'gadget', 'tech']):
                return ("Electronics", 0.3)
            else:
                # Default to Food (most common donation category)
                return ("Food", 0.2)
        
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # Smarter confidence calculation
        # Higher base confidence, scaled by score
        confidence = min(0.3 + (max_score / 50.0), 1.0)
        
        # Boost confidence if score is significantly higher than second best
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] > sorted_scores[1] * 2:
            confidence = min(confidence * 1.2, 1.0)
        
        return (best_category, round(confidence, 2))
    
    def _transformer_prediction(
        self,
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Use transformer model for prediction with keyword validation."""
        if not self.classifier:
            return self._keyword_based_prediction(description, available_categories)
        
        categories = list(self.CATEGORIES.keys())
        if available_categories:
            categories = [c for c in categories if c in available_categories]
        
        if not categories:
            return self._keyword_based_prediction(description, available_categories)
        
        try:
            # Use zero-shot classification
            result = self.classifier(
                description,
                candidate_labels=categories,
                multi_label=False
            )
            
            predicted_category = result['labels'][0]
            confidence = result['scores'][0]
            
            # Boost confidence if keywords also match
            keyword_cat, keyword_conf = self._keyword_based_prediction(
                description, 
                available_categories
            )
            
            if keyword_cat == predicted_category:
                # Both methods agree - high confidence boost
                confidence = min(confidence * 1.2, 1.0)
            elif keyword_conf > 0.6:
                # Keywords are very confident but transformer disagrees
                # Trust keywords more for domain-specific terms
                return (keyword_cat, round(min(keyword_conf * 0.9, confidence), 2))
            
            return (predicted_category, round(confidence, 2))
            
        except Exception as e:
            print(f"Transformer prediction failed: {e}")
            return self._keyword_based_prediction(description, available_categories)
    
    def _semantic_similarity_prediction(
        self,
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Use semantic similarity for prediction with minimum threshold."""
        if not self.embedder or self.category_embeddings is None:
            return self._transformer_prediction(description, available_categories)
        
        try:
            # Encode the description
            desc_embedding = self.embedder.encode(description, convert_to_tensor=True)
            
            # Calculate similarities
            similarities = util.cos_sim(desc_embedding, self.category_embeddings)[0]
            
            categories = list(self.CATEGORIES.keys())
            if available_categories:
                # Filter similarities for available categories
                filtered_sims = []
                filtered_cats = []
                for i, cat in enumerate(categories):
                    if cat in available_categories:
                        filtered_sims.append(similarities[i].item())
                        filtered_cats.append(cat)
                
                if not filtered_cats:
                    return self._keyword_based_prediction(description, available_categories)
                
                best_idx = filtered_sims.index(max(filtered_sims))
                best_category = filtered_cats[best_idx]
                confidence = filtered_sims[best_idx]
            else:
                best_idx = similarities.argmax().item()
                best_category = categories[best_idx]
                confidence = similarities[best_idx].item()
            
            # Ensure minimum confidence
            confidence = max(confidence, 0.3)
            
            return (best_category, round(confidence, 2))
            
        except Exception as e:
            print(f"Semantic similarity prediction failed: {e}")
            return self._transformer_prediction(description, available_categories)
    
    def predict_category(
        self,
        description: str,
        available_categories: Optional[List[str]] = None,
        method: str = "auto"
    ) -> Tuple[str, float]:
        """
        Predict category using AI models (transformer/semantic) with intelligent fallback.
        
        Args:
            description: Item description text
            available_categories: List of valid category names
            method: Prediction method - "auto", "transformer", "semantic", "keyword"
            
        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        # Use keyword-based for empty descriptions with default category
        if not description or not description.strip():
            return ("Food", 0.15)  # Default to most common donation category
        
        # Choose prediction method - prioritize AI models
        if method == "keyword":
            # Explicitly requested keyword-only
            result = self._keyword_based_prediction(description, available_categories)
        elif method == "transformer":
            # Explicitly requested transformer
            if self.classifier:
                result = self._transformer_prediction(description, available_categories)
            else:
                print("⚠️  Transformer not available, using keywords")
                result = self._keyword_based_prediction(description, available_categories)
        elif method == "semantic":
            # Explicitly requested semantic
            if self.embedder:
                result = self._semantic_similarity_prediction(description, available_categories)
            else:
                print("⚠️  Semantic model not available, using transformer or keywords")
                result = self._transformer_prediction(description, available_categories) if self.classifier else self._keyword_based_prediction(description, available_categories)
        else:  # auto - use best available AI model
            if self.embedder:
                # Best: Semantic similarity
                result = self._semantic_similarity_prediction(description, available_categories)
            elif self.classifier:
                # Good: Zero-shot transformer
                result = self._transformer_prediction(description, available_categories)
            else:
                # Fallback: Enhanced keywords
                result = self._keyword_based_prediction(description, available_categories)
        
        # Never return "Unknown" - always provide best guess
        if result[0] == "Unknown" or result[1] < 0.1:
            return self._keyword_based_prediction(description, available_categories)
        
        return result
    
    def get_model_status(self) -> dict:
        """Get the current status of loaded models."""
        return {
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "classifier_loaded": self.model_status.get("classifier", False),
            "embedder_loaded": self.model_status.get("embedder", False),
            "active_method": "semantic" if self.embedder else ("transformer" if self.classifier else "keyword")
        }
    
    def get_category_suggestions(
        self,
        description: str,
        top_n: int = 3,
        available_categories: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Get top N category suggestions with confidence scores.
        
        Args:
            description: Item description
            top_n: Number of suggestions to return
            available_categories: List of valid categories
            
        Returns:
            List of tuples (category, confidence)
        """
        if not description or not description.strip():
            return []
        
        categories = list(self.CATEGORIES.keys())
        if available_categories:
            categories = [c for c in categories if c in available_categories]
        
        if not categories:
            return []
        
        if self.classifier:
            try:
                result = self.classifier(
                    description,
                    candidate_labels=categories,
                    multi_label=False
                )
                return [
                    (label, round(score, 2))
                    for label, score in zip(result['labels'][:top_n], result['scores'][:top_n])
                ]
            except Exception:
                pass
        
        # Fallback to keyword-based
        processed = self.preprocess_text(description)
        tokens = set(processed.split())
        scores = {}
        
        for category in categories:
            keywords = set(self.CATEGORIES[category]['keywords'])
            matches = len(tokens & keywords)
            partial = sum(
                1 for token in tokens 
                for keyword in keywords 
                if keyword in token or token in keyword
            )
            scores[category] = matches * 3 + partial
        
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        for cat, score in sorted_cats:
            if score > 0:
                total = len(self.CATEGORIES[cat]['keywords'])
                conf = min(score / (total * 0.5), 1.0)
                results.append((cat, round(conf, 2)))
        
        return results


# Global predictor instance
predictor = None


def get_predictor() -> EnhancedCategoryPredictor:
    """Get or create the global predictor instance."""
    global predictor
    if predictor is None:
        predictor = EnhancedCategoryPredictor(use_transformers=True)
    return predictor


def predict_item_category(
    description: str,
    available_categories: Optional[List[str]] = None,
    method: str = "auto"
) -> Tuple[str, float]:
    """
    Convenience function for AI-powered category prediction.
    Uses transformer models when available, falls back to enhanced keywords.
    
    Args:
        description: Item description
        available_categories: List of valid categories
        method: Prediction method (auto uses best available AI model)
        
    Returns:
        Tuple of (category, confidence)
    """
    pred = get_predictor()
    return pred.predict_category(description, available_categories, method)


def get_model_status() -> dict:
    """
    Get status of loaded AI models.
    
    Returns:
        Dictionary with model loading status and active prediction method
    """
    pred = get_predictor()
    return pred.get_model_status()


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    pred = EnhancedCategoryPredictor()
    
    # Test items
    test_items = [
        "Paracetamol 500mg tablets for fever",
        "Fresh organic tomatoes",
        "Blue cotton t-shirt size M",
        "Antibacterial hand sanitizer gel",
        "Ballpoint pen pack of 10"
    ]
    
    print("\n=== Category Predictions ===\n")
    for item in test_items:
        category, confidence = pred.predict_category(item)
        print(f"Item: {item}")
        print(f"Category: {category} (Confidence: {confidence:.2%})")
        
        # Show top 3 suggestions
        suggestions = pred.get_category_suggestions(item, top_n=3)
        print(f"Suggestions: {suggestions}\n")