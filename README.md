# Natural Language Processing – Pizza Chatbot

A pizza ordering chatbot built with **ChatterBot** and a custom logic adapter.

## Project Overview

This project implements a conversational pizza assistant that can:
- Display a pizza menu
- Take specialty or custom pizza orders
- Ask for pizza size and toppings
- Collect delivery and payment details
- Show order summaries

## Repository Contents

- `Assignment6_Chatbot.ipynb` – assignment notebook with setup and demo flow
- `pizza_adapter.py` – custom `PizzaOrderLogicAdapter` implementation
- `pizza_bot.sqlite3` – chatbot storage database

## Requirements

- Python 3.10+
- `chatterbot==1.2.13`

Install dependency:

```bash
pip install chatterbot==1.2.13
```

## How to Run

1. Open and run the notebook:
   - `Assignment6_Chatbot.ipynb`
2. Ensure `pizza_adapter.py` is in the same project folder.
3. Run cells in order to initialize and chat with the bot.

## Notes

- SQLite WAL temporary files are generated automatically at runtime.
- Keep your virtual environment and cache files out of version control.

## Author

Ruthvik Bandari
