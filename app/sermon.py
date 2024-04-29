from flask import render_template
from flask import request, redirect, url_for
import os 
from .models.text import Text, Marginalia
from .models.citation import Citation
from .models.metadata import Metadata

from flask import Blueprint
bp = Blueprint('sermon', __name__)

@bp.route('/<tcpID>/citations', methods=['POST','GET'])
def get_citations(tcpID):
    metadata = Metadata.get_by_tcpID(tcpID)
    citations = Citation.get_by_tcpID(tcpID) 
    return render_template('citation.html',
                        citations = citations,
                        metadata=metadata)

@bp.route('/<tcpID>/<int:sidx>', methods=['POST','GET'])
def get_segment_and_notes(tcpID,sidx):
    metadata = Metadata.get_by_tcpID(tcpID)
    segment = Text.get_by_tcpID_sidx(tcpID,sidx)
    notes = Marginalia.get_by_tcpID_sidx(tcpID,sidx)
    has_notes = True 
    if len(notes) == 0: has_notes = False 
    citations = Citation.get_by_tcpID_sidx(tcpID,sidx)
    c_dict = {'in-text':[],'marginal':[],'t_outlier':[],'m_outlier':[]}
    for c in citations: 
        if c.loc == "In-Text": 
            c_dict["in-text"].append(c.citation)
            if c.outlier is not None: 
                c_dict["t_outlier"].append(c.outlier)
        else: 
            c_dict["marginal"].append(c.citation)
            if c.outlier is not None: 
                c_dict["m_outlier"].append(c.outlier)
    t_outlier, m_outlier = False, False
    if len(c_dict['t_outlier']) > 0: t_outlier = True 
    if len(c_dict['m_outlier']) > 0: m_outlier = True 
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