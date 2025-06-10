# Placeholder for Post model

class Post:
    def __init__(self, user_id, content_url, caption, generated_by_ai=False):
        self.user_id = user_id
        self.content_url = content_url
        self.caption = caption
        self.generated_by_ai = generated_by_ai

    def __repr__(self):
        return f'<Post {self.caption[:20]}...>'
