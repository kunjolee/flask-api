FLASK_APP=main
FLASK_DEBUG=1
FLASK_RUN_PORT=8080

# .flaskenv puede tener variables de entorno publicas, y flask va a leer este archivo solo si python-dotenv esta instalado
# .env puede ser usado tambien, y sobre escribe los valores de .flaskenv
# puedo usar tambien variables de entorno en la CLI (e.g. export FLASK_RUN_PORT=8000) y esta sobre escribe los valores de .env