import chromadb
from chromadb.config import Settings
class Vector_DB:
    def __init__(self, persist_directory='/Users/amycweng/DH/SERMONS_APP/db/data/chromadb'):
        self.persist_directory = persist_directory             
        self.client_settings = Settings(is_persistent= True, persist_directory= persist_directory, anonymized_telemetry=False)
        eras = ["pre-Elizabethan"]
        self.collections = {"pre-Elizabethan":{"text":[],"marginalia":[]}}
        self.queryclient = chromadb.PersistentClient(path= persist_directory, settings= self.client_settings)
        for era in eras:
            self.collections[era]["text"] = self.queryclient.get_collection(name=era)
            self.collections[era]["marginalia"] = self.queryclient.get_collection(name=f"{era}_marginalia")
        
    def search(self, collection_name, query,doc_type='text',k=10):
        collection = self.collections[collection_name][doc_type]
        results = collection.query(query_texts= [query], n_results= k)
        ret = []
        for idx, sublist in enumerate(results['documents']): 
            for i, item in enumerate(sublist): 
                meta = results['metadatas'][idx][i]
                sidx = meta['chunk_id']
                tcpID = meta['tcpID']
                if int(meta['is_note']) == -1: 
                    loc = 'In-Text'
                else: loc = f"Note {meta['is_note']}"
                ret.append((item,tcpID,sidx,loc))
        return ret
