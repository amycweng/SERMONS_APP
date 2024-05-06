from flask import render_template
from flask import request, redirect, url_for

import re
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
from flask import Blueprint
bp = Blueprint('sermon', __name__)

@bp.route('/<tcpID>/references', methods=['POST','GET'])
def get_citations(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    citations = Citation.get_by_tcpID(tcpID) 
    unique_aut = Metadata.get_aut_by_tcpID(tcpID)
    possible_qp = QuoteParaphrase.get_by_tcpID(tcpID)
    actual_qp = QuoteParaphrase.get_actual_by_tcpID(tcpID)
    qp_candidates = {}
    qp_segments = {}
    for a in actual_qp:
        if a[2] == "In-Text": 
            key = (a[0],a[1],a[2])
            segment = Text.get_by_tcpID_sidx(a[0],a[1])[0].tokens
            qp_segments[key] = segment 
        else:
            nidx = int(a[2].split(" ")[-1])
            segment = Marginalia.get_by_tcpID_sidx_nidx(a[0],a[1],nidx)[0].tokens
            qp_segments[key] = segment 
    for entry in possible_qp: 
        key = (entry.tcpID,entry.sidx,entry.loc)
        found = False 
        for a in actual_qp: 
            if a[0] == entry.tcpID and a[1] == entry.sidx and a[2] == entry.loc: 
                found = True 
                break
        if not found: 
            if key not in qp_candidates: qp_candidates[key] = []
            qp_candidates[key].append(entry.label)
        if entry.loc == "In-Text": 
            segment = Text.get_by_tcpID_sidx(entry.tcpID,entry.sidx)[0].tokens
            qp_segments[key] = segment 
        else:
            nidx = int(entry.loc.split(" ")[-1])
            segment = Marginalia.get_by_tcpID_sidx_nidx(entry.tcpID,entry.sidx,nidx)[0].tokens
            qp_segments[key] = segment 
    return render_template('sermon.html',
                        citations = citations,
                        unique_aut=unique_aut,
                        actual_qp=actual_qp,
                        metadata=metadata,
                        qp_candidates=qp_candidates,
                        qp_segments=qp_segments
                        )

@bp.route('/<tcpID>', methods=['POST','GET'])
def full_text(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    segments = Text.get_by_tcpID(tcpID)
    notes = Marginalia.get_by_tcpID(tcpID)
    unique_aut = Metadata.get_aut_by_tcpID(tcpID)
    return render_template('sermon_full.html',
                        metadata=metadata,
                        unique_aut=unique_aut,
                        segments = segments,
                        notes=notes)

@bp.route('/<tcpID>/references/<int:sidx>/<loc>/<int:cidx>/remove', methods=['POST','GET'])
def remove_citation(tcpID,sidx,loc,cidx):
    Citation.remove_citation(tcpID,sidx,loc,cidx) 
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/references/<int:sidx>/<loc>/edit', methods=['POST','GET'])
def edit_citation(tcpID,sidx,loc):
    if request.method == "POST": 
        new = request.form['new_citation']
        cidx = int(request.form['cidx'])
        orig_cidx = int(request.form['orig_cidx'])
        if cidx != orig_cidx: 
            Citation.update_index(tcpID,sidx,loc,cidx)
        if len(new) > 0: 
            Citation.update_text(tcpID,sidx,loc,cidx,new)
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/references/<int:sidx>/add', methods=['POST','GET'])
def add_citation(tcpID,sidx):
    if request.method == "POST": 
        loc = request.form['loc']
        cidx = int(request.form['cidx'])
        citation = request.form['parsed']
        original = request.form['orig']
        Citation.add_citation(tcpID,sidx,loc,cidx,citation,original)
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/remove/<int:sidx>/<int:vidx>', methods=['POST','GET'])
def remove_qp(tcpID,sidx,vidx):
    if request.method == 'POST':
        QuoteParaphrase.remove_by_tcpID_sidx_vidx(tcpID,sidx,vidx)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
        elif page == 'quoteparaphrase':
            return redirect(url_for('sermon.qp_candidates',tcpID=tcpID,sidx=sidx))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))

@bp.route('/<tcpID>/add/<int:sidx>/<loc>/<verse_id>', methods=['POST','GET'])
def add_qp(tcpID,sidx,loc,verse_id):
    if request.method == 'POST':
        QuoteParaphrase.add_qp(tcpID,sidx,loc,verse_id)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
        elif page == 'quoteparaphrase':
            return redirect(url_for('sermon.qp_candidates',tcpID=tcpID,sidx=sidx))
        elif page == "search": 
            return redirect(url_for('sermon.semantic_search_verse_get',verse_id=verse_id))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))

@bp.route('/<tcpID>/remove/<int:sidx>/<loc>/<verse_id>', methods=['POST','GET'])
def remove_actual_qp(tcpID,sidx,loc,verse_id):
    if request.method == 'POST':
        QuoteParaphrase.remove_actual_qp(tcpID,sidx,loc,verse_id)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
        elif page == 'quoteparaphrase':
            return redirect(url_for('sermon.qp_candidates',tcpID=tcpID,sidx=sidx))
        elif page == "search": 
            return redirect(url_for('sermon.semantic_search_verse_get',verse_id=verse_id))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))

def get_books_citations():
    books = {}
    citations = Citation.get_all()
    for c in citations: 
        c = c.citation.split("; ")[0].split(".")[0]
        c = c.split(" ")[:-1]
        books[" ".join(c)] = True 
    return sorted(list(books.keys()))

@bp.route('/index', methods=['POST','GET'])
def get_all():
    citations, qp_candidates, qp_segments,actual_qp = {},{},{},{}
    variants,verse_text = None, None 
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    books = get_books_citations()
    qp_books = ['Ecclesiastes', 'Susanna', '1 Timothy', '1 Kings', 'Proverbs', 'Song of Solomon', 'Baruch', 'Lamentations', 'Zephaniah', '1 Samuel', 'Ezra', 'Esther', 'Prayer of Manasseh', '1 Chronicles', '1 Maccabees', 'Ephesians', 'Isaiah', 'Leviticus', 'Galatians', '2 Maccabees', 'Wisdom of Solomon', '2 Peter', 'Haggai', '2 Samuel', '1 John', 'Philippians', 'Joshua', '2 Chronicles', 'Deuteronomy', 'Malachi', 'Colossians', 'Revelation', '3 John', 'Ecclesiasticus', 'Romans', 'Mark', 'Joel', 'Exodus', 'Amos', 'Tobit', 'John', '2 Thessalonians', 'Micah', 'Nahum', 'Jude', 'James', '2 Kings', '1 Esdras', 'Genesis', '1 Peter', 'Psalms', 'Zechariah', 'Philemon', '1 Corinthians', '2 Corinthians', 'Jeremiah', 'Titus', '1 Thessalonians', 'Ruth', '2 Timothy', 'Acts of the Apostles', 'Hosea', 'Epistle of Jeremiah', '2 John', 'Judges', 'Nehemiah', '2 Esdras', 'Hebrews', 'Habakkuk', 'Luke', 'Judith', 'Daniel', 'Bel and the Dragon', 'Job', 'Matthew', 'Obadiah', 'Ezekiel', 'Prayer of Azariah', 'Jonah', 'Numbers']
    qp_books = sorted(qp_books) 
    if request.method == 'POST':
        book = request.form['book']
        if len(book) > 0: 
            citations = Citation.get_by_label(book + "%")
            variants = {}
            for c in citations: 
                orig = c.replaced.split(" ")
                if len(orig[0]) == 1: 
                    variants[" ".join(orig[:2])] = True 
                else: 
                    variants[orig[0]] = True 

        verse_id = request.form['verse']
        if len(verse_id) > 0: 
            verse_text, lemmatized,phrases,indices = QuoteParaphrase.get_bible_verse(verse_id)
            actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
            for a in actual_qp:
                if a[2] == "In-Text": 
                    key = (a[0],a[1],a[2])
                    segment = Text.get_by_tcpID_sidx(a[0],a[1])[0].tokens
                    qp_segments[key] = segment 
                else:
                    nidx = int(a[2].split(" ")[-1])
                    segment = Marginalia.get_by_tcpID_sidx_nidx(a[0],a[1],nidx)[0].tokens
                    qp_segments[key] = segment 
            for phrase, idx in phrases:
                vidx = indices[idx]
                possible_qp =  QuoteParaphrase.get_by_vidx(vidx)
                for entry in possible_qp: 
                    key = (entry.tcpID,entry.sidx,entry.loc)
                    found = False 
                    for a in actual_qp: 
                        if a[0] == entry.tcpID and a[1] == entry.sidx and a[2] == entry.loc: 
                            found = True 
                            break
                    if not found: 
                        qp_candidates[key] = phrase
                    if entry.loc == "In-Text": 
                        segment = Text.get_by_tcpID_sidx(entry.tcpID,entry.sidx)[0].tokens
                        qp_segments[key] = segment 
                    else:
                        nidx = int(entry.loc.split(" ")[-1])
                        segment = Marginalia.get_by_tcpID_sidx_nidx(entry.tcpID,entry.sidx,nidx)[0].tokens
                        qp_segments[key] = segment 
        else: verse_id = None 
        return render_template('scriptural_index.html',
                           verse_ids=verse_ids,
                           book=book,
                           verse_text = verse_text,
                           verse_id=verse_id,
                           actual_qp=actual_qp,
                           books=books,
                           qp_books=qp_books,
                           variants=variants, 
                        citations = citations,
                        qp_candidates = qp_candidates,
                        qp_segments = qp_segments)
    return render_template('scriptural_index.html',
                           verse_ids=verse_ids,
                           books=books,
                           qp_books=qp_books)


@bp.route('/<tcpID>/<int:sidx>', methods=['POST','GET'])
def get_segment_and_notes(tcpID,sidx):
    metadata = Metadata.get_by_tcpID(tcpID)
    segment = []
    locations = ["In-Text"]
    s = Text.get_by_tcpID_sidx(tcpID,sidx)[0]
    unique_aut = Metadata.get_aut_by_tcpID(tcpID)
    sidx,loc_type,loc = s.sidx,s.loc_type,s.loc
    segment.append((s.tokens, s.lemmatized,"In-Text"))
    notes = Marginalia.get_by_tcpID_sidx(tcpID,sidx)
    for n in notes: 
        segment.append((n.tokens, n.lemmatized,f"Note {n.nidx}"))
        locations.append(f"Note {n.nidx}")
    
    citations_list = Citation.get_by_tcpID_sidx(tcpID,sidx)
    c_dict = {'in-text':{0:[]},'marginal':{},'t_outlier':{0:[]},'m_outlier':{}}
    citations = []
    for c in citations_list: 
        if c.loc == "In-Text": 
            c_dict["in-text"][0].append(c.citation)
            citations.append((c.citation,c.replaced,"In-Text",c.cidx))
            if c.outlier is not None: 
                c_dict["t_outlier"][0].append(c.outlier)
        else: 
            nidx = int(c.loc.split(" ")[-1])
            if nidx not in c_dict['marginal']: 
                c_dict['marginal'][nidx] = []
                c_dict['m_outlier'][nidx] = []
            c_dict["marginal"][nidx].append(c.citation)
            citations.append((c.citation,c.replaced,c.loc,c.cidx))
            if c.outlier is not None: 
                c_dict["m_outlier"][nidx].append(c.outlier)
    
    has_citations_text, has_citations_margin = False, False
    if len(c_dict["in-text"][0]) > 0: has_citations_text = True 
    if sum([len(_) for _ in c_dict["marginal"].values()]) > 0: has_citations_margin = True 
   
    t_outlier, m_outlier = False, False
    if len(c_dict['t_outlier'][0]) > 0: t_outlier = True
    for nidx, c_list in c_dict["m_outlier"].items(): 
        if len(c_list) > 0:
            m_outlier = True 
    
    possible_qp = QuoteParaphrase.get_by_tcpID(tcpID)
    actual_qp = QuoteParaphrase.get_actual_by_tcpID_sidx(tcpID,sidx)
    qp_candidates = []
    for entry in possible_qp: 
        if tcpID != entry.tcpID: continue
        if sidx != entry.sidx: continue
        found = False 
        for a in actual_qp: 
            if a[0] == tcpID and a[1] == sidx and a[2] == entry.loc: 
                found = True 
        if not found: 
            qp_candidates.append((entry.loc,entry.label,entry.full,entry.phrase,entry.score,entry.vidx))
    
    return render_template('segment.html',
                        metadata=metadata,
                        locations=locations,
                        tcpID=tcpID,
                        unique_aut=unique_aut,
                        segment = segment,
                        sidx =sidx,
                        actual_qp=actual_qp,
                        qp_candidates=qp_candidates,
                        loc_type=loc_type,
                        loc=loc,
                        notes=notes,
                        citations=citations,
                        c_dict=c_dict,
                        m_outlier = m_outlier,
                        t_outlier = t_outlier,
                        has_citations_text = has_citations_text,
                        has_citations_margin=has_citations_margin,
                        possible_qp = possible_qp)


@bp.route('/search', methods=['POST','GET'])
def semantic_search():
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    if request.method == 'POST':
        verse_id = request.form['verse']
        verse_text, lemmatized,phrases,vindices = QuoteParaphrase.get_bible_verse(verse_id)  
        actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
        qp_segments = {}
        for entry in actual_qp: 
            key = (entry[0],entry[1],entry[2])
            if entry.loc == "In-Text": 
                segment = Text.get_by_tcpID_sidx(entry[0],entry[1])[0].tokens
                qp_segments[key] = segment 
            else:
                nidx = int(entry[2].split(" ")[-1])
                segment = Marginalia.get_by_tcpID_sidx_nidx(entry[0],entry[1],nidx)[0].tokens
                qp_segments[key] = segment               
        return render_template('search.html',
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               lemmatized=lemmatized,
                               vindices=vindices,
                               verse_text=verse_text,
                               actual_qp=actual_qp,
                               qp_segments=qp_segments, 
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)

@bp.route('/remove/phrase/<int:vidx>', methods=['POST','GET'])
def remove_bible_phrase(vidx):
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    if request.method == 'POST':
        verse_id = request.form['verse_id']
        QuoteParaphrase.remove_bible_phrase(vidx)
        verse_text, lemmatized, lemmatized, phrases,vindices = QuoteParaphrase.get_bible_verse(verse_id)                
        return render_template('search.html',
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               vindices=vindices,
                               verse_text=verse_text, 
                               lemmatized=lemmatized,
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)

@bp.route('/search/verse/<verse_id>', methods=['POST','GET'])
def semantic_search_verse_get(verse_id):
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    verse_text, lemmatized, phrases,vindices = QuoteParaphrase.get_bible_verse(verse_id)
    actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
    qp_segments = {}
    for entry in actual_qp: 
        key = (entry[0],entry[1],entry[2])
        if entry.loc == "In-Text": 
            segment = Text.get_by_tcpID_sidx(entry[0],entry[1])[0].tokens
            qp_segments[key] = segment 
        else:
            nidx = int(entry[2].split(" ")[-1])
            segment = Marginalia.get_by_tcpID_sidx_nidx(entry[0],entry[1],nidx)[0].tokens
            qp_segments[key] = segment 
    return render_template('search.html',
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               actual_qp=actual_qp,
                               qp_segments=qp_segments,
                               vindices=vindices,
                               lemmatized=lemmatized,
                               verse_text=verse_text,
                               phrases=phrases)

@bp.route('/search/verse', methods=['POST','GET'])
def semantic_search_verse():
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    if request.method == 'POST':
        verse_id = request.form['verse_id']
        if len(verse_id) == 0: 
            verse_text, lemmatized, phrases,vindices = None,None,[],[]
        else: 
            verse_text, lemmatized, phrases,vindices = QuoteParaphrase.get_bible_verse(verse_id)    
        phrase = request.form['phrase']
        k = int(request.form['k'])
        results = QuoteParaphrase.search_bible_phrase('pre-Elizabethan',phrase,'text',k)
        m_k = int(request.form['m_k'])
        marginal_results = QuoteParaphrase.search_bible_phrase('pre-Elizabethan',phrase,'marginalia',m_k)
        actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
        t_results, m_results = [],[]
        for item,tcpID,sidx,loc in results: 
            found = False 
            for a in actual_qp: 
                if a[0] == tcpID and a[1] == sidx and a[2] == loc: 
                    found = True 
                    break
            if not found: 
                t_results.append((item,tcpID,sidx,loc))
        for item,tcpID,sidx,loc in marginal_results: 
            found = False 
            for a in actual_qp: 
                if a[0] == tcpID and a[1] == sidx and a[2] == loc: 
                    found = True 
                    break
            if not found: 
                m_results.append((item,tcpID,sidx,loc))
        qp_segments = {}
        for entry in actual_qp: 
            key = (entry[0],entry[1],entry[2])
            if entry.loc == "In-Text": 
                segment = Text.get_by_tcpID_sidx(entry[0],entry[1])[0].tokens
                qp_segments[key] = segment 
            else:
                nidx = int(entry[2].split(" ")[-1])
                segment = Marginalia.get_by_tcpID_sidx_nidx(entry[0],entry[1],nidx)[0].tokens
                qp_segments[key] = segment 
        return render_template('search.html',
                               verse_ids=verse_ids,
                               results=t_results,
                               lemmatized=lemmatized,
                               phrase=phrase,
                               actual_qp = actual_qp,
                               qp_segments = qp_segments,
                               marginal_results = m_results,
                               verse_id=verse_id,
                               vindices=vindices,
                               verse_text=verse_text,
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)