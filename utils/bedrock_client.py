import boto3
import json

class BedrockClient:
    def __init__(self):
        self.client = boto3.client('bedrock-runtime')
        self.model_id = 'amazon.titan-text-express-v1'

    def generate_response(self, prompt: str) -> str:
        try:
            body = json.dumps({
                "prompt": prompt,
                "max_gen_len": 512,
                "temperature": 0.7,
                "top_p": 0.9
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('generation', '').strip()  # Just return the raw output
        except Exception as e:
            return f"Error generating response: {str(e)}"