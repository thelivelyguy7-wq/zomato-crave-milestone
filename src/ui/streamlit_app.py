import streamlit as st
import logging
from typing import Optional

# Setup basic logging for Streamlit app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.models.preferences import UserPreferences, BudgetTier
from src.data.repository import RestaurantRepository
from src.services.llm.groq_client import GroqClient
from src.services.recommendation import RecommendationService
from src.config import get_settings

st.set_page_config(
    page_title="Zomato AI Recommendations",
    page_icon="🍽️",
    layout="wide",
)

# --- Caching Core Services ---

@st.cache_resource
def get_repository() -> RestaurantRepository:
    """Load dataset and repository once."""
    return RestaurantRepository()

@st.cache_resource
def get_llm_client() -> Optional[GroqClient]:
    """Initialize LLM Client once if API key is present."""
    settings = get_settings()
    if settings.has_api_key:
        try:
            return GroqClient()
        except Exception as e:
            logger.error(f"Failed to initialize GroqClient: {e}")
    return None

@st.cache_resource
def get_recommendation_service() -> RecommendationService:
    repo = get_repository()
    client = get_llm_client()
    return RecommendationService(repository=repo, llm_client=client)

# Initialize services
repo = get_repository()
service = get_recommendation_service()
locations = repo.get_locations()
cuisines = repo.get_cuisines()

# --- UI Layout ---

st.title("🍽️ Zomato AI Recommendations")
st.markdown(
    "Find your perfect dining spot! We use **Llama 3 70B** to rank and explain "
    "the best restaurant matches based on your specific preferences."
)

if not get_settings().has_api_key:
    st.warning("⚠️ **GROQ_API_KEY** is missing from your `.env` file. Using standard rating-based recommendations without AI explanations.")

# --- Sidebar Form ---

with st.sidebar:
    st.header("Your Preferences")
    
    with st.form("preferences_form"):
        # We add an empty string as the first option to force user to select
        location = st.selectbox("Location *", options=[""] + locations, help="Select a city or locality")
        
        budget = st.selectbox("Budget *", options=["low", "medium", "high"], index=1, help="Low <= 300, Medium 301-700, High > 700")
        
        cuisine = st.selectbox("Cuisine (Optional)", options=[""] + cuisines, help="Select a specific cuisine")
        
        min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=3.5, step=0.1)
        
        additional_prefs = st.text_area(
            "Additional Preferences", 
            placeholder="e.g., family-friendly, good for dates, fast service...",
            help="Any specific vibes or requirements?"
        )
        
        top_k = st.number_input("Number of Recommendations", min_value=1, max_value=20, value=5)
        
        submit_button = st.form_submit_button("Get Recommendations")

# --- Main Logic ---

if submit_button:
    if not location:
        st.error("Please select a location to get recommendations.")
    else:
        # Build UserPreferences
        prefs = UserPreferences(
            location=location,
            budget=budget, # type: ignore
            cuisine=cuisine if cuisine else None,
            min_rating=min_rating,
            additional_preferences=additional_prefs if additional_prefs else None,
            top_k=int(top_k)
        )
        
        # Get Recommendations
        with st.spinner("Analyzing restaurants with Llama 3..."):
            try:
                results = service.recommend(prefs)
                
                if not results:
                    st.info("No restaurants matched your filters. Try relaxing your criteria (e.g., lower rating or different location).")
                else:
                    st.subheader(f"Top {len(results)} Recommendations")
                    
                    for r in results:
                        rest = r.restaurant
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### #{r.rank} {rest.name}")
                                st.markdown(f"**Cuisine:** {rest.cuisine} | **Location:** {rest.location}")
                                st.write(f"💡 {r.explanation}")
                                
                            with col2:
                                st.metric("Rating", f"⭐ {rest.rating:.1f}")
                                st.metric("Cost for Two", f"₹{rest.cost_for_two}")
                                
            except Exception as e:
                logger.error(f"Error during recommendation: {e}")
                st.error("An error occurred while generating recommendations. Please try again.")
else:
    # Empty State
    st.write("👈 Set your preferences in the sidebar and click **Get Recommendations** to start!")
