from fastapi import FastAPI, HTTPException, Header, Depends
from .models import UserLogin, UserSignup, ProfileUpdate, InsuranceCreate, SettingsUpdate
from .database import supabase
from typing import Optional

app = FastAPI()

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
         raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup")
def signup(user: UserSignup):
    try:
        print(f"Signing up user: '{user.email}'")
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password,
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/me")
def get_user_details(user = Depends(get_current_user)):
    return user

# --- Profile Endpoints ---
@app.get("/profile")
def get_profile(user = Depends(get_current_user)):
    try:
        data = supabase.table("profiles").select("*").eq("id", user.id).single().execute()
        return data.data
    except Exception:
        # If profile doesn't exist, return basic user info or empty
        return {"id": user.id, "email": user.email, "full_name": "New User"}

@app.put("/profile")
def update_profile(profile: ProfileUpdate, user = Depends(get_current_user)):
    try:
        # Sanitize date if empty string is passed
        profile_data = profile.dict(exclude_unset=True)
        if "date_of_birth" in profile_data and not profile_data["date_of_birth"]:
            del profile_data["date_of_birth"]

        # Upsert profile
        data = supabase.table("profiles").upsert({
            "id": user.id,
            **profile_data,
            "updated_at": "now()"
        }).execute()
        return data.data
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# --- Insurance Endpoints ---
@app.get("/insurances")
def get_insurances(user = Depends(get_current_user)):
    try:
        data = supabase.table("insurances").select("*").eq("user_id", user.id).execute()
        return data.data
    except Exception as e:
        # Return empty list if table doesn't exist yet or error
        return []

@app.get("/insurances/summary")
def get_insurance_summary(user = Depends(get_current_user)):
    try:
        # Just getting all for now, logic to summarize can be here
        data = supabase.table("insurances").select("*").eq("user_id", user.id).limit(3).execute()
        return data.data
    except Exception:
        return []

@app.post("/insurances")
def create_insurance(insurance: InsuranceCreate, user = Depends(get_current_user)):
    try:
        ins_data = insurance.dict()
        # Handle empty dates (set to None if empty string)
        if not ins_data.get("start_date"): ins_data["start_date"] = None
        if not ins_data.get("end_date"): ins_data["end_date"] = None

        data = supabase.table("insurances").insert({
            "user_id": user.id,
            **ins_data,
            "created_at": "now()",
            "updated_at": "now()"
        }).execute()
        return data.data
    except Exception as e:
         print(f"Error creating insurance: {e}")
         raise HTTPException(status_code=400, detail=str(e))

# --- Settings Endpoints ---
@app.get("/settings")
def get_settings(user = Depends(get_current_user)):
    try:
        data = supabase.table("user_settings").select("*").eq("user_id", user.id).single().execute()
        return data.data
    except Exception:
        return {"theme_mode": "system", "notifications_enabled": True}

@app.put("/settings")
def update_settings(settings: SettingsUpdate, user = Depends(get_current_user)):
    try:
        data = supabase.table("user_settings").upsert({
            "user_id": user.id,
            **settings.dict(exclude_unset=True),
            "updated_at": "now()"
        }).execute()
        return data.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
