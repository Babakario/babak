# This script runs a lead processing job.
# It is self-contained and does not require external configuration files.

# --- Configuration ---
# In a real application, this might come from environment variables or a config service.
# For this script, please replace the placeholder values below.
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
# --- End Configuration ---

# The LeadProcessingService is defined in another file.
# Since this script is inside the 'app' directory, we can import services directly.
from services.lead_processing_service import LeadProcessingService

def main():
    """
    Initializes and runs the lead processing service.
    """
    print("Starting lead processing job...")

    lead_service = LeadProcessingService(
        telegram_token=TELEGRAM_TOKEN,
        chat_id=CHAT_ID
    )

    # Run the job
    lead_service.run_job()

    print("Lead processing job finished.")

if __name__ == "__main__":
    main()
