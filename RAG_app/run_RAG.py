import os
import warnings
warnings.filterwarnings("ignore")

from src.chat_class import RAG_Chat


if __name__ == "__main__":
    rag = RAG_Chat()
    rag()
