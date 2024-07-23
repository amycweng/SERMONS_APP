from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata

def get_books_citations():
    items = {}
    citations = Citation.get_all()
    for c in citations: 
        c = c.citation.split("; ")[0]
        items[c] = True 
        c = c.split(".")[0]
        items[c] = True 
        c = c.split(" ")[:-1]
        items[" ".join(c)] = True 
    return sorted(list(items.keys()))