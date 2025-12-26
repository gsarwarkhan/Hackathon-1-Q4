import os
import logging # Import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
import tiktoken # Import tiktoken
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type # Import tenacity components
import openai # Used for openai.APIError

load_dotenv()

# Configure logging for this module
logger = logging.getLogger(__name__)

class AIWrapper:
    def __init__(self):
        self.client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),  # load from .env only
        )
        self.model = os.getenv("CHAT_MODEL", "openai/gpt-4o-mini")
        self.extra_headers = {
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Physical AI & Humanoid Robotics Textbook",
        }
        
        # Initialize tiktoken encoder and max context tokens
        try:
            self.encoder = tiktoken.encoding_for_model(self.model.split('/')[-1]) 
        except KeyError:
            logger.warning(f"Could not find tiktoken encoder for model '{self.model}'. Using 'cl100k_base'.")
            self.encoder = tiktoken.get_encoding("cl100k_base")
        self.max_context_tokens = int(os.getenv("MAX_LLM_CONTEXT_TOKENS", "4096"))

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_fixed(2), # Wait 2 seconds between retries
        retry=retry_if_exception_type(openai.APIError), # Retry on specific API errors
        reraise=True # Re-raise the last exception after retries
    )
    def get_ai_response(self, messages: List[Dict[str, str]]) -> str:
        system_message_content = "You are an expert Robotics Professor for the Physical AI course. Answer technical questions about ROS 2, Isaac Sim, and Humanoid Control."
        conversation_for_llm = [{"role": "system", "content": system_message_content}]
        
        current_tokens = len(self.encoder.encode(system_message_content))
        
        prunable_messages = []
        for msg in messages:
            if msg["sender"] == "user":
                prunable_messages.append({"role": "user", "content": msg["text"]})
            elif msg["sender"] == "ai":
                prunable_messages.append({"role": "assistant", "content": msg["text"]})
        
        # Add messages, starting from most recent, until context limit
        # Iterate in reverse, adding to the front of the list (after system message)
        for msg in reversed(prunable_messages):
            msg_tokens = len(self.encoder.encode(msg["content"]))
            if current_tokens + msg_tokens < self.max_context_tokens:
                conversation_for_llm.insert(1, msg) 
                current_tokens += msg_tokens
            else:
                logger.warning(f"Truncating conversation history. Dropped old message from '{msg['sender']}' to fit within {self.max_context_tokens} tokens.")
                break
        
        # Log the conversation length for debugging
        logger.info(f"Sending {len(conversation_for_llm)} messages to LLM, total tokens: {current_tokens}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation_for_llm, # Use pruned conversation
                extra_headers=self.extra_headers,
            )
            return response.choices[0].message.content
        except openai.APIError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise ValueError(f"OpenRouter API returned an error: {e}") # Re-raise as ValueError
        except Exception as e:
            logger.exception("An unexpected error occurred during AI response generation.")
            raise ValueError(f"An unexpected error occurred: {e}") # Re-raise as ValueError

ai_wrapper = AIWrapper()
