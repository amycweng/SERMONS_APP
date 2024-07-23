from flask import render_template
from flask import request, redirect, url_for

import re
from io import BytesIO
import base64
from matplotlib.figure import Figure
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
from flask import Blueprint
bp = Blueprint('author', __name__)

@bp.route('/pubplace/<pubplace>', methods=['POST','GET'])
def find_pubplace_metadata(pubplace):
    sermons = Metadata.get_all()
    pubplaces = Metadata.get_pubplace_phrase(pubplace)
    pubplaces = {s[0]:s[1] for s in pubplaces}
    pubplaces_orig = {}
    standard = {}
    metadata = []
    for s in sermons: 
        if s.tcpID not in pubplaces: continue
        metadata.append(s)
        if s.pubplace not in pubplaces_orig: 
            pubplaces_orig[s.pubplace] = 0
            standard[s.pubplace] = {} 
        pubplaces_orig[s.pubplace] += 1
        standard[s.pubplace] = pubplaces[s.tcpID].split("; ") 
    
    counts = sorted(pubplaces_orig.items(),key = lambda x:x[1],reverse=True)
    
    return render_template('pubplace.html',
                        sermons=metadata,
                        counts=counts,
                        pubplace = pubplace,
                        standard = standard)

@bp.route('/pubplace/<pubplace>/edit', methods=['POST','GET'])
def edit_pubplace(pubplace):
    if request.method == "POST": 
        new = request.form["new"]
        old = request.form['old']
        Metadata.update_pubplace(old,new)
    return redirect(url_for('author.find_pubplace_metadata',pubplace=new))


@bp.route('/author/<author>', methods=['POST','GET'])
def find_author_references(author):
    aut_tcpIDs = Metadata.get_tcpIDs_by_aut(author)
    segment = []
    metadata = []
    possible_qp = {}
    c_dict = {'in-text':{0:[]},'marginal':{},'t_outlier':{0:[]},'m_outlier':{}}
    citations = []
    citations_list = Citation.get_by_aut(author)
    for c in citations_list: 
        if c.loc == "In-Text": 
            c_dict["in-text"][0].append(c.citation)
            citations.append(c)
            if c.outlier is not None: 
                c_dict["t_outlier"][0].append(c.outlier)
        else: 
            nidx = int(c.loc.split(" ")[-1])
            if nidx not in c_dict['marginal']: 
                c_dict['marginal'][nidx] = []
                c_dict['m_outlier'][nidx] = []
            c_dict["marginal"][nidx].append(c.citation)
            citations.append(c)
            if c.outlier is not None: 
                c_dict["m_outlier"][nidx].append(c.outlier)
    for author, tcpID in aut_tcpIDs:
        metadata.append(Metadata.get_by_tcpID(tcpID)[0])
        qp = QuoteParaphrase.get_by_tcpID(tcpID)
        possible_qp[tcpID] = qp

    has_citations_text, has_citations_margin = False, False
    if len(c_dict["in-text"][0]) > 0: has_citations_text = True 
    if sum([len(_) for _ in c_dict["marginal"].values()]) > 0: has_citations_margin = True 
    t_outlier, m_outlier = False, False
    if len(c_dict['t_outlier'][0]) > 0: t_outlier = True
    for nidx, c_list in c_dict["m_outlier"].items(): 
        if len(c_list) > 0:
            m_outlier = True 
    
    actual_qp = QuoteParaphrase.get_actual_by_aut(author)
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
    
    qp_candidates = []
    for tcpID, items in possible_qp.items(): 
        for entry in items: 
            key = (entry.tcpID,entry.sidx,entry.loc)
            found = False 
            for a in actual_qp: 
                if a[0] == entry.tcpID and a[1] == entry.sidx and a[2] == entry.loc and a[3] == entry.label: 
                    found = True 
                    break
            if not found: 
                qp_candidates.append(entry)
            if entry.loc == "In-Text": 
                segment = Text.get_by_tcpID_sidx(entry.tcpID,entry.sidx)[0].tokens
                qp_segments[key] = segment 
            else:
                nidx = int(entry.loc.split(" ")[-1])
                segment = Marginalia.get_by_tcpID_sidx_nidx(entry.tcpID,entry.sidx,nidx)[0].tokens
                qp_segments[key] = segment

    return render_template('author.html',
                        author=author,
                        metadata=metadata,
                        segment = segment,
                        actual_qp=actual_qp,
                        qp_candidates=qp_candidates,
                        qp_segments=qp_segments,
                        citations=citations,
                        c_dict=c_dict,
                        m_outlier = m_outlier,
                        t_outlier = t_outlier,
                        has_citations_text = has_citations_text,
                        has_citations_margin=has_citations_margin)
    