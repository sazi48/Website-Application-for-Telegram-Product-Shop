from flask import Flask, render_template, request, jsonify, session, url_for, redirect, flash
from flask_session import Session
from urllib.parse import quote
import requests  # в начале файла

TELEGRAM_BOT_TOKEN = '7675538685:AAH1qWdJ7zrTsTeMsftmbZsH7uX72w6c_L0'
TELEGRAM_CHAT_ID = '-1002506317243'  # либо твой user_id, либо ID канала

def send_telegram_message(message):
    bot_token = '7720822781:AAHtM7zAmDP7qT8brxlMkoH3q7VAw7hm7qc'  # твой токен
    chat_id = '-1002506317243'  # или ID, если пишешь себе
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
orders = []  # список всех заказов
next_order_id = 1  # автоинкремент id


products = [
    {'id': 1, 'name': 'АНАНАСОВЫЕ ДОЛЬКИ', 'image': 'Ананасовые дольки.jpg', 'description': 'Сочные, сладкие кусочки тропического тайского ананаса'},
    {'id': 2, 'name': 'АПЕЛЬСИНОВЫЙ ФРЕШ', 'image': 'Апельсиновый фреш.jpg', 'description': 'Свежевыжатый апельсиновый сок. Вмеру сладкий с легкой цитрусовой кислинкой'},
    {'id': 3, 'name': 'АРБУЗ-ДЫНЯ', 'image': 'Арбуз-дыня.jpg', 'description': 'Свежесть сладкого арбуза и бархатистая нежность спелой дыни'},
    {'id': 4, 'name': 'БАНАНОВЫЙ МИЛКШЕЙК', 'image': 'Банановый милкшейк.jpg', 'description': 'Тот самый молочный коктейль из детства Банановый с молочными нотами и щепоткой ванили'},
    {'id': 5, 'name': 'ВАФЕЛЬНЫЕ ТРУБОЧКИ', 'image': 'Вафельные трубочки.jpg', 'description': 'Изысканное лакомство мягких вафель и насыщенным, сливочным вкусом ирландского крема'},
    {'id': 6, 'name': 'ВИНОГДАРНАЯ ГАЗИРОВКА', 'image': 'Виноградная газировка.jpg', 'description': 'Яркий и освежающий вкус газировки с спелым виноградом'},
    {'id': 7, 'name': 'ВИШНЕВЫЙ СОК', 'image': 'Вишневый сок.jpg', 'description': 'Яркий, натуральный вишневый сок с благородной кислинкой'},
    {'id': 8, 'name': 'ГОРНАЯ ЧЕРНИКА', 'image': 'Горная черника.jpg', 'description': 'Аромат сочной черники, произрастащей в горных районах. Вкус тонкий, с легкой кислинкой и цветочными нотами'},
    {'id': 9, 'name': 'ГРАНАТОВОЕ ВИНО', 'image': 'Гранатовое вино.jpg', 'description': 'Это освежающее вино с гранатового-ягодным вкусом'},
    {'id': 10, 'name': 'ГРУШЕВЫЙ СМУЗИ', 'image': 'Грушевый смузи.jpg', 'description': 'Нежный, мягкий и насыщенный грушевый напиток'},
    {'id': 11, 'name': 'ЖЁЛТЫЙ КИВИ', 'image': 'Жёлтый киви.jpg', 'description': 'Сочный и сладкий аромат Ново-Зеландского желтого киви'},
    {'id': 12, 'name': 'ЗЕМЛЯНИКА', 'image': 'Земляника.jpg', 'description': 'Вкус сладкой смеси полевой и лесной земляники'},
    {'id': 13, 'name': 'КИСЛЫЙ ЛИМОН', 'image': 'Кислый лимон.jpg', 'description': 'Вкус настоящего спелого лимона'},
    {'id': 14, 'name': 'ЛЁД', 'image': 'Лёд.jpg', 'description': 'Холодок для твоего микса. Достаточно щепотки'},
    {'id': 15, 'name': 'ЛЕСНЫЕ ЯГОДЫ', 'image': 'Лесные ягоды.jpg', 'description': 'Неповторимое сочетание малины, черники и северных ягод'},
    {'id': 16, 'name': 'МАЛИНА', 'image': 'Малина.jpg', 'description': 'Тот самый вкус натуральной малины, который ты пробовал в деревне'},
    {'id': 17, 'name': 'МАНГОВЫЙ СМУЗИ', 'image': 'Манговый смузи.jpg', 'description': 'Сладкий манговый вкус с нотами тропических фруктов и мягкой кремовой текстурой'},
    {'id': 18, 'name': 'МЕДОВАЯ ДЫНЯ', 'image': 'Медовая дыня.jpg', 'description': 'Сочетание бархатной желтой сладкой дыни'},
    {'id': 19, 'name': 'ПАН', 'image': 'Пан.jpg', 'description': 'Аромат индийской специи ПАН. Ты знаешь этот аромат'},
    {'id': 20, 'name': 'РОЗОВЫЙ ГРЕЙПФРУТ', 'image': 'Розовый грейпфрут.jpg', 'description': 'Уникальный вкус розового грейпфрута. Сладкий с лёгкой горчинкой'},
    {'id': 21, 'name': 'СКИТТЛЗ', 'image': 'Скиттлз.jpg', 'description': 'Вкус яркого красного скиттлза'},
    {'id': 22, 'name': 'ЧЁРНАЯ СМОРОДИНА', 'image': 'Чёрная смородина.jpg', 'description': 'Насыщенный, сладкий аромат черной смородины с легкой кислинкой'},
    {'id': 23, 'name': 'ЯБЛОЧНЫЙ САУЭР', 'image': 'Яблочный сауэр.jpg', 'description': 'Нежный, сливочно-яблочный коктейль на основе джина с легкой кислинкой'},
    {'id': 24, 'name': 'ЯГОДНЫЙ ПУНШ', 'image': 'Ягодный пунш.jpg', 'description': 'Сочетание сладкой малины и клубники с кисло-сладкой мякотью грейпфрута'},
    {'id': 25, 'name': 'JAGERBOMB', 'image': 'Jаgerbomb.jpg', 'description': 'Коктейльная подача известного ликера с ванильной колой'},
    {'id': 26, 'name': 'МЯТНЫЙ ТИК ТАК', 'image': 'Мятный тик так.jpg', 'description': 'Легендарные мятные конфеты'},
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
                "image": quote(product["image"]),  # Кодируем путь
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
                    del cart[str(product_id)]  # Удаляем товар, если количество стало 0
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

# Модель заказа
class Order:
    def __init__(self, id, name, address, phone, cart):
        self.id = id
        self.name = name
        self.address = address
        self.phone = phone
        self.cart = cart
        self.status = 'Новый заказ'




# Страница оформления заказа
@app.route('/order', methods=['GET', 'POST'])
def order():
    global next_order_id
    cart = session.get('cart', {})

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']

        if not cart:
            flash('Корзина пуста. Добавьте товары перед оформлением заказа.', 'danger')
            return redirect(url_for('cart'))

        # Создаём заказ
        order = Order(id=next_order_id, name=name, address=address, phone=phone, cart=cart.copy())
        orders.append(order)
        next_order_id += 1
        # Формируем текст сообщения
        order_text = f"<b>Новый заказ #{order.id}</b>\n"
        order_text += f"👤 Имя: {order.name}\n"
        order_text += f"📞 Телефон: {order.phone}\n"
        order_text += f"🏠 Адрес: {order.address}\n"
        order_text += "\n🛒 Товары:\n"

        for product_id_str, quantity in order.cart.items():
            product = next((p for p in products if str(p["id"]) == product_id_str), None)
            if product:
                order_text += f"— {product['name']} x {quantity}\n"

        # Отправляем сообщение в Telegram
        send_telegram_message(order_text)

        # Очищаем корзину
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
