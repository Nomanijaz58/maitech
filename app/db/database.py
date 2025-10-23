import asyncio
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, OperationFailure
from app.core.config import configurations
from app.db.documents.user import User


class DatabaseService:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.users_collection: Optional[Collection] = None

    async def connect(self):
        """Connect to MongoDB using pymongo with manual async handling"""
        try:
            # Run pymongo connection in thread pool
            self.client = await asyncio.to_thread(
                MongoClient, 
                configurations.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            
            # Get database and collection
            self.database = await asyncio.to_thread(
                self.client.get_database
            )
            self.users_collection = await asyncio.to_thread(
                self.database.get_collection, "users"
            )
            
            # Test connection
            await asyncio.to_thread(self.client.admin.command, 'ping')
            print("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            await asyncio.to_thread(self.client.close)
            print("🔌 Disconnected from MongoDB")

    async def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            user_data = await asyncio.to_thread(
                self.users_collection.find_one, 
                {"email": email}
            )
            if user_data:
                user_data["_id"] = str(user_data["_id"])  # Convert ObjectId to string
                return User(**user_data)
            return None
        except Exception as e:
            print(f"Error finding user by email: {e}")
            return None

    async def create_user(self, user: User) -> Optional[User]:
        """Create a new user"""
        try:
            user_dict = user.dict(by_alias=True, exclude={"id"})
            result = await asyncio.to_thread(
                self.users_collection.insert_one,
                user_dict
            )
            if result.inserted_id:
                user.id = result.inserted_id
                return user
            return None
        except DuplicateKeyError:
            print(f"User with email {user.email} already exists")
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user by ID"""
        try:
            from bson import ObjectId
            result = await asyncio.to_thread(
                self.users_collection.update_one,
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            from bson import ObjectId
            result = await asyncio.to_thread(
                self.users_collection.delete_one,
                {"_id": ObjectId(user_id)}
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    async def get_all_users(self, limit: int = 100) -> List[User]:
        """Get all users with limit"""
        try:
            cursor = await asyncio.to_thread(
                self.users_collection.find,
                limit=limit
            )
            users_data = await asyncio.to_thread(list, cursor)
            
            users = []
            for user_data in users_data:
                user_data["_id"] = str(user_data["_id"])
                users.append(User(**user_data))
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []


# Global database service instance
db_service = DatabaseService()
