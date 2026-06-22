# PROJECT_MAP - Femme Fashion E-commerce

## [TECH_STACK]
| Layer | Technologie | Version |
|-------|------------|---------|
| Runtime | Python | 3.13.7 |
| Framework | Flask | 3.1.3 |
| Database | SQLite | 3.x (built-in) |
| Templating | Jinja2 | (bundled Flask) |
| Frontend | Vanilla JS + CSS3 | - |
| Auth | Werkzeug password hashing | (bundled Flask) |

## [SYSTEM_FLOW]
```
User ──► Home Page ──► Products ──► Product Detail ──► Cart ──► Checkout ──► Confirmation
                                  ▲                      │
                                  └── Admin Panel ◄──────┘
                                        │
                                    ┌───┴───┐
                                 Products   Orders
                                  CRUD       View
```

### User Journeys (Verifiable Goals)

**Client Flow:**
1. `[G1]` Home → Affiche produits vedettes + navigation
2. `[G2]` Tous les produits → Grille avec filtrage par catégorie
3. `[G3]` Détail produit → Nom, prix, description, bouton "Ajouter au panier"
4. `[G4]` Panier → Liste articles, quantité modifiable, total, bouton "Commander"
5. `[G5]` Checkout → Formulaire (nom, téléphone, adresse, notes) → validation → soumission
6. `[G6]` Confirmation → Message + résumé commande

**Admin Flow:**
7. `[G7]` Login → Accès protégé par mot de passe
8. `[G8]` Dashboard → Statistiques (total produits, total commandes)
9. `[G9]` Gestion produits → Liste, Ajouter, Modifier, Supprimer
10. `[G10]` Gestion commandes → Liste avec statut (pending/confirmed/completed/cancelled)

## [ARCHITECTURE]
```
femme-fashion/
├── app.py              # Flask app, config, routes (main + admin)
├── db.py               # SQLite init + query helpers
├── requirements.txt    # Python dependencies
├── PROJECT_MAP.md      # This file
├── static/
│   ├── style.css       # All styles
│   └── main.js         # Cart + form interactions
├── templates/
│   ├── base.html       # Layout (nav, footer)
│   ├── index.html      # Home page
│   ├── products.html   # Product grid
│   ├── product.html    # Product detail
│   ├── cart.html       # Shopping cart
│   ├── checkout.html   # Checkout form
│   ├── order_confirmed.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── products.html
│       ├── product_form.html
│       └── orders.html
└── data/
    └── seed.py         # Seed sample products
```

### Design Principles
- **Simplicity First**: Single app.py for all routes, no unnecessary abstractions
- **No ORM**: Raw SQLite (zero extra deps, full control)
- **Session Cart**: Flask session (no DB cart needed)
- **Admin Auth**: Simple password check via env var or config (no user mgmt complexity)
- **No JS framework**: Vanilla JS only for cart qty updates + UX enhancements

## [ORPHANS & PENDING]
- [ ] Product images: placeholder URLs (placehold.co) until real images provided
- [ ] Email notification for new orders (out of scope - future)
- [ ] Pagination for products (not needed < 100 products)
- [ ] Wilaya delivery pricing management from Admin panel (currently hardcoded in Python)
