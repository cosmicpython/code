DB_LINK = 'postgresql://postgres:mysecretpassword@localhost:5555'
APP_URL = 'http://localhost:5000'

# def get_db_link():
#     env = os.getenv('ENV')
#     if env == 'LOCAL':
#         port = os.getenv('DB_PORT')
#         user = os.getenv('DB_USER')
#         password = os.getenv('DB_PASSWORD')
#         return f'postgresql://{user}:{password}@localhost:{port}'
#     if env == 'TEST':
#         return f'postgresql://{user}:{password}@localhost:{port}'
