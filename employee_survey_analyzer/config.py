import os
from dotenv import load_dotenv

# pulls in .env file into app context
load_dotenv()

AWS_PROFILE = os.environ["AWS_PROFILE"]
AWS_REGION = os.environ["AWS_REGION"]

ADMIN_KEY = os.environ["ADMIN_KEY"]