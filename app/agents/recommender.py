import os
from openai import OpenAI
from app.config import settings
from app.database.vector_store import query_mechanics
from app.agents.user_simulator import simulate_user_review
from app.agents.templates import RECOMMENDER_AGENT_TEMPLATE
from app.schemas.persona import TaskASimulationPayload, UserPersona
from app.schemas.shop import MechanicShop

# Instantiated dynamically using properties from config layer.
client = OpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY
)

def generate_auto_recommendation(vehicle_issue: str, user_mood: str, sector_name: str, user_name: str = "Driver") -> str:
    """
    Executes the full pipeline:
    1. Fetches candidate shops from ChromaDB based on the vehicle issue.
    2. Evaluates each shop using structured schema payloads.
    3. Synthesizes user evaluations into a Lagos-localized blueprint.
    """
    print(f"Searching for mechanics matches: '{vehicle_issue}' in {sector_name} Axis...")
    
    # 1. Fetch relevant mechanic candidates from ChromaDB vector catalog
    raw_candidates = query_mechanics(query_text=vehicle_issue, n_results=3)
    
    if not raw_candidates:
        return f"Apologies! I wasn't able to find any mechanics matching that description near the {sector_name} Axis right now."

    # 2. REASONING & SIMULATION PHASE
    evaluated_candidates_text = ""
    print("Running Digital User behavioral simulation on candidate shops...")
    
    for idx, shop in enumerate(raw_candidates, 1):
        try:
            # Enforce data parsing into the explicit MechanicShop Pydantic model
            # This handles it smoothly whether query returns a dictionary or an object
            if isinstance(shop, dict):
                shop_obj = MechanicShop(**shop)
            else:
                shop_obj = shop

            # Reconstruct the dynamic driver profile state container
            user_persona_obj = UserPersona(
                name=user_name,
                persona_mood=user_mood,
                vehicle_issue=vehicle_issue,
                location=f"{sector_name} Axis, Lagos State, Nigeria"
            )

            # Package both inputs inside the strict validation payload contract
            simulation_payload = TaskASimulationPayload(
                user_persona=user_persona_obj,
                shop_data=shop_obj
            )
            
            # Execute the standalone simulation agent function using the updated signature
            simulation_result = simulate_user_review(simulation_payload)
            
            predicted_rating = simulation_result.get("predicted_rating", 3.0)
            simulated_review = simulation_result.get("simulated_review", "No feedback generated.")
            
            # Compile this simulated critique cleanly into a text block using object properties
            evaluated_candidates_text += (
                f"{idx}. {shop_obj.name}\n"
                f"   - Network Rating Score: {shop_obj.stars} / 5.0\n"
                f"   - Core Specializations: {shop_obj.categories}\n"
                f"   - DIGITAL TWIN SIMULATION FEEDBACK:\n"
                f"     * Predicted Choice Rating: {predicted_rating}/5.0\n"
                f"     * Simulated Local Review: \"{simulated_review}\"\n\n"
            )
        except Exception as loop_err:
            print(f"Skipping malformed workshop entity during simulation loop: {loop_err}")
            continue

    if not evaluated_candidates_text:
        return f"Apologies! We couldn't safely parse or simulate any available mechanics around the {sector_name} Axis."

    # 3. MULTI-TURN REASONING & RECOMMENDATION
    # Formats the final template prompt with all the combined contextual strings
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
        print(f"Error executing Recommender Agent multi-turn planner: {e}")
        return (
            "Apologies! I hit a temporary hitch while analyzing the final recommendations. "
            "Let's try refreshing this request in a moment!"
        )