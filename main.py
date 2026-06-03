from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import uuid

from database import users, books, members, records
from models import UserSignup, UserLogin, Book, Member, Record
from auth import hash_password, verify_password, create_token, get_current_user

app = FastAPI(title="Library Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HELPERS
# =========================

def get_user_by_id(user_id: str):
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None

def serialize(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def serialize_list(docs):
    return [serialize(d) for d in docs]


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {"message": "Library Management API 🚀"}


# =========================
# SIGNUP
# =========================

@app.post("/signup")
def signup(user: UserSignup):
    if users.find_one({"username": user.username}):
        return {"error": "Username already taken"}

    is_first = users.count_documents({}) == 0
    role = "admin" if is_first else "user"

    users.insert_one({
        "member_name": user.member_name,
        "username": user.username,
        "password": hash_password(user.password),
        "phone": user.phone,
        "role": role
    })

    return {"message": f"Account created as {role}"}


# =========================
# LOGIN
# =========================

@app.post("/login")
def login(user: UserLogin):
    db_user = users.find_one({"username": user.username})

    if not db_user:
        return {"error": "User not found"}

    if not verify_password(user.password, db_user["password"]):
        return {"error": "Invalid password"}

    token = create_token({
        "user_id": str(db_user["_id"]),
        "username": db_user["username"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.get("role", "user"),
        "member_name": db_user.get("member_name", "")
    }


# =========================
# PROFILE
# =========================

@app.get("/me")
def get_profile(user_id: str = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}
    return {
        "id": str(user["_id"]),
        "member_name": user.get("member_name", ""),
        "username": user.get("username", ""),
        "phone": user.get("phone", ""),
        "role": user.get("role", "user")
    }


# =========================
# BOOKS
# ✅ owner_id ensures each user sees ONLY their own books
# =========================

@app.get("/books")
def get_books(user_id: str = Depends(get_current_user)):
    data = list(books.find({"owner_id": user_id}))
    return serialize_list(data)


@app.post("/books")
def add_book(book: Book, user_id: str = Depends(get_current_user)):
    book_id = book.id or str(uuid.uuid4())
    books.insert_one({
        "id": book_id,
        "owner_id": user_id,          # ✅ tie book to logged-in user
        "title": book.title,
        "author": book.author,
        "price": book.price,
        "purchaseDate": book.purchaseDate,
        "description": book.description,
        "imageUri": book.imageUri,
        "isAvailable": book.isAvailable,
        "issuedToMemberId": book.issuedToMemberId,
        "issueDate": book.issueDate,
        "expectedReturnDate": book.expectedReturnDate,
        "actualReturnDate": book.actualReturnDate
    })
    return {"message": "Book added", "id": book_id}


@app.put("/books/{book_id}")
def update_book(book_id: str, book: Book, user_id: str = Depends(get_current_user)):
    result = books.update_one(
        {"id": book_id, "owner_id": user_id},   # ✅ can only update own books
        {"$set": {
            "title": book.title,
            "author": book.author,
            "price": book.price,
            "purchaseDate": book.purchaseDate,
            "description": book.description,
            "imageUri": book.imageUri,
            "isAvailable": book.isAvailable,
            "issuedToMemberId": book.issuedToMemberId,
            "issueDate": book.issueDate,
            "expectedReturnDate": book.expectedReturnDate,
            "actualReturnDate": book.actualReturnDate
        }}
    )
    if result.matched_count == 0:
        return {"error": "Book not found"}
    return {"message": "Book updated"}


@app.delete("/books/{book_id}")
def delete_book(book_id: str, user_id: str = Depends(get_current_user)):
    result = books.delete_one({"id": book_id, "owner_id": user_id})  # ✅ own books only
    if result.deleted_count == 0:
        return {"error": "Book not found"}
    return {"message": "Book deleted"}


# =========================
# MEMBERS
# ✅ owner_id ensures each user sees ONLY their own members
# =========================

@app.get("/members")
def get_members(user_id: str = Depends(get_current_user)):
    data = list(members.find({"owner_id": user_id}))
    return serialize_list(data)


@app.post("/members")
def add_member(member: Member, user_id: str = Depends(get_current_user)):
    member_id = member.id or str(uuid.uuid4())
    members.insert_one({
        "id": member_id,
        "owner_id": user_id,          # ✅ tie member to logged-in user
        "name": member.name,
        "phone": member.phone,
        "email": member.email,
        "notes": member.notes
    })
    return {"message": "Member added", "id": member_id}


@app.put("/members/{member_id}")
def update_member(member_id: str, member: Member, user_id: str = Depends(get_current_user)):
    result = members.update_one(
        {"id": member_id, "owner_id": user_id},
        {"$set": {
            "name": member.name,
            "phone": member.phone,
            "email": member.email,
            "notes": member.notes
        }}
    )
    if result.matched_count == 0:
        return {"error": "Member not found"}
    return {"message": "Member updated"}


@app.delete("/members/{member_id}")
def delete_member(member_id: str, user_id: str = Depends(get_current_user)):
    result = members.delete_one({"id": member_id, "owner_id": user_id})
    if result.deleted_count == 0:
        return {"error": "Member not found"}
    return {"message": "Member deleted"}


# =========================
# RECORDS
# ✅ owner_id ensures each user sees ONLY their own records
# =========================

@app.get("/records")
def get_records(user_id: str = Depends(get_current_user)):
    data = list(records.find({"owner_id": user_id}))
    return serialize_list(data)


@app.post("/records")
def add_record(record: Record, user_id: str = Depends(get_current_user)):
    record_id = record.id or str(uuid.uuid4())
    records.insert_one({
        "id": record_id,
        "owner_id": user_id,          # ✅ tie record to logged-in user
        "bookId": record.bookId,
        "bookTitle": record.bookTitle,
        "bookImage": record.bookImage,
        "memberId": record.memberId,
        "memberName": record.memberName,
        "issueDate": record.issueDate,
        "expectedReturnDate": record.expectedReturnDate,
        "actualReturnDate": record.actualReturnDate,
        "status": record.status
    })
    return {"message": "Record added", "id": record_id}


@app.put("/records/{record_id}")
def update_record(record_id: str, record: Record, user_id: str = Depends(get_current_user)):
    result = records.update_one(
        {"id": record_id, "owner_id": user_id},
        {"$set": {
            "actualReturnDate": record.actualReturnDate,
            "status": record.status,
            "issueDate": record.issueDate,
            "expectedReturnDate": record.expectedReturnDate,
            "memberId": record.memberId,
            "memberName": record.memberName
        }}
    )
    if result.matched_count == 0:
        return {"error": "Record not found"}
    return {"message": "Record updated"}
