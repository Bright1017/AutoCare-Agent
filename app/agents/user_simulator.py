import json
from openai import OpenAI
from app.config import settings
from app.agents.templates import USER_SIMULATOR_TEMPLATE

# Instantiated dynamically using properties from your config layer. This ensures that if you switch LLM providers or models in .env or config, the User Simulator will adapt without any hardcoded values, maintaining the modularity and flexibility of your architecture.
client = OpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY
)

def simulate_user_review(persona_mood: str, vehicle_issue: str, shop_data: dict) -> dict:
    """
    Executes Task A by spinning up the User's Digital Twin to evaluate a candidate mechanic shop.
    Returns a dictionary containing 'predicted_rating' and 'simulated_review'.
    """
    # Safeguard against missing or corrupted review contexts in the dataset
    review_context = shop_data.get("review_context", "No historical review snippets available for this shop.")
    if isinstance(review_context, list):
        review_context = " ".join(review_context)

    # Format the prompt template with real-time situational and database variables
    formatted_prompt = USER_SIMULATOR_TEMPLATE.format(
        persona_mood=persona_mood,
        vehicle_issue=vehicle_issue,
        shop_name=shop_data.get("name", "Unknown Mechanic"),
        shop_categories=shop_data.get("categories", "General Auto Repair"),
        shop_stars=shop_data.get("stars", 3.0),
        review_context=review_context
    )

    try:
        # Request a JSON-enforced response from the model
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,  # Dynamically points to your configured active model
            temperature=settings.TEMPERATURE,
            response_format={"type": "json_object"},  # Hard enforces a valid JSON return
            messages=[
                {
                    "role": "system", 
                    "content": "You are a rigid JSON generator. You must only return valid JSON matching the requested keys."
                },
                {
                    "role": "user", 
                    "content": formatted_prompt
                }
            ]
        )

        # Parse out the raw string response into a Python dictionary
        raw_output = response.choices[0].message.content
        parsed_json = json.loads(raw_output)
        
        return parsed_json

    except Exception as e:
        print(f"Error during User Simulator behavioral critique: {e}")
        # Fallback graceful payload to ensure the FastAPI pipeline never crashes during evaluation
        return {
            "predicted_rating": 3.0,
            "simulated_review": f"Abeg, i no process this evaluation smoothly due to a system glitch. But based on how the shop take get historical data, this shop averages {shop_data.get('stars')} stars."
        }