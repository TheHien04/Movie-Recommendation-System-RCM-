import os

from app import create_app

app = create_app()

if __name__ == "__main__":
  port = int(os.getenv("PORT", "5001"))
  debug = os.getenv("FLASK_ENV", "development") != "production"
  app.run(debug=debug, port=port)
