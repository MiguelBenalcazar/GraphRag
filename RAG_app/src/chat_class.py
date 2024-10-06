import os
import sys
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from typing import Any, List
# import ollama
from langchain_community.vectorstores import Neo4jVector
from langchain_community.llms import Ollama
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,PromptTemplate
from langchain.schema import StrOutputParser

# from sentence_transformers import CrossEncoder

from llama_index.postprocessor.colbert_rerank import ColbertRerank
import gradio as gr

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
# from RAG_BASIC.utils.utils import _load_data_structure
from RAG_BASIC.BM25_rank.BM25_class import BM25_score
from RAG_BASIC.encoder.custom_embeddings import CustomEmbeddings



# Global constants
VECTOR_INDEX_NAME = 'Chunk_Embedding_Vector'
VECTOR_NODE_LABEL = 'Chunk_Node'
FORM_LABEL = 'Chunk_Form'
FORM_IMAGES = 'Chunk_Images_Tables'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'
VECTOR_LENGTH = 384
MODEL_EMBEDDING = "all-MiniLM-L6-v2"

retrieval_query_window = f"""
MATCH window=
    (:{VECTOR_NODE_LABEL})-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:{VECTOR_NODE_LABEL})
    WITH node, score, window as longestWindow 
    ORDER BY length(window) DESC LIMIT 1
    WITH nodes(longestWindow) as chunkList, node, score
    UNWIND chunkList as chunkRows
    WITH collect(chunkRows.text) as textList, node, score
    RETURN apoc.text.join(textList, " \n ") as text,
        score,
        node {{.source}} AS metadata
"""


class RAG_Chat:
    def __init__(self, BM25_load_path:str="./BM25_retriever") -> Any:
        
        # Get the current script directory
        current_directory = os.path.dirname(__file__)
        # Construct the full path to the .env file
        dotenv_path = os.path.abspath(os.path.join(current_directory, '..', '..'))
        dotenv_path = os.path.join(dotenv_path, "RAG_BASIC", 'GraphDatabase', '.env' )
        # dotenv_path = os.path.join(current_directory, '.env')
        # Load environment variables
        load_dotenv(dotenv_path, override=True)
        
        '''
        INIT BM25 -> Sparse search
        '''
        self.bm25_score = BM25_score(path_load = BM25_load_path ,
                                     load=True, language='english') 
        
        '''
        INIT GRAPH SEARCH -> Dense search
        '''
        graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'),
            username=os.getenv('NEO4J_USERNAME'),
            password=os.getenv('NEO4J_PASSWORD'),
            database=os.getenv('NEO4J_DATABASE')
        )

        self.vector_store_extra_text = Neo4jVector.from_existing_index(
            embedding=CustomEmbeddings(MODEL_EMBEDDING),
            graph = graph,
            index_name=VECTOR_INDEX_NAME,
            text_node_property=VECTOR_SOURCE_PROPERTY,
            # retrieval_query=retrieval_query_window, # NEW !!!
        )

        """
        DEFINE LLM
        """
        self.chat_llm = Ollama(model="llama3.1", temperature='0.1')

        '''
        DEFINE PROMPT
        '''
        # prompt = ChatPromptTemplate.from_template(
        #     input_variables=["context", "question"],
        #     input_types = [List, str],
        #     template = [(
        #         "system",
        #         """
        #             1. Use the following pieces of context to answer the question at the end.
        #             2. If you don't know the answer, just say that "I don't know" but don't make up an answer on your own.\n
        #             3. Keep the answer crisp and limited to 3,4 sentences.
        #         """
        #     ),
        #     ("system", "{context}"),
        #     # MessagesPlaceholder(variable_name="chat_history"),
        #     ("human", "{question}"),
        #     ]
        # )

        prompt = ChatPromptTemplate.from_template(
            template = '''
                system:
                """
                    1. Use the following pieces of context to answer the question at the end.
                    2. If you don't know the answer, just say that "I don't know" but don't make up an answer on your own.\n
                    3. Keep the answer crisp and limited to 3,4 sentences.

                    from_template
                """

                system: "{context}"

                human: "{question}"

            '''
        )

        self.chat_chain = prompt | self.chat_llm | StrOutputParser()


        

        
    
    def respond(self, question,  history):
        responses = self.extract_results(self.bm25_score, self.vector_store_extra_text, query=question)
        rerank = self.reranking(query=question, responses=responses)

        rerank_text = [i['text'] for i in rerank]


        a = self.chat_chain.invoke({"context": rerank_text, "question":question})
        
        return a

    def __call__(self) -> Any:

        gr.ChatInterface(
            fn=self.respond ,
            chatbot=gr.Chatbot(height=500),
            textbox=gr.Textbox(placeholder="Ask me question about papers added to knowledge graph", container=False, scale=7),
            title="RAG Chatbot",
            examples=["What LLM they used?", "What database they used?"],
            cache_examples=True,
            retry_btn=None,

        ).launch(share = True)





        # while True:
        #     question = input("> ")

        #     if question=='/exit':
        #         break

           
        #     responses = self.extract_results(self.bm25_score, self.vector_store_extra_text, query=question)
        #     rerank = self.reranking(query=question, responses=responses)

        #     rerank_text = [i['text'] for i in rerank]


        #     a = self.chat_chain.invoke({"context": rerank_text, "question":question})
        #     print(a)
           


    @staticmethod
    def extract_results(bm25_score, vector_store_extra_text, query:str, bm25K:int=10, graphK:int=12)-> List[object]:
        response = []
        bm25_sparse = bm25_score.__search__(query=query, k=bm25K)
        graph_dense = vector_store_extra_text.similarity_search(query, k=graphK)

        response.extend([{'text': i['text']} for i in bm25_sparse[0][0]])
        response.extend([{'text': i.page_content, 'metadata': i.metadata} for i in graph_dense])

        return response
    

    @staticmethod
    def reranking(query:str, responses:List[object], top_rank:int=5)->List[object]:

        rerank_data = [ doc['text'] for doc in responses]

        colbert_reranker = ColbertRerank(
            top_n=5,
            model="colbert-ir/colbertv2.0",
            tokenizer="colbert-ir/colbertv2.0",
            keep_retrieval_score=True
        )
        rank = colbert_reranker._calculate_sim(query=query, documents_text_list =  rerank_data)
        # Extract the tensor values into a list of floats
        values = [t.item() for t in rank]

        for i in range(len(values)):
            responses[i]['rerank_score'] = values[i]

        sorted_data = sorted(responses, key=lambda x: x['rerank_score'], reverse=True)[:top_rank]
        
        return sorted_data


        
        




       


