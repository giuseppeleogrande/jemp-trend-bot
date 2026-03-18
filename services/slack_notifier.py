import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_message(markdown_text):
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    
    if not slack_token or "xoxb" not in slack_token:
        print("ATTENZIONE: SLACK_BOT_TOKEN non valido o non configurato. Salto l'invio su Slack.")
        print("\n=== ANTEPRIMA MESSAGGIO GENERATO DALLA AI ===\n")
        print(markdown_text)
        print("\n=============================================\n")
        return False
        
    client = WebClient(token=slack_token)
    
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=markdown_text,
            mrkdwn=True
        )
        print("✅ Messaggio recapitato con successo su Slack!")
        return True
    except SlackApiError as e:
        print(f"❌ Errore API Slack: {e.response['error']}")
        return False
