import streamlit as st
from main import DatabaseManager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

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
    pages = ['Overview', 'Branches', 'Tables', 'Migrations']
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

if __name__ == "__main__":
    main()