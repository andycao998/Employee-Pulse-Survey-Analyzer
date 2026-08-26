"""
Creating the SQLAlchemy extension that can be imported all over our app as needed
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()