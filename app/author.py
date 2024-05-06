from flask import render_template
from flask import request, redirect, url_for

import re
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
from flask import Blueprint
bp = Blueprint('author', __name__)

@bp.route('/<author>/<tcpID>', methods=['POST','GET'])
def find_author_references(author,tcpID):
    author,tcpIDs = Metadata.get_tcpIDs_by_aut(author)[0]
    segment = []
    metadata = []
    qp_candidates = []
    c_dict = {'in-text':{0:[]},'marginal':{},'t_outlier':{0:[]},'m_outlier':{}}
    citations = []
    for tcpID in tcpIDs.split("; "):
        metadata.append(Metadata.get_by_tcpID(tcpID)[0])
        citations_list = Citation.get_by_tcpID(tcpID)
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

            qp_candidates = QuoteParaphrase.get_by_tcpID(tcpID)

    has_citations_text, has_citations_margin = False, False
    if len(c_dict["in-text"][0]) > 0: has_citations_text = True 
    if sum([len(_) for _ in c_dict["marginal"].values()]) > 0: has_citations_margin = True 
    t_outlier, m_outlier = False, False
    if len(c_dict['t_outlier'][0]) > 0: t_outlier = True
    for nidx, c_list in c_dict["m_outlier"].items(): 
        if len(c_list) > 0:
            m_outlier = True 
    
    qp_segments = {}
    for entry in qp_candidates: 
        key = (entry.tcpID,entry.sidx,entry.loc)
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
                        qp_candidates=qp_candidates,
                        qp_segments=qp_segments,
                        citations=citations,
                        c_dict=c_dict,
                        m_outlier = m_outlier,
                        t_outlier = t_outlier,
                        has_citations_text = has_citations_text,
                        has_citations_margin=has_citations_margin)
    