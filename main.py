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
import csv
from history_manager import HistoryManager
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class MigrationManager:
    def __init__(self, config_path='.mydb/migrations.json'):
        self.config_path = config_path
        self.migrations = self._load_migrations()

    def _load_migrations(self):
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            return {}
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _save_migrations(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.migrations, f, indent=4)

    def create_migration(self, name, description, branch):
        migration_number = self._get_next_migration_number(branch)
        timestamp = datetime.now().isoformat()
        
        migration = {
            "number": migration_number,
            "name": name,
            "description": description,
            "branch": branch,
            "status": "pending",
            "created_at": timestamp,
            "applied_at": None
        }

        if branch not in self.migrations:
            self.migrations[branch] = []
        self.migrations[branch].append(migration)
        self._save_migrations()

        return migration_number

    def _get_next_migration_number(self, branch):
        if branch not in self.migrations or not self.migrations[branch]:
            return 1
        return max(m["number"] for m in self.migrations[branch]) + 1

    def apply_migration(self, migration_number, branch):
        for migration in self.migrations.get(branch, []):
            if migration["number"] == migration_number:
                migration["status"] = "applied"
                migration["applied_at"] = datetime.now().isoformat()
                self._save_migrations()
                return True
        return False

    def rollback_migration(self, migration_number, branch):
        for migration in self.migrations.get(branch, []):
            if migration["number"] == migration_number:
                migration["status"] = "rolled_back"
                migration["applied_at"] = None
                self._save_migrations()
                return True
        return False

    def get_migration_status(self, branch):
        return self.migrations.get(branch, [])

    def get_current_migration(self, branch):
        applied_migrations = [m for m in self.migrations.get(branch, []) if m["status"] == "applied"]
        if not applied_migrations:
            return -1
        return max(m["number"] for m in applied_migrations)


class DatabaseManager:
    def __init__(self, config_path='.mydb/config.json', config=None):
        self.config_path = config_path
        self.config = config or self._load_config()
        self.connection = None
        self.history_manager = HistoryManager()
        self.migration_manager = MigrationManager()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            return self._create_default_config()
    
        with open(self.config_path, 'r') as f:
            config = json.load(f)
    
        if not config or 'connection' not in config:
            return self._create_default_config()
    
        # Ensure auth_plugin is set in existing configs
        if 'auth_plugin' not in config['connection']:
            config['connection']['auth_plugin'] = 'mysql_native_password'
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
    
        return config

    def _create_default_config(self):
        """Create and save a default configuration"""
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
                'auth_plugin': 'mysql_native_password'
            }
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

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

    def see_databases(self):
        """List all configured databases."""
        databases = self.config.get('databases', {})
        if not databases:
            click.echo("No databases configured.")
            return

        headers = ['Name', 'Host', 'Database']
        data = [[name, db['host'], db['database']] for name, db in databases.items()]
        click.echo(tabulate(data, headers=headers, tablefmt='grid'))

    def connect_database(self, name, host, user, password, database):
        """Connect to a new database."""
        new_config = {
            'connection': {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'auth_plugin': 'mysql_native_password'
            }
        }

        # Test the connection
        temp_manager = DatabaseManager(config=new_config)
        if temp_manager.connect():
            # If connection successful, save the new database configuration
            if 'databases' not in self.config:
                self.config['databases'] = {}
            self.config['databases'][name] = new_config['connection']
            self._save_config()
            click.echo(f"Successfully connected and saved database '{name}'.")
        else:
            click.echo("Failed to connect to the database. Configuration not saved.")

    def reach_home(self):
        """Connect back to the default mydb database."""
        home_config = self.config['databases'].get('mydb')
        if home_config:
            self.config['connection'] = home_config
            self._save_config()
            if self.connect():
                click.echo("Successfully connected back to mydb database.")
            else:
                click.echo("Failed to connect to mydb database.")
        else:
            click.echo("Default mydb database not configured.")

    def create_branch(self, branch_name):
        """Create a new branch from current branch"""
        # add history code snippet 1 
        if branch_name in self.config['branches']:
            self.history_manager.add_entry(
                command='create_branch',
                details=f"Failed to create branch '{branch_name}' - branch already exists",
                status='failed'
            )
            click.echo(f"Branch '{branch_name}' already exists!")
            return False

        try:
            # Connect to database
            if not self.connect():
                return False

            cursor = self.connection.cursor()
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
                    if isinstance(table_name, bytearray):
                        table_name = table_name.decode('utf-8')
                    cursor.execute(f"CREATE TABLE {new_db_name}.{table_name} LIKE {current_db_name}.{table_name}")
                    cursor.execute(f"INSERT INTO {new_db_name}.{table_name} SELECT * FROM {current_db_name}.{table_name}")

            # Update config
            self.config['branches'][branch_name] = {
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'created_from': current_branch
            }
            self._save_config()

            # self.create_schema_migrations_table(branch_name)
            # click.echo(f"Initialized schema_migrations table in branch '{branch_name}'")
        
            click.echo(f"Successfully created branch '{branch_name}' from '{current_branch}'")
        
            # Record successful branch creation
            # add history code snippet 2
            self.history_manager.add_entry(
                command='create_branch',
                details=f"Successfully created branch '{branch_name}' from '{current_branch}'",
                status='success'
            )
            return True

        except Error as e:
            # Record failed branch creation
            # add history code snippet 3
            self.history_manager.add_entry(
                command='create_branch',
                details=f"Failed to create branch '{branch_name}' - {str(e)}",
                status='failed'
            )
            click.echo(f"Error creating branch: {e}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def switch_branch(self, branch_name):
        """Switch to a different branch"""
        if branch_name not in self.config['branches']:
            self.history_manager.add_entry(
                command='switch_branch',
                details=f"Failed to switch branch '{branch_name}' - branch does not exist",
                status='failed'
            )
            click.echo(f"Branch '{branch_name}' does not exist!")
            return False

        try:
            # Update current branch
            self.config['current_branch'] = branch_name
            self.config['branches'][branch_name]['last_accessed'] = datetime.now().isoformat()
            self._save_config()
            
            click.echo(f"Switched to branch '{branch_name}'")
            self.history_manager.add_entry(
                command='switch_branch',
                details=f"Successfully switched to branch '{branch_name}'",
                status='success'
            )
            return True

        except Exception as e:
            self.history_manager.add_entry(
                command='switch_branch',
                details=f"Failed to switch branch '{branch_name}' - {str(e)}",
                status='failed'
            )
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
            for table_row in tables:
                # Convert byte string to regular string if necessary
                table_name = table_row[0]
                if isinstance(table_name, bytes):
                    table_name = table_name.decode('utf-8')
                elif isinstance(table_name, bytearray):
                    table_name = table_name.decode('utf-8')
            
                # Use proper quoting for table names
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_stmt = cursor.fetchone()[1]
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
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

    def describe_table(self, table_name):
        """Show detailed information about a specific table"""
        try:
            if not self.connect():
                return None

            cursor = self.connection.cursor()
            current_branch = self.config['current_branch']
        
            # Get correct database name
            db_name = self.config['connection']['database']
            if current_branch != 'main':
                db_name = f"{db_name}_{current_branch}"
        
            # Switch to current database
            cursor.execute(f"USE `{db_name}`")
        
            # Get table description
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
        
            if not columns:
                return None

            # Format the results
            column_info = []
            for col in columns:
                column_info.append({
                    'Field': col[0],
                    'Type': col[1],
                    'Null': col[2],
                    'Key': col[3],
                    'Default': col[4],
                    'Extra': col[5]
                })

            return pd.DataFrame(column_info)

        except Error as e:
            print(f"Error describing table: {e}")
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if self.connection and self.connection.is_connected():
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
    
            # Create up.sql and down.sql files
            for file_name in ['up.sql', 'down.sql']:
                with open(f"{migration_dir}/{file_name}", "w") as f:
                    f.write(f"-- Migration: {name}\n")
                    f.write(f"-- Created at: {datetime.now().isoformat()}\n")
                    f.write(f"-- Branch: {branch}\n")
                    f.write(f"-- {file_name.split('.')[0].capitalize()} Migration\n\n")

            # Get parent branch information
            parent_branch = self.config['branches'][branch].get('created_from')
            parent_migration_number = self._get_parent_branch_migration_number(branch)

            # Create metadata for JSON
            migration_data = {
                "migration_number": migration_number,
                "name": name,
                "description": description,
                "branch": branch,
                "created_at": timestamp,
                "parent_branch": parent_branch,
                "parent_migration_number": parent_migration_number,
                "status": "pending",
                "applied_at": None
            }

            # Save metadata to JSON file
            if branch not in self.migration_manager.migrations:
                self.migration_manager.migrations[branch] = []
            self.migration_manager.migrations[branch].append(migration_data)
            self.migration_manager._save_migrations()

            # Create metadata.json in migration directory (for backwards compatibility)
            with open(f"{migration_dir}/metadata.json", "w") as f:
                json.dump(migration_data, f, indent=4)

            click.echo(f"Created migration {migration_number:04d}_{name} in branch '{branch}'")
            return True

        except Exception as e:
            click.echo(f"Error creating migration: {e}")
            return False

    def apply_migration(self, migration_number=None, branch_name=None):
        try:
            if not self.connect():
                return False, []

            cursor = self.connection.cursor()
            branch = branch_name or self.config['current_branch']

            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"

            if not self.connection.is_connected():
                click.echo("Reconnecting to the database...")
                self.connection.reconnect(attempts=3, delay=2)
                cursor = self.connection.cursor()

            cursor.execute(f"USE {db_name}")

            if migration_number is None:
                pending_migrations = [m for m in self.migration_manager.migrations.get(branch, [])
                                      if m['status'] == 'pending']
                if not pending_migrations:
                    click.echo(f"No pending migrations for branch '{branch}'")
                    return True, []

                migration = pending_migrations[0]
                migration_number = migration['migration_number']
                migration_name = migration['name']
                click.echo(f"Applying migration {migration_number:04d}_{migration_name}")

            migration_files = self._get_migration_files(branch, migration_number)
            if not migration_files:
                return False, []

            cursor.execute("START TRANSACTION")

            executed_queries = []
        
            with open(migration_files['up'], 'r') as f:
                sql = f.read()
                if sql.strip():
                    for statement in sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
                            executed_queries.append(statement.strip())

            for migration in self.migration_manager.migrations.get(branch, []):
                if migration['migration_number'] == migration_number:
                    migration['status'] = 'applied'
                    migration['applied_at'] = datetime.now().isoformat()
                    break

            self.migration_manager._save_migrations()

            cursor.execute("COMMIT")
            click.echo(f"Successfully applied migration {migration_number:04d} in branch '{branch}'")
            return True, executed_queries

        except Error as e:
            cursor.execute("ROLLBACK")
            for migration in self.migration_manager.migrations.get(branch, []):
                if migration['migration_number'] == migration_number:
                    migration['status'] = 'failed'
                    migration['error_message'] = str(e)
                    break

            self.migration_manager._save_migrations()
            click.echo(f"Error applying migration {migration_number:04d}: {e}")
            return False, []

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
        """Get detailed migration status for a branch, including current state."""
        try:
            if not self.connect():
                return False, "Failed to connect to the database.", None

            branch = branch_name or self.config['current_branch']
            migrations = self.migration_manager.migrations.get(branch, [])

            if not migrations:
                return True, f"No migrations found for branch '{branch}'", None

            # Get the current migration state
            current_migration = max(
                (m for m in migrations if m['status'] == 'applied'),
                key=lambda x: x['migration_number'],
                default=None
            )

            # Prepare migration data for tabulation
            headers = ['Number', 'Name', 'Status', 'Applied At', 'Error']
            table_data = [[
                f"{m['migration_number']:04d}",
                m['name'] or 'unnamed',
                m['status'],
                m['applied_at'] or 'N/A',
                (m.get('error_message', '')[:50] + '...') if m.get('error_message') and len(m.get('error_message')) > 50 else (m.get('error_message') or 'N/A')
            ] for m in migrations]

            return True, table_data, current_migration

        except Exception as e:
            return False, f"Error getting migration status: {str(e)}", None

    def _get_parent_branch_migration_number(self, branch):
        """Get the last migration number from parent branch when this branch was created."""
        parent_branch = self.config['branches'][branch].get('created_from')
        if not parent_branch:
            return 0

        branch_created_at = datetime.fromisoformat(self.config['branches'][branch]['created_at'])
        parent_migrations = self.migration_manager.migrations.get(parent_branch, [])

        applied_migrations = [
            m for m in parent_migrations
            if m['status'] == 'applied' and datetime.fromisoformat(m['applied_at']) <= branch_created_at
        ]

        if not applied_migrations:
            return 0

        return max(m['migration_number'] for m in applied_migrations)

    def get_current_migration(self):
        """Get the number of the last applied migration in current branch."""
        branch = self.config['current_branch']
        migrations = self.migration_manager.migrations.get(branch, [])

        applied_migrations = [m for m in migrations if m['status'] == 'applied']
        if not applied_migrations:
            return -1

        return max(m['migration_number'] for m in applied_migrations)

    def rollback_migration(self, migration_number):
        """Rollback a specific migration."""
        try:
            branch = self.config['current_branch']
        
            # Check if migration exists and is applied
            migration = next((m for m in self.migration_manager.migrations.get(branch, [])
                            if m['migration_number'] == migration_number), None)
        
            if not migration or migration['status'] != 'applied':
                click.echo(f"Migration {migration_number:04d} is not applied or doesn't exist")
                return False
        
            # Get migration files
            migration_files = self._get_migration_files(branch, migration_number)
            if not migration_files:
                return False
        
            # Connect to the database
            if not self.connect():
                return False

            cursor = self.connection.cursor()
        
            # Use branch-specific database
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
        
            cursor.execute(f"USE {db_name}")
        
            cursor.execute("START TRANSACTION")
        
            try:
                executed_queries = []
            
                # Apply down migration
                with open(migration_files['down'], 'r') as f:
                    sql = f.read()
                    if sql.strip():
                        for statement in sql.split(';'):
                            if statement.strip():
                                cursor.execute(statement)
                                executed_queries.append(statement.strip())
            
                # Update migration status in JSON
                migration['status'] = 'rolled_back'
                migration['applied_at'] = None
                self.migration_manager._save_migrations()
            
                cursor.execute("COMMIT")
                click.echo(f"Successfully rolled back migration {migration_number:04d}")
                return True, executed_queries

            except Error as e:
                cursor.execute("ROLLBACK")
                click.echo(f"Error rolling back migration: {e}")
                return False, []

        except Exception as e:
            click.echo(f"Error during rollback process: {e}")
            return False

        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

    def migrate_up(self):
        current_migration = self.get_current_migration()
        next_migration = current_migration + 1
        return self.apply_migration(next_migration)

    def migrate_down(self):
        current_migration = self.get_current_migration()
        if current_migration > 0:
            # We need to implement a rollback_migration method
            return self.rollback_migration(current_migration)
        else:
            return False, []

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
            # Get branch creation timestamps and parent information
            source_created_at = datetime.fromisoformat(self.config['branches'][branch]['created_at'])
            target_branch = self.config['current_branch']
            target_created_at = datetime.fromisoformat(self.config['branches'][target_branch]['created_at'])

            # Determine common ancestor
            source_lineage = self._get_branch_lineage(branch)
            target_lineage = self._get_branch_lineage(target_branch)
            common_ancestor = next((ancestor for ancestor in source_lineage if ancestor in target_lineage), None)

            if not common_ancestor:
                click.echo("No common ancestor found between branches")
                return []

            # Get migrations from source branch after common ancestor
            source_migrations = self.migration_manager.migrations.get(branch, [])
            common_ancestor_migrations = self.migration_manager.migrations.get(common_ancestor, [])

            # Find the last applied migration in common ancestor before source branch creation
            last_common_migration = max(
                (m for m in common_ancestor_migrations if m['status'] == 'applied' and 
                datetime.fromisoformat(m['applied_at']) <= source_created_at),
                key=lambda x: x['migration_number'],
                default=None
            )

            last_common_migration_number = last_common_migration['migration_number'] if last_common_migration else -1

            # Get all applied migrations from source branch after the common point
            source_applied_migrations = [
                (m['migration_number'], m['name']) for m in source_migrations
                if m['status'] == 'applied' and m['migration_number'] > last_common_migration_number
            ]

            # Get already applied migrations in target branch
            target_migrations = self.migration_manager.migrations.get(target_branch, [])
            applied_in_target = {m['migration_number'] for m in target_migrations if m['status'] == 'applied'}

            # Filter out migrations that are already applied in target
            pending_migrations = [
                (num, name) for num, name in source_applied_migrations 
                if num not in applied_in_target
            ]

            return pending_migrations

        except Exception as e:
            click.echo(f"Error checking source branch migrations: {e}")
            return []

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
            tuple: (bool, str) - (Success status, Message)
        """
        if source_branch not in self.config['branches']:
            return False, f"Source branch '{source_branch}' does not exist!"
        if target_branch not in self.config['branches']:
            return False, f"Target branch '{target_branch}' does not exist!"
        if source_branch == target_branch:
            return False, "Cannot merge a branch into itself!"

        try:
            if not self.connect():
                return False, "Failed to connect to the database."

            cursor = self.connection.cursor()

            source_db = self.config['connection']['database']
            if source_branch != 'main':
                source_db = f"{source_db}_{source_branch}"

            target_db = self.config['connection']['database']
            if target_branch != 'main':
                target_db = f"{target_db}_{target_branch}"

            cursor.execute(f"USE `{source_db}`")

            cursor.execute("SHOW TABLES")
            tables = [table[0].decode('utf-8') if isinstance(table[0], bytearray) else table[0] for table in cursor.fetchall()]
    
            if not tables:
                return True, f"No tables found in source branch '{source_branch}' to merge."

            merged_tables = []
            for table in tables:
                cursor.execute(f"USE `{target_db}`")
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not cursor.fetchone():
                    cursor.execute(f"CREATE TABLE `{target_db}`.`{table}` LIKE `{source_db}`.`{table}`")
                else:
                    cursor.execute(f"SHOW COLUMNS FROM `{source_db}`.`{table}`")
                    source_columns = {col[0]: col[1].decode('utf-8') if isinstance(col[1], bytearray) else col[1] for col in cursor.fetchall()}
                    cursor.execute(f"SHOW COLUMNS FROM `{target_db}`.`{table}`")
                    target_columns = {col[0]: col[1].decode('utf-8') if isinstance(col[1], bytearray) else col[1] for col in cursor.fetchall()}

                    for col_name, col_type in source_columns.items():
                        if col_name not in target_columns:
                            cursor.execute(f"ALTER TABLE `{target_db}`.`{table}` ADD COLUMN `{col_name}` {col_type}")

                cursor.execute(f"SHOW COLUMNS FROM `{source_db}`.`{table}`")
                columns = [col[0] for col in cursor.fetchall()]
                columns_str = ", ".join([f"`{col}`" for col in columns])
                update_str = ", ".join([f"`{col}`=VALUES(`{col}`)" for col in columns])

                merge_query = f"""
                    INSERT INTO `{target_db}`.`{table}` ({columns_str})
                    SELECT {columns_str} FROM `{source_db}`.`{table}`
                    ON DUPLICATE KEY UPDATE {update_str}
                """
                cursor.execute(merge_query)
                merged_tables.append(table)

            # Update migration history
            source_migrations = self.migration_manager.migrations.get(source_branch, [])
            target_migrations = self.migration_manager.migrations.get(target_branch, [])
        
            new_migrations = [m for m in source_migrations if m['migration_number'] > max([tm['migration_number'] for tm in target_migrations] + [0])]
            target_migrations.extend(new_migrations)
            self.migration_manager.migrations[target_branch] = sorted(target_migrations, key=lambda x: x['migration_number'])
            self.migration_manager._save_migrations()

            self.connection.commit()
            return True, f"Successfully merged contents of '{source_branch}' into '{target_branch}'. Merged tables: {', '.join(merged_tables)}"

        except Error as e:
            self.connection.rollback()
            return False, f"Error during merge: {str(e)}"
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close() 
    
    def export_data(self, table_name, file_path=None, export_format='csv'):
        """
        Export data from a specific table to a CSV or PDF file.
    
        Args:
            table_name (str): Name of the table to export
            file_path (str, optional): Path to save the exported file. If not provided, a default path will be used.
            export_format (str): Format to export ('csv' or 'pdf'). Defaults to 'csv'.
    
        Returns:
            tuple: (bool, str) - (Success status, Message or file path)
        """
        try:
            if not self.connect():
                return False, "Failed to connect to the database."

            cursor = self.connection.cursor(dictionary=True)
            branch = self.config['current_branch']
    
            # Get correct database name
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
    
            cursor.execute(f"USE `{db_name}`")
    
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE %s", (table_name,))
            if not cursor.fetchone():
                return False, f"Table '{table_name}' does not exist in branch '{branch}'."
    
            # Fetch all data from the table
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
    
            if not rows:
                return False, f"No data found in table '{table_name}'."

            # Generate file path if not provided
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"exports/{db_name}_{table_name}_{timestamp}.{export_format}"
        
                # Ensure exports directory exists
                os.makedirs("exports", exist_ok=True)
    
            if export_format.lower() == 'csv':
                # Export to CSV
                df = pd.DataFrame(rows)
                df.to_csv(file_path, index=False)
            elif export_format.lower() == 'pdf':
                # Export to PDF
                pdf = SimpleDocTemplate(file_path, pagesize=letter)
                table_data = [list(rows[0].keys())] + [list(row.values()) for row in rows]
                table = Table(table_data)
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)
                pdf.build([table])
            else:
                return False, f"Unsupported export format: {export_format}"
    
            return True, file_path

        except Exception as e:
            return False, f"Error exporting data: {str(e)}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def import_data(self, table_name, file_path, create_if_not_exists=False):
        """
        Import data from a CSV file into a specific table.
    
        Args:
            table_name (str): Name of the table to import data into
            file_path (str): Path of the CSV file to import
            create_if_not_exists (bool): If True, create the table if it doesn't exist

        Returns:
            tuple: (bool, str) - (Success status, Message)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            if not self.connect():
                return False, "Failed to connect to the database."

            cursor = self.connection.cursor()
            branch = self.config['current_branch']
        
            db_name = self.config['connection']['database']
            if branch != 'main':
                db_name = f"{db_name}_{branch}"
        
            cursor.execute(f"USE `{db_name}`")
        
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                if not create_if_not_exists:
                    return False, f"Table '{table_name}' does not exist in branch '{branch}'."
                else:
                    # Create the table based on CSV structure
                    with open(file_path, 'r') as csvfile:
                        csv_reader = csv.reader(csvfile)
                        headers = next(csv_reader)
                        create_table_query = f"CREATE TABLE `{table_name}` ("
                        create_table_query += ", ".join([f"`{header}` TEXT" for header in headers])
                        create_table_query += ")"
                        cursor.execute(create_table_query)
                    self.connection.commit()
                    print(f"Created new table '{table_name}' based on CSV structure.")

            # Get table columns
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = [column[0] for column in cursor.fetchall()]
        
            # Read CSV file and insert data
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    # Filter row to only include existing columns
                    filtered_row = {k: v for k, v in row.items() if k in columns}
                    placeholders = ', '.join(['%s'] * len(filtered_row))
                    columns_str = ', '.join(f'`{col}`' for col in filtered_row.keys())
                    sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(sql, list(filtered_row.values()))
        
            self.connection.commit()
            return True, f"Successfully imported data into table '{table_name}'."

        except Exception as e:
            self.connection.rollback()
            return False, f"Error importing data: {str(e)}"
        finally:
            if self.connection and self.connection.is_connected():
                cursor.close()
                self.connection.close()

@click.group()
def cli():
    """mydb-cli: A SQL Database Management tool with Git-like Precision!"""
    pass

@cli.command()
def status():
    """Check the status of the database connection and current branch."""
    db_manager = DatabaseManager()
    connection_status = db_manager.connect()
    
    if connection_status:
        click.echo("Database connection is active!")
        click.echo(f"Current branch: {db_manager.config['current_branch']}")
        db_manager.history_manager.add_entry(
            command='status',
            details=f"Checked status. Connection active. Current branch: {db_manager.config['current_branch']}",
            status='success'
        )
    else:
        click.echo("Failed to connect to the database.")
        db_manager.history_manager.add_entry(
            command='status',
            details="Checked status. Failed to connect to the database.",
            status='failed'
        )

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
    success, executed_queries = db_manager.migrate_up()
    
    if success:
        queries_str = "\n".join(executed_queries)
        db_manager.history_manager.add_entry(
            command='migrate_up',
            details=f"Applied next pending migration in branch '{db_manager.config['current_branch']}'",
            status='success',
            error=f"Executed queries:\n{queries_str}"
        )
    else:
        db_manager.history_manager.add_entry(
            command='migrate_up',
            details=f"Failed to apply next pending migration in branch '{db_manager.config['current_branch']}'",
            status='failed'
        )

@cli.command()
def migrate_down():
    """Rollback the last applied migration."""
    db_manager = DatabaseManager()
    success, executed_queries = db_manager.migrate_down()
    
    if success:
        queries_str = "\n".join(executed_queries)
        db_manager.history_manager.add_entry(
            command='migrate_down',
            details=f"Rolled back last applied migration in branch '{db_manager.config['current_branch']}'",
            status='success',
            error=f"Executed queries:\n{queries_str}"
        )
    else:
        db_manager.history_manager.add_entry(
            command='migrate_down',
            details=f"Failed to roll back last applied migration in branch '{db_manager.config['current_branch']}'",
            status='failed'
        )

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
    success, executed_queries = db_manager.apply_migration(migration_number=number)
    
    if success:
        queries_str = "\n".join(executed_queries)
        db_manager.history_manager.add_entry(
            command='apply_migration',
            details=f"Applied migration {number if number else 'next pending'} in branch '{db_manager.config['current_branch']}'",
            status='success',
            error=f"Executed queries:\n{queries_str}"
        )
    else:
        db_manager.history_manager.add_entry(
            command='apply_migration',
            details=f"Failed to apply migration {number if number else 'next pending'} in branch '{db_manager.config['current_branch']}'",
            status='failed'
        )

@cli.command()
def migration_status():
    """Show status of all migrations in current branch."""
    db_manager = DatabaseManager()
    success, result, current_migration = db_manager.migration_status()
    
    if success:
        if isinstance(result, str):
            click.echo(result)
        else:
            headers = ['Number', 'Name', 'Status', 'Applied At', 'Error']
            click.echo(f"\nMigration Status for branch '{db_manager.config['current_branch']}':")
            click.echo(tabulate(result, headers=headers, tablefmt='grid'))
            
            if current_migration:
                click.echo(f"\nCurrent Migration State: {current_migration['migration_number']:04d} - {current_migration['name']}")
            else:
                click.echo("\nCurrent Migration State: No migrations applied yet")
        
        db_manager.history_manager.add_entry(
            command='migration_status',
            details=f"Checked migration status for branch '{db_manager.config['current_branch']}'",
            status='success'
        )
    else:
        click.echo(f"Error: {result}")
        db_manager.history_manager.add_entry(
            command='migration_status',
            details=f"Failed to check migration status for branch '{db_manager.config['current_branch']}'",
            status='failed',
            error=result
        )

@cli.command()
@click.option("--source", prompt="Source branch name", help="The branch to merge from.")
@click.option("--target", prompt="Target branch name", help="The branch to merge into.")
def merge_branch(source, target):
    """Merge changes from source branch into target branch."""
    db_manager = DatabaseManager()
    success, message = db_manager.merge_branch(source, target)
    
    if success:
        db_manager.history_manager.add_entry(
            command='merge_branch',
            details=f"Merged branch '{source}' into '{target}'",
            status='success'
        )
        click.echo(message)
    else:
        db_manager.history_manager.add_entry(
            command='merge_branch',
            details=f"Failed to merge branch '{source}' into '{target}'",
            status='failed',
            error=message
        )
        click.echo(f"Merge failed: {message}")

@cli.command()
def studio():
    """Launch the MyDB Studio GUI interface."""
    try:
        import streamlit
        os.system(f"streamlit run studio.py")
    except ImportError:
        click.echo("Streamlit is required to run the studio. Install it with: pip install streamlit")

@cli.command()
@click.option('--limit', type=int, help='Limit the number of entries to show')
def history(limit):
    """Show command history with details."""
    db_manager = DatabaseManager()
    history_entries = db_manager.history_manager.get_history(limit)
    
    if not history_entries:
        click.echo("No history entries found.")
        return

    headers = ['Timestamp', 'Status', 'Command', 'Details', 'Error/SQL Query']
    click.echo("\nCommand History:")
    click.echo(tabulate(history_entries, headers=headers, tablefmt='grid'))

@cli.command()
@click.option("--table", prompt="Table name", help="Name of the table to export")
@click.option("--file", help="Path to save the exported file (optional)")
@click.option("--format", type=click.Choice(['csv', 'pdf'], case_sensitive=False), default='csv', help="Export format (csv or pdf)")
def export_data(table, file, format):
    """Export data from a table to a CSV or PDF file."""
    db_manager = DatabaseManager()
    success, result = db_manager.export_data(table, file, format)
    
    if success:
        db_manager.history_manager.add_entry(
            command='export_data',
            details=f"Exported data from table '{table}' to {format.upper()} file '{result}'",
            status='success'
        )
        click.echo(f"Data exported successfully. File saved as: {result}")
    else:
        db_manager.history_manager.add_entry(
            command='export_data',
            details=f"Failed to export data from table '{table}' to {format.upper()} format",
            status='failed',
            error=result
        )
        click.echo(f"Export failed: {result}")

@cli.command()
@click.option("--table", prompt="Table name", help="Name of the table to import data into")
@click.option("--file", prompt="File path", type=click.Path(exists=True), help="Path of the CSV file to import")
@click.option("--create", is_flag=True, help="Create the table if it doesn't exist")
def import_data(table, file, create):
    """Import data from a CSV file into a table."""
    db_manager = DatabaseManager()
    success, message = db_manager.import_data(table, file, create_if_not_exists=create)
    
    if success:
        db_manager.history_manager.add_entry(
            command='import_data',
            details=f"Imported data into table '{table}' from file '{file}'" + (" (table created)" if create else ""),
            status='success'
        )
        click.echo(message)
    else:
        db_manager.history_manager.add_entry(
            command='import_data',
            details=f"Failed to import data into table '{table}' from file '{file}'",
            status='failed',
            error=message
        )
        click.echo(f"Import failed: {message}")
    
@cli.command()
@click.option('--before', help='Clear history before this date (YYYY-MM-DD)')
@click.confirmation_option(prompt='Are you sure you want to clear the history?')
def clear_history(before):
    """Clear command history."""
    db_manager = DatabaseManager()
    
    before_date = None
    if before:
        try:
            before_date = datetime.strptime(before, '%Y-%m-%d')
        except ValueError:
            click.echo("Invalid date format. Please use YYYY-MM-DD")
            return

    if db_manager.history_manager.clear_history(before_date):
        message = "History cleared successfully"
        if before_date:
            message += f" (entries before {before})"
        click.echo(message)
    else:
        click.echo("Failed to clear history")

@cli.command()
@click.option('--path', help='Custom backup file path')
def backup_history(path):
    """Backup command history to a file."""
    db_manager = DatabaseManager()
    
    if db_manager.history_manager.backup_history(path):
        click.echo("History backup created successfully")
    else:
        click.echo("Failed to create history backup")

@cli.command()
def see_databases():
    """List all configured databases."""
    db_manager = DatabaseManager()
    db_manager.see_databases()

@cli.command()
@click.option("--name", prompt="Database name", help="Name for this database connection")
@click.option("--host", prompt="Host", help="Database host")
@click.option("--user", prompt="User", help="Database user")
@click.option("--password", prompt="Password", hide_input=True, help="Database password")
@click.option("--database", prompt="Database", help="Database name")
def connect_database(name, host, user, password, database):
    """Connect to a new database."""
    db_manager = DatabaseManager()
    db_manager.connect_database(name, host, user, password, database)

@cli.command()
def reach_home():
    """Connect back to the default mydb database."""
    db_manager = DatabaseManager()
    db_manager.reach_home()

if __name__ == '__main__':
    cli()