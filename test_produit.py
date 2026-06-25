import sys; sys.path.insert(0, 'C:/femme-fashion')
from app import app
rv = app.test_client().get('/product/11')
body = rv.data.decode('utf-8')

for id_name in ['qty-plus', 'qty-minus', 'qty-display', 'quantity', 'produit-total']:
    count = body.count('id="' + id_name + '"')
    print(id_name + ': ' + str(count) + ' occurrence(s)')

print('price-lg:', 'OK' if 'class="price-lg"' in body else 'MISSING')
print('JS versioned:', 'v=2' in body)
print('main.js loaded:', '/static/main.js' in body)
