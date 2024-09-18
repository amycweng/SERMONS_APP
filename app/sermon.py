from flask import render_template
from flask import request, redirect, url_for
from flask_login import current_user
import re
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase,Bible
from .models.metadata import Metadata
from .lib import *
from flask import Blueprint
bp = Blueprint('sermon', __name__)
import os,json
folder = os.getcwd()
 

def ORCP(etype,entities): 
    with open(f"{folder}/app/static/data/ORCP/{etype}_citations.json") as file: 
        orcp_C = json.load(file)
    with open(f"{folder}/app/static/data/ORCP/{etype}_QP.json") as file: 
        orcp_QP = json.load(file)
    ret = [[{},{}],[{},{}],[{},{}],[{},{}]]
    for e in entities: 
        for idx in range(4): 
            if e in orcp_C[idx]:  
                for key in orcp_C[idx][e]:  
                    ret[idx][0][key] = round(orcp_C[idx][e][key],4)
            if e in orcp_QP[idx]:  
                for key in orcp_QP[idx][e]:
                    ret[idx][1][key] = round(orcp_QP[idx][e][key],4)
    print(f"FINISHED GETTING {etype} DATA")
    return ret

@bp.route('/<tcpID>/references', methods=['POST','GET'])
def get_citations(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    for s in metadata:
        if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
        elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    citations = Citation.get_by_tcpID(tcpID) 
    biblever = Citation.get_ver_by_tcpID(tcpID)
    unique_aut = Metadata.get_aut_by_tcpID(tcpID)
    actual_qp = QuoteParaphrase.get_actual_by_tcpID(tcpID)
    proximal = {int(c.sidx): [] for c in citations}
    for qp in actual_qp: 
        if qp.loc == -1: 
            qp.loc = "In-Text"
        else: 
            qp.loc = f"Note {qp.loc}"
        if qp.sidx in proximal: 
            proximal[qp.sidx].append(qp.verse_id)
        else: 
            for i in range(1,3): 
                if qp.sidx-i in proximal: 
                    proximal[qp.sidx-i].append(qp.verse_id)
                if qp.sidx+i in proximal:
                    proximal[qp.sidx+i].append(qp.verse_id)
    for sidx, items in proximal.items():
        proximal[sidx] = "; ".join(list(set(items)))
    
    tcpIDs = {c.tcpID:None for c in citations}
    tcpIDs.update({q.tcpID:None for q in actual_qp})
    prominence = ORCP('tcpIDpub',tcpIDs)
    C_P = [sorted(p[0].items(),key=lambda x:x[1],reverse=True) for p in prominence]
    QP_P = [sorted(p[1].items(),key=lambda x:x[1],reverse=True) for p in prominence]    
    
    return render_template('sermon.html',
                        citations = citations,
                        unique_aut=unique_aut,
                        actual_qp=actual_qp,
                        proximal = proximal,
                        biblever=biblever,
                        metadata=metadata,
                        C_P = C_P,
                        QP_P = QP_P
                        )

@bp.route('/<tcpID>', methods=['POST','GET'])
def full_text(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    names = Text.get_section_names(tcpID) 
    for s in metadata:
        if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
        elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    if len(metadata) == 1:
        metadata = metadata[0]      
        segments = Text.get_by_tcpID(tcpID)
        notes = Marginalia.get_by_tcpID(tcpID)
        unique_aut = Metadata.get_aut_by_tcpID(tcpID)
        return render_template('sermon_full.html',
                            metadata=metadata,
                            unique_aut=unique_aut,
                            segments = segments,
                            names=names,
                            notes=notes)
    else: 
        return redirect(url_for('index.index',tcpID=tcpID))

@bp.route('/<tcpID>/references/<int:sidx>/<loc>/<int:cidx>/remove', methods=['POST','GET'])
def remove_citation(tcpID,sidx,loc,cidx):
    Citation.remove_citation(tcpID,sidx,loc,cidx) 
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/references/<int:sidx>/<loc>/edit', methods=['POST','GET'])
def edit_citation(tcpID,sidx,loc):
    if request.method == "POST": 
        new = request.form['new_citation']
        phrase = request.form['new_phrase']
        cidx = int(request.form['cidx'])
        orig_cidx = int(request.form['orig_cidx'])
        if cidx != orig_cidx: 
            Citation.update_index(tcpID,sidx,loc,cidx)
        if len(new) > 0: 
            Citation.update_text(tcpID,sidx,loc,cidx,new)
        if len(phrase) > 0: 
            Citation.update_phrase(tcpID,sidx,loc,cidx,phrase)
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/references/version', methods=['POST','GET'])
def edit_version(tcpID):
    if request.method == "POST": 
        ver = request.form['ver']
        sidx = request.form['sidx']
        current = Citation.get_ver_by_tcpID(tcpID)
        if current == 'Unknown': 
            Citation.add_ver(tcpID,ver)
        else: 
            Citation.update_ver(tcpID,ver)
        return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))


@bp.route('/<tcpID>/references/<int:sidx>/add', methods=['POST','GET'])
def add_citation(tcpID,sidx):
    if request.method == "POST": 
        loc = request.form['loc']
        cidx = int(request.form['cidx'])
        citation = request.form['parsed']
        original = request.form['orig']
        Citation.add_citation(tcpID,sidx,loc,cidx,citation,original)
    return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))

@bp.route('/<tcpID>/add/<int:sidx>/<loc>/<verse_id>', methods=['POST','GET'])
def add_qp(tcpID,sidx,loc,verse_id):
    if request.method == 'POST':
        phrase = request.form['phrase']
        score = str(request.form['score'])
        QuoteParaphrase.add_qp(tcpID,sidx,loc,verse_id,score,phrase)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
        elif page == "search": 
            return redirect(url_for('sermon.semantic_search_verse_get',verse_id=verse_id))
        elif page == "search_bible":
            phrase = request.form['phrase'] 
            return redirect(url_for('sermon.search_in_bible',tcpID=tcpID,verse_id=verse_id,sidx=sidx,phrase=phrase))
        elif page == "index":
            searchlabel = request.form['searchlabel'] 
            verse_id = request.form['verse_id'] 
            if searchlabel == "": searchlabel = "None"
            if verse_id == "": verse_id = "None"
            return redirect(url_for('sermon.get_all_redirect',book=searchlabel,verse_id=verse_id))
        else: return redirect(url_for('sermon.get_citations',tcpID=tcpID))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))

@bp.route('/<tcpID>/remove/qp/<int:sidx>/<loc>/<verse_id>', methods=['POST','GET'])
def remove_actual_qp(tcpID,sidx,loc,verse_id):
    if request.method == 'POST':
        QuoteParaphrase.remove_actual_qp(tcpID,sidx,loc,verse_id)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
        elif page == "search": 
            return redirect(url_for('sermon.semantic_search_verse_get',verse_id=verse_id))
        elif page == "index":
            searchlabel = request.form['searchlabel'] 
            verse_id = request.form['verse_id'] 
            if searchlabel == "": searchlabel = "None"
            if verse_id == "": verse_id = "None"
            return redirect(url_for('sermon.get_all_redirect',book=searchlabel,verse_id=verse_id))
        else: 
            return redirect(url_for('sermon.get_citations',tcpID=tcpID))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))



@bp.route('/segment/<tcpID>/<int:sidx>', methods=['POST','GET'])
def get_segment_and_notes(tcpID,sidx):
    metadata = Metadata.get_by_tcpID(tcpID)
    for s in metadata:
        if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
        elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    segment = []
    locations = ["In-Text"]
    s = Text.get_by_tcpID_sidx(tcpID,sidx)[0]
    unique_aut = Metadata.get_aut_by_tcpID(tcpID)
    sidx,loc_type,loc = s.sidx,s.loc_type,s.loc
    orig = s.tokens
    orig = re.sub("\<NOTE\>","&lt;NOTE&gt;",orig)
    clean = re.sub(r"\<\/i\>|\<NOTE\>|NONLATINALPHABET|\<i\>","",s.tokens)
    clean = re.sub(r"\s+"," ",clean)
    clean = clean.strip(" ")
    segment.append((orig, clean,"In-Text"))

    notes = Marginalia.get_by_tcpID_sidx(tcpID,sidx)
    for n in notes: 
        segment.append((n.tokens, None,f"Note {n.nidx}"))
        locations.append(f"Note {n.nidx}")
    nextsegment = len(Text.get_by_tcpID_sidx(tcpID,sidx+1))

    biblever = Citation.get_ver_by_tcpID(tcpID)
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
    
    proximal = []
    actual_qp = []
    all_qp = QuoteParaphrase.get_actual_by_tcpID(tcpID)
    for qp in all_qp:
        if int(qp.loc) == -1: 
            qp.loc = "In-Text"
        else: 
            qp.loc = f"Note {loc}"
        if qp.sidx == sidx: actual_qp.append(qp)
        # a window of two segments 
        elif abs(qp.sidx-sidx) <= 2: proximal.append(qp.verse_id)
    proximal = "<br>* ".join(proximal)
    if len(proximal) == 0: 
        proximal = None 
    if request.method == "POST":
        search = request.form['phrase']
        phrase_loc = request.form['loc']
        k = int(request.form['k'])
        results = Bible.search_in_bible(search,k)
        qp_candidates = []
        for item in results: 
            verse_id, score = item[:2]
            v = Bible.get_bible_verse_by_id(verse_id)[0]
            if len(item) == 2:
                part = v.verse_text
                scope = "Complete"
            elif len(item) == 3: 
                pidx = int(item[2])
                parts = re.split(r"\;|\:|\?|\.",v.verse_text)
                parts = [p.strip(" ") for p in parts if len(p.strip(" ").split(" ")) >= 5]
                part = parts[pidx]
                scope = "Partial"
            qp_candidates.append({
                "verse_id": verse_id,
                "verse_text": part,
                "score":score,
                "scope": scope 
            })
    else:
        qp_candidates = None 
        search = None 
        phrase_loc = None     
    return render_template('segment.html',
                           method=request.method,
                        metadata=metadata,
                        biblever=biblever,
                        locations=locations,
                        nextsegment=nextsegment,
                        tcpID=tcpID,
                        unique_aut=unique_aut,
                        segment = segment,
                        sidx =sidx,
                        phrase=search,
                        actual_qp=actual_qp,
                        qp_candidates=qp_candidates,
                        phrase_loc=phrase_loc,
                        loc_type=loc_type,
                        proximal = proximal,
                        loc=loc,
                        notes=notes,
                        citations=citations,
                        c_dict=c_dict,
                        m_outlier = m_outlier,
                        t_outlier = t_outlier,
                        has_citations_text = has_citations_text,
                        has_citations_margin=has_citations_margin)


@bp.route('/search', methods=['POST','GET'])
def semantic_search():
    with open(f"{folder}/app/static/data/verse_ids.json","r") as file: 
        verse_ids = json.load(file)
    if request.method == 'POST':
        verse_id = None 
        page_type = request.form['page']
        category = request.form['category']
        k = int(request.form['k'])
        actual_qp = None 
        qp_candidates = None 
        text_results, m_results = None, None 
        if page_type == "verse": 
            verse_id = request.form['verse']
            actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
            actual_qp_keys = {}
            for item in actual_qp: 
                actual_qp_keys[(item.tcpID,item.sidx,item.loc,item.verse_id)]
        elif page_type == "phrase": 
            phrase = request.form['phrase']
            if category == "Bibles": 
                print(category, phrase)
                results = Bible.search_in_bible(phrase,k)
                qp_candidates = []
                for item in results: 
                    verse_id, score = item[:2]
                    v = Bible.get_bible_verse_by_id(verse_id)[0]
                    if len(item) == 2:
                        part = v.verse_text
                        scope = "Complete"
                    elif len(item) == 3: 
                        pidx = int(item[2])
                        parts = re.split(r"\;|\:|\?|\.",v.verse_text)
                        parts = [p.strip(" ") for p in parts if len(p.strip(" ").split(" ")) >= 5]
                        part = parts[pidx]
                        scope = "Partial"
                    qp_candidates.append({
                        "verse_id": verse_id,
                        "verse_text": part,
                        "score":score,
                        "scope": scope 
                    })
            else:
                results = Bible.search_bible_phrase(phrase,category,k)
                if len(results["Marginal"]) > 0: 
                    m_results = []
                    for _, sim, docs in results["Marginal"]: 
                        docs = docs.split(";")
                        key = docs[0].split("_")
                        text = QuoteParaphrase.get_marginal_hits_by_ids(key[0],int(key[1]),int(key[2]))
                        for d in docs: 
                            d = d.split("_")
                            m_results.append({'tcpID':d[0],'sidx':d[1],'loc':f"Note {d[2]}", 'text':text, 'score':sim})
        return render_template('search.html',
                               phrase=phrase,
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               actual_qp = actual_qp,
                               qp_candidates = qp_candidates,
                               text_results = text_results,
                               m_results = m_results)
    return render_template('search.html',verse_ids=verse_ids)

@bp.route('/search/verse/<verse_id>', methods=['POST','GET'])
def semantic_search_verse_get(verse_id):
    verse_ids = Bible.get_bible_verse_ids()
    verse_ids = sorted(verse_ids)
    actual_qp = QuoteParaphrase.get_actual_verse_id(verse_id)
    
    return render_template('search.html',
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               actual_qp=actual_qp)

@bp.route('/search_verse', methods=['POST','GET'])
def semantic_search_verse():
    verse_ids = Bible.get_bible_verse_ids()
    verse_ids = sorted(verse_ids)
    if request.method == 'POST':
        verse_id = request.form['verse_id']   
        phrase = request.form['phrase']
        k = int(request.form['k'])
        results = Bible.search_bible_phrase('pre-Elizabethan',phrase,'text',k)
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
                               standardized=standardized,
                               phrase=phrase,
                               actual_qp = actual_qp,
                               qp_segments = qp_segments,
                               marginal_results = m_results,
                               verse_id=verse_id,
                               vindices=vindices,
                               verse_text=verse_text,
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)
