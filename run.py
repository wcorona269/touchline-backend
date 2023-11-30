from app import app
from waitress import serve

# production run command - Use waitress as the production server
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000)