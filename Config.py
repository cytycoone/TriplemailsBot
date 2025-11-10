import os
import sys

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID_STR = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is not set!")
    sys.exit(1)

if not API_ID_STR:
    print("ERROR: API_ID environment variable is not set!")
    sys.exit(1)

if not API_HASH:
    print("ERROR: API_HASH environment variable is not set!")
    sys.exit(1)

try:
    API_ID = int(API_ID_STR)
except ValueError:
    print(f"ERROR: API_ID must be a valid integer, got: {API_ID_STR}")
    sys.exit(1)

# If You're hosting in VPS replace the following lines 9,10,11 hash symbol and replacing the approriate values on it and put the hash symbol before the lines 3,4,5

# BOT_TOKEN = "<your bottoken>"
# API_ID = "<your api_id>"
# API_HASH = "<your api_hash>"
