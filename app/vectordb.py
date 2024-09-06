import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
class Vector_DB:
    def __init__(self, persist_directory='/Users/amycweng/DH/SERMONS_APP/db/data/EEPS_myvectordb'):
        self.persist_directory = persist_directory 
        self.bi_encoder = SentenceTransformer("/Users/amycweng/DH/SERMONS_APP/db/data/EEPS_emanjavacas-MacBERTh_2.0_2024-08-20_08-13-56") 
        self.basic_encoder = SentenceTransformer("multi-qa-mpnet-base-cos-v1") 
        self.client_settings = Settings(is_persistent= True, persist_directory= persist_directory, anonymized_telemetry=False)
        self.queryclient = chromadb.PersistentClient(path= persist_directory, settings= self.client_settings)
        self.bible = self.queryclient.get_collection(name="Bible")
        self.bibleparts = self.queryclient.get_collection(name="BibleParts")
        self.titles = self.queryclient.get_collection(name="Titles")
        self.eras = {"CivilWar":4}
        self.collections = {}
        for era,num in self.eras.items():
            self.collections[era] = {"text":[],"marginalia":[self.queryclient.get_collection(name=f"{era}_margin")]}
            for n in range(num):
                self.collections[era]["text"].append(self.queryclient.get_collection(name=f"{era}_{n}"))
        
    def search(self, query,doc_type='text',k=10):
        q_embedding = self.bi_encoder.encode([query])
        all_results = []
        for era,cdict in self.collections.items():
            for collection in cdict[doc_type]:
                results = collection.query(query_embeddings=[q_embedding], n_results= k,include=["distances"])
                all_results.append(results)
        
        ret = []
        for idx, sublist in enumerate(results['ids']): 
           for pidx,passage_id in enumerate(sublist): 
                sim = 1 - results["distances"][idx][pidx]
                ret.append((passage_id,sim))
        return ret
    
    def search_bible(self, query,k=20):
        q_embedding = self.bi_encoder.encode([query])
        results = self.bible.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances"])
        part_results = self.bibleparts.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances","documents"])
        ret = []
        for idx, sublist in enumerate(results['ids']): 
            for vidx,verse_id in enumerate(sublist): 
                sim = 1 - results["distances"][idx][vidx]
                ret.append((verse_id,sim))
        for idx, sublist in enumerate(part_results['ids']): 
            for vidx,verse_id in enumerate(sublist): 
                sim = 1 - results["distances"][idx][vidx]
                part = results["documents"][idx][vidx]
                ret.append((verse_id,sim,part))
        ret = sorted(ret,key=lambda x:x[1],reverse=True)
        return ret
    
    def search_title(self, query,k=20):
        q_embedding = self.basic_encoder.encode([query])
        results = self.titles.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances"])
        ret = []
        for idx, sublist in enumerate(results['ids']): 
            for vidx,tcpID in enumerate(sublist): 
                sim = 1 - results["distances"][idx][vidx]
                ret.append((tcpID,sim))
        ret = sorted(ret,key=lambda x:x[1],reverse=True)
        return ret
