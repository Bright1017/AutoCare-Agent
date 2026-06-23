import json
from openai import OpenAI
from app.config import settings
from app.agents.templates import USER_SIMULATOR_TEMPLATE
from app.schemas.persona import TaskASimulationPayload  

# Instantiated dynamically using properties from config layer.
client = OpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY
)

def simulate_user_review(payload: TaskASimulationPayload) -> dict:
    """
    Executes by spinning up the User's Digital Twin to evaluate a candidate mechanic shop.
    Accepts a strongly-typed TaskASimulationPayload object instead of raw primitives.
    """
    # Safely extract structured nested fields from Pydantic schemas
    persona = payload.user_persona
    shop = payload.shop_data

    # Safeguard against missing or corrupted review contexts in the dataset
    review_context = shop.review_context if shop.review_context else "No historical review snippets available for this shop."
    if isinstance(review_context, list):
        review_context = " ".join(review_context)

    # Format the prompt template with clean property lookups from schema models
    formatted_prompt = USER_SIMULATOR_TEMPLATE.format(
        persona_mood=f"{persona.name} (acting as a driver who is {persona.persona_mood})",
        vehicle_issue=persona.vehicle_issue,
        shop_name=shop.name,
        shop_categories=shop.categories,
        shop_stars=shop.stars,
        review_context=review_context
    )

    try:
        # Request a JSON-enforced response from the model
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            response_format={"type": "json_object"}, 
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
            "simulated_review": f"I didn't process this evaluation smoothly due to a system glitch. However, based on how {shop.name} takes historical data, this shop averages {shop.stars} stars."
        }