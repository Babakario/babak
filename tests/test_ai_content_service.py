import pytest
from app.services.ai_content_service import AIContentService

# Initialize the service once for all tests in this module if needed, or per test
@pytest.fixture
def ai_service():
    """Provides an instance of AIContentService."""
    return AIContentService()

def test_generate_caption_placeholder(ai_service):
    prompt = "test prompt"
    caption = ai_service.generate_caption(prompt)
    assert isinstance(caption, str)
    assert prompt in caption # The placeholder includes the prompt
    assert "#AICaption" in caption # Placeholder includes this hashtag

# --- Tests for the new generate_hashtags implementation ---

def test_generate_hashtags_normal(ai_service):
    text = "This is a great post about software engineering and python programming."
    hashtags = ai_service.generate_hashtags(text, num_hashtags=3)
    assert len(hashtags) == 3
    possible_tags = {"#great", "#post", "#software", "#engineering", "#python", "#programming"}
    for tag in hashtags:
        assert tag in possible_tags

def test_generate_hashtags_empty_input(ai_service):
    text = ""
    hashtags = ai_service.generate_hashtags(text)
    assert hashtags == []

def test_generate_hashtags_no_relevant_words(ai_service):
    text = "it is a and the or"
    hashtags = ai_service.generate_hashtags(text)
    # This now returns a default list based on the new implementation
    assert hashtags == ["#GeneratedContent", "#AI"]

def test_generate_hashtags_with_punctuation(ai_service):
    text = "Let's talk about python! It's amazing."
    hashtags = ai_service.generate_hashtags(text, num_hashtags=2)
    assert len(hashtags) == 2
    possible_tags = {"#lets", "#talk", "#python", "#amazing"}
    for tag in hashtags:
        assert tag in possible_tags

def test_generate_hashtags_num_hashtags_param(ai_service):
    text = "word1 word2 word3 word4 word5 word6"
    hashtags = ai_service.generate_hashtags(text, num_hashtags=2)
    assert len(hashtags) == 2
    hashtags_4 = ai_service.generate_hashtags(text, num_hashtags=4)
    assert len(hashtags_4) == 4

def test_generate_hashtags_case_insensitivity(ai_service):
    text = "Python is the same as python"
    hashtags = ai_service.generate_hashtags(text, num_hashtags=1)
    # With frequency count, 'python' appears twice and should be the top result
    assert hashtags == ["#python"]

# --- End of tests for generate_hashtags ---


def test_generate_image_from_text_placeholder(ai_service):
    prompt = "test image prompt"
    image_url = ai_service.generate_image_from_text(prompt)
    assert isinstance(image_url, str)
    assert "https://via.placeholder.com/" in image_url # Placeholder URL
    assert prompt.replace(" ", "+") in image_url

def test_generate_video_from_text_placeholder(ai_service):
    prompt = "test video prompt"
    video_url = ai_service.generate_video_from_text(prompt)
    assert isinstance(video_url, str)
    assert "https://fakevideoserver.com/" in video_url # Placeholder URL
    assert prompt.replace(" ", "_") in video_url

# To run tests (from the root directory):
# 1. Ensure pytest is installed: pip install pytest
# 2. Run: pytest
