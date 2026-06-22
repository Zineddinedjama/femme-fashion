import os
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash

from db import get_db, close_db, init_db, query, query_one, execute

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')
app.config['WHATSAPP_NUMBER'] = os.environ.get('WHATSAPP_NUMBER', '213XXXXXXXXX')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app.teardown_appcontext(close_db)

with app.app_context():
    init_db()
    if query_one("SELECT COUNT(*) as c FROM products")['c'] == 0:
        from data.seed import seed
        seed()

CATEGORIES = ['robe', 'chemise', 'pantalon', 'jupe', 'accessoire', 'autre']

WILAYAS = [
    (1, 'Adrar', 1100, 900), (2, 'Chlef', 700, 600), (3, 'Laghouat', 800, 700),
    (4, 'Oum El Bouaghi', 600, 500), (5, 'Batna', 600, 500), (6, 'Bejaia', 500, 400),
    (7, 'Biskra', 600, 500), (8, 'Bechar', 900, 800), (9, 'Blida', 400, 300),
    (10, 'Bouira', 500, 400), (11, 'Tamanrasset', 1100, 900), (12, 'Tebessa', 700, 600),
    (13, 'Tlemcen', 700, 600), (14, 'Tiaret', 700, 600), (15, 'Tizi Ouzou', 500, 400),
    (16, 'Alger', 300, 200), (17, 'Djelfa', 600, 500), (18, 'Jijel', 500, 400),
    (19, 'Setif', 500, 400), (20, 'Saida', 700, 600), (21, 'Skikda', 600, 500),
    (22, 'Sidi Bel Abbes', 700, 600), (23, 'Annaba', 600, 500), (24, 'Guelma', 600, 500),
    (25, 'Constantine', 600, 500), (26, 'Medea', 500, 400), (27, 'Mostaganem', 700, 600),
    (28, 'M\'Sila', 600, 500), (29, 'Mascara', 700, 600), (30, 'Ouargla', 900, 800),
    (31, 'Oran', 600, 500), (32, 'El Bayadh', 1000, 900), (33, 'Illizi', 1100, 1000),
    (34, 'Bordj Bou Arreridj', 600, 500), (35, 'Boumerdes', 400, 300),
    (36, 'El Tarf', 700, 600), (37, 'Tindouf', 1100, 1000), (38, 'Tissemsilt', 700, 600),
    (39, 'El Oued', 900, 800), (40, 'Khenchela', 700, 600), (41, 'Souk Ahras', 700, 600),
    (42, 'Tipaza', 400, 300), (43, 'Mila', 600, 500), (44, 'Ain Defla', 700, 600),
    (45, 'Naama', 1000, 900), (46, 'Ain Temouchent', 700, 600), (47, 'Ghardaia', 900, 800),
    (48, 'Relizane', 700, 600), (49, 'Timimoun', 1100, 1000),
    (50, 'Bordj Badji Mokhtar', 1200, 1100), (51, 'Ouled Djellal', 900, 800),
    (52, 'Beni Abbes', 1100, 1000), (53, 'In Salah', 1100, 1000),
    (54, 'In Guezzam', 1200, 1100), (55, 'Touggourt', 900, 800),
    (56, 'Djanet', 1200, 1100), (57, 'El M\'Ghair', 900, 800), (58, 'El Meniaa', 1000, 900),
]

def get_delivery_price(wilaya_id, delivery_type, phone):
    base_price = 0
    for wid, _, d_price, b_price in WILAYAS:
        if wid == wilaya_id:
            base_price = d_price if delivery_type == 'domicile' else b_price
            break
    order_count = query_one("SELECT COUNT(*) as c FROM orders WHERE customer_phone = ?", (phone,))['c']
    if delivery_type == 'bureau' and order_count >= 1:
        return 0
    if delivery_type == 'domicile' and order_count >= 2:
        return 0
    return base_price

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_globals():
    cart = session.get('cart', {})
    count = sum(item['qty'] for item in cart.values())
    return {'cart_count': count, 'wilayas': WILAYAS, 'whatsapp_number': app.config['WHATSAPP_NUMBER']}

def cart_items_and_total():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    for item_key, item in cart.items():
        items.append({'id': item_key, 'product_id': item.get('product_id', item_key), 'name': item['name'], 'price': item['price'], 'qty': item['qty'], 'image': item.get('image', ''), 'size': item.get('size', ''), 'color': item.get('color', '')})
        total += item['price'] * item['qty']
    return items, total

@app.route('/')
def index():
    products = query("SELECT * FROM products ORDER BY created_at DESC LIMIT 8")
    return render_template('index.html', products=products)

@app.route('/products')
def products():
    cat = request.args.get('category', '')
    if cat and cat in CATEGORIES:
        all_products = query("SELECT * FROM products WHERE category = ? ORDER BY name", (cat,))
    else:
        all_products = query("SELECT * FROM products ORDER BY name")
    return render_template('products.html', products=all_products, categories=CATEGORIES, current_cat=cat)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = query_one("SELECT * FROM products WHERE id = ?", (product_id,))
    if not product:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('products'))
    items, cart_total = cart_items_and_total()
    return render_template('product.html', product=product, cart_items=items, cart_total=cart_total)

@app.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = str(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 1))
    size = request.form.get('size', '').strip()
    color = request.form.get('color', '').strip()
    product = query_one("SELECT * FROM products WHERE id = ?", (product_id,))
    if not product:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('products'))
    item_key = product_id
    if size:
        item_key += f'_size_{size}'
    if color:
        item_key += f'_color_{color}'
    cart = session.get('cart', {})
    if item_key in cart:
        cart[item_key]['qty'] += qty
    else:
        cart[item_key] = {'name': product['name'], 'price': product['price'], 'qty': qty, 'image': product['image_url'], 'size': size, 'color': color, 'product_id': product_id}
    session['cart'] = cart
    flash(f'"{product["name"]}" ajouté au panier !', 'success')
    if request.form.get('redirect') == 'checkout':
        return redirect(url_for('checkout'))
    return redirect(request.referrer or url_for('products'))

@app.route('/cart/update', methods=['POST'])
def cart_update():
    item_key = str(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 0))
    cart = session.get('cart', {})
    if qty <= 0:
        cart.pop(item_key, None)
    elif item_key in cart:
        cart[item_key]['qty'] = qty
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove/<item_key>')
def cart_remove(item_key):
    cart = session.get('cart', {})
    cart.pop(item_key, None)
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    items = []
    total = 0.0
    for item_key, item in cart_items.items():
        items.append({'id': item_key, 'product_id': item.get('product_id', item_key), 'name': item['name'], 'price': item['price'], 'qty': item['qty'], 'image': item.get('image', ''), 'size': item.get('size', ''), 'color': item.get('color', '')})
        total += item['price'] * item['qty']
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout')
def checkout():
    items, subtotal = cart_items_and_total()
    if not items:
        flash('Votre panier est vide.', 'info')
        return redirect(url_for('products'))
    return render_template('checkout.html', items=items, subtotal=subtotal, wilayas=WILAYAS)

@app.route('/checkout/submit', methods=['POST'])
def checkout_submit():
    items, subtotal = cart_items_and_total()
    if not items:
        flash('Votre panier est vide.', 'error')
        return redirect(url_for('products'))
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    wilaya_id = request.form.get('wilaya_id', type=int, default=0)
    commune = request.form.get('commune', '').strip()
    delivery_type = request.form.get('delivery_type', 'domicile')
    notes = request.form.get('notes', '').strip()
    if not name or not phone or not commune or not wilaya_id:
        flash('Veuillez remplir tous les champs obligatoires.', 'error')
        return render_template('checkout.html', items=items, subtotal=subtotal, wilayas=WILAYAS)
    if len(phone) != 10 or not phone.isdigit():
        flash('Le numéro de téléphone doit contenir exactement 10 chiffres.', 'error')
        return render_template('checkout.html', items=items, subtotal=subtotal, wilayas=WILAYAS)
    if delivery_type not in ('domicile', 'bureau'):
        delivery_type = 'domicile'
    delivery_price = get_delivery_price(wilaya_id, delivery_type, phone)
    total = subtotal + delivery_price
    wilaya_name = ''
    for wid, wname, _, _ in WILAYAS:
        if wid == wilaya_id:
            wilaya_name = wname
            break
    address = f"{commune}, {wilaya_name}"
    order_id = execute(
        "INSERT INTO orders (customer_name, customer_phone, customer_address, wilaya, wilaya_id, commune, delivery_type, delivery_price, notes, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, phone, address, wilaya_name, wilaya_id, commune, delivery_type, delivery_price, notes, total)
    )
    for item in items:
        execute(
            "INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, item_size, item_color) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_id, item.get('product_id', item['id']), item['name'], item['qty'], item['price'], item.get('size', ''), item.get('color', ''))
        )
    session.pop('cart', None)
    return redirect(url_for('order_confirmed', order_id=order_id))

@app.route('/order/<int:order_id>')
def order_confirmed(order_id):
    order = query_one("SELECT * FROM orders WHERE id = ?", (order_id,))
    items = query("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    if not order:
        flash('Commande introuvable.', 'error')
        return redirect(url_for('index'))
    return render_template('order_confirmed.html', order=order, items=items)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Mot de passe incorrect.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    total_products = query_one("SELECT COUNT(*) as c FROM products")['c']
    total_orders = query_one("SELECT COUNT(*) as c FROM orders")['c']
    pending_orders = query_one("SELECT COUNT(*) as c FROM orders WHERE status = 'pending'")['c']
    recent_orders = query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
    return render_template('admin/dashboard.html', total_products=total_products, total_orders=total_orders, pending_orders=pending_orders, recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    all_products = query("SELECT * FROM products ORDER BY name")
    return render_template('admin/products.html', products=all_products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_product_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', 0)
        category = request.form.get('category', 'general')
        description = request.form.get('description', '')
        video_url = request.form.get('video_url', '').strip()
        sizes = request.form.get('sizes', '').strip()
        colors = request.form.get('colors', '').strip()
        image_url = ''
        if not name or not price:
            flash('Nom et prix sont obligatoires.', 'error')
            return render_template('admin/product_form.html', product=None, categories=CATEGORIES)
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_url = url_for('static', filename=f'uploads/{filename}')
        execute("INSERT INTO products (name, description, price, image_url, video_url, sizes, colors, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, description, float(price), image_url, video_url, sizes, colors, category))
        flash('Produit ajouté avec succès.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None, categories=CATEGORIES)

@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_product_edit(product_id):
    product = query_one("SELECT * FROM products WHERE id = ?", (product_id,))
    if not product:
        flash('Produit introuvable.', 'error')
        return redirect(url_for('admin_products'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', 0)
        category = request.form.get('category', 'general')
        description = request.form.get('description', '')
        video_url = request.form.get('video_url', '').strip()
        sizes = request.form.get('sizes', '').strip()
        colors = request.form.get('colors', '').strip()
        image_url = product['image_url']
        if not name or not price:
            flash('Nom et prix sont obligatoires.', 'error')
            return render_template('admin/product_form.html', product=product, categories=CATEGORIES)
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_url = url_for('static', filename=f'uploads/{filename}')
        execute("UPDATE products SET name=?, description=?, price=?, image_url=?, video_url=?, sizes=?, colors=?, category=? WHERE id=?",
                (name, description, float(price), image_url, video_url, sizes, colors, category, product_id))
        flash('Produit modifié avec succès.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=product, categories=CATEGORIES)

@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def admin_product_delete(product_id):
    execute("DELETE FROM products WHERE id = ?", (product_id,))
    flash('Produit supprimé.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    status_filter = request.args.get('status', '')
    if status_filter:
        all_orders = query("SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC", (status_filter,))
    else:
        all_orders = query("SELECT * FROM orders ORDER BY created_at DESC")
    return render_template('admin/orders.html', orders=all_orders, current_status=status_filter)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
def admin_order_status(order_id):
    status = request.form.get('status', 'pending')
    if status not in ('pending', 'confirmed', 'completed', 'cancelled'):
        flash('Statut invalide.', 'error')
        return redirect(url_for('admin_orders'))
    execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    flash('Statut mis à jour.', 'success')
    return redirect(url_for('admin_orders'))

if __name__ == '__main__':
    app.run(debug=True)
