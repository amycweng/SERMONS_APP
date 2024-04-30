from flask import render_template
from flask import request, redirect, url_for
import os 
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrse
from .models.metadata import Metadata

from flask import Blueprint
bp = Blueprint('sermon', __name__)

@bp.route('/<tcpID>/citations', methods=['POST','GET'])
def get_citations(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    citations = Citation.get_by_tcpID(tcpID) 
    hits =
    return render_template('sermon.html',
                        citations = citations,
                        metadata=metadata)

@bp.route('/<tcpID>/citations/<int:sidx>/<loc>/edit', methods=['POST','GET'])
def edit_citations(tcpID,sidx,loc):
    if loc != "In-Text": loc = f"Note {loc}"
    citations = Citation.get_by_tcpID_sidx_loc(tcpID,sidx,loc) 
    return render_template('citation_edit.html',
                        citations = citations)

@bp.route('/<tcpID>/<int:sidx>', methods=['POST','GET'])
def get_segment_and_notes(tcpID,sidx):
    metadata = Metadata.get_by_tcpID(tcpID)
    segment = Text.get_by_tcpID_sidx(tcpID,sidx)
    notes = Marginalia.get_by_tcpID_sidx(tcpID,sidx)
    has_notes = True 
    if len(notes) == 0: has_notes = False 
    citations = Citation.get_by_tcpID_sidx(tcpID,sidx)
    c_dict = {'in-text':{0:[]},'marginal':{},'t_outlier':{0:[]},'m_outlier':{}}
    for c in citations: 
        if c.loc == "In-Text": 
            c_dict["in-text"][0].append(c.citation)
            if c.outlier is not None: 
                c_dict["t_outlier"][0].append(c.outlier)
        else: 
            nidx = int(c.loc.split(" ")[-1])
            if nidx not in c_dict['marginal']: 
                c_dict['marginal'][nidx] = []
                c_dict['m_outlier'][nidx] = []
            c_dict["marginal"][nidx].append(c.citation)
            if c.outlier is not None: 
                c_dict["m_outlier"][nidx].append(c.outlier)
    t_outlier, m_outlier = False, False
    if len(c_dict['t_outlier'][0]) > 0: t_outlier = True
    for nidx, c_list in c_dict["m_outlier"].items(): 
        if len(c_list) > 0:
            m_outlier = True 
    return render_template('segment.html',
                        metadata=metadata,
                        s = segment[0],
                        notes=notes,
                        citations=c_dict,
                        m_outlier = m_outlier,
                        t_outlier = t_outlier,
                        has_notes = has_notes)

@bp.route('/paraphrases')
def semantic_search():
    return None