import os

from dotenv import load_dotenv


load_dotenv()

# 例: "sqlite:///./dashcam-tools.db"
DATABASE_URL: str = os.environ["DATABASE_URL"]
