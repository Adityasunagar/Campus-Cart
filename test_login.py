#!/usr/bin/env python3
"""
Quick test script to verify login functionality
"""
import sys
from app import app
from models.user import User
from utils.db import get_db

def test_database_connection():
    """Test if database connection works"""
    print("🔍 Testing database connection...")
    try:
        with app.app_context():
            db = get_db()
            cursor = db.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_admin_user():
    """Check if admin user exists"""
    print("\n🔍 Checking for admin user...")
    try:
        with app.app_context():
            admin = User.find_by_email("admin@campuscart.com")
            if admin:
                print(f"✅ Admin user found: {admin['username']} (ID: {admin['id']})")
                return admin
            else:
                print("❌ Admin user not found")
                return None
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return None

def test_authenticate():
    """Test authentication with admin credentials"""
    print("\n🔍 Testing authentication...")
    try:
        with app.app_context():
            user = User.authenticate("admin@campuscart.com", "admin123")
            if user == 'banned':
                print("⚠️  Admin user is banned")
                return False
            elif user:
                print(f"✅ Authentication successful for: {user['username']}")
                print(f"   - User ID: {user['id']}")
                print(f"   - Email: {user['email']}")
                print(f"   - Is Admin: {user['is_admin']}")
                return True
            else:
                print("❌ Authentication failed (invalid credentials)")
                return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def test_session_config():
    """Check session configuration"""
    print("\n🔍 Checking Flask session configuration...")
    with app.app_context():
        print(f"✅ SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        print(f"✅ PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
        print(f"✅ SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
        print(f"✅ SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")

if __name__ == '__main__':
    print("=" * 60)
    print("CampusCart Login Functionality Tester")
    print("=" * 60)
    
    # Run all tests
    db_ok = test_database_connection()
    admin_ok = test_admin_user()
    auth_ok = test_authenticate()
    test_session_config()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"  Admin User: {'✅ OK' if admin_ok else '❌ FAILED'}")
    print(f"  Authentication: {'✅ OK' if auth_ok else '❌ FAILED'}")
    print("=" * 60)
    
    if db_ok and admin_ok and auth_ok:
        print("\n✅ All tests passed! You should be able to log in.")
        print("\nTEST LOGIN STEPS:")
        print("1. Run: python app.py")
        print("2. Visit: http://localhost:5000/login")
        print("3. Email: admin@campuscart.com")
        print("4. Password: admin123")
        print("5. After login, check if navbar shows 'Logout' instead of 'Login'")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
