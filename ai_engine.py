import os
import google.generativeai as genai

import json

def get_recommendations(record):
    """
    Generate personalized recommendations based on the user's latest carbon record
    using the Gemini API, formatted as structured JSON for Do's and Don'ts.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "general": "Keep up the great work! Your efforts are making a difference.",
            "dos": ["Reduce car usage by taking public transport.", "Switch to LED bulbs to save energy."],
            "donts": ["Leave appliances on standby mode.", "Waste water during showers."]
        }
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
        You are a sustainability expert AI for 'EcoPulse AI'. 
        Analyze the following user's recent carbon emissions (in kg CO2) and provide structured, highly personalized recommendations.
        
        Transportation: {record.transport_emissions} kg
        Home Energy: {record.energy_emissions} kg
        Food: {record.food_emissions} kg
        Waste: {record.waste_emissions} kg
        Water: {record.water_emissions} kg
        Total: {record.total} kg
        
        You must return ONLY a raw JSON object (without markdown code blocks) with the following structure:
        {{
            "general": "A one sentence encouraging overview of their footprint.",
            "dos": ["Actionable specific thing they SHOULD do", "Another specific actionable thing"],
            "donts": ["Specific thing they SHOULD AVOID doing", "Another thing to avoid"]
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "general": "We encountered an issue generating your customized report. Please try again later.",
            "dos": ["Consider carpooling to reduce transport emissions.", "Try to eat a plant-based meal once a week."],
            "donts": ["Unplug devices when not in use.", "Avoid single-use plastics."]
        }

def chat_with_ai(message, user_context=None):
    """
    Interact with the AI assistant based on a user's prompt and their footprint context.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "I'm currently running in demo mode without an API key, but I'd love to chat about sustainability once it's configured!"
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context_str = ""
        if user_context:
            context_str = f"Context: The user's total carbon footprint is {user_context.get('total', 0)} kg CO2. "
            
        prompt = f"""
        You are 'EcoPulse Assistant', a friendly, concise, and helpful sustainability AI coach.
        {context_str}
        User says: {message}
        
        Provide a helpful and concise response. Keep it under 3-4 sentences.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in Chat AI: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later!"
