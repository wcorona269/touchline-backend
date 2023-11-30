from dotenv import load_dotenv
load_dotenv(".flaskenv")
import os

class Config(object):
  SECRET_KEY = os.getenv('SECRET_KEY') or 'key-for-devs'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
  AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
  AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
  AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")