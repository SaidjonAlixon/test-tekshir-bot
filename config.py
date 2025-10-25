import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
OPEN_CHANNEL = os.getenv('OPEN_CHANNEL')
CLOSED_GROUP_ID = int(os.getenv('CLOSED_GROUP_ID', '-1')) 