# 🚀 VitaFuel Setup Guide for Friend

## Quick Setup (5 minutes)

### Step 1: Install Prerequisites
1. **Install Python 3.8+** from [python.org](https://www.python.org/downloads/)
2. **Install MongoDB** from [mongodb.com](https://www.mongodb.com/try/download/community)

### Step 2: Easy Start (Choose ONE method)

#### Method A: Automatic Start (Recommended)
1. **Double-click** `start_vitafuel.bat` (Windows) or `start_vitafuel.ps1` (PowerShell)
2. **Wait** for both servers to start (about 10 seconds)
3. **Browser will open automatically** to the registration page
4. **Done!** 🎉

#### Method B: Manual Start
1. **Open 2 command prompts/terminals**

2. **Terminal 1 (Backend):**
   ```bash
   cd "VitaFuel3/VitaFuel 3/VitaFuel 2/server"
   pip install -r requirements.txt
   python -m uvicorn main:app --host 127.0.0.1 --port 8004 --reload
   ```

3. **Terminal 2 (Frontend):**
   ```bash
   cd "VitaFuel3/VitaFuel 3/VitaFuel 2/client"
   python -m http.server 5500
   ```

4. **Open browser:** `http://127.0.0.1:5500/register.html`

### Step 3: Test the Application

1. **Registration Test:**
   - Fill out the registration form with a new email
   - Click "Create Account"
   - Should redirect to dashboard ✅

2. **Login Test:**
   - Go to `http://127.0.0.1:5500/login.html`
   - Use the email/password you just created
   - Should login successfully ✅

## 🔧 Important Notes

- **Backend MUST run on port 8004** (already configured)
- **Frontend MUST run on port 5500** (already configured)
- **MongoDB must be running** (usually starts automatically)
- **Both servers must be running** for the app to work

## 🚨 If Something Goes Wrong

1. **"Failed to fetch" error:**
   - Make sure both servers are running
   - Check ports 8004 and 5500 are not used by other apps

2. **"Profile save failed" error:**
   - Backend server is not running
   - Restart the backend server

3. **"User already exists" error:**
   - This is normal! Use the login page instead

4. **MongoDB errors:**
   - Install MongoDB from mongodb.com
   - Start MongoDB service

## 🎯 Success Checklist

- ✅ Backend shows: `Uvicorn running on http://127.0.0.1:8004`
- ✅ Frontend shows: `Serving HTTP on 0.0.0.0 port 5500`
- ✅ Registration form loads
- ✅ Can create new account
- ✅ Can login with existing account
- ✅ Dashboard loads after login

## 📞 Need Help?

1. Check the full `README.md` file
2. Make sure all prerequisites are installed
3. Try restarting both servers
4. Check that ports 8004 and 5500 are available

---

**That's it! The app should work perfectly now! 🎉**
