"""
PizzaOrderLogicAdapter - Custom ChatterBot logic adapter for pizza ordering.

Handles the complete pizza ordering workflow including:
- Pizza selection (specialty or custom with toppings)
- Size selection (small, medium, large)
- Delivery address collection
- Credit card payment collection
- Order summary display
"""

from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement


# ──────────────────────────────────────────────────────────────────────
# Pizza Menu Configuration
# ──────────────────────────────────────────────────────────────────────

PIZZA_MENU = {
    'specialty_pizzas': {
        'margherita':   ['mozzarella', 'tomato sauce', 'fresh basil'],
        'pepperoni':    ['mozzarella', 'pepperoni', 'tomato sauce'],
        'hawaiian':     ['mozzarella', 'ham', 'pineapple', 'tomato sauce'],
        'veggie':       ['mozzarella', 'bell peppers', 'mushrooms', 'onions', 'olives', 'tomato sauce'],
        'meat lovers':  ['mozzarella', 'pepperoni', 'sausage', 'bacon', 'ham', 'tomato sauce'],
        'bbq chicken':  ['mozzarella', 'grilled chicken', 'red onions', 'bbq sauce'],
        'supreme':      ['mozzarella', 'pepperoni', 'sausage', 'bell peppers', 'mushrooms', 'onions', 'olives'],
    },
    'sizes': ['small', 'medium', 'large'],
    'prices': {'small': 8.99, 'medium': 11.99, 'large': 14.99},
    'topping_surcharge': 1.50,
    'available_toppings': [
        'pepperoni', 'sausage', 'mushrooms', 'onions', 'olives',
        'bell peppers', 'bacon', 'ham', 'pineapple', 'jalapenos',
        'extra cheese', 'tomatoes', 'grilled chicken', 'anchovies',
        'fresh basil', 'spinach',
    ],
}


# ──────────────────────────────────────────────────────────────────────
# Order State (module level, persists across adapter calls)
# ──────────────────────────────────────────────────────────────────────

def _fresh_order():
    """Return a blank order dictionary."""
    return {
        'stage': 'idle',
        'items': [],
        'current_pizza': {},
        'delivery_address': '',
        'payment': {},
    }

order = _fresh_order()


def reset_order():
    """Reset the order state (useful for demo reruns)."""
    global order
    order = _fresh_order()


# ──────────────────────────────────────────────────────────────────────
# Helper: build a readable order summary
# ──────────────────────────────────────────────────────────────────────

def _format_summary():
    """Return a friendly summary of everything we know about the order."""
    lines = []
    lines.append('Here is everything I have for your order so far:')
    lines.append('')

    if order['items']:
        total = 0.0
        for i, pizza in enumerate(order['items'], 1):
            name = pizza.get('name', 'Custom pizza')
            size = pizza.get('size', 'medium')
            toppings = pizza.get('toppings', [])
            base_price = PIZZA_MENU['prices'].get(size, 11.99)
            extra_count = max(0, len(toppings) - 3)
            price = base_price + (extra_count * PIZZA_MENU['topping_surcharge'])
            total += price

            topping_str = ', '.join(toppings) if toppings else 'classic toppings'
            lines.append(f'  Pizza {i}: {name.title()} ({size}) - {topping_str} -- ${price:.2f}')

        lines.append(f'  Estimated total: ${total:.2f}')
    else:
        lines.append('  Pizzas: None added yet.')

    lines.append('')
    if order['delivery_address']:
        lines.append(f'  Delivery address: {order["delivery_address"]}')
    else:
        lines.append('  Delivery address: Not provided yet.')

    if order['payment']:
        card = order['payment'].get('card_number', '')
        masked = '**** **** **** ' + card[-4:] if len(card) >= 4 else '****'
        lines.append(f'  Payment: Card ending in {masked}')
        if order['payment'].get('expiry'):
            lines.append(f'  Expiry: {order["payment"]["expiry"]}')
        if order['payment'].get('name_on_card'):
            lines.append(f'  Name on card: {order["payment"]["name_on_card"]}')
    else:
        lines.append('  Payment: Not provided yet.')

    return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────────────
# Helper: build the menu display
# ──────────────────────────────────────────────────────────────────────

def _format_menu():
    """Return a nicely formatted menu string."""
    lines = []
    lines.append('Here is our menu! We have some wonderful specialty pizzas:')
    lines.append('')
    for name, toppings in PIZZA_MENU['specialty_pizzas'].items():
        lines.append(f'  {name.title():16s} - {", ".join(toppings)}')
    lines.append('')
    lines.append('Sizes and prices:')
    for size in PIZZA_MENU['sizes']:
        lines.append(f'  {size.title():8s}  ${PIZZA_MENU["prices"][size]:.2f}')
    lines.append(f'  (extra toppings beyond 3: +${PIZZA_MENU["topping_surcharge"]:.2f} each)')
    lines.append('')
    lines.append('You can also build your own pizza with any of these toppings:')
    lines.append(f'  {", ".join(PIZZA_MENU["available_toppings"])}')
    lines.append('')
    lines.append('Just tell me the name of a specialty pizza, or say "custom" to build your own!')
    return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────────────
# Intent Detection
# ──────────────────────────────────────────────────────────────────────

def _detect_intent(text):
    """
    Analyze user input and return an intent string.
    Returns None if the input does not relate to pizza ordering.
    """
    t = text.lower().strip()

    # Summary / status request
    summary_phrases = [
        'what do you know', 'order so far', 'my order', 'order summary',
        'order status', 'what have i', 'show order', 'tell me what you know',
        'everything you know', 'what is known', 'review order',
    ]
    if any(phrase in t for phrase in summary_phrases):
        return 'summary'

    # Cancel
    cancel_phrases = ['cancel order', 'cancel my order', 'forget it', 'never mind', 'start over']
    if any(phrase in t for phrase in cancel_phrases):
        return 'cancel'

    # Menu request
    menu_phrases = ['menu', 'what do you have', 'what pizzas', 'show me options', 'what can i order', 'options']
    if any(phrase in t for phrase in menu_phrases):
        return 'show_menu'

    # Detect specialty pizza names
    for pizza_name in PIZZA_MENU['specialty_pizzas']:
        if pizza_name in t:
            return f'named_pizza:{pizza_name}'

    # Custom pizza trigger
    if 'custom' in t or 'build my own' in t or 'build your own' in t or 'make my own' in t:
        return 'custom_pizza'

    # Size detection
    for size in PIZZA_MENU['sizes']:
        if size in t:
            return f'size:{size}'

    # Topping detection
    found_toppings = [tp for tp in PIZZA_MENU['available_toppings'] if tp in t]
    if found_toppings:
        return 'toppings:' + ','.join(found_toppings)

    # Done ordering pizzas
    done_phrases = [
        "that's all", 'that is all', 'done ordering', 'no more',
        'nothing else', 'checkout', 'place order', 'finish order',
        'complete order', 'just that', 'no thanks', 'nope',
    ]
    if any(phrase in t for phrase in done_phrases):
        return 'done_ordering'

    # Yes / affirmative
    if t in ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'absolutely', 'yes please', 'yup', 'y']:
        return 'yes'

    # No / negative
    if t in ['no', 'nah', 'nope', 'n', 'no thanks']:
        return 'no'

    # Order initiation (kept near the end so it does not mask
    # more specific intents like named pizzas or toppings)
    order_phrases = [
        'order a pizza', 'order pizza', 'want a pizza', 'want pizza',
        'get a pizza', 'get pizza', 'like a pizza', 'like pizza',
        'buy a pizza', 'buy pizza', 'i want to order', 'place an order',
        'can i order', 'hungry',
    ]
    if any(phrase in t for phrase in order_phrases):
        return 'start_order'

    if ('i would like' in t or "i'd like" in t) and ('pizza' in t or 'order' in t):
        return 'start_order'

    return None


# ──────────────────────────────────────────────────────────────────────
# The Custom Logic Adapter
# ──────────────────────────────────────────────────────────────────────

class PizzaOrderLogicAdapter(LogicAdapter):
    """
    Custom ChatterBot logic adapter that manages a full pizza ordering
    conversation, including pizza selection, delivery address, and
    credit card payment collection.
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        """
        Return True if this adapter should handle the input.
        We handle it when a pizza related intent is detected
        or an order is already in progress.
        """
        intent = _detect_intent(statement.text)
        if order['stage'] != 'idle':
            return True
        if intent is not None:
            return True
        return False

    def process(self, input_statement, additional_response_selection_parameters):
        """
        Process the input and return an appropriate response
        based on the current order stage and detected intent.
        """
        global order
        text = input_statement.text
        intent = _detect_intent(text)
        stage = order['stage']
        response_text = ''
        confidence = 0.95

        # ──── SUMMARY (available at any stage) ────
        if intent == 'summary':
            response_text = _format_summary()

        # ──── CANCEL (available at any stage) ─────
        elif intent == 'cancel':
            reset_order()
            response_text = (
                "No worries at all! I have cleared your order. "
                "Whenever you are ready to start fresh, just let me know!"
            )

        # ──── SHOW MENU (available at any stage) ──
        elif intent == 'show_menu':
            response_text = _format_menu()

        # ──── IDLE STAGE ──────────────────────────
        elif stage == 'idle':
            if intent == 'start_order':
                order['stage'] = 'ordering'
                response_text = (
                    "Oh wonderful, I would love to help you with that! "
                    "Would you like to pick from our specialty pizzas, or build your own? "
                    "You can also say 'menu' to see all our options."
                )
            elif intent and intent.startswith('named_pizza:'):
                pizza_name = intent.split(':', 1)[1]
                order['stage'] = 'awaiting_size'
                order['current_pizza'] = {
                    'name': pizza_name,
                    'toppings': list(PIZZA_MENU['specialty_pizzas'][pizza_name]),
                }
                toppings_str = ', '.join(PIZZA_MENU['specialty_pizzas'][pizza_name])
                sp = PIZZA_MENU['prices']['small']
                mp = PIZZA_MENU['prices']['medium']
                lp = PIZZA_MENU['prices']['large']
                response_text = (
                    f"Great taste! A {pizza_name.title()} it is, that comes with {toppings_str}. "
                    f"What size would you like? We have small (${sp:.2f}), "
                    f"medium (${mp:.2f}), or large (${lp:.2f})."
                )
            else:
                confidence = 0.65
                response_text = (
                    "Hey there! I am your pizza ordering assistant. "
                    "Just say 'I want to order a pizza' to get started, "
                    "or 'menu' to see what we have!"
                )

        # ──── ORDERING STAGE ──────────────────────
        elif stage == 'ordering':
            if intent and intent.startswith('named_pizza:'):
                pizza_name = intent.split(':', 1)[1]
                order['stage'] = 'awaiting_size'
                order['current_pizza'] = {
                    'name': pizza_name,
                    'toppings': list(PIZZA_MENU['specialty_pizzas'][pizza_name]),
                }
                toppings_str = ', '.join(PIZZA_MENU['specialty_pizzas'][pizza_name])
                response_text = (
                    f"Lovely choice! The {pizza_name.title()} comes with {toppings_str}. "
                    f"What size would you like? Small, medium, or large?"
                )
            elif intent == 'custom_pizza':
                order['stage'] = 'awaiting_toppings'
                order['current_pizza'] = {'name': 'Custom pizza', 'toppings': []}
                available = ', '.join(PIZZA_MENU['available_toppings'])
                response_text = (
                    f"Awesome, let us build your perfect pizza! "
                    f"Which toppings would you like? Here is what we have: {available}. "
                    f"Feel free to list as many as you would like!"
                )
            elif intent and intent.startswith('toppings:'):
                topping_list = intent.split(':', 1)[1].split(',')
                order['stage'] = 'awaiting_size'
                order['current_pizza'] = {'name': 'Custom pizza', 'toppings': topping_list}
                topping_display = ', '.join(topping_list)
                response_text = (
                    f"Nice picks! I have added {topping_display} to your custom pizza. "
                    f"What size would you like? Small, medium, or large?"
                )
            elif intent and intent.startswith('size:'):
                response_text = (
                    "I have noted the size! But first, which pizza would you like? "
                    "You can pick a specialty like Margherita or Pepperoni, or say 'custom' to build your own."
                )
            else:
                response_text = (
                    "Sure thing! Would you like one of our specialty pizzas "
                    "(like Margherita, Pepperoni, Hawaiian, Veggie, Meat Lovers, BBQ Chicken, or Supreme), "
                    "or would you prefer to build a custom pizza? "
                    "Just say the pizza name or 'custom' to get started!"
                )

        # ──── AWAITING TOPPINGS ───────────────────
        elif stage == 'awaiting_toppings':
            if intent and intent.startswith('toppings:'):
                topping_list = intent.split(':', 1)[1].split(',')
                order['current_pizza']['toppings'].extend(topping_list)
                order['stage'] = 'awaiting_size'
                all_toppings = ', '.join(order['current_pizza']['toppings'])
                response_text = (
                    f"Sounds delicious! Your pizza now has: {all_toppings}. "
                    f"What size would you like? Small, medium, or large?"
                )
            elif intent == 'done_ordering' or intent == 'no':
                if order['current_pizza'].get('toppings'):
                    order['stage'] = 'awaiting_size'
                    response_text = (
                        "Perfect! What size would you like for this pizza? "
                        "Small, medium, or large?"
                    )
                else:
                    response_text = (
                        "Hmm, it looks like we have not added any toppings yet. "
                        "Could you let me know which toppings you would like?"
                    )
            else:
                available = ', '.join(PIZZA_MENU['available_toppings'])
                response_text = (
                    f"I would love to add those toppings! Could you pick from our list? "
                    f"We have: {available}"
                )

        # ──── AWAITING SIZE ───────────────────────
        elif stage == 'awaiting_size':
            if intent and intent.startswith('size:'):
                size = intent.split(':', 1)[1]
                order['current_pizza']['size'] = size
                order['items'].append(dict(order['current_pizza']))
                order['current_pizza'] = {}
                order['stage'] = 'awaiting_more'

                pizza_name = order['items'][-1]['name']
                count = len(order['items'])
                s_suffix = 's' if count > 1 else ''
                response_text = (
                    f"Wonderful! I have added a {size} {pizza_name.title()} to your order. "
                    f"That is {count} pizza{s_suffix} so far. "
                    f"Would you like to add another pizza, or are you all set?"
                )
            else:
                sp = PIZZA_MENU['prices']['small']
                mp = PIZZA_MENU['prices']['medium']
                lp = PIZZA_MENU['prices']['large']
                response_text = (
                    "I just need the size for your pizza. "
                    f"We have small (${sp:.2f}), "
                    f"medium (${mp:.2f}), or "
                    f"large (${lp:.2f}). Which would you prefer?"
                )

        # ──── AWAITING MORE PIZZAS ────────────────
        elif stage == 'awaiting_more':
            if intent == 'yes' or intent == 'start_order':
                order['stage'] = 'ordering'
                response_text = (
                    "Great, let us add another one! Which pizza would you like next? "
                    "Specialty name or 'custom' to build your own."
                )
            elif intent and intent.startswith('named_pizza:'):
                pizza_name = intent.split(':', 1)[1]
                order['stage'] = 'awaiting_size'
                order['current_pizza'] = {
                    'name': pizza_name,
                    'toppings': list(PIZZA_MENU['specialty_pizzas'][pizza_name]),
                }
                response_text = (
                    f"Ooh nice, adding a {pizza_name.title()}! What size for this one?"
                )
            elif intent in ('no', 'done_ordering') or intent is None:
                order['stage'] = 'awaiting_address'
                response_text = (
                    "Alright, your pizzas are all set! "
                    "Now, could you share the delivery address where we should send your order?"
                )
            else:
                order['stage'] = 'awaiting_address'
                response_text = (
                    "Sounds like you are all set with pizzas! "
                    "Could you please share your delivery address?"
                )

        # ──── AWAITING ADDRESS ────────────────────
        elif stage == 'awaiting_address':
            if len(text.strip()) > 3:
                order['delivery_address'] = text.strip()
                order['stage'] = 'awaiting_payment'
                response_text = (
                    f"Got it, delivering to: {text.strip()}. "
                    f"Almost done! Could you please provide your credit card details? "
                    f"I will need the card number, expiration date, and the name on the card. "
                    f"You can share them all at once, for example: "
                    f"'4111 1111 1111 1234, 12/27, John Doe'"
                )
            else:
                response_text = (
                    "I would need a bit more detail for the delivery address. "
                    "Could you provide the full street address, please?"
                )

        # ──── AWAITING PAYMENT ────────────────────
        elif stage == 'awaiting_payment':
            import re
            parts = [p.strip() for p in text.split(',')]
            card_number = ''
            expiry = ''
            name_on_card = ''

            for part in parts:
                digits_only = re.sub(r'\D', '', part)
                if len(digits_only) >= 13 and len(digits_only) <= 19:
                    card_number = digits_only
                elif re.match(r'^\d{1,2}[/\-]\d{2,4}$', part.strip()):
                    expiry = part.strip()
                elif re.match(r'^[A-Za-z\s]{2,}$', part.strip()):
                    name_on_card = part.strip()

            if card_number:
                order['payment'] = {
                    'card_number': card_number,
                    'expiry': expiry if expiry else 'not provided',
                    'name_on_card': name_on_card if name_on_card else 'not provided',
                }
                order['stage'] = 'confirmed'
                masked = '**** **** **** ' + card_number[-4:]

                summary = _format_summary()
                response_text = (
                    f"Thank you so much! Payment done (card ending in {masked}).\n\n"
                    f"{summary}\n\n"
                    f"Your order has been placed! Thank you for choosing Pizza Palace. "
                    f"Your delicious pizza is on its way. Enjoy your meal!"
                )
            else:
                response_text = (
                    "I was not quite able to read the card details. No worries! "
                    "Could you share them in this format: "
                    "'card number, expiry (MM/YY), name on card'?\n"
                    "For example: '4111 1111 1111 1234, 12/27, John Doe'"
                )

        # ──── CONFIRMED STAGE ─────────────────────
        elif stage == 'confirmed':
            if intent == 'start_order':
                reset_order()
                order['stage'] = 'ordering'
                response_text = (
                    "A fresh new order! What pizza can I get for you this time?"
                )
            elif intent == 'summary':
                response_text = _format_summary()
            else:
                response_text = (
                    "Your order is already placed and on its way! "
                    "If you would like to place a new order, just say 'order pizza'. "
                    "Thanks again for ordering with us!"
                )

        # ──── FALLBACK ────────────────────────────
        else:
            confidence = 0.4
            response_text = (
                "I am here to help with your pizza order! "
                "Say 'order pizza' to get started, or 'menu' to see our options."
            )

        response_statement = Statement(text=response_text)
        response_statement.confidence = confidence
        return response_statement
