import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database configuration
DB_FILE = "database.db"

# File handling
MAX_FILE_SIZE = 5  # MB
ALLOWED_EXTENSIONS = ['cpp', 'py', 'txt', 'csv']

# Logging
LOG_LEVEL = "INFO"

# LaTeX rendering
MATPLOTLIB_CONFIG = {
    'text.usetex': True,
    'font.family': 'serif',
    'text.latex.preamble': r'\usepackage{amsmath}'
}

# OpenAI configuration
OPENAI_MODEL = "gpt-4"
SYSTEM_PROMPT = """You are universal assistant with a focus in advanced math and programming. 
When you're asked to solve some problems requiring LaTeX notation you must use $ and $$ delimiters for it.
Don't ask about if user wants to do with your response (like extend, continue solving etc., 
instead you must clarify that user should create new prompt with specific task. 
You must use code block if user explicitly asks to generate LaTeX or TeX text. 
When you're asked to solve math problem, you do it till the end until you give an exact answer."""