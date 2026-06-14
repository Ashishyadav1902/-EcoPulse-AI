from app import app, db

with app.app_context():
    try:
        db.session.execute(db.text("ALTER TABLE ecopulse_users ADD COLUMN location_lat FLOAT;"))
        db.session.execute(db.text("ALTER TABLE ecopulse_users ADD COLUMN location_lon FLOAT;"))
        db.session.execute(db.text("ALTER TABLE ecopulse_users ADD COLUMN location_name VARCHAR(100);"))
        db.session.commit()
        print("Successfully added location columns to ecopulse_users table.")
    except Exception as e:
        print(f"Error adding columns (they might already exist): {e}")
