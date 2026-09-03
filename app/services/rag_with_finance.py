# app/services/rag_with_finance.py
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class RAGWithFinance:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = []
        
    def index_financial_data(self, data: List[Dict[str, Any]]):
        \"\"\"Индексация финансовых данных\"\"\"
        for item in data:
            text = self._format_document(item)
            self.documents.append(text)
            embedding = self.embedder.encode(text)
            self.embeddings.append(embedding)
        logger.info(f"Индексировано {len(data)} документов")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        \"\"\"Поиск релевантных документов\"\"\"
        if not self.embeddings:
            return []
        
        query_embedding = self.embedder.encode(query)
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "similarity": float(similarities[idx])
            })
        
        return results
    
    def _format_document(self, item: Dict) -> str:
        \"\"\"Форматирование документа для индексации\"\"\"
        return f"Проект: {item.get('project_name', '')}\n" \
               f"Затраты: {item.get('costs', 0)}\n" \
               f"Команда: {item.get('team_size', 0)}\n" \
               f"Описание: {item.get('description', '')}"
