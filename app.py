from flask import Flask, render_template, request, jsonify, session, url_for, redirect, flash
from flask_session import Session
from urllib.parse import quote
import requests  

TELEGRAM_BOT_TOKEN = '' # your token
TELEGRAM_CHAT_ID = ''  # where the message is sent

def send_telegram_message(message):
    bot_token = '*************'  # your token
    chat_id = '********' # where the message is sent
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)



app = Flask(__name__)
app.secret_key = 'supersecret'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
orders = []   # list of all orders
next_order_id = 1  # autoincrement id


products = [
    {'id': 1, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 2, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 3, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 4, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 5, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 6, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 7, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 8, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 9, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 10, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 11, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 12, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 13, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 14, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 15, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 16, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 17, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 18, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 19, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 20, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 21, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 22, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 23, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 24, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 25, 'name': '*', 'image': '*.jpg', 'description': '*'},
    {'id': 26, 'name': '*', 'image': '*.jpg', 'description': '*'},
]

@app.route('/')
def catalog():
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('catalog.html', products=products, cart=cart, cart_count=cart_count)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    data = request.get_json()
    cart = session.get('cart', {})
    try:
        quantity = max(0, int(request.get_json().get('quantity', 1)))

    except (ValueError, TypeError):
        return jsonify(success=False, message="Invalid quantity"), 400
    if quantity > 0:
        cart[str(product_id)] = quantity
    elif str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return jsonify(success=True, cart_count=sum(cart.values()), quantity=quantity)

@app.route('/cart')
def cart():
    cart = session.get("cart", {})
    cart_items = []

    for product_id_str, quantity in cart.items():
        product = next((p for p in products if str(p["id"]) == product_id_str), None)
        if product:
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "image": quote(product["image"]),  # Encoding the path
                "quantity": quantity
            })

    cart_count = sum(cart.values())
    return render_template("cart.html", cart_items=cart_items, cart_count=cart_count)


@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session["cart"] = cart

    return redirect(url_for("cart"))


@app.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    try:
        action = request.form.get('action')
        cart = session.get('cart', {})

        if str(product_id) in cart:
            if action == 'increase':
                cart[str(product_id)] += 1
            elif action == 'decrease':
                cart[str(product_id)] -= 1
                if cart[str(product_id)] <= 0:
                    del cart[str(product_id)]  # We delete the product if the quantity becomes 0
        else:
            print("Товар не найден в корзине")

        session['cart'] = cart
    except Exception as e:
        print(f"Error: {e}")

    return redirect(url_for('cart'))


@app.route('/update_cart_quantity_ajax/<int:product_id>', methods=['POST'])
def update_cart_quantity_ajax(product_id):
    action = request.get_json().get('action')
    cart = session.get('cart', {})

    if str(product_id) in cart:
        if action == 'increase':
            cart[str(product_id)] += 1
        elif action == 'decrease':
            cart[str(product_id)] -= 1
            if cart[str(product_id)] <= 0:
                cart.pop(str(product_id))

    session['cart'] = cart
    return jsonify({
        'success': True,
        'new_quantity': cart.get(str(product_id), 0),
        'cart_count': sum(cart.values())
    })

# Order model
class Order:
    def __init__(self, id, name, address, phone, cart, zavedenie, telegramuser):
        self.id = id
        self.name = name
        self.address = address
        self.phone = phone
        self.cart = cart
        self.zavedenie = zavedenie 
        self.telegramuser = telegramuser
        self.status = 'Новый заказ'

# Checkout page
@app.route('/order', methods=['GET', 'POST'])
def order():
    global next_order_id
    cart = session.get('cart', {})

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        telegramuser = request.form['telegramuser']
        zavedenie = request.form['zavedenie']

        if not cart:
            flash('Корзина пуста. Добавьте товары перед оформлением заказа.', 'danger')
            return redirect(url_for('cart'))

        # Create an order
        order = Order(id=next_order_id, name=name, address=address, phone=phone, cart=cart.copy(), zavedenie=zavedenie, telegramuser = telegramuser)
        orders.append(order)
        next_order_id += 1
        # Forming the message text
        order_text = f"Новый заказ #{order.id}\n"
        order_text += f"👤 Имя: {order.name}\n"
        order_text += f"📞 Телефон: {order.phone}\n"
        order_text += f"🏠 Адрес: {order.address}\n"
        order_text += f"📣 Телеграм: {order.telegramuser}\n"
        order_text += f"🏪 Заведение: {order.zavedenie}\n"
        order_text += "\n🛒 Товары:\n"

        for product_id_str, quantity in order.cart.items():
            product = next((p for p in products if str(p["id"]) == product_id_str), None)
            if product:
                order_text += f"— {product['name']} x {quantity}\n"

        # Send a message to Telegram
        send_telegram_message(order_text)

        # Empty the trash
        session['cart'] = {}

        flash('Ваш заказ был успешно оформлен!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))

    cart_items = []
    for product_id_str, quantity in cart.items():
        product = next((p for p in products if str(p["id"]) == product_id_str), None)
        if product:
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "image": quote(product["image"]),
                "quantity": quantity
            })

    cart_count = sum(cart.values())
    return render_template('order.html', cart=cart, cart_items=cart_items, cart_count=cart_count)



@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = next((o for o in orders if o.id == order_id), None)
    if not order:
        return "Заказ не найден", 404

    cart_items = []
    for product_id_str, quantity in order.cart.items():
        product = next((p for p in products if str(p["id"]) == product_id_str), None)
        if product:
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "image": quote(product["image"]),
                "quantity": quantity
            })

    return render_template('order_confirmation.html', order=order, cart_items=cart_items)

@app.route("/remove_from_cart_ajax/<int:product_id>", methods=["POST"])
def remove_from_cart_ajax(product_id):
    cart = session.get("cart", {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session["cart"] = cart

    cart_count = sum(cart.values())
    return jsonify(success=True, cart_count=cart_count)


if __name__ == '__main__':
    app.run(debug=True)
