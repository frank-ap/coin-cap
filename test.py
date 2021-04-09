import os
from dotenv import load_dotenv

load_dotenv()

egg = os.getenv('TEST')

print(egg*3)