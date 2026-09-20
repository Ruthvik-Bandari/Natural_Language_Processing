# Natural Language Processing — Pizza Ordering Chatbot

A conversational pizza-ordering assistant built on **ChatterBot** with a custom logic adapter that holds order state across turns. Coursework for AAI 6620, Assignment 6.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![ChatterBot](https://img.shields.io/badge/ChatterBot-1.2.13-4B8BBE)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)

## Contents

- [What it does](#what-it-does)
- [How the adapter works](#how-the-adapter-works)
- [Menu and pricing](#menu-and-pricing)
- [Requirements](#requirements)
- [How to run](#how-to-run)
- [Example session](#example-session)
- [Repository contents](#repository-contents)
- [Limitations](#limitations)
- [Author](#author)

## What it does

- Displays the pizza menu on request, at any point in the conversation
- Takes specialty or fully custom pizza orders
- Prompts for size and toppings
- Accumulates a multi-pizza order
- Collects delivery and payment details
- Prints a running order summary with an itemised total
- Cancels and resets the order on request

## How the adapter works

`pizza_adapter.py` (528 lines) implements `PizzaOrderLogicAdapter`, a ChatterBot `LogicAdapter`.
ChatterBot's default adapters are stateless corpus matchers, which cannot run an order, so this one
adds two things:

**Intent detection.** `_detect_intent()` classifies each utterance by keyword and pattern matching
into one of: `start_order`, `custom_pizza`, `show_menu`, `toppings:<list>`, `summary`,
`done_ordering`, `cancel`, `yes`, `no`. Topping detection returns every matched topping as a
comma-joined payload rather than a single label, so "mushrooms and olives" is handled in one turn.

**Order state.** The adapter keeps the in-progress order in module-level state, so `process()` knows
which stage the conversation is at and what it still needs to ask for. `show_menu` is handled
before the stage machine, so the menu is reachable mid-order without losing progress. A reset
helper clears state, which is what makes the notebook re-runnable.

`can_process()` gates the adapter so it only claims utterances it recognises, leaving anything else
to ChatterBot's normal response selection.

## Menu and pricing

| Size | Price |
|---|---|
| Small | $8.99 |
| Medium | $11.99 |
| Large | $14.99 |

Extra toppings beyond three add **$1.50** each.

**Specialty pizzas (7):** Margherita, Pepperoni, Hawaiian, Veggie, Meat Lovers, BBQ Chicken, Supreme.

**Available toppings (16):** pepperoni, sausage, mushrooms, onions, olives, bell peppers, bacon,
ham, pineapple, jalapenos, extra cheese, tomatoes, grilled chicken, anchovies, fresh basil, spinach.

## Requirements

- Python 3.10+
- `chatterbot==1.2.13`

```bash
pip install chatterbot==1.2.13
```

The pinned version matters: ChatterBot's adapter API changed across releases, and this adapter
targets 1.2.x.

## How to run

1. Keep `pizza_adapter.py` in the same directory as the notebook.
2. Open `Assignment6_Chatbot.ipynb`.
3. Run the cells in order to build the chatbot and start a conversation.

The chatbot persists its corpus in `pizza_bot.sqlite3`, which is created on first run and is
not tracked in git.

## Example session

```
You:  show me the menu
Bot:  Specialty pizzas:
        Margherita    - mozzarella, tomato sauce, fresh basil
        ...
      Sizes and prices:
        Small     $8.99
        Medium    $11.99
        Large     $14.99
        (extra toppings beyond 3: +$1.50 each)

You:  I'd like a large pepperoni
Bot:  Added: Pepperoni (large) - mozzarella, pepperoni, tomato sauce -- $14.99
      Anything else?

You:  that's all
Bot:  Order summary:
        Pizza 1: Pepperoni (large) - ... -- $14.99
      Total: $14.99
```

## Repository contents

| File | Purpose |
|---|---|
| `Assignment6_Chatbot.ipynb` | Assignment notebook: setup, training and demo conversation |
| `pizza_adapter.py` | `PizzaOrderLogicAdapter` — intent detection, order state, pricing |
| `pizza_bot.sqlite3` | ChatterBot storage, created on first run (not tracked) |

## Limitations

- **Intent detection is keyword and pattern matching**, not a trained classifier. Phrasing outside
  the expected patterns falls through to ChatterBot's generic responses.
- **Order state is module-level**, so a single process serves one conversation. It is not safe for
  concurrent users.
- No payment processing or delivery integration; those details are collected but not acted on.
- No automated tests.
- SQLite WAL files are created at runtime and should stay out of version control.

## License

[MIT](LICENSE) &copy; Ruthvik Nath Bandari

## Author

**Ruthvik Nath Bandari** — MS Applied AI, Northeastern University
[GitHub](https://github.com/Ruthvik-Bandari) · [LinkedIn](https://www.linkedin.com/in/ruthvik-nath-bandari/)
