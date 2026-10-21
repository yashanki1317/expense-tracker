from app import app, db
import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Starting Flask App via runner...")
    app.run(host='127.0.0.1', port=5001, debug=False)