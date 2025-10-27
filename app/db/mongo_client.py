"""
MongoDB client setup using PyMongo (synchronous).

This module provides a PyMongo MongoClient connection to MongoDB.
We use PyMongo for actual database operations while Beanie models
are used only for schema definition and validation.
"""

from pymongo import MongoClient
from app.core.config import configurations

# Initialize PyMongo client
client = MongoClient(configurations.MONGODB_URL)

# Get the database instance
db = client.maitech

# Export the database object for use in other modules
__all__ = ["db"]
