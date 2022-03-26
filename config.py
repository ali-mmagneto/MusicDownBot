import os

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    SUDO = os.environ.get("SUDO")
    BOT_USERNAME = os.environ.get("BOT_USERNAME")
    PLAYLIST_ID = int(os.environ.get("PLAYLIST_ID"))
