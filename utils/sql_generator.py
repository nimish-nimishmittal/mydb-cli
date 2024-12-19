from .bedrock_client import BedrockClient
import re

class SQLGenerator:
    def __init__(self):
        self.bedrock = BedrockClient()

    def _clean_response(self, response: str) -> str:
        """Clean the LLM response to extract just the SQL query."""
        # Remove any markdown code block syntax
        response = re.sub(r'^```sql\s*|\s*```$', '', response, flags=re.MULTILINE)
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        return response

    def _validate_query(self, query: str) -> bool:
        """Validate that the response appears to be a valid SQL query."""
        if not query or len(query) < 10:
            return False
            
        # List of common SQL keywords
        sql_keywords = [
            'select', 'from', 'where', 'group by', 'having', 'order by',
            'insert into', 'update', 'delete from', 'create table',
            'alter table', 'drop table', 'join', 'inner join', 'left join',
            'right join', 'full join', 'union', 'with'
        ]
        
        # Convert query to lowercase for keyword checking
        query_lower = query.lower()
        
        # Check if query contains at least one SQL keyword
        has_sql_keyword = any(keyword in query_lower for keyword in sql_keywords)
        
        # Basic syntax validation
        has_valid_structure = (
            # SELECT queries
            ('select' in query_lower and 'from' in query_lower) or
            # INSERT queries
            ('insert' in query_lower and 'into' in query_lower) or
            # UPDATE queries
            ('update' in query_lower and 'set' in query_lower) or
            # DELETE queries
            ('delete' in query_lower and 'from' in query_lower) or
            # CREATE/ALTER/DROP queries
            any(keyword in query_lower for keyword in ['create', 'alter', 'drop'])
        )
        
        return has_sql_keyword and has_valid_structure

    def generate_query(self, user_input: str, schema_context: str) -> str:
        """Generate a SQL query based on user input and database schema."""
        try:
            prompt = f"""Based on the following database schema, generate a SQL query that addresses the user's request.

Database Schema:
{schema_context}

User Request: {user_input}

Important:
- Respond ONLY with the SQL query, no explanations or additional text
- The query must start with a SQL keyword (SELECT, INSERT, UPDATE, etc.)
- Wrap table and column names in backticks
- Include proper JOIN conditions if multiple tables are involved
- Use appropriate WHERE clauses for filtering
- Consider using appropriate aggregate functions when needed
- Do not include markdown code block syntax
"""
            
            # Get response from Bedrock
            response = self.bedrock.generate_response(prompt)
            
            # Clean the response
            cleaned_response = self._clean_response(response)
            
            # Validate the cleaned response
            # if not self._validate_query(cleaned_response):
            #     raise ValueError(
            #         "Generated response does not appear to be a valid SQL query. "
            #         "Please try rephrasing your request."
            #     )
            
            return cleaned_response
            
        except Exception as e:
            return f"Error generating SQL query: {str(e)}"