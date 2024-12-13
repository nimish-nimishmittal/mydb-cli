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