import sys; sys.path.insert(0, 'C:/femme-fashion')
from app import app

c = app.test_client()
rv = c.post('/admin/login', data={'password': 'admin123'}, follow_redirects=True)
rv = c.get('/admin/orders')
body = rv.data.decode('utf-8')

print('Status:', rv.status_code)
if 'Traceback' in body or 'Internal Server Error' in body:
    print('ERROR FOUND:')
    # Find the error
    if 'Traceback' in body:
        start = body.find('Traceback')
        end = body.find('\n\n', start)
        print(body[start:end+100])
    else:
        print(body[:2000])
else:
    print('Page loads OK')
    print('Has table:', 'admin-table' in body)
    print('Has "Aucune commande":', 'Aucune commande' in body)
