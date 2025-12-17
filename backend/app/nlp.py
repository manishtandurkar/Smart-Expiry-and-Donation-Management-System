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
                'rice', 'wheat', 'flour', 'grain', 'cereal', 'bread', 'pasta',
                'beans', 'lentils', 'milk', 'cheese', 'yogurt', 'butter',
                'egg', 'meat', 'chicken', 'fish', 'vegetable', 'fruit',
                'oil', 'sugar', 'salt', 'spice', 'snack', 'candy', 'chocolate',
                'juice', 'water', 'beverage', 'canned', 'frozen', 'fresh'
            ]
        },
        'Medicine': {
            'description': 'Medicines, drugs, pharmaceuticals, medical supplies, and healthcare products',
            'keywords': [
                'tablet', 'capsule', 'syrup', 'medicine', 'drug', 'pharmaceutical',
                'antibiotic', 'painkiller', 'paracetamol', 'aspirin', 'ibuprofen',
                'vitamin', 'supplement', 'injection', 'vaccine', 'bandage',
                'antiseptic', 'ointment', 'prescription', 'medical', 'treatment'
            ]
        },
        'Clothing': {
            'description': 'Clothing items, apparel, footwear, and fashion accessories',
            'keywords': [
                'shirt', 'pant', 'trouser', 'dress', 'skirt', 'jacket', 'coat',
                'sweater', 't-shirt', 'jeans', 'shorts', 'underwear',
                'sock', 'shoe', 'sandal', 'boot', 'hat', 'cap', 'scarf',
                'fabric', 'textile', 'garment', 'apparel', 'clothing', 'wear'
            ]
        },
        'Hygiene': {
            'description': 'Personal care products, cleaning supplies, and hygiene items',
            'keywords': [
                'soap', 'shampoo', 'conditioner', 'detergent', 'cleanser',
                'sanitizer', 'hand wash', 'body wash', 'toothpaste', 'toothbrush',
                'deodorant', 'perfume', 'lotion', 'moisturizer', 'sunscreen',
                'tissue', 'toilet paper', 'diaper', 'sanitary', 'towel'
            ]
        },
        'Stationery': {
            'description': 'Office supplies, school items, writing materials, and art supplies',
            'keywords': [
                'pen', 'pencil', 'eraser', 'notebook', 'paper', 'book',
                'marker', 'highlighter', 'ruler', 'scissors', 'glue', 'tape',
                'stapler', 'folder', 'file', 'calculator', 'crayon', 'paint'
            ]
        }
    }
    
    def __init__(self, use_transformers: bool = True, model_name: str = "facebook/bart-large-mnli"):
        """
        Initialize the enhanced predictor.
        
        Args:
            use_transformers: Whether to use transformer models
            model_name: Name of the zero-shot classification model
        """
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.classifier = None
        self.embedder = None
        self.category_embeddings = None
        
        if self.use_transformers:
            try:
                print("Loading zero-shot classification model...")
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model=model_name,
                    device=-1  # Use CPU (-1) or 0 for GPU
                )
                print("Model loaded successfully!")
                
                # Try to load sentence transformer for semantic similarity
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    try:
                        print("Loading sentence transformer...")
                        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                        self._compute_category_embeddings()
                        print("Sentence transformer loaded!")
                    except Exception as e:
                        print(f"Could not load sentence transformer: {e}")
                        self.embedder = None
                        
            except Exception as e:
                print(f"Could not load transformer model: {e}")
                print("Falling back to keyword-based prediction")
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
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def _keyword_based_prediction(
        self, 
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Fallback keyword-based prediction."""
        if not description or not description.strip():
            return ("Unknown", 0.0)
        
        processed = self.preprocess_text(description)
        tokens = set(processed.split())
        
        scores = {}
        categories = self.CATEGORIES.keys()
        if available_categories:
            categories = [c for c in categories if c in available_categories]
        
        for category in categories:
            keywords = set(self.CATEGORIES[category]['keywords'])
            # Count exact matches
            matches = len(tokens & keywords)
            # Check partial matches
            partial = sum(
                1 for token in tokens 
                for keyword in keywords 
                if keyword in token or token in keyword
            )
            scores[category] = matches * 3 + partial
        
        if not scores or max(scores.values()) == 0:
            return ("Unknown", 0.0)
        
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # Normalize confidence
        total_keywords = len(self.CATEGORIES[best_category]['keywords'])
        confidence = min(max_score / (total_keywords * 0.5), 1.0)
        
        return (best_category, round(confidence, 2))
    
    def _transformer_prediction(
        self,
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Use transformer model for prediction."""
        if not self.classifier:
            return self._keyword_based_prediction(description, available_categories)
        
        categories = list(self.CATEGORIES.keys())
        if available_categories:
            categories = [c for c in categories if c in available_categories]
        
        if not categories:
            return ("Unknown", 0.0)
        
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
            
            if keyword_cat == predicted_category and keyword_conf > 0.5:
                confidence = min(confidence * 1.1, 1.0)  # 10% boost
            
            return (predicted_category, round(confidence, 2))
            
        except Exception as e:
            print(f"Transformer prediction failed: {e}")
            return self._keyword_based_prediction(description, available_categories)
    
    def _semantic_similarity_prediction(
        self,
        description: str,
        available_categories: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Use semantic similarity for prediction."""
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
                    return ("Unknown", 0.0)
                
                best_idx = filtered_sims.index(max(filtered_sims))
                best_category = filtered_cats[best_idx]
                confidence = filtered_sims[best_idx]
            else:
                best_idx = similarities.argmax().item()
                best_category = categories[best_idx]
                confidence = similarities[best_idx].item()
            
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
        Predict category for an item.
        
        Args:
            description: Item description text
            available_categories: List of valid category names
            method: Prediction method - "auto", "transformer", "semantic", "keyword"
            
        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        if not description or not description.strip():
            return ("Unknown", 0.0)
        
        # Choose prediction method
        if method == "keyword" or not self.use_transformers:
            return self._keyword_based_prediction(description, available_categories)
        elif method == "transformer":
            return self._transformer_prediction(description, available_categories)
        elif method == "semantic" and self.embedder:
            return self._semantic_similarity_prediction(description, available_categories)
        else:  # auto
            if self.embedder:
                return self._semantic_similarity_prediction(description, available_categories)
            elif self.classifier:
                return self._transformer_prediction(description, available_categories)
            else:
                return self._keyword_based_prediction(description, available_categories)
    
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
    Convenience function for category prediction.
    
    Args:
        description: Item description
        available_categories: List of valid categories
        method: Prediction method
        
    Returns:
        Tuple of (category, confidence)
    """
    pred = get_predictor()
    return pred.predict_category(description, available_categories, method)


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