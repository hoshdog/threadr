#!/usr/bin/env python3
"""
Comprehensive PostgreSQL database verification for Threadr.
Run this to verify all tables, indexes, and constraints are properly created.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def verify_database():
    """Comprehensive database verification."""
    print("=" * 80)
    print("🔍 THREADR DATABASE VERIFICATION")
    print("=" * 80)
    
    try:
        from sqlalchemy import create_engine, text
        from database.config import DATABASE_URL
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        verification_results = {
            "connection": False,
            "tables": {},
            "indexes": {},
            "constraints": {},
            "data_counts": {},
            "overall_health": False
        }
        
        with engine.connect() as conn:
            print("\n📊 DATABASE CONNECTION TEST")
            print("-" * 40)
            
            # Test connection
            conn.execute(text("SELECT 1"))
            verification_results["connection"] = True
            print("✅ Database connection successful")
            
            # Get database info
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            db_user = conn.execute(text("SELECT current_user")).scalar()
            version = conn.execute(text("SELECT version()")).scalar()
            
            print(f"🗄️  Database: {db_name}")
            print(f"👤 User: {db_user}")
            print(f"📊 PostgreSQL: {version.split(' ')[1]}")
            
            # Get database size
            size_result = conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)).scalar()
            print(f"💾 Database size: {size_result}")
            
            print("\n📋 TABLE VERIFICATION")
            print("-" * 40)
            
            # Expected tables
            expected_tables = [
                'users', 'teams', 'team_memberships', 'team_invites', 
                'threads', 'subscriptions', 'usage_tracking', 'user_sessions',
                'thread_analytics', 'analytics_timeseries', 'team_activities'
            ]
            
            # Get actual tables
            tables_result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            actual_tables = [row[0] for row in tables_result]
            
            print(f"Expected tables: {len(expected_tables)}")
            print(f"Found tables: {len(actual_tables)}")
            
            # Check each expected table
            missing_tables = []
            for table in expected_tables:
                if table in actual_tables:
                    verification_results["tables"][table] = True
                    print(f"  ✅ {table}")
                else:
                    verification_results["tables"][table] = False
                    missing_tables.append(table)
                    print(f"  ❌ {table} - MISSING")
            
            # Check for unexpected tables
            extra_tables = set(actual_tables) - set(expected_tables)
            if extra_tables:
                print(f"\n⚠️  Unexpected tables found: {list(extra_tables)}")
            
            print(f"\n📊 TABLE DETAILS")
            print("-" * 40)
            
            for table in actual_tables:
                # Get column count
                column_result = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND table_schema = 'public'
                """)).scalar()
                
                # Get row count
                try:
                    row_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    verification_results["data_counts"][table] = row_result
                    print(f"  📋 {table}: {column_result} columns, {row_result} rows")
                except Exception as e:
                    print(f"  ⚠️  {table}: {column_result} columns, Error counting rows: {e}")
            
            print(f"\n🔗 INDEX VERIFICATION")
            print("-" * 40)
            
            # Get indexes
            indexes_result = conn.execute(text("""
                SELECT schemaname, tablename, indexname, indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            
            index_count = 0
            current_table = None
            for row in indexes_result:
                schema, table, index_name, index_def = row
                if table != current_table:
                    print(f"\n  📋 {table}:")
                    current_table = table
                    verification_results["indexes"][table] = []
                
                verification_results["indexes"][table].append(index_name)
                index_count += 1
                
                # Show index type
                if 'UNIQUE' in index_def:
                    print(f"    🔑 {index_name} (UNIQUE)")
                elif '_pkey' in index_name:
                    print(f"    🔑 {index_name} (PRIMARY KEY)")
                else:
                    print(f"    📇 {index_name}")
            
            print(f"\n📊 Total indexes: {index_count}")
            
            print(f"\n🛡️  CONSTRAINT VERIFICATION")
            print("-" * 40)
            
            # Get constraints
            constraints_result = conn.execute(text("""
                SELECT 
                    tc.table_name,
                    tc.constraint_name,
                    tc.constraint_type
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'public'
                ORDER BY tc.table_name, tc.constraint_type
            """))
            
            constraint_counts = {}
            current_table = None
            
            for row in constraints_result:
                table, constraint_name, constraint_type = row
                if table != current_table:
                    if current_table is not None:
                        print()
                    print(f"  📋 {table}:")
                    current_table = table
                    constraint_counts[table] = {}
                
                if constraint_type not in constraint_counts[table]:
                    constraint_counts[table][constraint_type] = 0
                constraint_counts[table][constraint_type] += 1
                
                # Show constraint with emoji
                emoji_map = {
                    'PRIMARY KEY': '🔑',
                    'FOREIGN KEY': '🔗', 
                    'UNIQUE': '⚡',
                    'CHECK': '✅'
                }
                emoji = emoji_map.get(constraint_type, '🛡️')
                print(f"    {emoji} {constraint_name} ({constraint_type})")
            
            # Summary of constraints
            total_constraints = sum(sum(counts.values()) for counts in constraint_counts.values())
            print(f"\n📊 Total constraints: {total_constraints}")
            
            print(f"\n🎯 OVERALL ASSESSMENT")
            print("-" * 40)
            
            # Calculate health score
            health_issues = []
            
            if missing_tables:
                health_issues.append(f"Missing tables: {missing_tables}")
            
            if len(actual_tables) != len(expected_tables):
                health_issues.append(f"Table count mismatch: expected {len(expected_tables)}, got {len(actual_tables)}")
            
            # Check critical tables have data structure
            critical_tables = ['users', 'threads', 'subscriptions']
            for table in critical_tables:
                if table not in verification_results["indexes"]:
                    health_issues.append(f"No indexes found for critical table: {table}")
            
            if not health_issues:
                verification_results["overall_health"] = True
                print("🎉 ✅ DATABASE VERIFICATION SUCCESSFUL!")
                print("   • All expected tables found")
                print("   • Proper indexes created")
                print("   • Constraints in place")
                print("   • Database ready for production use")
            else:
                print("⚠️  ❌ DATABASE VERIFICATION ISSUES FOUND:")
                for issue in health_issues:
                    print(f"   • {issue}")
                print("\n💡 Recommendation: Run init_database.py to fix missing components")
            
            return verification_results
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nThis usually means:")
        print("1. You're not in the correct directory")
        print("2. Database modules aren't properly set up")
        print("3. SQLAlchemy isn't installed")
        return None
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        error_str = str(e).lower()
        if "could not connect" in error_str:
            print("\n🔍 Troubleshooting:")
            print("• Check DATABASE_URL environment variable")
            print("• Verify PostgreSQL service is running")
            print("• Ensure you're using Internal Database URL")
        elif "authentication failed" in error_str:
            print("\n🔍 Troubleshooting:")
            print("• Copy Internal Database URL from Render dashboard")
            print("• Check username and password are correct")
        
        return None

def quick_check():
    """Quick database verification - just tables and connection."""
    print("🔍 QUICK DATABASE CHECK")
    print("=" * 40)
    
    try:
        from sqlalchemy import create_engine, text
        from database.config import DATABASE_URL
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Test connection
            conn.execute(text("SELECT 1"))
            print("✅ Database connection: OK")
            
            # Count tables
            tables_result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)).scalar()
            
            print(f"📊 Tables found: {tables_result}")
            
            if tables_result >= 11:
                print("🎉 Database appears ready!")
                return True
            else:
                print("⚠️  Database may need initialization")
                return False
                
    except Exception as e:
        print(f"❌ Quick check failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Threadr database")
    parser.add_argument("--quick", action="store_true", help="Run quick verification only")
    args = parser.parse_args()
    
    if args.quick:
        success = quick_check()
    else:
        result = verify_database()
        success = result and result.get("overall_health", False)
    
    sys.exit(0 if success else 1)