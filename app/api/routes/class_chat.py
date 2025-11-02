from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Class Chat"])


@router.get("/class-chat/conversations", summary="List conversations")
async def list_conversations():
    return {"message": "Success", "endpoint": "class-chat/conversations"}


@router.get("/class-chat/conversation/{chat_id}/messages", summary="Get conversation messages")
async def get_conversation_messages(chat_id: str):
    return {"message": "Success", "endpoint": "class-chat/conversation/{chat_id}/messages", "chat_id": chat_id}


@router.post("/class-chat/conversation/{chat_id}/message", summary="Post message to conversation")
async def post_conversation_message(chat_id: str):
    return {"message": "Success", "endpoint": "class-chat/conversation/{chat_id}/message", "chat_id": chat_id}


