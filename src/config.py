"""Application configuration."""
import os
import re
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load dotenv
dotenv_path = os.path.join(ROOT_DIR, '.env')
load_dotenv(dotenv_path)

# Out dir
OUT_DIR = os.path.join(ROOT_DIR, 'out')

# Set the settings
cdn_base_url = re.sub(r"https?://", '//', os.getenv('CDN_BASE_URL').rstrip('/'))

config = {
	'CORE_DB_HOST': os.getenv('CORE_DB_HOST'),
	'CORE_DB_NAME': os.getenv('CORE_DB_NAME'),
	'CORE_DB_PORT': os.getenv('CORE_DB_PORT'),
	'CORE_DB_USER': os.getenv('CORE_DB_USER'),
	'CORE_DB_PASSWORD': os.getenv('CORE_DB_PASSWORD'),
	'PROFILE_DB_HOST': os.getenv('PROFILE_DB_HOST'),
	'PROFILE_DB_NAME': os.getenv('PROFILE_DB_NAME'),
	'PROFILE_DB_PORT': os.getenv('PROFILE_DB_PORT'),
	'PROFILE_DB_USER': os.getenv('PROFILE_DB_USER'),
	'PROFILE_DB_PASSWORD': os.getenv('PROFILE_DB_PASSWORD'),
	'ROOT_DIR': ROOT_DIR,
	'OUT_DIR': OUT_DIR,
	'IN_DIR': os.getenv('IN_DIR').rstrip('/'),
	'IS_PRODUCTION': os.getenv('PRODUCTION') == '1',
	'CDN_BASE_URL': cdn_base_url
}


def get_config():
	return config
