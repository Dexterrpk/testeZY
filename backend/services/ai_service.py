# Service for interacting with the AI model (e.g., OpenAI GPT)

import openai
from sqlmodel import Session, select
from typing import List

from ..core.config import settings
from ..models.ai_training import AiTrainingData
from ..services import ai_training_service # To fetch training data

# Configure OpenAI client if API key is available
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
else:
    print("Warning: OPENAI_API_KEY not found in environment variables. AI features will be limited.")
    # You might want to raise an error or use a fallback mechanism here

def get_ai_response(db: Session, user_query: str, owner_id: int) -> str:
    """Generates a response from the AI based on user query and trained data."""
    
    if not settings.OPENAI_API_KEY:
        return "Desculpe, a funcionalidade de IA não está configurada corretamente (sem chave de API)."

    # 1. Fetch relevant training data for the user
    # This is a simplified example; real implementation might involve vector search
    # or more sophisticated retrieval based on the query.
    training_data_list: List[AiTrainingData] = ai_training_service.get_training_data_by_owner(db, owner_id=owner_id, limit=50) # Limit for context window
    
    # 2. Format training data into a context string or system prompt
    context = "Baseado nas seguintes informações da empresa:\n"
    for item in training_data_list:
        context += f"- Tipo: {item.data_type}, Conteúdo: {item.content}\n"
    context += "\nResponda à seguinte pergunta do cliente da forma mais útil e humanizada possível, aplicando técnicas de vendas como Rapport e SPIN Selling quando apropriado. Se a informação não estiver disponível, admita educadamente.\n"

    # 3. Call the OpenAI API (Example using ChatCompletion)
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo", # Or specify another model like gpt-4
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_query}
            ],
            max_tokens=150 # Adjust as needed
        )
        ai_message = response.choices[0].message.content.strip()
        return ai_message
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação com a IA."

# Add more functions as needed, e.g., for fine-tuning (if applicable), personality adjustment, etc.

