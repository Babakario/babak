# Placeholder for Auto DM (Automated Direct Message) Service

class AutoDMService:
    def __init__(self, instagram_client=None):
        # In a real scenario, this service would use the Instagram client
        # to listen for DMs and send replies.
        self.instagram_client = instagram_client
        # Rules could be loaded from a database or config file
        self.dm_rules = {
            "hello": "Hi there! Thanks for your message.",
            "hi": "Hi there! Thanks for your message.",
            "help": "Sure, I can help. What do you need assistance with?",
            "price": "You can find our pricing details on our website [link_to_website].",
            "product": "Tell me more about which product you're interested in!",
            "default": "Thanks for reaching out! We'll get back to you as soon as possible."
        }
        print("AutoDMService initialized (placeholder).")

    def add_dm_rule(self, keyword, response):
        # Placeholder for adding a new DM rule
        keyword = keyword.lower()
        self.dm_rules[keyword] = response
        print(f"DM rule added: '{keyword}' -> '{response}'")
        return True

    def remove_dm_rule(self, keyword):
        # Placeholder for removing a DM rule
        keyword = keyword.lower()
        if keyword in self.dm_rules:
            del self.dm_rules[keyword]
            print(f"DM rule removed for keyword: '{keyword}'")
            return True
        print(f"No DM rule found for keyword: '{keyword}'")
        return False

    def process_incoming_dm(self, user_id, message_text):
        # Placeholder for processing an incoming DM and generating a reply.
        # In a real app, this would be triggered by an event from the Instagram API.
        print(f"Processing incoming DM from {user_id}: '{message_text}' (placeholder)")

        message_lower = message_text.lower()
        reply_text = self.dm_rules.get("default") # Default reply

        for keyword, response in self.dm_rules.items():
            if keyword in message_lower: # Simple keyword matching
                reply_text = response
                break

        # Simulate sending the reply via Instagram client
        if self.instagram_client:
            # self.instagram_client.send_dm(user_id, reply_text)
            print(f"Simulating sending DM reply to {user_id}: '{reply_text}'")
        else:
            print(f"Generated reply for {user_id} (no client to send): '{reply_text}'")

        return reply_text

# Example usage (for testing purposes)
if __name__ == '__main__':
    # from app.instagram_api.client import InstagramClient # Assuming this exists
    # mock_ig_client = InstagramClient() # Or None

    auto_dm_service = AutoDMService(instagram_client=None) # Pass mock client if needed

    print("\nInitial DM Rules:", auto_dm_service.dm_rules)

    auto_dm_service.add_dm_rule("support", "For support, please email support@example.com")
    auto_dm_service.add_dm_rule("thanks", "You're welcome!")

    print("\nUpdated DM Rules:", auto_dm_service.dm_rules)

    auto_dm_service.remove_dm_rule("product")
    print("\nRules after removing 'product':", auto_dm_service.dm_rules)

    print("\n--- Simulating Incoming DMs ---")
    reply1 = auto_dm_service.process_incoming_dm("user123", "Hello, I need some help.")
    # Expected: help rule -> "Sure, I can help. What do you need assistance with?"

    reply2 = auto_dm_service.process_incoming_dm("user456", "What's the price of your service?")
    # Expected: price rule -> "You can find our pricing details on our website [link_to_website]."

    reply3 = auto_dm_service.process_incoming_dm("user789", "Just wanted to say great work!")
    # Expected: default rule or if "thanks" is more prominent, its rule.
    # Current simple logic will pick first match or default.
    # For "great work!", if "thanks" is not a rule, it will be default.
    # If "thanks" rule exists: "You're welcome!" (if "thanks" is in "great work!", which it isn't)
    # So, likely default: "Thanks for reaching out! We'll get back to you as soon as possible."

    reply4 = auto_dm_service.process_incoming_dm("userABC", "Hi")
    # Expected: hi/hello rule
