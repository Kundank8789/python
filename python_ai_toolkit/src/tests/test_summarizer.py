import pytest
from unittest.mock import Mock, patch
from src.processors.summarizer import Summarizer

@pytest.fixture
def summarizer():
    return Summarizer()

@patch('src.processors.summarizer.openai_client')
def test_summarize_success(mock_client, summarizer):
    # Mock successful API response
    mock_client.call_api.return_value = {
        'success': True,
        'content': 'This is a summary.',
        'usage': {'total_tokens': 100}
    }
    mock_client.count_tokens.return_value = 50
    
    result = summarizer.summarize("Long text to summarize")
    
    assert result['success'] is True
    assert 'summary' in result['content'] or result['content'] == 'This is a summary.'
    assert 'metadata' in result

@patch('src.processors.summarizer.openai_client')
def test_summarize_error(mock_client, summarizer):
    mock_client.call_api.return_value = {
        'success': False,
        'error': 'API Error'
    }
    
    result = summarizer.summarize("Test text")
    
    assert result['success'] is False
    assert 'error' in result