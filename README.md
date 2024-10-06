# TO RUN
1. Run NEO4j Database
2.  Go to RAG_app folder
- to add new data execute
- python run_new_data.py
- if you want to runn RAG system once you added the data
- python run_RAG.py

- Verify the local host
![Alt Text]([https://github.com/MiguelBenalcazar/GraphRag/blob/main/Screenshot%20from%202024-10-06%2021-34-33.png])


# INSTALL PACKAGES

## for re-ranking Cross_Encoders
https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2?text=I+like+you.+I+love+you
cross-encoder/ms-marco-MiniLM-L-12-v2

cross-encoder/ms-marco-TinyBERT-L-2-v2  better

cross-encoder/ms-marco-TinyBERT-L-2 --> better results than both 


## BM25

### https://bm25s.github.io/
### https://link.springer.com/chapter/10.1007/978-3-030-45442-5_4
pip install bm25s[full]



## Ollama 
pip install ollama

This system requires to install ollama service. You can install the system as follows:
https://ollama.com/
https://medium.com/@gabrielrodewald/running-models-with-ollama-step-by-step-60b6f6125807

- you can start ollama service by console, just simply typing ollama
ollama

- install new LLM (Large Language Model) in the computer to run locally
ollama pull model_name

example:
ollama pull llama3
ollama pull phi3

- test ollama 
to test ollama service and a determined model 

ollama run llama3 "your prompt"

## Unstructured Package for extract data from pdf. 
https://pypi.org/project/unstructured/

- Required Packages

pip install unstructured

pip3 install pillow-heif

pip install unstructured-inference

pip install unstructured-pytesseract

pip install "unstructured[all-docs]"


ORC package
https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html

sudo apt-get install tesseract-ocr-eng --> to install option for working with english
 
sudo apt-get install tesseract-ocr-spa --> to install option for working with spanish


## Install spacy
pip install spacy
https://spacy.io/models

https://spacy.io/models/es

both are required 

python -m spacy download es_dep_news_trf  --> for efficiency

python -m spacy download es_core_news_sm  --> for accuracy



## chrome vector database

https://docs.trychroma.com/

pip install chromadb 




## Install langchain_comunity

pip install langchain-community langchain-core

## Install pyPDF2

pip install PyPDF2


## sentence-transformers 
pip install sentence-transformers


## colorlog 6.8.2
pip install colorlog


pip install --upgrade nltk


## llamaIndex

pip install llama-index

pip install llama-index-core

pip install --quiet transformers torch

pip install llama-index-embeddings-openai

pip install llama-index-llms-openai

pip install llama-index-postprocessor-colbert-rerank



https://medium.com/@imabhi1216/implementing-rag-using-langchain-and-ollama-93bdf4a9027c


# NEO4j

## Install
https://neo4j.com/docs/operations-manual/current/installation/
install desktop version too


### 1. In console
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg
echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
sudo apt-get update

### 2. install console - Community Edition
sudo apt-get install neo4j=1:5.22.0

## Once installed
### 1. check status

sudo systemctl status neo4j

### 2. start service
sudo systemctl start neo4j

### 3. stop serviceDefault login is username 'neo4j' and password 'neo4j'
sudo systemctl stop neo4j

### 4. Enable Neo4j to Start on Boot
sudo systemctl enable neo4j

### 5. Disable Neo4j from Starting on Boot
sudo systemctl disable neo4j


### 6. View Neo4j Logs
sudo journalctl -u neo4j


## Configure service web-browser
http://localhost:7474/browser/
Default login is username 'neo4j' and password 'neo4j'





## APOC
if error APOC please go to Desktop APP, select project and plugins tab, install APOC



pip install neo4j
