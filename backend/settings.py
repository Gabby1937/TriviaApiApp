from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.environ.get("db_name")
test_db_name = os.environ.get("test_db_name")
db_user = os.environ.get("db_user")
db_password = os.environ.get("db_password")