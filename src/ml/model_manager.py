from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional, Dict, Any, List
import logging

class ModelManager:
    """Manages ML model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_model(self, model_name: str = "facebook/opt-125m") -> bool:
        """Load the specified model and tokenizer"""
        try:
            self.logger.info(f"Loading model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False

    def generate_sql(self, prompt: str, schema_context: str) -> Optional[str]:
        """Generate SQL based on natural language prompt and schema context"""
        if not self.model or not self.tokenizer:
            self.logger.error("Model not loaded")
            return None
            
        try:
            # Format the prompt with schema context
            full_prompt = f"""
            Given this database schema:
            {schema_context}
            
            Generate SQL for this request: {prompt}
            
            SQL:
            """
            
            inputs = self.tokenizer(full_prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            generated_sql = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the SQL part
            sql_start = generated_sql.find("SQL:")
            if sql_start != -1:
                generated_sql = generated_sql[sql_start + 4:].strip()
                
            return generated_sql
            
        except Exception as e:
            self.logger.error(f"Error generating SQL: {str(e)}")
            return None

    def analyze_schema(self, schema_info: Dict[str, List[str]]) -> Optional[Dict[str, Any]]:
        """Analyze database schema and provide insights"""
        if not self.model or not self.tokenizer:
            self.logger.error("Model not loaded")
            return None
            
        try:
            # Format schema for analysis
            schema_text = "Database Schema:\n"
            for table, columns in schema_info.items():
                schema_text += f"\nTable: {table}\n"
                for col in columns:
                    schema_text += f"- {col}\n"
                    
            prompt = f"""
            {schema_text}
            
            Analyze this database schema and provide:
            1. Potential relationships between tables
            2. Suggested indexes
            3. Data type consistency checks
            4. Normalization recommendations
            """
            
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=300,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            analysis = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse the analysis into structured format
            sections = analysis.split("\n\n")
            result = {
                "relationships": [],
                "indexes": [],
                "data_type_checks": [],
                "normalization": []
            }
            
            current_section = None
            for section in sections:
                if "relationships" in section.lower():
                    current_section = "relationships"
                elif "indexes" in section.lower():
                    current_section = "indexes"
                elif "data type" in section.lower():
                    current_section = "data_type_checks"
                elif "normalization" in section.lower():
                    current_section = "normalization"
                elif current_section and section.strip():
                    result[current_section].append(section.strip())
                    
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing schema: {str(e)}")
            return None