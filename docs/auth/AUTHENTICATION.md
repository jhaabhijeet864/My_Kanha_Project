# JWT Authentication & User Management

## Overview

The Kanha API now includes JWT-based user authentication that enables:
- **User Registration** - Create new user accounts
- **User Login** - Authenticate users and receive JWT tokens
- **Persistent Chat History** - Link conversations to authenticated users
- **Session Management** - Create, list, and delete conversation sessions
- **Optional Authentication** - Chat endpoints work with or without login

---

## Authentication Features

### 1. User Registration
Register a new user account with email and password.

**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "username": "seeker_123",
  "email": "seeker@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Seeker"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "a1b2c3d4e5f6",
    "username": "seeker_123",
    "email": "seeker@example.com",
    "full_name": "John Seeker",
    "created_at": "2026-01-24T10:30:00",
    "last_login": "2026-01-24T10:30:00"
  }
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric + underscore only
- Email: Valid email format
- Password: Minimum 8 characters
- Full name: Optional, max 100 characters

---

### 2. User Login
Authenticate with username/email and password.

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "username": "seeker_123",
  "password": "SecurePassword123!"
}
```

**Response:** (Same as registration)

---

### 3. Get Current User Profile
Retrieve authenticated user information.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "a1b2c3d4e5f6",
  "username": "seeker_123",
  "email": "seeker@example.com",
  "full_name": "John Seeker",
  "created_at": "2026-01-24T10:30:00",
  "last_login": "2026-01-24T10:30:00"
}
```

---

### 4. Refresh Token
Get a new access token before expiration.

**Endpoint:** `POST /auth/refresh`

**Headers:**
```
Authorization: Bearer <expired_token>
```

**Response:** (Same as login)

---

## Chat with Authentication

### Authenticated Chat
When a user logs in, they can chat with their account linked.

**Endpoint:** `POST /chat`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "What is the meaning of life?",
  "language": "english",
  "top_k": 5
}
```

**Response:**
```json
{
  "response": "Dear seeker, the Bhagavad Gita teaches...",
  "sources": [...],
  "language": "english",
  "session_id": "session_123",
  "user_id": "a1b2c3d4e5f6",
  "metadata": {}
}
```

**Key Features:**
- ✅ Chat automatically linked to user account
- ✅ Conversation history saved to user's profile
- ✅ Can access session later via history endpoints
- ✅ Token-based security (no password in chat requests)

---

### Anonymous Chat (Optional)
Chat without authentication - no history saved to account.

**Endpoint:** `POST /chat`

**Request:** (No Authorization header)
```json
{
  "message": "What is the meaning of life?",
  "language": "english",
  "top_k": 5
}
```

**Response:**
```json
{
  "response": "Dear seeker, the Bhagavad Gita teaches...",
  "sources": [...],
  "language": "english",
  "session_id": "temp_session_123",
  "user_id": "temp_user_456",
  "metadata": {}
}
```

---

## Chat History Management

All history endpoints require JWT authentication.

### 1. Create New Session
Start a new conversation session.

**Endpoint:** `POST /history/new`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `language` (optional): "english" or "hindi" (default: "english")

**Response:**
```json
{
  "session_id": "session_abc123",
  "user_id": "user_123",
  "created_at": "2026-01-24T10:30:00",
  "language": "english",
  "message": "New conversation session created"
}
```

---

### 2. List User Sessions
Get all conversation sessions for authenticated user.

**Endpoint:** `GET /history/list`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "a1b2c3d4e5f6",
  "total_sessions": 5,
  "sessions": [
    {
      "session_id": "session_1",
      "created_at": "2026-01-24T10:30:00",
      "last_updated": "2026-01-24T11:45:00",
      "language": "english",
      "message_count": 8
    },
    ...
  ]
}
```

---

### 3. Get Session Details
Retrieve full conversation with all messages.

**Endpoint:** `GET /history/{session_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `max_messages` (optional): Limit number of messages returned

**Response:**
```json
{
  "session_id": "session_1",
  "user_id": "a1b2c3d4e5f6",
  "created_at": "2026-01-24T10:30:00",
  "last_updated": "2026-01-24T11:45:00",
  "language": "english",
  "message_count": 8,
  "messages": [
    {
      "role": "user",
      "content": "What is karma?",
      "sources": [...]
    },
    {
      "role": "assistant",
      "content": "Dear seeker, karma is...",
      "sources": [...]
    },
    ...
  ],
  "metadata": {}
}
```

---

### 4. Get Session Statistics
Retrieve analytics for a conversation.

**Endpoint:** `GET /history/{session_id}/stats`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "session_id": "session_1",
  "user_id": "a1b2c3d4e5f6",
  "created_at": "2026-01-24T10:30:00",
  "last_updated": "2026-01-24T11:45:00",
  "total_messages": 8,
  "user_messages": 4,
  "assistant_messages": 4,
  "language": "english",
  "duration_minutes": 75.5,
  "metadata": {}
}
```

---

### 5. Delete Session
Remove a conversation session.

**Endpoint:** `DELETE /history/{session_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "session_1"
}
```

---

### 6. Get User Statistics
View overall conversation metrics.

**Endpoint:** `GET /history/me/stats`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "a1b2c3d4e5f6",
  "total_sessions": 5,
  "total_messages": 42,
  "avg_session_duration_minutes": 45.3,
  "languages_used": ["english", "hindi"],
  "created_at": "2026-01-20T00:00:00",
  "last_conversation": "2026-01-24T11:45:00"
}
```

---

### 7. Cleanup Old Sessions
Delete old sessions, keeping only the N most recent.

**Endpoint:** `POST /history/me/cleanup`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `max_sessions`: Keep only this many recent sessions (default: 50)

**Response:**
```json
{
  "user_id": "a1b2c3d4e5f6",
  "deleted_sessions": 3,
  "message": "Cleaned up 3 old sessions"
}
```

---

## Streaming Chat with Authentication

The streaming endpoint also supports JWT authentication for persistent history.

**Endpoint:** `POST /chat/stream`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "What is dharma?",
  "language": "english",
  "top_k": 5
}
```

**Response:** SSE stream with chunks
```
data: {"content": "Dear", "is_complete": false}
data: {"content": " seeker,", "is_complete": false}
...
data: {"content": "", "is_complete": true, "sources": [...]}
```

---

## Database & Data Persistence

The authentication system supports multiple persistence layers for flexibility:

### 1. Primary DB (PostgreSQL)
Managed via **Firebase Data Connect**. This is the production-ready layer used for high-scale user management and cross-platform synchronization.

### 2. Local Auth DB (SQLite)
Used for local development and edge deployments where a full PostgreSQL instance is not required.

**Database Location:** `./data/users/users.db`

### 3. Conversation Store (JSON/MVP)
Currently, conversation history is stored as structured JSON files to allow for rapid iteration and easy migration to the Data Connect schema.

**Storage Location:** `./data/conversations/`

### Password Security
- ✅ **PBKDF2 Hashing** - 100,000 iterations
- ✅ **Unique Salts** - Random salt per user
- ✅ **Never Stored** - Password never stored in logs or responses

### Token Security
- ✅ **JWT Signature** - HS256 algorithm
- ✅ **Token Expiration** - 24 hours (configurable)
- ✅ **No Refresh Issues** - Refresh endpoint for token renewal
- ✅ **Bearer Scheme** - Standard HTTP Authorization header

### Data Privacy
- ✅ **User Isolation** - Sessions only accessible to owner
- ✅ **History Encryption** - Optional (can be added)
- ✅ **CORS Protection** - Configured origins only
- ✅ **Rate Limiting** - Prevents brute force attacks (planned)

---

## Environment Configuration

Add to `.env` file:

```env
# JWT Configuration
JWT_SECRET_KEY="your-super-secret-key-change-this-in-production"
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL="sqlite:///./data/users/users.db"
```

**⚠️ IMPORTANT:** 
- Change `JWT_SECRET_KEY` in production to a strong random string
- Generate strong key: `openssl rand -hex 32`
- Store securely in environment variables, not in code

---

## Usage Examples

### Complete Authentication Flow

**1. Register User**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seeker",
    "email": "seeker@example.com",
    "password": "MySecurePass123",
    "full_name": "John Seeker"
  }'
```

**2. Save Token**
```bash
# Extract from response and store securely
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**3. Chat with Authentication**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is the purpose of life?",
    "language": "english",
    "top_k": 5
  }'
```

**4. View Chat History**
```bash
curl -X GET "http://localhost:8000/history/list" \
  -H "Authorization: Bearer $TOKEN"
```

**5. Get Specific Session**
```bash
curl -X GET "http://localhost:8000/history/session_123" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing

Run authentication tests:

```bash
cd backend
pytest tests/test_auth.py -v
```

Test login/registration:
```bash
pytest tests/test_auth.py::test_register -v
pytest tests/test_auth.py::test_login -v
```

---

## Migration Guide (For Existing Users)

If you had anonymous chats before authentication:

1. **Create Account**
   - Register new user account via `/auth/register`
   
2. **Receive JWT Token**
   - Token valid for 24 hours
   - Use for all authenticated endpoints

3. **Link to Existing Sessions**
   - Chat with new user_id (JWT authenticated)
   - Old anonymous sessions remain accessible but not associated

4. **Backward Compatibility**
   - Anonymous chat still works (no Authorization header)
   - Both methods coexist seamlessly

---

## Roadmap

### Implemented ✅
- [x] User registration with email validation
- [x] Secure password hashing (PBKDF2)
- [x] JWT authentication & tokens
- [x] Token refresh mechanism
- [x] User profile endpoints
- [x] Chat history tied to users
- [x] Session management (create, list, delete)
- [x] Optional auth for chat endpoints

### Planned 🚀
- [ ] Email verification
- [ ] Password reset via email
- [ ] Two-factor authentication
- [ ] OAuth2 integration (Google, GitHub)
- [ ] User preferences & settings
- [ ] Chat history encryption
- [ ] Rate limiting per user
- [ ] Conversation sharing
- [ ] Export conversation history
- [ ] Advanced user analytics

---

## Troubleshooting

### "Invalid or expired token"
- Token has expired → Use `/auth/refresh` to get new token
- Token is malformed → Re-login via `/auth/login`
- Token is wrong → Verify Authorization header is present

### "Session not found"
- Session belongs to different user → Sessions are user-specific
- Session was deleted → Check if it was cleaned up
- User_id mismatch → Ensure you're using correct token

### "Username already exists"
- Username taken → Choose different username
- Email already exists → Different error message returned
- Case-sensitive → Usernames are case-sensitive

---

## Support

For authentication issues:
1. Check error message in response
2. Verify JWT token is valid
3. Ensure Authorization header format: `Authorization: Bearer <token>`
4. Check database connection: `./data/users/users.db`

---

**Built with security & privacy in mind 🔒**
