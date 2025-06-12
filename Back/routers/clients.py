from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from database.dao import user_dao
from data.show_data import ClientPurchase, UserCreate, LoginRequest
from utils.middlewares import get_current_user
from utils.string_utils import is_valid_israeli_id
router = APIRouter()


@router.post("/login")
def login_user(login_data: LoginRequest):
    try:
        token = user_dao.login(login_data)
        return {"data": token, "status": 200, "message": "Logged in successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"data": None, "message": "Login failed", "error": str(e)},
        )


@router.post("/register", status_code=200)
def register_user(user: UserCreate):
    try:

        if not is_valid_israeli_id(user.passport_id):
            raise HTTPException(
                status_code=409, detail="Passport id is not a valid israeli id"
            )

        existing = user_dao.get_user_by_email_or_passport_id(
            user.email, user.passport_id
        )
        if existing:
            raise HTTPException(
                status_code=409, detail="User with email or passport id already exists"
            )
        uid = user_dao.register(user)
        return {
            "message": "User registered",
            "status": 200,
            "data": {"user_id": str(uid)},
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"data": None, "message": "Register failed", "error": str(e)},
        )


@router.get("/me")
def me(current_user=Depends(get_current_user)):

    try:
        user = user_dao.get_user_by_id(current_user["_id"])
        return {
            "status": 200,
            "message": "Fetched user details successfully",
            "data": user,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "message": "Fetching user details failed",
                "error": str(e),
            },
        )


@router.post("/purchase")
def make_purchase(purchase: ClientPurchase, current_user=Depends(get_current_user)):
    try:
        purchase = user_dao.add_purchase(purchase, current_user)
        return {
            "status": 200,
            "message": "Purchase successful",
            "data": purchase,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={"data": None, "message": "Purchase failed", "error": str(e), "status": 400})

@router.get("/purchases")
def get_purchases(current_user=Depends(get_current_user)):
    try:
        purchases = user_dao.get_purchases(current_user["_id"])
        return {
            "status": 200,
            "message": "Purchases fetched successfully",
            "data": purchases,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={"data": None, "message": "Fetching purchases failed", "error": str(e)})