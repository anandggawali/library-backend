from typing import Optional
from pydantic import BaseModel

# ---- AUTH MODELS ----

class UserSignup(BaseModel):
    member_name: str
    username: str
    password: str
    phone: str

class UserLogin(BaseModel):
    username: str
    password: str

# ---- BOOK MODEL ----

class Book(BaseModel):
    id: Optional[str] = None
    title: str
    author: Optional[str] = ""
    price: Optional[str] = ""
    purchaseDate: Optional[str] = ""
    description: Optional[str] = ""
    imageUri: Optional[str] = None
    isAvailable: Optional[bool] = True
    issuedToMemberId: Optional[str] = None
    issueDate: Optional[str] = None
    expectedReturnDate: Optional[str] = None
    actualReturnDate: Optional[str] = None

# ---- MEMBER MODEL (library member, NOT login user) ----

class Member(BaseModel):
    id: Optional[str] = None
    name: str
    phone: str
    email: Optional[str] = ""
    notes: Optional[str] = ""

# ---- RECORD MODEL ----

class Record(BaseModel):
    id: Optional[str] = None
    bookId: str
    bookTitle: str
    bookImage: Optional[str] = None
    memberId: str
    memberName: str
    issueDate: str
    expectedReturnDate: str
    actualReturnDate: Optional[str] = None
    status: Optional[str] = "issued"
