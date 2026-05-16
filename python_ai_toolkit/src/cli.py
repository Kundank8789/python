#!/usr/bin/env python3
"""
Python AI Toolkit CLI
A command-line tool for text processing using OpenAI API
"""

import argparse
import sys
import os
from typing import Optional
from pathlib import Path
from contextlib import contextmanager

# Add src to path - FIXED PATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Now import using absolute imports
from src.processors.summarizer import Summarizer
from src.processors.translator import Translator
from src.processors.sentiment import SentimentAnalyzer
from src.openai_client import openai_client

# Try to import rich for better output formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

class AIToolkitCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.summarizer = Summarizer()
        self.translator = Translator()
        self.sentiment = SentimentAnalyzer()
    
    def read_input(self, text: Optional[str], input_file: Optional[str]) -> str:
        """Read input from either direct text or file"""
        if text:
            return text
        elif input_file:
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                self.error(f"File not found: {input_file}")
                sys.exit(1)
            except Exception as e:
                self.error(f"Error reading file: {e}")
                sys.exit(1)
        else:
            # Read from stdin
            self.info("Enter text (Ctrl-D or Ctrl-Z to finish):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            return '\n'.join(lines)
    
    def output_result(self, result: dict, output_file: Optional[str] = None, format_type: str = "text"):
        """Output the result to console or file"""
        if not result['success']:
            self.error(f"API Error: {result.get('error', 'Unknown error')}")
            return
        
        content = result['content']
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.success(f"Output saved to: {output_file}")
            except Exception as e:
                self.error(f"Error writing to file: {e}")
        
        # Print to console
        if RICH_AVAILABLE and console:
            self._rich_output(result, format_type)
        else:
            self._simple_output(result, format_type)
    
    def _rich_output(self, result: dict, format_type: str):
        """Output using rich library"""
        content = result['content']
        
        if format_type == "json":
            from json import dumps
            console.print(Syntax(dumps(result, indent=2), "json", theme="monokai"))
        elif format_type == "markdown":
            console.print(Panel(content, title="Result", border_style="green"))
        else:
            console.print(Panel(content, title="Result", border_style="blue"))
        
        # Show token usage if available
        if 'usage' in result:
            usage = result['usage']
            console.print(f"\n[dim]📊 Tokens used: {usage['total_tokens']} "
                         f"(prompt: {usage['prompt_tokens']}, "
                         f"completion: {usage['completion_tokens']})[/dim]")
        
        # Show metadata if available
        if 'metadata' in result:
            meta = result['metadata']
            console.print("\n[bold cyan]📋 Metadata:[/bold cyan]")
            for key, value in meta.items():
                console.print(f"  • {key}: {value}")
    
    def _simple_output(self, result: dict, format_type: str):
        """Simple text output without rich"""
        content = result['content']
        
        if format_type == "json":
            import json
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "="*50)
            print("RESULT:")
            print("="*50)
            print(content)
            print("="*50)
            
            if 'usage' in result:
                print(f"\nTokens used: {result['usage']['total_tokens']}")
    
    def info(self, message: str):
        """Print info message"""
        if RICH_AVAILABLE and console:
            console.print(f"[cyan]ℹ️  {message}[/cyan]")
        else:
            print(f"INFO: {message}")
    
    def success(self, message: str):
        """Print success message"""
        if RICH_AVAILABLE and console:
            console.print(f"[green]✅ {message}[/green]")
        else:
            print(f"SUCCESS: {message}")
    
    def error(self, message: str):
        """Print error message"""
        if RICH_AVAILABLE and console:
            console.print(f"[red]❌ {message}[/red]")
        else:
            print(f"ERROR: {message}", file=sys.stderr)
    
    @contextmanager
    def show_progress(self, message: str):
        """Simple progress indicator"""
        print(f"{message}... ", end='', flush=True)
        yield
        print("Done!")
    
    def run_summarize(self, args):
        """Handle summarize command"""
        text = self.read_input(args.text, args.input_file)
        
        if not text.strip():
            self.error("No text provided for summarization")
            return
        
        self.info(f"Summarizing text ({len(text)} characters)...")
        
        with self.show_progress("Generating summary"):
            result = self.summarizer.summarize(
                text,
                max_length=args.length,
                focus=args.focus
            )
        
        self.output_result(result, args.output, args.format)
    
    def run_translate(self, args):
        """Handle translate command"""
        text = self.read_input(args.text, args.input_file)
        
        if not text.strip():
            self.error("No text provided for translation")
            return
        
        self.info(f"Translating to {args.target}...")
        
        with self.show_progress("Translating"):
            result = self.translator.translate(
                text,
                target_lang=args.target,
                source_lang=args.source,
                preserve_formatting=not args.no_formatting
            )
        
        self.output_result(result, args.output, args.format)
    
    def run_sentiment(self, args):
        """Handle sentiment command"""
        text = self.read_input(args.text, args.input_file)
        
        if not text.strip():
            self.error("No text provided for sentiment analysis")
            return
        
        self.info("Analyzing sentiment...")
        
        with self.show_progress("Analyzing"):
            result = self.sentiment.analyze(text, detailed=args.detailed)
        
        if result['success'] and args.detailed:
            # Special formatting for sentiment
            analysis = result.get('analysis', {})
            
            if RICH_AVAILABLE and console:
                self._display_sentiment(result)
            else:
                print(f"\nSentiment: {analysis.get('sentiment', 'unknown')}")
                print(f"Confidence: {analysis.get('confidence', 0)}")
                print(f"Emotions: {', '.join(analysis.get('emotions', []))}")
                print(f"Intensity: {analysis.get('intensity', 'unknown')}")
                if 'explanation' in analysis:
                    print(f"\nExplanation: {analysis.get('explanation', 'N/A')}")
        
        self.output_result(result, args.output, args.format)
    
    def _display_sentiment(self, result: dict):
        """Display sentiment with rich formatting"""
        analysis = result.get('analysis', {})
        sentiment = analysis.get('sentiment', 'neutral')
        
        # Color based on sentiment
        color = {
            'positive': 'green',
            'negative': 'red',
            'neutral': 'yellow'
        }.get(sentiment, 'white')
        
        console.print(f"\n[bold {color}]Sentiment: {sentiment.upper()}[/bold {color}]")
        
        if 'confidence' in analysis:
            console.print(f"Confidence: {analysis['confidence']:.2%}")
        
        if 'emotions' in analysis:
            emotions_str = ", ".join(analysis['emotions'])
            console.print(f"Emotions: {emotions_str}")
        
        if 'intensity' in analysis:
            intensity_color = {
                'low': 'green',
                'medium': 'yellow',
                'high': 'red'
            }.get(analysis['intensity'], 'white')
            console.print(f"Intensity: [{intensity_color}]{analysis['intensity'].upper()}[/{intensity_color}]")
        
        if 'explanation' in analysis:
            console.print(f"\n[dim]Explanation:[/dim] {analysis['explanation']}")
    
    def run_interactive(self, args):
        """Run in interactive mode"""
        self.info("Starting interactive mode. Type 'exit' to quit.")
        self.info("Commands: summarize, translate, sentiment, help, exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'exit':
                    self.success("Goodbye!")
                    break
                elif command == 'help':
                    print("""
Commands:
  summarize [text]  - Summarize the following text
  translate [text]  - Translate the following text  
  sentiment [text]  - Analyze sentiment of the following text
  exit             - Exit interactive mode
                    """)
                elif command in ['summarize', 'translate', 'sentiment']:
                    text = input("Enter text to process: ")
                    
                    # Create dummy args
                    class DummyArgs:
                        pass
                    
                    dummy = DummyArgs()
                    dummy.text = text
                    dummy.input_file = None
                    dummy.output = None
                    dummy.format = 'text'
                    
                    if command == 'summarize':
                        dummy.length = 'medium'
                        dummy.focus = 'general'
                        self.run_summarize(dummy)
                    elif command == 'translate':
                        dummy.target = input("Target language: ")
                        dummy.source = None
                        dummy.no_formatting = False
                        self.run_translate(dummy)
                    else:
                        dummy.detailed = True
                        self.run_sentiment(dummy)
                elif command:
                    self.error(f"Unknown command: {command}")
            
            except KeyboardInterrupt:
                print("\n")
                self.success("Goodbye!")
                break
            except EOFError:
                break

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Python AI Toolkit - Text processing with OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize text
  python cli.py summarize --text "Long article text here..."
  
  # Summarize from file
  python cli.py summarize --input article.txt --length short --focus key_points
  
  # Translate text
  python cli.py translate --text "Hello world" --target spanish
  
  # Analyze sentiment
  python cli.py sentiment --text "I love this product!" --detailed
  
  # Interactive mode
  python cli.py interactive
  
  # Pipe input
  cat file.txt | python cli.py summarize
        """
    )
    
    parser.add_argument(
        '--format', 
        choices=['text', 'json', 'markdown'], 
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save output to file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize text')
    summarize_parser.add_argument('--text', '-t', help='Text to summarize')
    summarize_parser.add_argument('--input', '-i', dest='input_file', help='Input file')
    summarize_parser.add_argument('--length', choices=['short', 'medium', 'long'], default='medium')
    summarize_parser.add_argument('--focus', choices=['general', 'key_points', 'actionable'], default='general')
    summarize_parser.add_argument('--output', '-o', help='Output file')
    summarize_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text')
    
    # Translate command
    translate_parser = subparsers.add_parser('translate', help='Translate text')
    translate_parser.add_argument('--text', '-t', help='Text to translate')
    translate_parser.add_argument('--input', '-i', dest='input_file', help='Input file')
    translate_parser.add_argument('--target', '-l', required=True, help='Target language')
    translate_parser.add_argument('--source', '-s', help='Source language (auto-detect if not specified)')
    translate_parser.add_argument('--no-formatting', action='store_true', help='Don\'t preserve formatting')
    translate_parser.add_argument('--output', '-o', help='Output file')
    translate_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text')
    
    # Sentiment command
    sentiment_parser = subparsers.add_parser('sentiment', help='Analyze sentiment')
    sentiment_parser.add_argument('--text', '-t', help='Text to analyze')
    sentiment_parser.add_argument('--input', '-i', dest='input_file', help='Input file')
    sentiment_parser.add_argument('--detailed', '-d', action='store_true', help='Detailed analysis')
    sentiment_parser.add_argument('--output', '-o', help='Output file')
    sentiment_parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not found in environment.", file=sys.stderr)
        print("Please create a .env file with your API key.", file=sys.stderr)
        print("See .env.example for reference.", file=sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = AIToolkitCLI()
    
    # Route to appropriate handler
    if args.command == 'summarize':
        cli.run_summarize(args)
    elif args.command == 'translate':
        cli.run_translate(args)
    elif args.command == 'sentiment':
        cli.run_sentiment(args)
    elif args.command == 'interactive':
        cli.run_interactive(args)

if __name__ == '__main__':
    main()