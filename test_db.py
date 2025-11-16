#!/usr/bin/env python
"""
Script để test database connection
Chạy: python test_db.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

def test_connection():
    """Test database connection"""
    
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get DATABASE_URL from environment
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("\n❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nSet it first:")
        print('  export DATABASE_URL="postgresql://user:pass@host:5432/dbname"')
        print('\nOr for SQLite (local dev):')
        print('  export DATABASE_URL="sqlite:///students.db"')
        return False
    
    # Parse and display info (hide password)
    parsed = urlparse(db_url)
    safe_url = db_url.replace(parsed.password or '', '****') if parsed.password else db_url
    
    print(f"\n📍 Connection String:")
    print(f"   {safe_url[:80]}{'...' if len(safe_url) > 80 else ''}")
    print(f"\n🔧 Parsed Info:")
    print(f"   Scheme: {parsed.scheme}")
    print(f"   Host: {parsed.hostname}")
    print(f"   Port: {parsed.port or 'default'}")
    print(f"   Database: {parsed.path.lstrip('/')}")
    print(f"   Username: {parsed.username}")
    
    # Fix postgres:// to postgresql://
    original_url = db_url
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        print(f"\n⚠️  Fixed URL: postgres:// → postgresql://")
    
    print(f"\n🔌 Testing connection...")
    print(f"   Timeout: 10 seconds")
    
    try:
        # Create engine with timeout
        engine = create_engine(
            db_url,
            connect_args={
                'connect_timeout': 10
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            if 'postgresql' in db_url or 'postgres' in db_url:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                db_type = "PostgreSQL"
            elif 'sqlite' in db_url:
                result = conn.execute(text("SELECT sqlite_version();"))
                version = result.fetchone()[0]
                db_type = "SQLite"
            else:
                version = "Unknown"
                db_type = "Unknown"
            
            # Test a simple query
            result = conn.execute(text("SELECT 1 as test;"))
            test_value = result.fetchone()[0]
            
            print(f"\n✅ CONNECTION SUCCESSFUL!")
            print(f"\n📊 Database Info:")
            print(f"   Type: {db_type}")
            print(f"   Version: {version[:60]}...")
            print(f"   Test Query: SELECT 1 = {test_value}")
            
            # Try to check if tables exist
            if 'postgresql' in db_url or 'postgres' in db_url:
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """))
                table_count = result.fetchone()[0]
                print(f"   Tables: {table_count} table(s) found")
            elif 'sqlite' in db_url:
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM sqlite_master 
                    WHERE type='table';
                """))
                table_count = result.fetchone()[0]
                print(f"   Tables: {table_count} table(s) found")
            
            print(f"\n✨ Database is ready to use!")
            return True
            
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"\n🔍 Error Details:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        # Provide specific help based on error
        error_msg = str(e).lower()
        
        print(f"\n💡 Troubleshooting Tips:")
        
        if 'name or service not known' in error_msg or 'nodename nor servname' in error_msg:
            print("   • Hostname cannot be resolved")
            print("   • Check if you're using Internal Database URL (not External)")
            print("   • Verify the hostname includes full domain:")
            print("     ✅ dpg-xxxxx-a.oregon-postgres.render.com")
            print("     ❌ dpg-xxxxx-a")
        
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            print("   • Connection timeout")
            print("   • Database might be starting up (wait 1-2 minutes)")
            print("   • Check if database status is 'Available' on Render")
            print("   • Verify firewall/network settings")
        
        elif 'authentication failed' in error_msg or 'password' in error_msg:
            print("   • Username or password incorrect")
            print("   • Get fresh credentials from Render dashboard")
            print("   • Make sure URL is properly URL-encoded")
        
        elif 'does not exist' in error_msg:
            print("   • Database name is incorrect")
            print("   • Check database name in Render dashboard")
            print("   • Ensure database has been created")
        
        elif 'could not connect' in error_msg:
            print("   • Cannot reach database server")
            print("   • Check if database is running")
            print("   • Verify you're using correct host and port")
        
        else:
            print("   • Check DATABASE_URL format")
            print("   • Ensure database is created and running")
            print("   • Try using psycopg2 driver: postgresql+psycopg2://...")
        
        print(f"\n📝 Expected URL format:")
        print(f"   PostgreSQL: postgresql://user:pass@host:5432/dbname")
        print(f"   SQLite: sqlite:///path/to/database.db")
        
        return False
    
    finally:
        print("\n" + "=" * 60)

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)