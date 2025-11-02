# Notification API Test Guide for Swagger UI

## 📋 Prerequisites

Before testing, you'll need some test notifications in the database. You can create them using the Python shell or create a test endpoint.

### Option 1: Create Test Data via Python (Recommended)
Run this in Python shell after starting the server:

```python
from app.db.documents.notification import Notification
from datetime import datetime, timezone

# Create test notifications
notifications = [
    {
        "user_id": "user-123",
        "title": "New Chat Message",
        "message": "You have received a new message from John Doe",
        "type": "chat",
        "status": "unread",
        "related_resource_id": "chat-456"
    },
    {
        "user_id": "user-123",
        "title": "Flagged Content Alert",
        "message": "Inappropriate content has been flagged in your class",
        "type": "flagged_content",
        "status": "unread",
        "related_resource_id": "alert-789"
    },
    {
        "user_id": "user-456",
        "title": "System Update",
        "message": "Your account settings have been updated",
        "type": "system",
        "status": "read",
        "related_resource_id": None
    },
    {
        "user_id": "user-123",
        "title": "Assignment Graded",
        "message": "Your Math assignment has been graded",
        "type": "system",
        "status": "unread",
        "related_resource_id": "assignment-101"
    }
]

# Insert notifications
for notif_data in notifications:
    notif = Notification(**notif_data)
    await notif.insert()
    print(f"Created notification: {notif.id}")
```

---

## 🧪 Test Parameters for Each Endpoint

### 1️⃣ **GET /api/notifications** - Get All Notifications

**Query Parameters:**
- `limit`: `20` (default, can be 1-100)
- `offset`: `0` (default, number to skip)
- `status`: `unread` (optional: "unread", "read", or "dismissed")
- `user_id`: `user-123` (optional, filter by user)

**Test Scenarios:**

**Scenario 1: Get all notifications (default)**
```
GET /api/notifications
No parameters needed
```

**Scenario 2: Get unread notifications for a specific user**
```
GET /api/notifications?limit=10&offset=0&status=unread&user_id=user-123
```

**Scenario 3: Paginated results**
```
GET /api/notifications?limit=5&offset=0
GET /api/notifications?limit=5&offset=5
```

**Expected Response:**
```json
{
  "notifications": [
    {
      "id": "507f1f77bcf86cd799439011",
      "user_id": "user-123",
      "title": "New Chat Message",
      "message": "You have received a new message from John Doe",
      "type": "chat",
      "status": "unread",
      "created_at": "2025-10-31T21:00:00Z",
      "related_resource_id": "chat-456"
    }
  ],
  "total": 4,
  "limit": 20,
  "offset": 0
}
```

---

### 2️⃣ **PATCH /api/notifications/mark-read** - Mark Multiple Notifications as Read

**Request Body:**
```json
{
  "notification_ids": [
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439012"
  ]
}
```

**Test Scenarios:**

**Scenario 1: Mark 2 notifications as read**
```json
{
  "notification_ids": [
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439012"
  ]
}
```

**Scenario 2: Mark single notification**
```json
{
  "notification_ids": [
    "507f1f77bcf86cd799439011"
  ]
}
```

**Expected Response:**
```json
{
  "message": "Successfully marked 2 notification(s) as read",
  "status": "success"
}
```

**Error Case (Invalid ID format):**
```json
{
  "notification_ids": ["invalid-id"]
}
```
Returns: `400 Bad Request - Invalid notification ID format: invalid-id`

---

### 3️⃣ **PATCH /api/notifications/{notification_id}/read** - Mark Single Notification as Read

**Path Parameters:**
- `notification_id`: `507f1f77bcf86cd799439011` (valid MongoDB ObjectId)

**Test Scenarios:**

**Scenario 1: Mark notification as read**
```
PATCH /api/notifications/507f1f77bcf86cd799439011/read
```

**Expected Response:**
```json
{
  "message": "Notification marked as read successfully",
  "status": "success"
}
```

**Error Case (Invalid ID):**
```
PATCH /api/notifications/invalid-id/read
```
Returns: `400 Bad Request - Invalid notification ID format`

**Error Case (Not Found):**
```
PATCH /api/notifications/507f1f77bcf86cd799439999/read
```
Returns: `404 Not Found - Notification not found`

---

### 4️⃣ **DELETE /api/notifications/{notification_id}/dismiss** - Dismiss Notification

**Path Parameters:**
- `notification_id`: `507f1f77bcf86cd799439011` (valid MongoDB ObjectId)

**Test Scenarios:**

**Scenario 1: Dismiss a notification**
```
DELETE /api/notifications/507f1f77bcf86cd799439011/dismiss
```

**Expected Response:**
```json
{
  "message": "Notification dismissed successfully",
  "status": "success"
}
```

**Error Cases:**
- Invalid ID: `400 Bad Request`
- Not Found: `404 Not Found`

---

### 5️⃣ **GET /api/notifications/search** - Search Notifications

**Query Parameters:**
- `query`: `"chat"` (required, minimum 1 character)
- `limit`: `20` (optional, default: 20, max: 100)
- `offset`: `0` (optional, default: 0)
- `user_id`: `user-123` (optional, filter by user)

**Test Scenarios:**

**Scenario 1: Search for "chat" in all notifications**
```
GET /api/notifications/search?query=chat
```

**Scenario 2: Search for "flagged" with user filter**
```
GET /api/notifications/search?query=flagged&user_id=user-123&limit=10
```

**Scenario 3: Case-insensitive search**
```
GET /api/notifications/search?query=ASSIGNMENT
GET /api/notifications/search?query=assignment
```
Both should return the same results.

**Scenario 4: Partial word search**
```
GET /api/notifications/search?query=grade
```
Will match "graded", "grading", etc.

**Expected Response:**
```json
{
  "notifications": [
    {
      "id": "507f1f77bcf86cd799439011",
      "user_id": "user-123",
      "title": "Assignment Graded",
      "message": "Your Math assignment has been graded",
      "type": "system",
      "status": "unread",
      "created_at": "2025-10-31T21:00:00Z",
      "related_resource_id": "assignment-101"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

**Error Case (Empty query):**
```
GET /api/notifications/search?query=
```
Returns: `422 Validation Error - String should have at least 1 character`

---

### 6️⃣ **POST /api/flagged-content/{alert_id}/ignore** - Ignore Flagged Content

**Path Parameters:**
- `alert_id`: `alert-789` (the related_resource_id of flagged content notification)

**Test Scenarios:**

**Scenario 1: Ignore flagged content**
```
POST /api/flagged-content/alert-789/ignore
```

**Expected Response:**
```json
{
  "message": "Flagged content alert alert-789 has been ignored",
  "status": "success"
}
```

**Error Case (Not Found):**
```
POST /api/flagged-content/non-existent-alert/ignore
```
Returns: `404 Not Found - Flagged content notification not found`

---

### 7️⃣ **POST /api/flagged-content/{alert_id}/action** - Take Action on Flagged Content

**Path Parameters:**
- `alert_id`: `alert-789` (the related_resource_id of flagged content notification)

**Request Body:**
```json
{
  "action": "resolve",
  "details": "Content reviewed and found acceptable"
}
```

**Test Scenarios:**

**Scenario 1: Resolve flagged content**
```json
{
  "action": "resolve",
  "details": "Content reviewed and determined to be appropriate"
}
```

**Scenario 2: Mark as action taken**
```json
{
  "action": "action_taken",
  "details": "Content removed and user warned"
}
```

**Scenario 3: Without details**
```json
{
  "action": "resolve"
}
```

**Expected Response:**
```json
{
  "message": "Flagged content alert alert-789 marked as resolve: Content reviewed and found acceptable",
  "status": "success"
}
```

**Error Cases:**

**Invalid action:**
```json
{
  "action": "invalid_action",
  "details": "Some details"
}
```
Returns: `400 Bad Request - Invalid action. Must be one of: resolve, action_taken`

**Not Found:**
```
POST /api/flagged-content/non-existent-alert/action
Body: {"action": "resolve"}
```
Returns: `404 Not Found - Flagged content notification not found`

---

## 🎯 Quick Test Flow

1. **Create test notifications** (using Python script above)
2. **Get all notifications**: `GET /api/notifications`
3. **Search for specific notification**: `GET /api/notifications/search?query=chat`
4. **Mark one as read**: `PATCH /api/notifications/{id}/read`
5. **Mark multiple as read**: `PATCH /api/notifications/mark-read` with IDs
6. **Test flagged content**: 
   - `POST /api/flagged-content/alert-789/ignore`
   - `POST /api/flagged-content/alert-789/action` with action body
7. **Dismiss notification**: `DELETE /api/notifications/{id}/dismiss`

---

## 💡 Tips for Swagger UI Testing

1. **Get Notification IDs**: First call `GET /api/notifications` to get actual notification IDs from the response
2. **Copy IDs**: Use the `id` field from the response to test other endpoints
3. **Test Filtering**: Try different `status` values: "unread", "read", "dismissed"
4. **Test Pagination**: Use `limit` and `offset` to see pagination in action
5. **Error Testing**: Try invalid IDs and missing parameters to see error responses

---

## 📝 Sample Complete Workflow

```
1. GET /api/notifications
   → Returns list of notifications with IDs

2. Copy a notification ID, e.g., "507f1f77bcf86cd799439011"

3. PATCH /api/notifications/507f1f77bcf86cd799439011/read
   → Marks it as read

4. GET /api/notifications?status=read
   → Should show the notification you just marked

5. DELETE /api/notifications/507f1f77bcf86cd799439011/dismiss
   → Dismisses it

6. GET /api/notifications?status=dismissed
   → Should show the dismissed notification
```







