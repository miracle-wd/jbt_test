import json
import os
import base64
import hashlib
import hmac
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_FILE = os.path.join(os.path.dirname(__file__), "users.txt")

app = FastAPI(title="Mini Login Site")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 密码哈希：PBKDF2（标准库） ============
PBKDF2_ITERS = 200_000

def hash_password(password: str) -> str:
    # 支持超长密码
    if len(password) > 10000:
        raise HTTPException(status_code=400, detail="password too long (max 10000 chars)")

    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERS, dklen=32)
    return "pbkdf2${}${}${}".format(
        PBKDF2_ITERS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iters, salt_b64, dk_b64 = stored.split("$", 3)
        if scheme != "pbkdf2":
            return False
        iters = int(iters)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        dk_expected = base64.b64decode(dk_b64.encode("ascii"))
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters, dklen=len(dk_expected))
        return hmac.compare_digest(dk, dk_expected)
    except Exception:
        return False

# ============ 用户存储============
def read_users():
    users = {}
    if not os.path.exists(DATA_FILE):
        return users
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            users[obj["username"]] = obj["password_hash"]
    return users

def append_user(username: str, password_hash: str):
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"username": username, "password_hash": password_hash}, ensure_ascii=False) + "\n")

# ============ API ============
class RegisterReq(BaseModel):
    username: str
    password: str

class LoginReq(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(req: RegisterReq):
    users = read_users()
    if req.username in users:
        raise HTTPException(status_code=400, detail="username already exists")
    pw_hash = hash_password(req.password)
    append_user(req.username, pw_hash)
    return {"ok": True}

@app.post("/login")
def login(req: LoginReq):
    users = read_users()
    if req.username not in users:
        raise HTTPException(stcdatus_code=401, detail="invalid credentials")
    if not verify_password(req.password, users[req.username]):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"ok": True}

