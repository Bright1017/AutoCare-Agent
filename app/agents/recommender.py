import os
from openai import OpenAI
from app.config import settings
from app.database.vector_store import query_mechanics
from app.agents.user_simulator import simulate_user_review
from app.agents.templates import RECOMMENDER_AGENT_TEMPLATE

# Initialize the client pointed directly at Groq's open-source API cluster
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY
)

#  Accepts the user's vehicle issue, mood, and location sector to generate a personalized auto repair recommendation plan.
def generate_auto_recommendation(vehicle_issue: str, user_mood: str, sector_name: str) -> str:
    """
    Executes the full pipeline:
    1. Fetches candidate shops from ChromaDB.
    2. Runs Task A (Reasoning): Simulates the user twin's review & rating for each shop.
    3. Runs Task B (Recommendation): Synthesizes those reviews to output a ranked action plan.
    """
    print(f"Searching database for matches matching: '{vehicle_issue}'...")
    
    # 1. Fetch relevant mechanic candidates from ChromaDB vector catalog
    raw_candidates = query_mechanics(query_text=vehicle_issue, n_results=3)
    
    if not raw_candidates:
        return f"Abeg no vex, I no find any mechanics matching that description near {sector_name} right now."

    # 2. TASK A: REASONING & SIMULATION PHASE
    # loops through each mechanic and let the Digital Twin evaluate it
    evaluated_candidates_text = ""
    
    print("Running Digital User behavioral simulation on candidate shops...")
    for idx, shop in enumerate(raw_candidates, 1):
        # Trigger the user simulation function
        simulation_result = simulate_user_review(
            persona_mood=user_mood,
            vehicle_issue=vehicle_issue,
            shop_data=shop
        )
        
        predicted_rating = simulation_result.get("predicted_rating", 3.0)
        simulated_review = simulation_result.get("simulated_review", "No feedback generated.")
        
        # Compile this simulated critique into a text block for the final recommender
        evaluated_candidates_text += (
            f"{idx}. {shop.get('name', 'Unknown Shop')}\n"
            f"   - Historical Yelp Stars: {shop.get('stars', 'N/A')}\n"
            f"   - Specialties: {shop.get('categories', 'General Auto Repair')}\n"
            f"   - DIGITAL USER ANALYSIS & FEELINGS:\n"
            f"     * Predicted Rating from User Profile: {predicted_rating}/5.0\n"
            f"     * Simulated User Review: \"{simulated_review}\"\n\n"
        )

    # 3. TASK B: MULTI-TURN REASONING & RECOMMENDATION
    # template final prompt with all the candidate evaluations and situational context for the concierge agent
    final_prompt = RECOMMENDER_AGENT_TEMPLATE.format(
        user_mood=user_mood,
        vehicle_issue=vehicle_issue,
        sector_name=sector_name,
        retrieved_candidates=evaluated_candidates_text
    )

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional, empathetic auto care concierge planner specialized in the Lagos logistics landscape."
                },
                {
                    "role": "user", 
                    "content": final_prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error executing Recommender Agent: {e}")
        return (
            "E sun mi o! I hit a temporary hitch while analyzing the final recommendations. "
            "Please check your network connection or API keys, and let's try sorting this out again sharp-sharp!"
        )