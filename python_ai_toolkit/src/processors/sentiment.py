from src.openai_client import openai_client

class SentimentAnalyzer:
    """Sentiment analysis processor"""
    
    def analyze(self, text: str, detailed: bool = True) -> dict:
        """Analyze sentiment of the given text"""
        if detailed:
            prompt = f"""Analyze the sentiment of this text.
            
            Text: {text}
            
            Provide response in format:
            SENTIMENT: [positive/negative/neutral]
            CONFIDENCE: [0-1]
            EMOTIONS: [comma-separated emotions]
            INTENSITY: [low/medium/high]
            EXPLANATION: [brief explanation]
            
            Analysis:"""
            
            result = openai_client.call_api(prompt=prompt, temperature=0.2)
            
            if result['success']:
                # Parse the response
                analysis = {}
                lines = result['content'].strip().split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        
                        if key == 'confidence':
                            try:
                                value = float(value)
                            except:
                                value = 0.5
                        elif key == 'emotions':
                            value = [v.strip() for v in value.split(',')]
                        
                        analysis[key] = value
                
                result['analysis'] = analysis
        
        else:
            prompt = f"Respond with only one word (positive/negative/neutral): {text}"
            result = openai_client.call_api(prompt=prompt, temperature=0)
            if result['success']:
                result['analysis'] = {'sentiment': result['content'].strip().lower()}
        
        return result