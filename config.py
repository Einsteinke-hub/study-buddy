import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'Bd72!k9@qL#p5Rs8*vT2&wY5z$8XpN6x')  # Change this to a strong random value in production
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')  # Usually 'localhost' if MySQL is on same machine
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')       # Your MySQL username
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '22222222')   # Your MySQL password
    MYSQL_DB = os.getenv('MYSQL_DB', 'study_buddy')    # Database name you created
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))    # Default MySQL port