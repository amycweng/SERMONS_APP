import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os 
folder = os.getcwd()
class Vector_DB:
    def __init__(self, persist_directory=f'{folder}/app/static/data/VECTORDB'):
        self.persist_directory = persist_directory 
        self.bi_encoder = SentenceTransformer(f"{folder}/app/static/data/EEPS_emanjavacas-MacBERTh_2.0_2024-08-20_08-13-56") 
        self.basic_encoder = SentenceTransformer("msmarco-distilbert-base-v4") 
        self.client_settings = Settings(is_persistent= True, persist_directory= persist_directory, anonymized_telemetry=False)
        self.queryclient = chromadb.PersistentClient(path= persist_directory, settings= self.client_settings)
        self.titles = self.queryclient.get_collection(name="Titles")
        self.bible = self.queryclient.get_collection(name="Bible")
        self.bibleparts = self.queryclient.get_collection(name="BibleParts")
        self.eras = {"pre-Elizabethan_margin": 1,"Elizabethan_margin":2,"Jacobean_margin":2,
                     "Carolinian_margin":2,"CivilWar_margin":1,"Interregnum_margin":1,
                     "CharlesII_margin":2,"JamesII_margin":1,"WilliamAndMary_margin":1}
        self.collections = {}
        for era,num in self.eras.items():
            self.collections[era] = []
            for n in range(num):
                self.collections[era].append(n)
        
    def search(self, query,doc_type='Marginal',k=10):
        q_embedding = self.basic_encoder.encode([query])
        ret = {"In-Text":[],"Marginal":[]}
        for era,clist in self.collections.items():
            if doc_type == "In-Text" and "margin" in era: continue 
            elif doc_type == "Marginal" and "margin" not in era: continue 
            for cidx in clist: 
                collection = self.queryclient.get_collection(name=f"{era}_{cidx}")
                results = collection.query(query_embeddings=q_embedding.tolist(), n_results= k,include=["distances","documents"])
                if cidx is None: 
                    key = era 
                else: 
                    key = f"{era}_{cidx}"
                for idx, sublist in enumerate(results['ids']): 
                    for pidx,passage_id in enumerate(sublist): 
                        sim = 1 - results["distances"][idx][pidx]
                        docs = results['documents'][idx][pidx]
                        if "margin" not in era: 
                            ret["In-Text"].append((f"{key}_{passage_id}", sim, docs)) 
                        else: 
                            ret["Marginal"].append((f"{key}_{passage_id}", sim, docs))      
        
        ret["In-Text"] = sorted(ret["In-Text"],key=lambda x:x[1],reverse=True)[:k]
        ret["Marginal"] = sorted(ret["Marginal"],key=lambda x:x[1],reverse=True)[:k]
        return ret
    
    def search_bible(self, query,k=20):
        q_embedding = self.bi_encoder.encode([query])
        print("FINISHED EMBEDDING")
        results = self.bible.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances"])
        print("FINISHED QUERYING - COMPLETE")
        part_results = self.bibleparts.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances"])
        print("FINISHED QUERYING - PARTIAL")
        ret = []
        found = {}
        for idx, sublist in enumerate(part_results['ids']): 
            for vidx,verse_id in enumerate(sublist): 
                sim = 1 - part_results["distances"][idx][vidx]
                verse_id, pidx = verse_id.split(" - ") 
                if verse_id in found: 
                    if sim > found[verse_id][0]: 
                        found[verse_id] = (sim,pidx)
                else: 
                    found[verse_id] = (sim,pidx) 
                # ret.append((verse_id,sim,pidx))
        for idx, sublist in enumerate(results['ids']): 
            for vidx,verse_id in enumerate(sublist): 
                sim = 1 - results["distances"][idx][vidx]
                if verse_id not in found: 
                    ret.append((verse_id,sim))
                elif sim > found[verse_id][0]: 
                    ret.append((verse_id,sim))
                    found[verse_id] = (None,None)
        for verse_id, item in found.items(): 
            if item[0] is None: continue 
            ret.append((verse_id,item[0],item[1]))
                    
        ret = sorted(ret,key=lambda x:x[1],reverse=True)[:k]
        return ret
    
    def search_title(self, query,k=50):
        q_embedding = self.basic_encoder.encode([query])
        results = self.titles.query(query_embeddings= q_embedding.tolist(), n_results= k, include=["distances"])
        ret = []
        for idx, sublist in enumerate(results['ids']): 
            for vidx,tcpID in enumerate(sublist): 
                sim = 1 - results["distances"][idx][vidx]
                ret.append((tcpID,sim))
        ret = sorted(ret,key=lambda x:x[1],reverse=True)
        return ret
