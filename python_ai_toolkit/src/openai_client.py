"""OpenAI Client - Forced Mock Mode (No API credits needed)"""

import os
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    """Mock client that works without API credits"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("🤖 AI TOOLKIT - DEMO MODE")
        print("="*60)
        print("Running in simulation mode (no API credits required)")
        print("To use real AI, add billing at: https://platform.openai.com/settings/billing")
        print("="*60 + "\n")
    
    def count_tokens(self, text: str) -> int:
        """Simulate token counting"""
        return len(text) // 4
    
    def call_api(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """Return mock responses based on prompt type"""
        
        prompt_lower = prompt.lower()
        
        # SENTIMENT ANALYSIS
        if "sentiment" in prompt_lower or "analyze the sentiment" in prompt_lower:
            text_to_analyze = prompt
            # Extract the actual text
            if "Text: " in prompt:
                text_match = re.search(r'Text: (.*?)(?:\n\n|$)', prompt, re.DOTALL)
                if text_match:
                    text_to_analyze = text_match.group(1).lower()
            
            # Simple sentiment detection
            positive_words = ['love', 'amazing', 'great', 'good', 'excellent', 'fantastic', 'awesome', 'beautiful', 'perfect', 'wonderful']
            negative_words = ['hate', 'terrible', 'bad', 'awful', 'worst', 'disappointed', 'sad', 'angry', 'frustrated', 'horrible']
            
            positive_count = sum(1 for word in positive_words if word in text_to_analyze)
            negative_count = sum(1 for word in negative_words if word in text_to_analyze)
            
            if positive_count > negative_count:
                sentiment = "positive"
                confidence = 0.85 + (positive_count * 0.03)
                emotions = ["happy", "satisfied", "pleased"]
                intensity = "high" if positive_count > 2 else "medium"
                explanation = f"The text contains positive language including: {', '.join([w for w in positive_words if w in text_to_analyze][:3])}"
            elif negative_count > positive_count:
                sentiment = "negative"
                confidence = 0.85 + (negative_count * 0.03)
                emotions = ["disappointed", "frustrated", "unhappy"]
                intensity = "high" if negative_count > 2 else "medium"
                explanation = f"The text expresses dissatisfaction with words like: {', '.join([w for w in negative_words if w in text_to_analyze][:3])}"
            else:
                sentiment = "neutral"
                confidence = 0.70
                emotions = ["neutral", "factual"]
                intensity = "low"
                explanation = "The text appears factual without strong emotional indicators."
            
            content = f"""SENTIMENT: {sentiment}
CONFIDENCE: {min(0.99, confidence):.2f}
EMOTIONS: {', '.join(emotions)}
INTENSITY: {intensity}
EXPLANATION: {explanation}"""
        
        # TRANSLATION
        elif "translate" in prompt_lower:
            # Extract target language
            target_lang = "spanish"  # default
            if "spanish" in prompt_lower:
                target_lang = "Spanish"
            elif "french" in prompt_lower:
                target_lang = "French"
            elif "german" in prompt_lower:
                target_lang = "German"
            elif "japanese" in prompt_lower:
                target_lang = "Japanese"
            elif "chinese" in prompt_lower:
                target_lang = "Chinese"
            
            # Simple translations for common phrases
            translations = {
                "hello world": {
                    "Spanish": "¡Hola mundo!",
                    "French": "Bonjour le monde!",
                    "German": "Hallo Welt!",
                    "Japanese": "こんにちは世界",
                    "Chinese": "你好世界"
                },
                "good morning": {
                    "Spanish": "Buenos días",
                    "French": "Bonjour",
                    "German": "Guten Morgen",
                    "Japanese": "おはようございます",
                    "Chinese": "早上好"
                },
                "how are you": {
                    "Spanish": "¿Cómo estás?",
                    "French": "Comment allez-vous?",
                    "German": "Wie geht es dir?",
                    "Japanese": "お元気ですか",
                    "Chinese": "你好吗"
                },
                "i love you": {
                    "Spanish": "Te amo",
                    "French": "Je t'aime",
                    "German": "Ich liebe dich",
                    "Japanese": "愛しています",
                    "Chinese": "我爱你"
                }
            }
            
            # Check for known phrases
            text_to_translate = prompt.split("Text:")[-1].split("Translation:")[0].strip() if "Text:" in prompt else prompt
            text_lower = text_to_translate.lower()
            
            translated = False
            for phrase, trans_dict in translations.items():
                if phrase in text_lower:
                    content = trans_dict.get(target_lang, f"[Translation to {target_lang} of: '{text_to_translate[:50]}...']")
                    translated = True
                    break
            
            if not translated:
                content = f"[DEMO TRANSLATION to {target_lang}] '{text_to_translate[:100]}...'"
        
        # SUMMARIZATION
        elif "summarize" in prompt_lower:
            # Extract text to summarize
            text_to_summarize = ""
            if "Text: " in prompt:
                text_match = re.search(r'Text: (.*?)(?:\n\n|$)', prompt, re.DOTALL)
                if text_match:
                    text_to_summarize = text_match.group(1).strip()
            
            if not text_to_summarize:
                text_to_summarize = prompt
            
            # Generate a simple summary
            words = text_to_summarize.split()
            if len(words) > 30:
                # Take first 15 words and last 5 words for a basic summary
                summary_words = words[:15] + ["..."] + words[-5:]
                content = " ".join(summary_words)
                content += "\n\n[DEMO MODE: This is a simulated summary. Add OpenAI billing for AI-powered summaries.]"
            else:
                content = text_to_summarize
                content += "\n\n[DEMO MODE: Simulated response - add API credits for real AI summaries]"
        
        # DEFAULT
        else:
            content = "[DEMO MODE: This is a simulated response. Add billing to your OpenAI account for real AI responses.]"
        
        return {
            'success': True,
            'content': content,
            'usage': {
                'total_tokens': 150,
                'prompt_tokens': 100,
                'completion_tokens': 50
            },
            'metadata': {'demo_mode': True},
            'mock': True
        }

# Create global instance
openai_client = OpenAIClient()