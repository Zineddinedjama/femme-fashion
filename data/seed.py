import psycopg2
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

DATABASE_URL = os.environ.get('DATABASE_URL', '')

PRODUCTS = [
    ('Robe d\'ete florale', 'Robe legere avec motif floral parfaite pour les journees ensoleillees.', 4500, 'https://picsum.photos/seed/robe-florale/400/500', 'robe'),
    ('Chemise blanche classique', 'Chemise en coton blanc intemporelle pour un look elegant.', 3200, 'https://picsum.photos/seed/chemise-blanche/400/500', 'chemise'),
    ('Pantalon a taille haute', 'Pantalon confortable a taille haute en tissu leger.', 3800, 'https://picsum.photos/seed/pantalon-ta/400/500', 'pantalon'),
    ('Jupe plissee midi', 'Jupe elegante plissee longueur midi, ideale pour le bureau.', 2900, 'https://picsum.photos/seed/jupe-plissee/400/500', 'jupe'),
    ('Sac a main en cuir', 'Sac a main en cuir veritable avec fermeture a glissiere.', 6500, 'https://picsum.photos/seed/sac-cuir/400/500', 'accessoire'),
    ('Robe de soiree elegante', 'Robe longue en satin pour les occasions speciales.', 8900, 'https://picsum.photos/seed/robe-soiree/400/500', 'robe'),
    ('Chemise en soie', 'Chemise legere en soie naturelle avec col en V.', 5400, 'https://picsum.photos/seed/chemise-soie/400/500', 'chemise'),
    ('Pantalon cargo detente', 'Pantalon cargo confortable avec poches laterales.', 3500, 'https://picsum.photos/seed/cargo/400/500', 'pantalon'),
    ('Echarpe en cachemire', 'Echarpe douce en cachemire pour l\'hiver.', 2800, 'https://picsum.photos/seed/echarpe/400/500', 'accessoire'),
    ('Jupe crayon noire', 'Jupe crayon noire classique coupe ajustee.', 2600, 'https://picsum.photos/seed/jupe-noire/400/500', 'jupe'),
]

def seed():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] > 0:
        print('Database already has products, skipping seed.')
        cur.close()
        conn.close()
        return
    for name, desc, price, image, cat in PRODUCTS:
        cur.execute(
            "INSERT INTO products (name, description, price, image_url, category) VALUES (%s, %s, %s, %s, %s)",
            (name, desc, price, image, cat)
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f'Seeded {len(PRODUCTS)} products.')

if __name__ == '__main__':
    seed()
