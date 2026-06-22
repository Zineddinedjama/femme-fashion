import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import DATABASE as DB_PATH

PRODUCTS = [
    ('Robe d\'ete florale', 'Robe legere avec motif floral parfaite pour les journees ensoleillees.', 4500, 'https://placehold.co/400x500/7c3aed/ffffff?text=Robe+Florale', 'robe'),
    ('Chemise blanche classique', 'Chemise en coton blanc intemporelle pour un look elegant.', 3200, 'https://placehold.co/400x500/4f46e5/ffffff?text=Chemise+Blanche', 'chemise'),
    ('Pantalon a taille haute', 'Pantalon confortable a taille haute en tissu leger.', 3800, 'https://placehold.co/400x500/0891b2/ffffff?text=Pantalon+TA', 'pantalon'),
    ('Jupe plissee midi', 'Jupe elegante plissee longueur midi, ideale pour le bureau.', 2900, 'https://placehold.co/400x500/dc2626/ffffff?text=Jupe+Plissee', 'jupe'),
    ('Sac a main en cuir', 'Sac a main en cuir veritable avec fermeture a glissiere.', 6500, 'https://placehold.co/400x500/059669/ffffff?text=Sac+Cuir', 'accessoire'),
    ('Robe de soiree elegante', 'Robe longue en satin pour les occasions speciales.', 8900, 'https://placehold.co/400x500/9333ea/ffffff?text=Robe+Soiree', 'robe'),
    ('Chemise en soie', 'Chemise legere en soie naturelle avec col en V.', 5400, 'https://placehold.co/400x500/0d9488/ffffff?text=Chemise+Soie', 'chemise'),
    ('Pantalon cargo detente', 'Pantalon cargo confortable avec poches laterales.', 3500, 'https://placehold.co/400x500/b45309/ffffff?text=Cargo', 'pantalon'),
    ('Echarpe en cachemire', 'Echarpe douce en cachemire pour l\'hiver.', 2800, 'https://placehold.co/400x500/be185d/ffffff?text=Echarpe', 'accessoire'),
    ('Jupe crayon noire', 'Jupe crayon noire classique coupe ajustee.', 2600, 'https://placehold.co/400x500/1f2937/ffffff?text=Jupe+Noire', 'jupe'),
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] > 0:
        print('Database already has products, skipping seed.')
        conn.close()
        return
    for name, desc, price, image, cat in PRODUCTS:
        cur.execute(
            "INSERT INTO products (name, description, price, image_url, category) VALUES (?, ?, ?, ?, ?)",
            (name, desc, price, image, cat)
        )
    conn.commit()
    conn.close()
    print(f'Seeded {len(PRODUCTS)} products.')

if __name__ == '__main__':
    seed()
