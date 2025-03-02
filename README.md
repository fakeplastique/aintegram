<<<<<<< HEAD
# aitegram
Telegram Math &amp; Programming Bot Using OpenAI API
=======
# Integration of OpenAI API into Telegram Bot for Math and Programmings Tasks 

A Telegram bot that provides assistance for mathematical and programming questions using OpenAI's GPT-4, with special handling for LaTeX notation and image processing capabilities.

## 📚 Features

- **Math Processing**: Parses and renders LaTeX expressions
- **Programming Help**: Answers coding questions and analyzes code snippets
- **Image Recognition**: Uses OCR to extract LaTeX from images
- **File Processing**: Handles document uploads for code analysis

## 🛠️ Technologies Used

- **Python 3.8+**
- **Aiogram 3.x**: Telegram Bot API framework
- **OpenAI API**: For GPT-4 integration
- **Pix2Tex**: LaTeX OCR for extracting equations from images
- **Matplotlib**: For rendering LaTeX expressions
- **SQLite**: For persistent storage
- **SymPy**: For mathematical expression parsing

## 🚀 Project Structure

```
/project_root
├── main.py                # Entry point
├── config.py              # Configuration settings
├── database/
│   ├── __init__.py
│   ├── models.py          # Database models/schema
│   └── db_manager.py      # Database operations
├── services/
│   ├── __init__.py
│   ├── openai_service.py  # OpenAI API integration
│   ├── latex_service.py   # LaTeX processing and rendering
│   └── image_service.py   # Image processing
├── handlers/
│   ├── __init__.py
│   ├── commands.py        # Command handlers
│   └── messages.py        # Message handlers
└── utils/
    ├── __init__.py
    └── text_processing.py # Text manipulation utilities
```

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-math-bot.git
   cd telegram-math-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   OPENAI_API_KEY=your_openai_api_key
   ```

## 🏁 Running the Bot

```bash
python main.py
```

## 📋 Usage

The bot responds to the following:

### Commands
- `/start` - Introduces the bot and provides basic information

### Content Types
- **Text** - Answer questions about math or programming
- **Images** - Extract and process LaTeX equations from images
- **Documents** - Analyze code files or text documents

### Examples

1. **Math Question**:
   ```
   Solve the differential equation: dy/dx + 2y = x^2
   ```

2. **Programming Question**:
   ```
   How do I implement a quick sort algorithm in Python?
   ```

3. **Upload an image** of a math equation for recognition

4. **Upload a code file** for analysis or explanation

## 📝 Database

The bot stores:
- Message history
- Errors for debugging

Database structure is defined in `database/models.py`.

## 🔒 Security

- API keys are stored in environment variables
- Error handling with proper logging
- Input validation for all user submissions

## 🔄 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Acknowledgements

- [OpenAI](https://openai.com/) for GPT-4
- [Pix2Tex](https://github.com/lukas-blecher/LaTeX-OCR) for LaTeX OCR
- [Aiogram](https://aiogram.dev/) for Telegram bot framework
>>>>>>> e49b22d (Initial commit)
