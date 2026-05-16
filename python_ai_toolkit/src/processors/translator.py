from typing import Dict, Any, Optional
from src.openai_client import openai_client

class Translator:
    """Text translation processor"""
    
    SUPPORTED_LANGUAGES = {
        'spanish': 'es',
        'french': 'fr',
        'german': 'de',
        'italian': 'it',
        'portuguese': 'pt',
        'dutch': 'nl',
        'russian': 'ru',
        'japanese': 'ja',
        'korean': 'ko',
        'chinese': 'zh',
        'arabic': 'ar',
        'hindi': 'hi'
    }
    
    def __init__(self):
        self.system_prompt = """You are a professional translator.
        Translate the given text accurately while preserving:
        - Original meaning and nuance
        - Tone and style
        - Cultural context when appropriate
        Do not add or remove information unless necessary for natural expression."""
    
    def translate(
        self, 
        text: str, 
        target_lang: str,
        source_lang: Optional[str] = None,
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Input text to translate
            target_lang: Target language (e.g., 'spanish', 'french')
            source_lang: Source language (auto-detect if None)
            preserve_formatting: Keep line breaks and formatting
        
        Returns:
            Dictionary with translation and metadata
        """
        # Normalize language names
        target_lang = target_lang.lower()
        if target_lang in self.SUPPORTED_LANGUAGES:
            target_lang_name = target_lang
            target_code = self.SUPPORTED_LANGUAGES[target_lang]
        else:
            target_lang_name = target_lang
            target_code = target_lang
        
        source_text = f"from {source_lang}" if source_lang else "(auto-detect)"
        
        formatting_instruction = "Preserve original line breaks and paragraph structure." if preserve_formatting else ""
        
        prompt = f"""Translate the following text {source_text} to {target_lang_name}.
        
        {formatting_instruction}
        
        Original text:
        {text}
        
        Translation to {target_lang_name}:"""
        
        result = openai_client.call_api(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3  # Lower temperature for consistent translations
        )
        
        if result['success']:
            result['metadata'] = {
                'input_length': len(text),
                'input_tokens': openai_client.count_tokens(text),
                'output_length': len(result['content']),
                'target_language': target_lang_name,
                'source_language': source_lang or 'auto-detected'
            }
        
        return result
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the given text"""
        prompt = f"""Detect the language of the following text.
        Respond with ONLY the language name in English.
        
        Text: {text}
        
        Language:"""
        
        result = openai_client.call_api(prompt=prompt, temperature=0)
        
        if result['success']:
            result['detected_language'] = result['content'].strip()
        
        return result