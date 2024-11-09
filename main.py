#!/usr/bin/env python
import click
import mysql.connector
from mysql.connector import Error
import json
import os
from datetime import datetime
import shutil
from typing import List
from tabulate import tabulate

class DatabaseManager:
    def __init__(self, config_path='.mydb/config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self.connection = None
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            default_config = {
                'current_branch': 'main',
                'branches': {
                    'main': {
                        'created_at': datetime.now().isoformat(),
                        'last_accessed': datetime.now().isoformat()
                    }
                },
                'connection': {
                    'user': 'root',
                    'password': 'B#@w@+123',
                    'host': 'localhost',
                    'port': 3306,
                    'database': 'mydb',
                    'auth_plugin': 'mysql_native_password'  # Add this line
                }
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            # Ensure auth_plugin is set in existing configs
            if 'auth_plugin' not in config['connection']:
                config['connection']['auth_plugin'] = 'mysql_native_password'
                with open(self.config_path, 'w') as f:
                    json.dump(config, f, indent=4)
            return config

    def _save_config(self):
        """Save current configuration to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config['connection'])
            return self.connection.is_connected()
        except Error as e:
            click.echo(f"Error connecting to database: {e}")
            return False

    def create_branch(self, branch_name):
        """Create a new branch from current branch"""
        if branch_name in self.config['branches']:
            click.echo(f"Branch '{branch_name}' already exists!")
            return False

        try:
            # Connect to database
            if not self.connect():
                return False

            cursor = self.connection.cursor()
        
            # Get current branch name
            current_branch = self.config['current_branch']
        
            # Create new database for branch
            new_db_name = f"{self.config['connection']['database']}_{branch_name}"
            cursor.execute(f"CREATE DATABASE {new_db_name}")

            # If this is not the main branch, copy data from current branch
            if current_branch == 'main' and branch_name != 'main':
                # For main branch, just create the database
                pass
            else:
                # Copy from current branch
                current_db_name = f"{self.config['connection']['database']}_{current_branch}"
                cursor.execute(f"SHOW TABLES FROM {current_db_name}")
                tables = cursor.fetchall()
            
                # Copy schema and data
                for (table_name,) in tables:
                    cursor.execute(f"CREATE TABLE {new_db_name}.{table_name} LIKE {current_db_name}.{table_name}")
                    cursor.execute(f"INSERT INTO {new_db_name}.{table_name} SELECT * FROM {current_db_name}.{table_name}")

            # Update config
            self.config['branches'][branch_name] = {
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'created_from': current_branch
            }
            self._save_config()

            self.create_schema_migrations_table(branch_name)
            click.echo(f"Initialized schema_migrations table in branch '{branch_name}'")
        
            click.echo(f"Successfully created branch '{branch_name}' from '{current_branch}'")
            return True

        except Error as e:
            click.echo(f"Error creating branch: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def switch_branch(self, branch_name):
        """Switch to a different branch"""
        if branch_name not in self.config['branches']:
            click.echo(f"Branch '{branch_name}' does not exist!")
            return False

        try:
            # Update current branch
            self.config['current_branch'] = branch_name
            self.config['branches'][branch_name]['last_accessed'] = datetime.now().isoformat()
            self._save_config()
            
            click.echo(f"Switched to branch '{branch_name}'")
            return True

        except Exception as e:
            click.echo(f"Error switching branch: {e}")
            return False

    def delete_branch(self, branch_name):
        """Delete a branch"""
        if branch_name not in self.config['branches']:
            click.echo(f"Branch '{branch_name}' does not exist!")
            return False

        if branch_name == 'main':
            click.echo("Cannot delete 'main' branch!")
            return False

        if branch_name == self.config['current_branch']:
            click.echo("Cannot delete current branch!")
            return False

        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            
            # Drop the branch database
            db_name = f"{self.config['connection']['database']}_{branch_name}"
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            
            # Remove branch from config
            del self.config['branches'][branch_name]
            self._save_config()
            
            click.echo(f"Successfully deleted branch '{branch_name}'")
            return True

        except Error as e:
            click.echo(f"Error deleting branch: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def list_branches(self):
        """List all branches"""
        click.echo("\nAvailable branches:")
        click.echo("================")
        
        for branch_name, branch_info in self.config['branches'].items():
            current = "*" if branch_name == self.config['current_branch'] else " "
            created_at = datetime.fromisoformat(branch_info['created_at']).strftime("%Y-%m-%d %H:%M:%S")
            click.echo(f"{current} {branch_name} (created: {created_at})")

    def create_table(self, table_name: str, columns: List[str]):
        """Create a new table in the current branch"""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            current_branch = self.config['current_branch']
        
            # Determine the appropriate database name
            if current_branch == 'main':
                current_db = self.config['connection']['database']  # Use 'mydb'
            else:
                current_db = f"{self.config['connection']['database']}_{current_branch}"  # e.g., 'mydb_nimish'

            # Use the appropriate database
            cursor.execute(f"USE {current_db}")
        
            # Create the table with the provided columns
            create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
            cursor.execute(create_table_sql)
        
            click.echo(f"Successfully created table '{table_name}' in branch '{current_branch}'")
            return True

        except Error as e:
            click.echo(f"Error creating table: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def list_tables(self):
        """List all tables in the current branch"""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            current_branch = self.config['current_branch']
            
            if current_branch == 'main':
                current_db = self.config['connection']['database']  # Use 'mydb'
            else:
                current_db = f"{self.config['connection']['database']}_{current_branch}"  # e.g., 'mydb_nimish'
            
            cursor.execute(f"USE {current_db}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
        
            if not tables:
                click.echo(f"No tables found in branch '{current_branch}'")
                return True

            # Get table information
            table_info = []
            for (table_name,) in tables:
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_stmt = cursor.fetchone()[1]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                table_info.append([table_name, row_count])

            # Display tables in a nice format
            click.echo(f"\nTables in branch '{current_branch}':")
            click.echo(tabulate(table_info, headers=['Table Name', 'Row Count'], tablefmt='grid'))
            return True

        except Error as e:
            click.echo(f"Error listing tables: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def describe_table(self, table_name: str):
        """Show detailed information about a specific table"""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            current_branch = self.config['current_branch']
            
            if current_branch == 'main':
                current_db = self.config['connection']['database']  # Use 'mydb'
            else:
                current_db = f"{self.config['connection']['database']}_{current_branch}"  # e.g., 'mydb_nimish'
            
            # Switch to current database
            cursor.execute(f"USE {current_db}")
        
            # Get table description
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
        
            if not columns:
                click.echo(f"Table '{table_name}' not found in branch '{current_branch}'")
                return False

            # Display table structure
            column_info = [[col[0], col[1], col[2], col[3], col[4], col[5]] for col in columns]
            headers = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
            click.echo(f"\nStructure of table '{table_name}':")
            click.echo(tabulate(column_info, headers=headers, tablefmt='grid'))
            return True

        except Error as e:
            click.echo(f"Error describing table: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def drop_table(self, table_name: str):
        """Drop a table from the current branch"""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            current_branch = self.config['current_branch']

            if current_branch == 'main':
                current_db = self.config['connection']['database']  # Use 'mydb'
            else:
                current_db = f"{self.config['connection']['database']}_{current_branch}"  # e.g., 'mydb_nimish'
            
            # Switch to current database
            cursor.execute(f"USE {current_db}")
        
            # Drop the table
            cursor.execute(f"DROP TABLE {table_name}")
            click.echo(f"Successfully dropped table '{table_name}' from branch '{current_branch}'")
            return True

        except Error as e:
            click.echo(f"Error dropping table: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def _init_branch_migrations(self, branch_name):
        """Initialize migrations directory structure for a branch"""
        branch_migrations_dir = f"migrations/{branch_name}"
        os.makedirs(branch_migrations_dir, exist_ok=True)
        return branch_migrations_dir

    def create_schema_migrations_table(self, branch_name=None):
        """Create branch-specific schema_migrations table with proper structure."""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            branch = branch_name or self.config['current_branch']
        
            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
        
            cursor.execute(f"USE {db_name}")

            # Drop existing table if it exists to ensure correct structure
            cursor.execute("DROP TABLE IF EXISTS schema_migrations")

            # Create schema_migrations table with corrected structure
            cursor.execute("""
                CREATE TABLE schema_migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    migration_number INT NOT NULL,
                    migration_name VARCHAR(255),
                    description TEXT,
                    branch_name VARCHAR(255) NOT NULL,
                    parent_branch VARCHAR(255),
                    parent_migration_number INT,
                    status ENUM('pending', 'applied', 'failed', 'rolled_back') DEFAULT 'pending',
                    applied_at TIMESTAMP NULL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_migration (migration_number, branch_name)
                )
            """)
        
            self.connection.commit()
            click.echo(f"Successfully created schema_migrations table in database '{db_name}'")
            return True
        
        except Error as e:
            click.echo(f"Error creating schema_migrations table: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def get_next_migration_number(self, branch_name=None):
        """Get the next migration number for a specific branch."""
        branch = branch_name or self.config['current_branch']
    
        # Set branch-specific migrations directory
        branch_migrations_dir = f"migrations/{branch}"
    
        # Ensure the directory exists
        if not os.path.exists(branch_migrations_dir):
            os.makedirs(branch_migrations_dir, exist_ok=True)
            return 0  # Start at 0000 if no migrations exist for the branch

        # List all migration folders and find the highest number
        existing_migrations = [
            d for d in os.listdir(branch_migrations_dir) if os.path.isdir(os.path.join(branch_migrations_dir, d))
        ]
    
        if not existing_migrations:
            return 0  # Start at 0000 if no migrations exist
    
        # Extract migration numbers from folder names and find the highest one
        migration_numbers = [
            int(m.split('_')[0]) for m in existing_migrations if m.split('_')[0].isdigit()
        ]
        next_number = max(migration_numbers) + 1 if migration_numbers else 0

        return next_number

    def create_migration(self, name, description=None):
        """Create a new migration for the current branch."""
        try:
            branch = self.config['current_branch']
            migration_number = self.get_next_migration_number(branch)
        
            if migration_number is None:
                return False

            # Get branch-specific migration directory
            branch_dir = self._init_branch_migrations(branch)
            migration_dir = f"{branch_dir}/{migration_number:04d}_{name}"
            os.makedirs(migration_dir, exist_ok=True)

            # Create migration files
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
            # Create up.sql with header
            with open(f"{migration_dir}/up.sql", "w") as f:
                f.write(f"-- Migration: {name}\n")
                f.write(f"-- Created at: {timestamp}\n")
                f.write(f"-- Branch: {branch}\n")
                f.write("-- Up Migration\n\n")

            # Create down.sql with header
            with open(f"{migration_dir}/down.sql", "w") as f:
                f.write(f"-- Migration: {name}\n")
                f.write(f"-- Created at: {timestamp}\n")
                f.write(f"-- Branch: {branch}\n")
                f.write("-- Down Migration\n\n")

            # Get parent branch information
            parent_branch = self.config['branches'][branch].get('created_from')
            parent_migration_number = self._get_parent_branch_migration_number(branch)

            # Create metadata.json
            metadata = {
                "migration_number": migration_number,
                "name": name,
                "description": description,
                "branch": branch,
                "created_at": timestamp,
                "parent_branch": parent_branch,
                "parent_migration_number": parent_migration_number
            }
        
            with open(f"{migration_dir}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=4)

            # Insert migration record into schema_migrations table
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
            cursor.execute(f"USE {db_name}")

            # Insert migration record with branch information
            cursor.execute("""
            INSERT INTO schema_migrations (
                migration_number, migration_name, branch_name, 
                parent_branch, parent_migration_number, status, applied_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (migration_number, name, branch, parent_branch, parent_migration_number, 'pending', None))

            self.connection.commit()
            click.echo(f"Created migration {migration_number:04d}_{name} in branch '{branch}'")
            return True

        except Exception as e:
            click.echo(f"Error creating migration: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def apply_migration(self, migration_number=None, branch_name=None):
        try:
            # Establish connection or reconnect if needed
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            branch = branch_name or self.config['current_branch']

            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"

            # Explicitly check and reconnect if needed
            if not self.connection.is_connected():
                click.echo("Reconnecting to the database...")
                self.connection.reconnect(attempts=3, delay=2)
                cursor = self.connection.cursor()  # Create a new cursor after reconnect

            cursor.execute(f"USE {db_name}")

            # Fetch the next pending migration if not specified
            if migration_number is None:
                cursor.execute("""
                    SELECT migration_number, migration_name
                    FROM schema_migrations
                    WHERE branch_name = %s AND status = 'pending'
                    ORDER BY migration_number ASC LIMIT 1
                """, (branch,))
                result = cursor.fetchone()

                if not result:
                    click.echo(f"No pending migrations for branch '{branch}'")
                    return True

                migration_number, migration_name = result
                click.echo(f"Applying migration {migration_number:04d}_{migration_name}")

            # Load migration files
            migration_files = self._get_migration_files(branch, migration_number)
            if not migration_files:
                return False

            cursor.execute("START TRANSACTION")

            # Apply up migration
            with open(migration_files['up'], 'r') as f:
                sql = f.read()
                if sql.strip():
                    for statement in sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)

            # Update migration status
            cursor.execute("""
                UPDATE schema_migrations
                SET status = 'applied', applied_at = CURRENT_TIMESTAMP
                WHERE migration_number = %s AND branch_name = %s
            """, (migration_number, branch))

            cursor.execute("COMMIT")
            click.echo(f"Successfully applied migration {migration_number:04d} in branch '{branch}'")
            return True

        except Error as e:
            cursor.execute("ROLLBACK")
            cursor.execute("""
                UPDATE schema_migrations
                SET status = 'failed', error_message = %s
                WHERE migration_number = %s AND branch_name = %s
            """, (str(e), migration_number, branch))
            click.echo(f"Error applying migration {migration_number:04d}: {e}")
            return False

        finally:
            if cursor:
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def _get_migration_files(self, branch, migration_number):
        """Get migration files for a specific branch and migration number."""
        branch_dir = f"migrations/{branch}"
        if not os.path.exists(branch_dir):
            click.echo(f"No migrations directory for branch '{branch}'")
            return None

        # Find migration directory (accounts for named migrations)
        migration_dirs = [d for d in os.listdir(branch_dir) 
                        if d.startswith(f"{migration_number:04d}_")]
        
        if not migration_dirs:
            click.echo(f"Migration {migration_number:04d} not found in branch '{branch}'")
            return None

        migration_dir = f"{branch_dir}/{migration_dirs[0]}"
        return {
            'up': f"{migration_dir}/up.sql",
            'down': f"{migration_dir}/down.sql",
            'metadata': f"{migration_dir}/metadata.json"
        }

    def migration_status(self, branch_name=None):
        """Get detailed migration status for a branch."""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            branch = branch_name or self.config['current_branch']
            
            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
            
            cursor.execute(f"USE {db_name}")

            # Get all migrations for this branch
            cursor.execute("""
                SELECT migration_number, migration_name, status, 
                       applied_at, error_message 
                FROM schema_migrations 
                WHERE branch_name = %s 
                ORDER BY migration_number ASC
            """, (branch,))
            
            migrations = cursor.fetchall()

            if not migrations:
                click.echo(f"No migrations found for branch '{branch}'")
                return True

            # Display migration status
            headers = ['Number', 'Name', 'Status', 'Applied At', 'Error']
            table_data = [[
                f"{m[0]:04d}",
                m[1] or 'unnamed',
                m[2],
                m[3].strftime('%Y-%m-%d %H:%M:%S') if m[3] else 'N/A',
                (m[4][:50] + '...') if m[4] and len(m[4]) > 50 else (m[4] or 'N/A')
            ] for m in migrations]

            click.echo(f"\nMigration Status for branch '{branch}':")
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
            return True

        except Error as e:
            click.echo(f"Error getting migration status: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def _get_parent_branch_migration_number(self, branch):
        """Get the last migration number from parent branch when this branch was created."""
        try:
            parent_branch = self.config['branches'][branch].get('created_from')
            if not parent_branch:
                return 0

            if not self.connect():
                return 0

            cursor = self.connection.cursor()
            
            # Use parent branch database
            db_name = self.config['connection']['database']
            if parent_branch != 'main':
                db_name = f"{db_name}_{parent_branch}"
            
            cursor.execute(f"USE {db_name}")

            # Get last successful migration before branch creation time
            branch_created_at = datetime.fromisoformat(
                self.config['branches'][branch]['created_at']
            )
            
            cursor.execute("""
                SELECT MAX(migration_number) 
                FROM schema_migrations 
                WHERE branch_name = %s 
                AND status = 'applied' 
                AND applied_at <= %s
            """, (parent_branch, branch_created_at))
            
            result = cursor.fetchone()
            return result[0] or 0

        except Error as e:
            click.echo(f"Error getting parent branch migration number: {e}")
            return 0
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()
    
    def get_current_migration(self):
        """Get the number of the last applied migration in current branch."""
        try:
            if not self.connect():
                return -1

            cursor = self.connection.cursor()
            branch = self.config['current_branch']
        
            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
        
            cursor.execute(f"USE {db_name}")
        
            # Get the highest applied migration number
            cursor.execute("""
                SELECT MAX(migration_number)
                FROM schema_migrations
                WHERE branch_name = %s AND status = 'applied'
            """, (branch,))
        
            result = cursor.fetchone()
            return result[0] if result[0] is not None else -1

        except Error as e:
            click.echo(f"Error getting current migration: {e}")
            return -1
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def rollback_migration(self, migration_number):
        """Rollback a specific migration."""
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            branch = self.config['current_branch']
        
            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
        
            cursor.execute(f"USE {db_name}")
        
            # Check if migration exists and is applied
            cursor.execute("""
                SELECT status
                FROM schema_migrations
                WHERE migration_number = %s AND branch_name = %s
            """, (migration_number, branch))
        
            result = cursor.fetchone()
            if not result or result[0] != 'applied':
                click.echo(f"Migration {migration_number:04d} is not applied or doesn't exist")
                return False
        
            # Get migration files
            migration_files = self._get_migration_files(branch, migration_number)
            if not migration_files:
                return False
        
            cursor.execute("START TRANSACTION")
        
            # Apply down migration
            with open(migration_files['down'], 'r') as f:
                sql = f.read()
                if sql.strip():
                    for statement in sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
        
            # Update migration status
            cursor.execute("""
                UPDATE schema_migrations
                SET status = 'rolled_back', 
                    applied_at = NULL
                WHERE migration_number = %s AND branch_name = %s
            """, (migration_number, branch))
        
            cursor.execute("COMMIT")
            click.echo(f"Successfully rolled back migration {migration_number:04d}")
            return True

        except Error as e:
            cursor.execute("ROLLBACK")
            click.echo(f"Error rolling back migration: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def _get_parent_branch_pending_migrations(self, branch):
        """
        Get pending migrations from source branch that need to be applied to current branch.
        This considers the branch ancestry and ensures proper migration ordering.
    
        Args:
            branch (str): Source branch name to check migrations from
    
        Returns:
            list: List of tuples (migration_number, migration_name) that need to be applied
        """
        try:
            if not self.connect():
                return []

            cursor = self.connection.cursor()
        
            # Get branch creation timestamps and parent information
            source_created_at = datetime.fromisoformat(self.config['branches'][branch]['created_at'])
            target_branch = self.config['current_branch']
            target_created_at = datetime.fromisoformat(self.config['branches'][target_branch]['created_at'])
        
            # Determine common ancestor
            source_lineage = self._get_branch_lineage(branch)
            target_lineage = self._get_branch_lineage(target_branch)
            common_ancestor = None
        
            for ancestor in source_lineage:
                if ancestor in target_lineage:
                    common_ancestor = ancestor
                    break
                
            if not common_ancestor:
                click.echo("No common ancestor found between branches")
                return []
            
            # Get migrations from source branch after common ancestor
            source_db = (self.config['connection']['database'] if branch == 'main' 
                        else f"{self.config['connection']['database']}_{branch}")
            cursor.execute(f"USE {source_db}")
        
            # Get all applied migrations from source branch after the common point
            cursor.execute("""
                SELECT m1.migration_number, m1.migration_name
                FROM schema_migrations m1
                WHERE m1.branch_name = %s 
                AND m1.status = 'applied'
                AND m1.migration_number > (
                    SELECT COALESCE(MAX(migration_number), -1)
                    FROM schema_migrations
                    WHERE branch_name = %s
                    AND status = 'applied'
                    AND applied_at <= %s
                )
                ORDER BY m1.migration_number ASC
            """, (branch, common_ancestor, source_created_at))
        
            source_migrations = cursor.fetchall()
        
            # Get target branch migrations
            target_db = (self.config['connection']['database'] if target_branch == 'main' 
                        else f"{self.config['connection']['database']}_{target_branch}")
            cursor.execute(f"USE {target_db}")
        
            # Get already applied migrations in target branch
            cursor.execute("""
                SELECT migration_number 
                FROM schema_migrations 
                WHERE branch_name = %s 
                AND status = 'applied'
            """, (target_branch,))
        
            applied_in_target = {row[0] for row in cursor.fetchall()}
        
            # Filter out migrations that are already applied in target
            pending_migrations = [
                (num, name) for num, name in source_migrations 
                if num not in applied_in_target
            ]
        
            return pending_migrations

        except Error as e:
            click.echo(f"Error checking source branch migrations: {e}")
            return []
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def _get_branch_lineage(self, branch_name):
        """
        Get the complete lineage of a branch back to main.
    
        Args:
            branch_name (str): Name of the branch to trace
        
        Returns:
            list: List of branch names representing the lineage back to main
        """
        lineage = [branch_name]
        current = branch_name
    
        while current in self.config['branches']:
            parent = self.config['branches'][current].get('created_from')
            if not parent or parent == current:
                break
            lineage.append(parent)
            current = parent
    
        return lineage

    def merge_branch(self, source_branch, target_branch):
        """
        Merge complete contents (schema + data) from source_branch into target_branch.
        Args:
            source_branch (str): Name of the branch to merge from
            target_branch (str): Name of the branch to merge into
        Returns:
            bool: True if merge was successful, False otherwise
        """
        if source_branch not in self.config['branches']:
            click.echo(f"Source branch '{source_branch}' does not exist!")
            return False
        if target_branch not in self.config['branches']:
            click.echo(f"Target branch '{target_branch}' does not exist!")
            return False
        if source_branch == target_branch:
            click.echo("Cannot merge a branch into itself!")
            return False

        try:
            if not self.connect():
                click.echo("Failed to connect to the database.")
                return False

            cursor = self.connection.cursor()

            # Use source branch database
            source_db = self.config['connection']['database']
            if source_branch != 'main':
                source_db = f"{source_db}_{source_branch}"

            # Use target branch database
            target_db = self.config['connection']['database']
            if target_branch != 'main':
                target_db = f"{target_db}_{target_branch}"

            # Switch to source database
            cursor.execute(f"USE {source_db}")

            # Get all tables from the source branch
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

            if not tables:
                click.echo(f"No tables found in source branch '{source_branch}' to merge.")
                return True

            click.echo(f"Found {len(tables)} tables to merge.")

            # Switch to target database
            cursor.execute(f"USE {target_db}")

            # Start merging tables
            for table in tables:
                click.echo(f"Merging table '{table}'...")

                # Ensure table exists in target; if not, create it
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not cursor.fetchone():
                    # Table does not exist in target, copy schema from source
                    cursor.execute(f"CREATE TABLE {target_db}.{table} LIKE {source_db}.{table}")

                # Copy data using INSERT ... ON DUPLICATE KEY UPDATE for merging
                columns_query = f"SHOW COLUMNS FROM {source_db}.{table}"
                cursor.execute(columns_query)
                columns = [col[0] for col in cursor.fetchall()]
                columns_str = ", ".join(columns)

                # Construct ON DUPLICATE KEY UPDATE part
                update_str = ", ".join([f"{col}=VALUES({col})" for col in columns])

                merge_query = f"""
                    INSERT INTO {target_db}.{table} ({columns_str})
                    SELECT {columns_str} FROM {source_db}.{table}
                    ON DUPLICATE KEY UPDATE {update_str}
                """
                cursor.execute(merge_query)

            self.connection.commit()
            click.echo(f"Successfully merged contents of '{source_branch}' into '{target_branch}'")
            return True

        except Error as e:
            click.echo(f"Error during merge: {e}")
            self.connection.rollback()
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

@click.group()
def cli():
    """mydb-cli: A tool to manage your MySQL database with branching functionality."""
    pass

@cli.command()
def status():
    """Check the status of the database connection and current branch."""
    db_manager = DatabaseManager()
    if db_manager.connect():
        click.echo("Database connection is active!")
        click.echo(f"Current branch: {db_manager.config['current_branch']}")
    else:
        click.echo("Failed to connect to the database.")

@cli.command()
@click.option("--branch", prompt="Branch name", help="The name of the new branch to create.")
def create_branch(branch):
    """Create a new database branch."""
    db_manager = DatabaseManager()
    db_manager.create_branch(branch)

@cli.command()
@click.option("--branch", prompt="Branch name", help="The branch to switch to.")
def switch_branch(branch):
    """Switch to a different database branch."""
    db_manager = DatabaseManager()
    db_manager.switch_branch(branch)

@cli.command()
@click.option("--branch", prompt="Branch name", help="The branch to delete.")
def delete_branch(branch):
    """Delete a database branch."""
    db_manager = DatabaseManager()
    db_manager.delete_branch(branch)

@cli.command()
def list_branches():
    """List all available branches."""
    db_manager = DatabaseManager()
    db_manager.list_branches()

@cli.command()
@click.option("--name", prompt="Table name", help="The name of the table to create")
def create_table(name):
    """Create a new table in the current branch."""
    columns = []
    click.echo("Enter column definitions (press Enter twice to finish):")
    click.echo("Format: column_name datatype [constraints]")
    click.echo("Example: id INT PRIMARY KEY AUTO_INCREMENT")
    
    while True:
        column = click.prompt("Column definition", default="", show_default=False)
        if not column:
            if columns:
                break
            click.echo("Please enter at least one column!")
            continue
        columns.append(column)
    
    db_manager = DatabaseManager()
    db_manager.create_table(name, columns)

@cli.command()
def list_tables():
    """List all tables in the current branch."""
    db_manager = DatabaseManager()
    db_manager.list_tables()

@cli.command()
@click.option("--name", prompt="Table name", help="The name of the table to describe")
def describe_table(name):
    """Show detailed information about a specific table."""
    db_manager = DatabaseManager()
    db_manager.describe_table(name)

@cli.command()
@click.option("--name", prompt="Table name", help="The name of the table to drop")
@click.confirmation_option(prompt="Are you sure you want to drop this table?")
def drop_table(name):
    """Drop a table from the current branch."""
    db_manager = DatabaseManager()
    db_manager.drop_table(name)

@cli.command()
def migrate_up():
    """Apply the next pending migration."""
    db_manager = DatabaseManager()
    if not db_manager.connect():
        return

    current_migration = db_manager.get_current_migration()
    next_migration = current_migration + 1
    if db_manager.apply_migration(next_migration):
        click.echo(f"Migration {next_migration:04d} applied successfully.")
    else:
        click.echo(f"Failed to apply migration {next_migration:04d}.")

@cli.command()
def migrate_down():
    """Rollback the last applied migration."""
    db_manager = DatabaseManager()
    if not db_manager.connect():
        return

    current_migration = db_manager.get_current_migration()
    if current_migration > 0:
        if db_manager.rollback_migration(current_migration):
            click.echo(f"Migration {current_migration:04d} rolled back successfully.")
        else:
            click.echo(f"Failed to rollback migration {current_migration:04d}.")
    else:
        click.echo("No migrations to roll back.")

@cli.command()
@click.option("--name", prompt="Migration name", help="Name of the migration")
@click.option("--description", help="Optional description of the migration")
def create_migration(name, description):
    """Create a new migration for the current branch."""
    db_manager = DatabaseManager()
    db_manager.create_migration(name, description)

@cli.command()
@click.option("--number", type=int, help="Specific migration number to apply")
def apply_migration(number):
    """Apply a specific or next pending migration."""
    db_manager = DatabaseManager()
    db_manager.apply_migration(migration_number=number)

@cli.command()
def migration_status():
    """Show status of all migrations in current branch."""
    db_manager = DatabaseManager()
    db_manager.migration_status()

@cli.command()
@click.option("--source", prompt="Source branch name", help="The branch to merge from.")
@click.option("--target", prompt="Target branch name", help="The branch to merge into.")
def merge_branch(source, target):
    """Merge changes from source branch into target branch."""
    db_manager = DatabaseManager()
    db_manager.merge_branch(source, target)

@cli.command()
def studio():
    """Launch the MyDB Studio GUI interface."""
    try:
        import streamlit
        os.system(f"streamlit run studio.py")
    except ImportError:
        click.echo("Streamlit is required to run the studio. Install it with: pip install streamlit")

if __name__ == '__main__':
    cli()