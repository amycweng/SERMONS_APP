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
    possible_qp = QuoteParaphrase.get_by_tcpID(tcpID)
    qp_segments = {}
    for entry in possible_qp: 
        if entry.loc == "In-Text": 
            segment = Text.get_by_tcpID_sidx(entry.tcpID,entry.sidx)[0].tokens
            qp_segments[(entry.tcpID,entry.sidx,entry.loc)] = segment 
        else:
            nidx = int(entry.loc.split(" ")[-1])
            segment = Marginalia.get_by_tcpID_sidx_nidx(entry.tcpID,entry.sidx,nidx)[0].tokens
            qp_segments[(entry.tcpID,entry.sidx,entry.loc)] = segment 
    return render_template('sermon.html',
                        citations = citations,
                        metadata=metadata,
                        possible_qp=possible_qp,
                        qp_segments=qp_segments
                        )

@bp.route('/<tcpID>', methods=['POST','GET'])
def full_text(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    segments = Text.get_by_tcpID(tcpID)
    notes = Marginalia.get_by_tcpID(tcpID)
    return render_template('sermon_full.html',
                        metadata=metadata,
                        segments = segments,
                        notes=notes)

@bp.route('/<tcpID>/references/<int:sidx>/<loc>/edit', methods=['POST','GET'])
def edit_citations(tcpID,sidx,loc):
    if loc != "In-Text": loc = f"Note {loc}"
    citations = Citation.get_by_tcpID_sidx_loc(tcpID,sidx,loc) 
    return render_template('citation_edit.html',
                        citations = citations)


@bp.route('/<tcpID>/remove/<int:sidx>/<int:vidx>', methods=['POST','GET'])
def remove_qp(tcpID,sidx,vidx):
    if request.method == 'POST':
        QuoteParaphrase.remove_by_tcpID_sidx_vidx(tcpID,sidx,vidx)  
        page = request.form['page']
        if page == 'segment':
            return redirect(url_for('sermon.get_segment_and_notes',tcpID=tcpID,sidx=sidx))
    return redirect(url_for('sermon.get_citations',tcpID=tcpID))


@bp.route('/index', methods=['POST','GET'])
def get_all():
    citations = Citation.get_all()
    return render_template('scriptural_index.html',
                        citations = citations)

@bp.route('/index/<label>', methods=['POST','GET'])
def get_by_label(label):
    citations = Citation.get_by_label(label)
    label = re.sub("\%","",label)
    return render_template('scriptural_index.html',
                        citations = citations,
                        label=label)


@bp.route('/<tcpID>/<int:sidx>', methods=['POST','GET'])
def get_segment_and_notes(tcpID,sidx):
    metadata = Metadata.get_by_tcpID(tcpID)
    segment = []
    s = Text.get_by_tcpID_sidx(tcpID,sidx)[0]
    sidx,loc_type,loc = s.sidx,s.loc_type,s.loc
    segment.append((s.tokens, s.lemmatized,"In-Text"))
    notes = Marginalia.get_by_tcpID_sidx(tcpID,sidx)
    for n in notes: 
        segment.append((n.tokens, n.lemmatized,f"Note {n.nidx}"))
    
    citations_list = Citation.get_by_tcpID_sidx(tcpID,sidx)
    c_dict = {'in-text':{0:[]},'marginal':{},'t_outlier':{0:[]},'m_outlier':{}}
    citations = []
    for c in citations_list: 
        if c.loc == "In-Text": 
            c_dict["in-text"][0].append(c.citation)
            citations.append((c.citation,c.replaced,"In-Text"))
            if c.outlier is not None: 
                c_dict["t_outlier"][0].append(c.outlier)
        else: 
            nidx = int(c.loc.split(" ")[-1])
            if nidx not in c_dict['marginal']: 
                c_dict['marginal'][nidx] = []
                c_dict['m_outlier'][nidx] = []
            c_dict["marginal"][nidx].append(c.citation)
            citations.append((c.citation,c.replaced,c.loc))
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
    possible_qp = QuoteParaphrase.get_by_tcpID_sidx(tcpID,sidx)
    return render_template('segment.html',
                        metadata=metadata,
                        segment = segment,
                        sidx =sidx,
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
        verse_text, phrases = QuoteParaphrase.get_bible_verse(verse_id)                

        return render_template('search.html',
                               verse_ids=verse_ids,
                               verse_id=verse_id,
                               verse_text=verse_text, 
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)

@bp.route('/search/verse', methods=['POST','GET'])
def semantic_search_verse():
    verse_ids = QuoteParaphrase.get_bible_verse_ids()
    if request.method == 'POST':
        verse_id = request.form['verse']
        if len(verse_id) == 0: 
            verse_text, phrases = None,[]
        else: 
            verse_text, phrases = QuoteParaphrase.get_bible_verse(verse_id)    
        phrase = request.form['phrase']
        k = int(request.form['k'])
        results = QuoteParaphrase.search_bible_phrase('pre-Elizabethan',phrase,'text',k)
        m_k = int(request.form['m_k'])
        marginal_results = QuoteParaphrase.search_bible_phrase('pre-Elizabethan',phrase,'marginalia',m_k)
        return render_template('search.html',
                               verse_ids=verse_ids,
                               results=results,
                               phrase=phrase,
                               marginal_results = marginal_results,
                               verse_id=verse_id,
                               verse_text=verse_text,
                               phrases=phrases)
    return render_template('search.html',verse_ids=verse_ids)