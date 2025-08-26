import requests

class LeadProcessingService:
    def __init__(self, telegram_token, chat_id):
        self.telegram_token = telegram_token
        self.chat_id = chat_id

    def send_alert(self, message):
        """Sends a message to the configured Telegram chat."""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        try:
            response = requests.post(url, data={"chat_id": self.chat_id, "text": message})
            response.raise_for_status()
            print("Alert sent successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram alert: {e}")

    def is_important_lead(self, lead, threshold=1000):
        """
        Determines if a lead is important based on a value threshold.
        """
        return lead.get("value", 0) > threshold

    def process_leads(self, leads, important_lead_threshold=1000):
        """
        Processes a list of leads and sends alerts for important ones.
        """
        print("Processing leads...")
        for lead in leads:
            if self.is_important_lead(lead, important_lead_threshold):
                alert_message = f"🚨 Important Lead: {lead.get('name', 'N/A')} with value {lead.get('value', 0)}"
                self.send_alert(alert_message)
            else:
                print(f"❌ Lead {lead.get('name', 'N/A')} is not considered important.")
        print("Lead processing finished.")

    def run_job(self):
        """
        Simulates a job that fetches leads and processes them.
        """
        # In a real application, you would fetch these leads from a CRM, database, or API.
        simulated_leads = [
            {"name": "Ali", "value": 500},
            {"name": "Maryam", "value": 2000},
            {"name": "Reza", "value": 1500},
            {"name": "Sara", "value": 800},
        ]

        self.process_leads(simulated_leads)
