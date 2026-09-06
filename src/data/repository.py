import logging
from typing import List, Set
from src.models.restaurant import Restaurant
from src.data.loader import load_zomato_dataset

logger = logging.getLogger(__name__)

class RestaurantRepository:
    """In-memory repository for restaurants."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.restaurants = []
            cls._instance.locations = set()
            cls._instance.cuisines = set()
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_data()
            self._initialized = True

    def _load_data(self):
        logger.info("Initializing RestaurantRepository...")
        self.restaurants = load_zomato_dataset()
        
        # Populate unique locations and cuisines for UI dropdowns
        for r in self.restaurants:
            self.locations.add(r.location)
            
            # Cuisines are comma separated
            if r.cuisine and r.cuisine != "Unknown":
                for c in r.cuisine.split(","):
                    c = c.strip()
                    if c:
                        self.cuisines.add(c)
                        
        logger.info(f"Repository initialized with {len(self.locations)} locations and {len(self.cuisines)} distinct cuisines.")

    def get_all(self) -> List[Restaurant]:
        return self.restaurants
        
    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        for r in self.restaurants:
            if r.id == restaurant_id:
                return r
        return None

    def get_locations(self) -> List[str]:
        return sorted(list(self.locations))
        
    def get_cuisines(self) -> List[str]:
        return sorted(list(self.cuisines))
