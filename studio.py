import streamlit as st
from main import DatabaseManager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from google.generativeai import GenerativeModel
import google.generativeai as genai
from typing import List, Dict

def init_session_state():
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Overview'
    # Initialize flags for state management
    if 'migration_applied' not in st.session_state:
        st.session_state.migration_applied = False
    if 'branch_switched' not in st.session_state:
        st.session_state.branch_switched = False

def render_sidebar():
    st.sidebar.title("MyDB Studio")
    pages = ['Overview', 'Branches', 'Tables', 'Migrations', 'Ask Gemini']
    st.session_state.current_page = st.sidebar.radio("Navigation", pages)
    
    # Always show current branch status
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current Branch:** {st.session_state.db_manager.config['current_branch']}")

def render_overview_page():
    st.title("Database Overview")
    
    # Database Connection Status
    if st.session_state.db_manager.connect():
        st.success("✅ Database Connection Active")
    else:
        st.error("❌ Database Connection Failed")
        return  # Exit if connection fails
    
    # Branch Statistics
    branches = st.session_state.db_manager.config['branches']
    total_branches = len(branches)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Branches", total_branches)
    with col2:
        st.metric("Current Branch", st.session_state.db_manager.config['current_branch'])
    
    # Branch Timeline
    branch_data = []
    for branch_name, branch_info in branches.items():
        created_at = datetime.fromisoformat(branch_info['created_at'])
        branch_data.append({
            'Branch': branch_name,
            'Created At': created_at,
            'End Date': datetime.now()
        })
    
    df = pd.DataFrame(branch_data)
    if not df.empty:
        fig = px.timeline(df, x_start="Created At", x_end="End Date", y="Branch", title="Branch Creation Timeline")
        st.plotly_chart(fig)

def render_branches_page():
    st.title("Branch Management")
    
    # Ensure database connection
    if not st.session_state.db_manager.connect():
        st.error("❌ Database Connection Failed")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Branch")
        new_branch_name = st.text_input("Branch Name")
        if st.button("Create Branch"):
            if new_branch_name:
                success = st.session_state.db_manager.create_branch(new_branch_name)
                if success:
                    st.success(f"Created branch: {new_branch_name}")
                    st.rerun()
                else:
                    st.error("Failed to create branch")
    
    with col2:
        st.subheader("Switch Branch")
        branches = list(st.session_state.db_manager.config['branches'].keys())
        selected_branch = st.selectbox("Select Branch", branches)
        if st.button("Switch"):
            success = st.session_state.db_manager.switch_branch(selected_branch)
            if success:
                st.success(f"Switched to branch: {selected_branch}")
                st.rerun()
            else:
                st.error("Failed to switch branch")

    st.markdown("---")
    
    # Branch visualization
    st.subheader("Branch Structure")
    branches = st.session_state.db_manager.config['branches']
    
    if len(branches) > 0:
        branch_links = []
        for branch_name, branch_info in branches.items():
            parent = branch_info.get('created_from', None)
            if parent:
                branch_links.append((parent, branch_name))
        
        if branch_links:
            import networkx as nx
            G = nx.DiGraph()
            G.add_edges_from(branch_links)
            pos = nx.spring_layout(G)
            
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines')
                
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="top center",
                marker=dict(
                    size=20,
                    color='#1f77b4',
                    line_width=2))
                    
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=0, l=0, r=0, t=0),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                           )
                           
            st.plotly_chart(fig)

def render_tables_page():
    st.title("Table Management")
    
    # Ensure database connection
    if not st.session_state.db_manager.connect():
        st.error("❌ Database Connection Failed")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Table")
        table_name = st.text_input("Table Name")
        columns_text = st.text_area(
            "Column Definitions",
            "Enter one column per line in format:\ncolumn_name datatype [constraints]",
            height=150
        )
        
        if st.button("Create Table"):
            if table_name and columns_text:
                columns = [col.strip() for col in columns_text.split('\n') if col.strip()]
                success = st.session_state.db_manager.create_table(table_name, columns)
                if success:
                    st.success(f"Created table: {table_name}")
                    st.rerun()
                else:
                    st.error("Failed to create table")
    
    with col2:
        st.subheader("Describe Table")
        cursor = st.session_state.db_manager.connection.cursor()
        current_branch = st.session_state.db_manager.config['current_branch']
        db_name = st.session_state.db_manager.config['connection']['database']
        if current_branch != 'main':
            db_name = f"{db_name}_{current_branch}"
        
        try:
            cursor.execute(f"USE {db_name}")
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if tables:
                selected_table = st.selectbox("Select Table", tables)
                if st.button("Describe"):
                    result = st.session_state.db_manager.describe_table(selected_table)
                    if result:
                        st.write(result)
                    else:
                        st.error("Failed to describe table")
            else:
                st.info("No tables found in current branch")
        except Exception as e:
            st.error(f"Error accessing tables: {str(e)}")

    st.markdown("---")

    # new section for export and import [work in progess, it has !major errors]
    st.subheader("Export and Import Data")
    col3, col4 = st.columns(2)

    with col3:
        st.write("Export Table Data")
        export_table = st.selectbox("Select Table to Export", tables, key="export_table")
        export_file_name = st.text_input("Export File Name (optional)", key="export_file_name")
        
        if st.button("Export Data"):
            try:
                success, result = st.session_state.db_manager.export_data(export_table, export_file_name)
                if success:
                    st.success(f"Data exported successfully. File saved as: {result}")
                    st.download_button(
                        label="Download Exported Data",
                        data=open(result, "rb").read(),
                        file_name=os.path.basename(result),
                        mime="text/csv"
                    )
                else:
                    st.error(f"Failed to export data: {result}")
            except Exception as e:
                st.error(f"Error during export: {str(e)}")

    with col4:
        st.write("Import Table Data")
        import_table = st.selectbox("Select Table to Import Into", tables, key="import_table")
        uploaded_file = st.file_uploader("Choose a CSV file to import", type="csv")
        
        if uploaded_file is not None and st.button("Import Data"):
            try:
                # Save the uploaded file temporarily
                with open("temp_import.csv", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                success, message = st.session_state.db_manager.import_data(import_table, "temp_import.csv")
                if success:
                    st.success(message)
                else:
                    st.error(f"Failed to import data: {message}")
                
                # Clean up the temporary file
                os.remove("temp_import.csv")
            except Exception as e:
                st.error(f"Error during import: {str(e)}")
                if os.path.exists("temp_import.csv"):
                    os.remove("temp_import.csv")

    st.markdown("---")

def render_migrations_page():
    st.title("Migration Management")
    
    # Ensure database connection
    if not st.session_state.db_manager.connect():
        st.error("❌ Database Connection Failed")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create Migration")
        migration_name = st.text_input("Migration Name")
        migration_desc = st.text_area("Migration Description")
        
        # Note about SQL files
        st.info("""
        This will create migration files:
        - migrations/migrationNumber_migrationName/up.sql
        - migrations/migrationNumber_migrationName/down.sql
        
        Use the CLI to edit the SQL files after creation.
        """)
        
        if st.button("Create Migration"):
            if migration_name:
                try:
                    success = st.session_state.db_manager.create_migration(
                        migration_name, 
                        migration_desc
                    )
                    if success:
                        st.success(f"""
                        Created migration: {migration_name}
                        Please edit the up.sql and down.sql files in the migrations folder.
                        """)
                        st.rerun()
                    else:
                        st.error("Failed to create migration")
                except Exception as e:
                    st.error(f"Error creating migration: {str(e)}")
    
    with col2:
        st.subheader("Apply Migration")
        try:
            current_migration = st.session_state.db_manager.get_current_migration()
            
            # Show current migration status
            if current_migration:
                st.info(f"Current Migration: {current_migration}")
            else:
                st.info("No pending migrations fuond yet")
            
            # Migration actions
            col2_1, col2_2 = st.columns(2)
            
            with col2_1:
                if st.button("Apply Next Migration ⬆️"):
                    success = st.session_state.db_manager.apply_migration()
                    if success:
                        st.success("Migration applied successfully")
                        st.rerun()
                    else:
                        st.error("Failed to apply migration")
            
            with col2_2:
                if st.button("Rollback Migration ⬇️"):
                    success = st.session_state.db_manager.rollback_migration()
                    if success:
                        st.success("Migration rolled back successfully")
                        st.rerun()
                    else:
                        st.error("Failed to rollback migration")

        except Exception as e:
            st.error(f"Error with migration: {str(e)}")

    st.markdown("---")
    
    # Migration Status
    st.subheader("Migration Status")
    try:
        status = st.session_state.db_manager.migration_status()
        if status:
            st.code(status, language="plain")
        else:
            st.info("No pending migrations found")
    except Exception as e:
        st.error(f"Error getting migration status: {str(e)}")

def setup_genai(api_key: str) -> None:
    """Initialize the Gemini API with the provided key."""
    genai.configure(api_key=api_key)

def debug_print(message: str):
    """Helper function to print debug messages to Streamlit."""
    st.sidebar.markdown(f"**Debug:** {message}")

def get_table_schema() -> Dict[str, List[str]]:
    """Get schema information for all tables in current database."""
    if not st.session_state.db_manager.connect():
        return {}
    
    connection = st.session_state.db_manager.connection
    cursor = connection.cursor()
    
    # Get current database name
    current_branch = st.session_state.db_manager.config['current_branch']
    db_name = st.session_state.db_manager.config['connection']['database']
    if current_branch != 'main':
        db_name = f"{db_name}_{current_branch}"
    
    schemas = {}
    try:
        # Switch to the correct database
        cursor.execute(f"USE `{db_name}`")
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables_raw = cursor.fetchall()
        
        # Debug table names
        debug_print(f"Raw tables: {tables_raw}")
        
        # Extract table names
        tables = []
        for table_row in tables_raw:
            table_name = table_row[0]
            if isinstance(table_name, bytes):
                table_name = table_name.decode('utf-8')
            elif isinstance(table_name, bytearray):
                table_name = table_name.decode('utf-8')
            tables.append(table_name)
        
        # Debug processed table names
        debug_print(f"Processed tables: {tables}")
        
        for table in tables:
            try:
                cursor.execute(f"DESCRIBE `{table}`")
                columns = cursor.fetchall()
                schemas[table] = [f"{col[0]} ({col[1]})" for col in columns]
            except Exception as e:
                debug_print(f"Error describing table {table}: {str(e)}")
        
    except Exception as e:
        st.error(f"Error fetching schema: {str(e)}")
        return {}
    finally:
        cursor.close()
    
    return schemas

def auto_analyze_tables() -> None:
    """Automated analysis of database tables."""
    schemas = get_table_schema()
    if not schemas:
        st.error("No tables found or couldn't access database")
        return
    
    st.write("📊 **Automated Table Analysis**")
    
    for table, columns in schemas.items():
        with st.expander(f"Analysis for {table}"):
            cursor = st.session_state.db_manager.connection.cursor()
            
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                row_count = cursor.fetchone()[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Rows", row_count)
                    st.write("**Columns:**")
                    for col in columns:
                        st.write(f"- {col}")
                
                with col2:
                    # Try to get statistics for numeric columns
                    try:
                        cursor.execute(f"""
                            SELECT 
                                COLUMN_NAME, 
                                DATA_TYPE 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = %s 
                            AND TABLE_NAME = %s 
                            AND DATA_TYPE IN ('int', 'decimal', 'float', 'double')
                        """, (st.session_state.db_manager.config['connection']['database'], table))
                        
                        numeric_cols = cursor.fetchall()
                        
                        if numeric_cols:
                            st.write("**Numeric Column Statistics:**")
                            for col in numeric_cols:
                                col_name = col[0]
                                try:
                                    cursor.execute(f"""
                                        SELECT 
                                            MIN(`{col_name}`) as min_val,
                                            MAX(`{col_name}`) as max_val,
                                            AVG(`{col_name}`) as avg_val
                                        FROM `{table}`
                                    """)
                                    stats = cursor.fetchone()
                                    if stats:
                                        st.write(f"*{col_name}*")
                                        st.write(f"- Min: {stats[0]}")
                                        st.write(f"- Max: {stats[1]}")
                                        st.write(f"- Avg: {round(float(stats[2]), 2) if stats[2] is not None else 'N/A'}")
                                except Exception as e:
                                    st.warning(f"Could not calculate statistics for {col_name}: {str(e)}")
                                    
                    except Exception as e:
                        st.warning(f"Could not fetch numeric columns: {str(e)}")
                
            except Exception as e:
                st.error(f"Error analyzing table {table}: {str(e)}")
            finally:
                cursor.close()

def sql_chat_assistant(user_input: str, schema_context: str) -> str:
    """Generate SQL queries based on user input using Gemini."""
    model = GenerativeModel('gemini-pro')
    prompt = f"""
    As a SQL expert, help me write a SQL query based on the following schema:
    {schema_context}
    
    User request: {user_input}
    
    Provide only the SQL query without any explanation. The query should be correct, efficient, and follow best practices.
    Ensure to wrap table and column names in backticks to handle special characters.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def render_ask_gemini_page():
    st.title("Ask Gemini 🤖")
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=False)
    
    # Check for API key
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar to continue")
        return
    
    setup_genai(api_key)
    
    # Tab selection
    tab1, tab2 = st.tabs(["🔍 Auto Analyze", "💬 SQL Assistant"])
    
    with tab1:
        st.header("Automated Database Analysis")
        if st.button("Run Analysis"):
            with st.spinner("Analyzing database..."):
                auto_analyze_tables()
    
    with tab2:
        st.header("SQL Query Assistant")
        
        # Get and display schema context
        with st.spinner("Loading database schema..."):
            schemas = get_table_schema()
            
        if schemas:
            schema_context = "Available tables and their columns:\n"
            for table, columns in schemas.items():
                schema_context += f"\n{table}:\n"
                for col in columns:
                    schema_context += f"- {col}\n"
            
            if debug_mode:
                st.sidebar.markdown("### Schema Context")
                st.sidebar.code(schema_context)
            
            # Chat interface
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Describe the SQL query you need..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Generating SQL query..."):
                        response = sql_chat_assistant(prompt, schema_context)
                    st.code(response, language="sql")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Execute Query"):
                            cursor = None
                            try:
                                cursor = st.session_state.db_manager.connection.cursor()
                                cursor.execute(response)
                                results = cursor.fetchall()
                                if results:
                                    # Get column names from cursor description
                                    columns = [desc[0] for desc in cursor.description]
                                    df = pd.DataFrame(results, columns=columns)
                                    st.dataframe(df)
                                else:
                                    st.info("Query executed successfully but returned no results")
                            except Exception as e:
                                st.error(f"Error executing query: {str(e)}")
                            finally:
                                if cursor:
                                    cursor.close()
                
                st.session_state.messages.append({"role": "assistant", "content": f"```sql\n{response}\n```"})
        else:
            st.error("Unable to fetch database schema. Please check your connection.")

def main():
    st.set_page_config(
        page_title="MyDB Studio",
        layout="wide"
    )
    
    init_session_state()
    render_sidebar()
    
    # Render the selected page
    if st.session_state.current_page == 'Overview':
        render_overview_page()
    elif st.session_state.current_page == 'Branches':
        render_branches_page()
    elif st.session_state.current_page == 'Tables':
        render_tables_page()
    elif st.session_state.current_page == 'Migrations':
        render_migrations_page()
    elif st.session_state.current_page == 'Ask Gemini':
        render_ask_gemini_page()

if __name__ == "__main__":
    main()