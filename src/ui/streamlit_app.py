import streamlit as st
import logging
from typing import Optional

# Setup basic logging for Streamlit app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.models.preferences import UserPreferences
from src.data.repository import RestaurantRepository
from src.services.llm.groq_client import GroqClient
from src.services.recommendation import RecommendationService
from src.config import get_settings

st.set_page_config(
    page_title="CraveAI - Zomato Recommendations",
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
settings = get_settings()
repo = get_repository()
service = get_recommendation_service()
locations = repo.get_locations()
cuisines = repo.get_cuisines()

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

# --- Header ---

title_col, status_col = st.columns([3, 1])
with title_col:
    st.title("🍽️ CraveAI")
    st.caption("Zomato-style restaurant recommendations, ranked and explained by AI.")
with status_col:
    st.metric("Restaurants loaded", f"{len(repo.get_all())}")

if not settings.has_api_key:
    st.warning(
        "⚠️ **GROQ_API_KEY** is missing — showing standard rating-based recommendations "
        "without AI explanations. Add a key to `.env` to enable AI ranking."
    )
else:
    st.caption(f"🤖 AI ranking powered by **{settings.llm_model}** via Groq")

# --- Sidebar Form ---

with st.sidebar:
    st.header("Refine your craving")

    with st.form("preferences_form"):
        # Empty string ("Bengaluru (All)") means no location filter — search every area.
        location = st.selectbox(
            "Location",
            options=[""] + locations,
            format_func=lambda v: "Bengaluru (All)" if v == "" else v,
            help="Pick a locality, or leave as Bengaluru (All) to search the whole city",
        )

        budget = st.select_slider(
            "Budget *", options=["low", "medium", "high"], value="medium",
            help="Low ≤ ₹300 · Medium ₹301–700 · High > ₹700",
        )

        cuisine = st.selectbox("Cuisine (optional)", options=[""] + cuisines, help="Select a specific cuisine")

        min_rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=3.5, step=0.1)

        additional_prefs = st.text_area(
            "Describe your vibe (optional)",
            placeholder="e.g., cozy spot for a date, quick solo lunch, family-friendly...",
            max_chars=500,
        )

        top_k = st.slider("Number of recommendations", min_value=1, max_value=15, value=5)

        submit_button = st.form_submit_button("✨ Get AI Recommendations", use_container_width=True)

    st.caption(f"📍 {len(locations)} locations · 🍜 {len(cuisines)} cuisines available")

# --- Main Logic ---

if submit_button:
    prefs = UserPreferences(
        location=location,
        budget=budget,  # type: ignore
        cuisine=cuisine if cuisine else None,
        min_rating=min_rating,
        additional_preferences=additional_prefs if additional_prefs else None,
        top_k=int(top_k),
    )
    location_label = location if location else "Bengaluru"

    spinner_label = (
        f"Asking {settings.llm_model} for personalized picks…"
        if settings.has_api_key
        else "Ranking restaurants by rating…"
    )
    with st.spinner(spinner_label):
        try:
            results = service.recommend(prefs)

            if not results:
                st.info(
                    "🔍 No restaurants matched your filters. Try lowering the minimum rating, "
                    "widening the budget tier, or clearing the cuisine filter."
                )
            else:
                fallback_used = not service.llm_client or results[0].explanation.startswith(
                    "Matches your preferences"
                )
                if fallback_used and service.llm_client:
                    st.warning("⚠️ AI ranking is temporarily unavailable — showing standard rating-based picks instead.")

                st.subheader(f"✨ Top {len(results)} picks in {location_label}")

                for r in results:
                    rest = r.restaurant
                    medal = RANK_MEDALS.get(r.rank, f"#{r.rank}")
                    with st.container(border=True):
                        header_col, rating_col = st.columns([4, 1])
                        with header_col:
                            st.markdown(f"#### {medal} {rest.name}")
                            st.caption(f"🍽️ {rest.cuisine}  ·  📍 {rest.location}")
                        with rating_col:
                            st.markdown(f"### ⭐ {rest.rating:.1f}")
                            st.caption(f"₹{rest.cost_for_two} for two")

                        if not fallback_used:
                            st.info(f"💡 **Why AI chose this:** {r.explanation}")
                        else:
                            st.caption(f"💡 {r.explanation}")

        except Exception as e:
            logger.error(f"Error during recommendation: {e}")
            st.error("An error occurred while generating recommendations. Please try again.")
else:
    st.info("👈 Set your preferences in the sidebar and click **Get AI Recommendations** to start.")
