import os
from dotenv import load_dotenv
import vertexai

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"]      = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"]     = LOCATION

vertexai.init(project=PROJECT_ID, location=LOCATION)
print(f"✅ Vertex AI iniciado → Proyecto: {PROJECT_ID} | Región: {LOCATION}")