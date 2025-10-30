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

    def connect(self):
        """Connect to MongoDB using pymongo - synchronous operation"""
        try:
            # Direct pymongo connection - no asyncio.to_thread wrapper
            self.client = MongoClient(
                configurations.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            
            # Get database and collection
            self.database = self.client.get_database()
            self.users_collection = self.database.get_collection("users")
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self):
        """Disconnect from MongoDB - synchronous operation"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

    def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email - synchronous operation"""
        try:
            user_data = self.users_collection.find_one({"email": email})
            if user_data:
                # Keep ObjectId as is; pydantic model is configured to accept ObjectId
                return User(**user_data)
            return None
        except Exception as e:
            print(f"Error finding user by email: {e}")
            raise  # Re-raise exception so caller knows about the failure

    def create_user(self, user: User) -> Optional[User]:
        """Create a new user - synchronous operation"""
        try:
            user_dict = user.dict(by_alias=True, exclude={"id"})
            result = self.users_collection.insert_one(user_dict)
            if result.inserted_id:
                user.id = result.inserted_id
                return user
            return None
        except DuplicateKeyError:
            print(f"User with email {user.email} already exists")
            raise  # Re-raise exception so caller knows about the failure
        except Exception as e:
            print(f"Error creating user: {e}")
            raise  # Re-raise exception so caller knows about the failure

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user by ID - synchronous operation"""
        try:
            from bson import ObjectId
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            raise  # Re-raise exception so caller knows about the failure

    def delete_user(self, user_id: str) -> bool:
        """Delete user by ID - synchronous operation"""
        try:
            from bson import ObjectId
            result = self.users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise  # Re-raise exception so caller knows about the failure

    def get_all_users(self, limit: int = 100) -> List[User]:
        """Get all users with limit - synchronous operation"""
        try:
            cursor = self.users_collection.find(limit=limit)
            users_data = list(cursor)
            
            users = []
            for user_data in users_data:
                # Keep ObjectId type for _id
                users.append(User(**user_data))
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            raise  # Re-raise exception so caller knows about the failure

    # Notifications helpers removed (using Beanie in routes)


# Global database service instance
db_service = DatabaseService()
