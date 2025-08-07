#!/usr/bin/env python3
"""
Database Operations Script for Threadr
Handles backup, restore, monitoring, and maintenance operations
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import json
import time

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.database.config import (
    get_database_info, get_database_stats, check_database_connection,
    cleanup_expired_sessions, cleanup_expired_invites,
    vacuum_analyze_tables, update_table_statistics,
    get_connection_metrics, db_config
)
from src.database.migrations import run_full_migration, validate_migration
from src.database.models import Base, User, Thread, Subscription, UsageTracking

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/threadr/database_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# BACKUP OPERATIONS
# ============================================================================

class DatabaseBackupManager:
    """Manage database backups with retention policies"""
    
    def __init__(self, backup_dir: str = "/backups/threadr"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        self.max_backups = int(os.getenv("MAX_BACKUP_COUNT", "50"))
    
    def create_backup(self, backup_type: str = "full") -> dict:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"threadr_{backup_type}_{timestamp}.dump"
        backup_path = self.backup_dir / backup_filename
        
        logger.info(f"Creating {backup_type} backup: {backup_path}")
        
        try:
            # Build pg_dump command
            cmd = [
                "pg_dump",
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                "--format=custom",
                "--compress=9",
                f"--file={backup_path}",
                db_config.database_url
            ]
            
            # Add schema-only option if requested
            if backup_type == "schema":
                cmd.append("--schema-only")
            elif backup_type == "data":
                cmd.append("--data-only")
            
            # Run backup
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            duration = time.time() - start_time
            
            if result.returncode == 0:
                backup_size = backup_path.stat().st_size
                logger.info(f"Backup completed in {duration:.2f}s, size: {backup_size:,} bytes")
                
                # Clean up old backups
                self.cleanup_old_backups()
                
                return {
                    "success": True,
                    "backup_path": str(backup_path),
                    "backup_size": backup_size,
                    "duration_seconds": duration,
                    "timestamp": timestamp
                }
            else:
                logger.error(f"Backup failed: {result.stderr}")
                if backup_path.exists():
                    backup_path.unlink()  # Remove failed backup
                
                return {
                    "success": False,
                    "error": result.stderr,
                    "duration_seconds": duration
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Backup timeout after 1 hour")
            return {"success": False, "error": "Backup timeout"}
        except Exception as e:
            logger.error(f"Backup failed with exception: {e}")
            return {"success": False, "error": str(e)}
    
    def restore_backup(self, backup_path: str, confirm: bool = False) -> dict:
        """Restore database from backup"""
        if not confirm:
            logger.error("Restore requires explicit confirmation (--confirm flag)")
            return {"success": False, "error": "Confirmation required"}
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return {"success": False, "error": "Backup file not found"}
        
        logger.warning(f"RESTORING DATABASE FROM: {backup_path}")
        logger.warning("THIS WILL OVERWRITE ALL CURRENT DATA!")
        
        try:
            # Build pg_restore command
            cmd = [
                "pg_restore",
                "--verbose",
                "--clean",
                "--if-exists",
                "--no-owner",
                "--no-privileges",
                "--dbname", db_config.database_url,
                str(backup_file)
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            duration = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"Restore completed in {duration:.2f}s")
                return {
                    "success": True,
                    "duration_seconds": duration,
                    "backup_file": str(backup_file)
                }
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "duration_seconds": duration
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Restore timeout after 1 hour")
            return {"success": False, "error": "Restore timeout"}
        except Exception as e:
            logger.error(f"Restore failed with exception: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_backups(self):
        """Clean up old backup files based on retention policy"""
        try:
            backup_files = list(self.backup_dir.glob("threadr_*.dump"))
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            deleted_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Keep the newest N backups, but delete anything older than retention_days
            for i, backup_file in enumerate(backup_files):
                file_age = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                # Delete if older than retention period or beyond max count
                if (file_age < cutoff_date) or (i >= self.max_backups):
                    logger.info(f"Deleting old backup: {backup_file.name}")
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backup files")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def list_backups(self) -> list:
        """List available backup files"""
        try:
            backup_files = []
            for backup_file in self.backup_dir.glob("threadr_*.dump"):
                stat = backup_file.stat()
                backup_files.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_days": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                })
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x["created"], reverse=True)
            return backup_files
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

# ============================================================================
# MONITORING AND HEALTH CHECKS
# ============================================================================

class DatabaseMonitor:
    """Monitor database health and performance"""
    
    def __init__(self):
        self.alert_thresholds = {
            "connection_usage_percent": 80,
            "replication_lag_seconds": 60,
            "slow_query_threshold": 5.0,
            "lock_timeout_threshold": 30,
            "disk_usage_percent": 85,
        }
    
    def health_check(self) -> dict:
        """Comprehensive database health check"""
        logger.info("Running database health check...")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        try:
            # Basic connection test
            health_status["checks"]["connection"] = {
                "status": "healthy" if check_database_connection() else "unhealthy",
                "description": "Database connection test"
            }
            
            # Get database info
            db_info = get_database_info()
            health_status["checks"]["database_info"] = {
                "status": "healthy" if db_info.get("status") == "connected" else "unhealthy",
                "details": db_info
            }
            
            # Connection metrics
            conn_metrics = get_connection_metrics()
            if conn_metrics:
                usage_percent = (conn_metrics["total_connections"] / conn_metrics["max_connections"]) * 100
                health_status["checks"]["connections"] = {
                    "status": "healthy" if usage_percent < self.alert_thresholds["connection_usage_percent"] else "warning",
                    "usage_percent": usage_percent,
                    "details": conn_metrics
                }
            
            # Database statistics
            db_stats = get_database_stats()
            health_status["checks"]["statistics"] = {
                "status": "healthy",
                "details": db_stats
            }
            
            # Check for long-running queries
            long_running_queries = self.check_long_running_queries()
            health_status["checks"]["long_running_queries"] = {
                "status": "healthy" if len(long_running_queries) == 0 else "warning",
                "count": len(long_running_queries),
                "queries": long_running_queries[:5]  # Limit output
            }
            
            # Check table sizes and growth
            table_growth = self.check_table_growth()
            health_status["checks"]["table_growth"] = {
                "status": "healthy",
                "details": table_growth
            }
            
            # Overall status
            warning_checks = [check for check in health_status["checks"].values() if check["status"] == "warning"]
            unhealthy_checks = [check for check in health_status["checks"].values() if check["status"] == "unhealthy"]
            
            if unhealthy_checks:
                health_status["overall_status"] = "unhealthy"
            elif warning_checks:
                health_status["overall_status"] = "warning"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)
            return health_status
    
    def check_long_running_queries(self) -> list:
        """Check for long-running queries"""
        try:
            from src.database.config import get_db_session
            from sqlalchemy import text
            
            with get_db_session() as db:
                result = db.execute(text("""
                    SELECT 
                        pid,
                        now() - pg_stat_activity.query_start as duration,
                        query,
                        state,
                        usename,
                        application_name
                    FROM pg_stat_activity 
                    WHERE state != 'idle' 
                        AND now() - pg_stat_activity.query_start > interval '30 seconds'
                        AND query NOT LIKE '%pg_stat_activity%'
                    ORDER BY duration DESC
                    LIMIT 10
                """))
                
                return [{
                    "pid": row.pid,
                    "duration_seconds": row.duration.total_seconds(),
                    "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                    "state": row.state,
                    "user": row.usename,
                    "application": row.application_name
                } for row in result]
                
        except Exception as e:
            logger.error(f"Failed to check long-running queries: {e}")
            return []
    
    def check_table_growth(self) -> dict:
        """Check table growth patterns"""
        try:
            from src.database.config import get_db_session
            from sqlalchemy import text
            
            with get_db_session() as db:
                # Get current table sizes
                result = db.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_rows,
                        n_dead_tup as dead_rows,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """))
                
                tables = []
                for row in result:
                    tables.append({
                        "table": f"{row.schemaname}.{row.tablename}",
                        "live_rows": row.live_rows,
                        "dead_rows": row.dead_rows,
                        "dead_row_ratio": (row.dead_rows / max(row.live_rows, 1)) * 100,
                        "last_vacuum": row.last_vacuum.isoformat() if row.last_vacuum else None,
                        "last_analyze": row.last_analyze.isoformat() if row.last_analyze else None,
                        "needs_vacuum": row.dead_rows > 1000 and (row.dead_rows / max(row.live_rows, 1)) > 0.1
                    })
                
                return {"tables": tables}
                
        except Exception as e:
            logger.error(f"Failed to check table growth: {e}")
            return {"error": str(e)}
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate comprehensive monitoring report"""
        logger.info("Generating database monitoring report...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "database_config": {
                "host": db_config.host,
                "database": db_config.database,
                "pool_size": db_config.pool_size,
                "max_overflow": db_config.max_overflow
            },
            "health_check": self.health_check(),
            "database_stats": get_database_stats(),
            "connection_metrics": get_connection_metrics()
        }
        
        # Convert to JSON
        report_json = json.dumps(report, indent=2, default=str)
        
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(report_json)
            logger.info(f"Report saved to: {output_path}")
        
        return report_json

# ============================================================================
# MAINTENANCE OPERATIONS
# ============================================================================

class DatabaseMaintenance:
    """Database maintenance operations"""
    
    def run_maintenance(self, tasks: list = None) -> dict:
        """Run maintenance tasks"""
        if tasks is None:
            tasks = ["cleanup_sessions", "cleanup_invites", "vacuum", "analyze"]
        
        logger.info(f"Running maintenance tasks: {', '.join(tasks)}")
        
        results = {}
        
        try:
            if "cleanup_sessions" in tasks:
                results["cleanup_sessions"] = cleanup_expired_sessions()
            
            if "cleanup_invites" in tasks:
                results["cleanup_invites"] = cleanup_expired_invites()
            
            if "vacuum" in tasks:
                results["vacuum"] = vacuum_analyze_tables()
            
            if "analyze" in tasks:
                results["analyze"] = update_table_statistics()
            
            if "reindex" in tasks:
                results["reindex"] = self.reindex_tables()
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Maintenance failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": results
            }
    
    def reindex_tables(self) -> bool:
        """Reindex database tables"""
        try:
            from src.database.config import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                conn = conn.execution_options(autocommit=True)
                conn.execute(text("REINDEX DATABASE threadr"))
                logger.info("Database reindex completed")
                return True
        except Exception as e:
            logger.error(f"Reindex failed: {e}")
            return False

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

async def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(description="Threadr Database Operations")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Database backup operations")
    backup_parser.add_argument("--type", choices=["full", "schema", "data"], default="full")
    backup_parser.add_argument("--dir", default="/backups/threadr", help="Backup directory")
    
    restore_parser = subparsers.add_parser("restore", help="Database restore operations")
    restore_parser.add_argument("backup_file", help="Path to backup file")
    restore_parser.add_argument("--confirm", action="store_true", help="Confirm restore operation")
    
    list_backups_parser = subparsers.add_parser("list-backups", help="List available backups")
    list_backups_parser.add_argument("--dir", default="/backups/threadr", help="Backup directory")
    
    # Monitoring commands
    health_parser = subparsers.add_parser("health", help="Database health check")
    health_parser.add_argument("--output", help="Save report to file")
    
    monitor_parser = subparsers.add_parser("monitor", help="Generate monitoring report")
    monitor_parser.add_argument("--output", help="Save report to file")
    
    # Maintenance commands
    maintenance_parser = subparsers.add_parser("maintenance", help="Run maintenance tasks")
    maintenance_parser.add_argument("--tasks", nargs="+", 
                                  choices=["cleanup_sessions", "cleanup_invites", "vacuum", "analyze", "reindex"],
                                  help="Specific tasks to run")
    
    # Migration commands
    migrate_parser = subparsers.add_parser("migrate", help="Database migration operations")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Run migration in dry-run mode")
    
    validate_parser = subparsers.add_parser("validate", help="Validate database migration")
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.command == "backup":
            backup_manager = DatabaseBackupManager(args.dir)
            result = backup_manager.create_backup(args.type)
            print(json.dumps(result, indent=2))
        
        elif args.command == "restore":
            backup_manager = DatabaseBackupManager()
            result = backup_manager.restore_backup(args.backup_file, args.confirm)
            print(json.dumps(result, indent=2))
        
        elif args.command == "list-backups":
            backup_manager = DatabaseBackupManager(args.dir)
            backups = backup_manager.list_backups()
            print(json.dumps(backups, indent=2))
        
        elif args.command == "health":
            monitor = DatabaseMonitor()
            health = monitor.health_check()
            if args.output:
                Path(args.output).write_text(json.dumps(health, indent=2, default=str))
                print(f"Health report saved to: {args.output}")
            else:
                print(json.dumps(health, indent=2, default=str))
        
        elif args.command == "monitor":
            monitor = DatabaseMonitor()
            report = monitor.generate_report(args.output)
            if not args.output:
                print(report)
        
        elif args.command == "maintenance":
            maintenance = DatabaseMaintenance()
            result = maintenance.run_maintenance(args.tasks)
            print(json.dumps(result, indent=2, default=str))
        
        elif args.command == "migrate":
            result = await run_full_migration(args.dry_run)
            print(json.dumps(result, indent=2, default=str))
        
        elif args.command == "validate":
            result = validate_migration()
            print(json.dumps(result, indent=2, default=str))
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())