# MyDB CLI & Studio

MyDB is a Python-based MySQL management tool with branching functionality. It enables database branching, migration management, and a graphical interface for managing database structures and migrations using Streamlit.

## Features

- **Database Branching**: Create, switch, and delete branches of your database, enabling separate development environments within the same MySQL instance.
- **Table Management**: Create, list, describe, and drop tables in each branch.
- **Migration System**: Define, apply, and rollback schema migrations for each branch.
- **Streamlit GUI**: MyDB Studio provides a graphical interface with visual tools for branch and migration management, and a SQL assistant with Google Gemini integration.

---

## Getting Started

### Prerequisites

- Python 3.6+
- MySQL Database
- Required Python libraries (install with `pip`):
  ```bash
  pip install click mysql-connector-python streamlit pandas plotly networkx google-generative-ai
  ```

## Configuration

- Set up your database credentials in config.json under .mydb directory. The file will look like this by default:

```bash
{
  "connection": {
    "user": "root",
    "password": "B#@w@+123",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "auth_plugin": "mysql_native_password"
  },
  "current_branch": "main",
  "branches": {
    "main": {
      "created_at": "2023-11-08T10:00:00",
      "last_accessed": "2023-11-08T10:00:00"
    }
  }
}

```

## Running MyDB CLI

- To launch the CLI, use the following command:

```bash
python main.py [command]

```

CLI Commands

- Database Connection Status

```bash
python main.py status

```

```bash
# Branch Management
python main.py create_branch        # Create Branch
python main.py switch_branch        # Switch Branch
python main.py delete_branch        # Delete Branch
python main.py list_branches        # List Branches
```
```bash
# Table Management
python main.py create_table         # Create Table
python main.py list_tables          # List Tables
python main.py describe_table       # Describe Table
python main.py drop_table           # Drop Table
```
```bash
# Migration Management
python main.py create_migration     # Create Migration
python main.py apply_migration      # Apply Migration
python main.py migrate_down         # Rollback Migration
python main.py migration_status     # View Migration Status
python main.py merge_branch         # Merge Branch
```
# Launch MyDB Studio GUI

```bash
python main.py studio

```

## MyDB Studio

**Run the following command to start the Streamlit interface:**

```bash
streamlit run studio.py

```

## GUI Pages

1. **Overview**: Displays connection status and branch overview.

2. **Branches**: Manage branches, switch between branches, and view branch dependencies.

3. **Tables**: Create, list, and describe tables. Also view schema information.

4. **Migrations**: Create, apply, and view migration status.

5. **Ask Gemini**: SQL assistant powered by Google Gemini for generating SQL queries based on schema context.

# Google Gemini API

**To use the SQL assistant in MyDB Studio, obtain an API key from Google Gemini and enter it in the sidebar under "Ask Gemini."**

## Dependencies

- MySQL Connector
- Streamlit
- Pandas
- Plotly
- Google Generative AI

## License

This project is licensed under the BSD-3 Clause license.
