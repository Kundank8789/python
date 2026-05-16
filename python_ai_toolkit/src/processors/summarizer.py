from typing import Dict, Any
from src.openai_client import openai_client

class Summarizer:
    """Text summarization processor"""
    
    def __init__(self):
        self.system_prompt = """You are a professional text summarizer. 
        Summarize the given text concisely while preserving key information.
        Focus on main points and maintain the original tone.
        Keep the summary to 3-5 sentences unless specified otherwise."""
    
    def summarize(
        self, 
        text: str, 
        max_length: str = "medium",
        focus: str = "general"
    ) -> Dict[str, Any]:
        """
        Summarize the given text
        
        Args:
            text: Input text to summarize
            max_length: 'short', 'medium', or 'long'
            focus: 'general', 'key_points', or 'actionable'
        
        Returns:
            Dictionary with summary and metadata
        """
        length_instructions = {
            'short': '1-2 sentences',
            'medium': '3-5 sentences',
            'long': '6-10 sentences'
        }
        
        focus_instructions = {
            'general': 'general overview',
            'key_points': 'bullet points of key information',
            'actionable': 'actionable insights and conclusions'
        }
        
        prompt = f"""Summarize the following text.
        
        Length: {length_instructions.get(max_length, '3-5 sentences')}
        Focus: {focus_instructions.get(focus, 'general overview')}
        
        Text to summarize:
        {text}
        
        Summary:"""
        
        result = openai_client.call_api(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3  # Lower temperature for more consistent summaries
        )
        
        if result['success']:
            # Add metadata
            result['metadata'] = {
                'input_length': len(text),
                'input_tokens': openai_client.count_tokens(text),
                'summary_length': len(result['content']),
                'max_length_setting': max_length,
                'focus_setting': focus
            }
        
        return result

    def summarize_batch(self, texts: list[str], **kwargs) -> list[Dict[str, Any]]:
        """Summarize multiple texts (sequential, not parallel)"""
        results = []
        for i, text in enumerate(texts):
            print(f"Processing text {i+1}/{len(texts)}...")
            result = self.summarize(text, **kwargs)
            results.append(result)
        return results