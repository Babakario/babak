import pytest
from app.services.ai_content_service import AIContentService

# Initialize the service once for all tests in this module if needed, or per test
@pytest.fixture
def ai_service():
    return AIContentService()

def test_generate_caption_placeholder(ai_service):
    prompt = "test prompt"
    caption = ai_service.generate_caption(prompt)
    assert isinstance(caption, str)
    assert prompt in caption # The placeholder includes the prompt
    assert "#AICaption" in caption # Placeholder includes this hashtag

def test_generate_hashtags_placeholder(ai_service):
    content = "Some sample content for testing hashtags"
    hashtags = ai_service.generate_hashtags(content)
    assert isinstance(hashtags, list)
    if hashtags: # It might return an empty list if content is very short or unusual
      for tag in hashtags:
          assert tag.startswith("#")
    # Check if default hashtags are returned for empty/problematic content
    empty_hashtags = ai_service.generate_hashtags("")
    assert "#GeneratedContent" in empty_hashtags


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
