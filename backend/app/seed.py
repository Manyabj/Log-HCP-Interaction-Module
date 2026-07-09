"""
Run with: python -m app.seed
Populates sample Product and Material master data for local development.
"""
from app.database import SessionLocal, Base, engine
from app.models.product import Product
from app.models.material import Material

SAMPLE_PRODUCTS = ["Product X", "Product Y", "CardioMax", "NeuroCare"]
SAMPLE_MATERIALS = [("Brochure", "Brochure"), ("Sample Pack", "Sample"), ("Visual Aid", "Leaflet")]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for name in SAMPLE_PRODUCTS:
            if not db.query(Product).filter(Product.name == name).first():
                db.add(Product(name=name))

        for name, mtype in SAMPLE_MATERIALS:
            if not db.query(Material).filter(Material.name == name).first():
                db.add(Material(name=name, type=mtype))

        db.commit()
        print("Seed data inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
