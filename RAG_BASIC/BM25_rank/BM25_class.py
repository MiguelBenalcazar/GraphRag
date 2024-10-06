import warnings
warnings.filterwarnings("ignore")

import bm25s
from typing import List, Any
import spacy
import Stemmer


class BM25_score:
    '''
        Methods:
        Robertson et al. (method="robertson")
        ATIRE (method="atire")
        BM25L (method="bm25l")
        BM25+ (method="bm25+")
        Lucene (method="lucene")
    '''
    # Class-level caching for loaded models
    spacy_models = {
        "spanish": None,
        "english": None
    }

    def __init__(self, corpus: List[str] = None, path_load: str = None, load: bool = False, method: str = "bm25+", load_corpus: bool = True, language: str = "spanish") -> None:
        self.language = language

        # Load or reuse the spacy model for the language
        if self.spacy_models[language] is None:
            if language == "spanish":
                self.spacy_models["spanish"] = spacy.load("es_dep_news_trf")
            elif language == "english":
                self.spacy_models["english"] = spacy.load("en_core_web_sm")
            else:
                raise ValueError("Language not supported. Choose 'english' or 'spanish'.")
        
        
        self.nlp = self.spacy_models[language]
        self.stemmer = Stemmer.Stemmer(language)

        # Initialize BM25 retriever
        if not load:
            if not corpus:
                raise TypeError("To create a new retriever, please provide a corpus")
            text_cleaned = self.clean_text(corpus)
            corpus_tokens = bm25s.tokenize(text_cleaned, stemmer=self.stemmer)
            self.retriever = bm25s.BM25(corpus=corpus, method=method)
            self.retriever.index(corpus_tokens)
        else:
            if not path_load:
                raise TypeError("Please provide the path to load the retriever")
            self.retriever = bm25s.BM25.load(path_load, load_corpus=load_corpus)

    def __search__(self, query: str, k: int = 5) -> (Any, Any):
        text_cleaned = self.clean_text([query])  # No need to wrap query in another list
        query_tokens = bm25s.tokenize(text_cleaned, stemmer=self.stemmer)
        docs, scores = self.retriever.retrieve(query_tokens, k=k)
        return docs, scores
    
    def save(self, path: str = './BM25_retriever') -> None:
        self.retriever.save(path)
        print(f"Retriever saved in {path}")

    def clean_text(self, corpus: List[str]) -> List[str]:
        if not corpus:
            raise TypeError("Please provide the corpus information")

        txt = []
        # Use nlp.pipe for efficient batch processing
        for doc in self.nlp.pipe(corpus, disable=["ner", "parser"]):  # Disable components not needed
            filtered_tokens = [token.text for token in doc if 
                               not token.is_stop  # remove stop words
                               and not token.is_punct  # remove punctuation
                               and not token.is_space]  # remove spaces
            txt.append(" ".join(filtered_tokens))
        return txt

