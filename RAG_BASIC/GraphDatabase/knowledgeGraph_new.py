# Warning control
import os
import sys
import warnings
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_community.graphs import Neo4jGraph
# from graph_database import KnowledgeBase

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from RAG_BASIC.GraphDatabase.graph_database import KnowledgeBase
from RAG_BASIC.utils.utils import _load_data_structure
# from encoder.embedding import Embeddings
from RAG_BASIC.encoder.custom_embeddings import CustomEmbeddings as Embeddings

# Suppress warnings
warnings.filterwarnings("ignore")






# Global constants
VECTOR_INDEX_NAME = 'Chunk_Embedding_Vector'
VECTOR_NODE_LABEL = 'Chunk_Node'
FORM_LABEL = 'Chunk_Form'
FORM_IMAGES = 'Chunk_Images_Tables'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'textEmbedding'
VECTOR_LENGTH = 384
MODEL_EMBEDDING = "all-MiniLM-L6-v2"




class Create_Form_Nodes_Knowledge_Graph:
    def __init__(self, chunk_file_path:str, chunk_images_tables_path:str=None) -> None:

        if chunk_file_path == None:
            raise FileNotFoundError("Please add file to load.") 
        

        # Get the current script directory
        current_directory = os.path.dirname(__file__)
        # Construct the full path to the .env file
        dotenv_path = os.path.join(current_directory, '.env')
        # Load environment variables
        load_dotenv(dotenv_path, override=True)

        neo4j_config = {
            "neo4j_uri" : os.getenv('NEO4J_URI'),
            "neo4j_username"  : os.getenv('NEO4J_USERNAME'),
            "neo4j_password" : os.getenv('NEO4J_PASSWORD'),
            "neo4j_database" : os.getenv('NEO4J_DATABASE')
        }

        self.data = _load_data_structure(path=chunk_file_path)
        self.knowledgeBase = KnowledgeBase(neo4j_config=neo4j_config)
        self.exist_img = False

        if chunk_images_tables_path != None:
            self.data_img_table = _load_data_structure(path=chunk_images_tables_path)
            self.exist_img = True

        print(self.data_img_table)

    def __call__(self):

        
        # Constrain to avoid duplicate chunks
        query = f"""
            CREATE CONSTRAINT unique_chunk IF NOT EXISTS 
            FOR (c:{VECTOR_NODE_LABEL}) 
            REQUIRE c.chunk_id IS UNIQUE
        """
        print(self.knowledgeBase.execute_query(query=query))

        
        # Merge node
        query = f"""
            MERGE (x:{VECTOR_NODE_LABEL} {{chunk_id: $chunkParam.metadata.chunk_id}})
            ON CREATE SET 
                x.formId = $chunkParam.metadata.formId, 
                x.chunkSeqId = $chunkParam.metadata.chunkSeqId, 
                x.language = $chunkParam.metadata.languages,
                x.filetype = $chunkParam.metadata.filetype,
                x.text = $chunkParam.text
            RETURN x
        """


        node_count = 0
        for i in tqdm(range(len(self.data))):
            chunk = self.data[i]
            # print(f"Creating `:{VECTOR_NODE_LABEL}` node for chunk ID {chunk['metadata']['chunk_id']}")
            self.knowledgeBase.execute_query(query, params={'chunkParam': chunk})
            node_count += 1
        # print(f"Created {node_count} nodes")

        
        # Create a vector index
        
        query = f"""
            CREATE VECTOR INDEX {VECTOR_INDEX_NAME} IF NOT EXISTS
            FOR (c:{VECTOR_NODE_LABEL}) 
            ON (c.{VECTOR_EMBEDDING_PROPERTY}) 
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: $chunkParam,
                    `vector.similarity_function`: 'cosine'
                }}
            }}
        """
        print(self.knowledgeBase.execute_query(query=query, params={'chunkParam': VECTOR_LENGTH}))

        # Create a vector index

        print(self.knowledgeBase.execute_query(query = "SHOW INDEXES"))


        # Create vector embeddings 
        query = f"""
            MATCH (chunk:{VECTOR_NODE_LABEL})
            WHERE chunk.chunk_id = $chunkParam.metadata.chunk_id
            CALL db.create.setNodeVectorProperty(chunk, "{VECTOR_EMBEDDING_PROPERTY}", $chunkEmbedding)
        """
      
        
        encoder = Embeddings(model= MODEL_EMBEDDING)
        node_count = 0
        for i in tqdm(range(len(self.data))):
            chunk = self.data[i]
            embedding_txt = encoder.embed_query([self.data[i]['text']])
            embedding_txt =  embedding_txt[0]
            self.knowledgeBase.execute_query(query, params={'chunkParam': chunk, 'chunkEmbedding':embedding_txt})

        print(f"Created {node_count} nodes - Embedding")   

    
        # REFRESH 
        self.knowledgeBase.kg.refresh_schema()
        print(self.knowledgeBase.kg.schema)

        ### CREATE A NODE THAT REPRESENT THE FILE OR FORM

        query = f"""
            MATCH (x:{VECTOR_NODE_LABEL})
            WITH x
            WHERE x.formId = '{self.data[0]['metadata']['formId']}'
            RETURN x {{.chunk_id, .formId, .filetype, .language}} as formInfo
            LIMIT 1
        """
        form_info_list = self.knowledgeBase.execute_query(query)
        form_info = form_info_list[0]['formInfo']

        query = f"""
            MERGE (f:{FORM_LABEL} {{formId: $formInfoParam.formId}})
            ON CREATE 
                SET f.filetype = $formInfoParam.filetype,
                    f.language = $formInfoParam.language
        """

        self.knowledgeBase.execute_query(query, params={'formInfoParam': form_info})


        # Add a NEXT relationship between subsequent chunks
        query = f"""
            MATCH (from_same_section:{VECTOR_NODE_LABEL})
            WHERE from_same_section.formId = $formIdParam
            WITH from_same_section
            ORDER BY from_same_section.chunkSeqId ASC
            WITH collect(from_same_section) as section_chunk_list
            CALL apoc.nodes.link(section_chunk_list, "NEXT", {{avoidDuplicates: true}})
            RETURN size(section_chunk_list)
        """

        print(self.knowledgeBase.execute_query(query, params={'formIdParam': form_info['formId']}))

        # REFRESH 
        self.knowledgeBase.kg.refresh_schema()
        print(self.knowledgeBase.kg.schema)

        # Connect chunks to their parent form with a PART_OF relationship

        query = f"""
            MATCH (first:{VECTOR_NODE_LABEL}), (f:{FORM_LABEL})
            WHERE first.formId = f.formId
                AND first.chunkSeqId = 0
            WITH first, f
                MERGE (f)-[r:SECTION ]->(first)
            RETURN count(r)
        """

        self.knowledgeBase.execute_query(query)


        if self.exist_img :
            
            # create Main Node to branch Images and Tables
            query = f"""
                MERGE (f:{FORM_IMAGES} {{formId: $formInfoParam.formId}})
                ON CREATE 
                SET f.filetype = $formInfoParam.filetype
            """

            self.knowledgeBase.execute_query(query, params={'formInfoParam': self.data_img_table[0]})

            # add nodes Images / Tables
            query = f"""
                MERGE (x:{VECTOR_NODE_LABEL} {{chunk_id: $chunkParam.chunk_id}})
                ON CREATE SET 
                    x.formId = $chunkParam.formId, 
                    x.chunkSeqId = $chunkParam.chunkSeqId, 
                    x.filetype = $chunkParam.filetype,
                    x.text = $chunkParam.text,
                    x.source = $chunkParam.source
                RETURN x
            """

            node_count = 0

            for i in tqdm(range(len(self.data_img_table))):
                chunk = self.data_img_table[i]
                # print(f"Creating `:{VECTOR_NODE_LABEL}` node for chunk ID {chunk['metadata']['chunk_id']}")
                self.knowledgeBase.execute_query(query, params={'chunkParam': chunk})
                node_count += 1

            # Create vector embeddings 
            query = f"""
                MATCH (chunk:{VECTOR_NODE_LABEL})
                WHERE chunk.chunk_id = $chunkParam.chunk_id
                CALL db.create.setNodeVectorProperty(chunk, "{VECTOR_EMBEDDING_PROPERTY}", $chunkEmbedding)
            """
      
          
            node_count = 0
            for i in tqdm(range(len(self.data_img_table))):
                chunk = self.data_img_table[i]
                embedding_txt = encoder.embed_query([chunk['text']])
                embedding_txt =  embedding_txt[0]
                self.knowledgeBase.execute_query(query, params={'chunkParam': chunk, 'chunkEmbedding':embedding_txt})

            print(f"Created {node_count} nodes - Embedding")   


            # Create relationship between node and node_images_tables
            query = f"""
                MATCH (n:{VECTOR_NODE_LABEL}), (f:{FORM_IMAGES})
                WHERE n.formId = $data.formId
                AND n.filetype <> $data.filetype 
                AND f.formId =  $data.formId
                WITH n, f
                MERGE (f)-[r:INCLUDE ]->(n)
                RETURN count(r)

            """

        

            response = self.knowledgeBase.execute_query(query, params={'data':self.data[0]['metadata']})
            print(f"{response} Relationship between main node images tables and node images & tables")

            # Create relationship between node_images_tables with form
            query = f"""
                MATCH (n:{FORM_LABEL}), (f:{FORM_IMAGES})
                WHERE n.formId = $data.formId
                AND f.formId =  $data.formId 
                MERGE (n)-[r:SECTION ]->(f)
                RETURN count(r)

            """

            response = self.knowledgeBase.execute_query(query, params={'data': self.data_img_table[0]})
            print(f"{response} Relationship between Main node and node images tables")