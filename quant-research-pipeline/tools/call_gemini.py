import os
from google import genai # Use the new Gemini SDK

def call_gemini_api(prompt: str, model_name: str = "gemini-pro") -> str:
    """
    Calls the Google Gemini API with the given prompt and returns the generated text.

    Args:
        prompt: The text prompt to send to the Gemini model.
        model_name: The name of the Gemini model to use (e.g., "gemini-pro", "gemini-ultra").

    Returns:
        The generated text from the Gemini model.
    """
    
    # The genai.Client() automatically reads GOOGLE_API_KEY from environment variables.
    client = genai.Client()
    model = client.get_model(model_name)

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return ""

if __name__ == "__main__":
    # Example usage:
    test_prompt = "What is the capital of France?"
    print(f"Calling Gemini with prompt: '{test_prompt}'")
    
    # Ensure GOOGLE_API_KEY is set in your environment variables for this to work
    # For testing purposes, you can temporarily set it like:
    # export GOOGLE_API_KEY='YOUR_API_KEY'
    
    response_text = call_gemini_api(test_prompt)
    print(f"Gemini's response: {response_text}")
