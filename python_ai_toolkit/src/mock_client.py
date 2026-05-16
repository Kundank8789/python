"""Mock OpenAI client for testing without API credits"""

class MockOpenAIClient:
    """Mock client that returns simulated responses"""
    
    def __init__(self):
        print("⚠️  Using MOCK client - no API calls will be made")
        print("💡 Set OPENAI_API_KEY to use real API\n")
    
    def count_tokens(self, text: str) -> int:
        """Simulate token counting"""
        return len(text) // 4  # Rough approximation
    
    def call_api(self, prompt: str, system_prompt=None, temperature=None, **kwargs):
        """Return mock responses based on prompt type"""
        
        # Check what type of request it is
        prompt_lower = prompt.lower()
        
        # Sentiment analysis
        if "sentiment" in prompt_lower or "analyze the sentiment" in prompt_lower:
            # Simple sentiment detection
            if any(word in prompt_lower for word in ['love', 'amazing', 'great', 'good', 'excellent', 'fantastic']):
                sentiment = "positive"
                confidence = 0.95
                emotions = ["happy", "excited", "satisfied"]
                intensity = "high"
                explanation = "The text contains strongly positive emotional language."
            elif any(word in prompt_lower for word in ['hate', 'terrible', 'bad', 'awful', 'worst', 'disappointed']):
                sentiment = "negative"
                confidence = 0.92
                emotions = ["angry", "frustrated", "disappointed"]
                intensity = "high"
                explanation = "The text expresses strong negative emotions."
            else:
                sentiment = "neutral"
                confidence = 0.70
                emotions = ["neutral", "factual"]
                intensity = "low"
                explanation = "The text appears factual without strong emotional content."
            
            content = f"""SENTIMENT: {sentiment}
CONFIDENCE: {confidence}
EMOTIONS: {', '.join(emotions)}
INTENSITY: {intensity}
EXPLANATION: {explanation}"""
            
        # Translation
        elif "translate" in prompt_lower:
            # Simulate translation
            target = "spanish" if "spanish" in prompt_lower else "french" if "french" in prompt_lower else "target language"
            content = f"[MOCK TRANSLATION to {target}] The original text would be translated here."
            
            if "hello world" in prompt_lower:
                content = "¡Hola mundo!" if "spanish" in prompt_lower else "Bonjour le monde!"
            elif "artificial intelligence" in prompt_lower:
                content = "Inteligencia artificial" if "spanish" in prompt_lower else "Intelligence artificielle"
        
        # Summarization
        elif "summarize" in prompt_lower:
            # Extract original text from prompt
            import re
            text_match = re.search(r'Text: (.*?)(?:\n\n|$)', prompt, re.DOTALL)
            if text_match:
                original = text_match.group(1)
                if len(original) > 100:
                    content = original[:100] + "... [MOCK SUMMARY: This is a simulated summary since no API credits are available.]"
                else:
                    content = original + " [MOCK SUMMARY - Add billing to OpenAI to get real summaries]"
            else:
                content = "[MOCK SUMMARY: Add billing to your OpenAI account to get real AI-powered summaries.]"
        
        else:
            content = "[MOCK RESPONSE: This is a simulated response. Add billing to your OpenAI account to get real AI responses.]"
        
        return {
            'success': True,
            'content': content,
            'usage': {
                'total_tokens': 100,
                'prompt_tokens': 80,
                'completion_tokens': 20
            },
            'metadata': {'mock': True}
        }

# Use mock client if no API key or quota issues
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('OPENAI_API_KEY'):
    try:
        from openai import OpenAI
        # Try to create real client
        test_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Test with a simple call (optional - might use credits)
        # For now, just use real client but it will fail if quota exceeded
        from openai_client import OpenAIClient
        openai_client = OpenAIClient()
    except Exception as e:
        print(f"⚠️  Using mock client due to: {e}")
        openai_client = MockOpenAIClient()
else:
    print("⚠️  No API key found. Using mock client.")
    openai_client = MockOpenAIClient()