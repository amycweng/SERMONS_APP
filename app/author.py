from flask import render_template
from flask import request, redirect, url_for
from flask_login import current_user
import re
from io import BytesIO
import base64
from matplotlib.figure import Figure
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
from flask import Blueprint
bp = Blueprint('author', __name__)
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
    citations = Citation.get_by_pubplace("%"+pubplace+"%") 
    actual_qp = QuoteParaphrase.get_actual_by_pubplace("%"+pubplace+"%")
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
    
    prominence = ORCP('pubplace',standard)
    C_P = [sorted(p[0].items(),key=lambda x:x[1],reverse=True) for p in prominence]
    QP_P = [sorted(p[1].items(),key=lambda x:x[1],reverse=True) for p in prominence]    
    
    return render_template('pubplace.html',
                        sermons=metadata,
                        counts=counts,
                        pubplace = pubplace,
                        standard = standard,
                        citations =citations,
                        actual_qp=actual_qp,
                        proximal=proximal,
                        C_P = C_P,
                        QP_P=QP_P)

@bp.route('/pubplace/<pubplace>/edit', methods=['POST','GET'])
def edit_pubplace():
    if request.method == "POST": 
        new = request.form["new"]
        old = request.form['old']
        Metadata.update_pubplace(old,new)
    return redirect(url_for('author.find_pubplace_metadata',pubplace=new))



@bp.route('/author/<author>', methods=['POST','GET'])
def find_author_references(author):
    # aut_tcpIDs = Metadata.get_by_author(author)
    # for s in aut_tcpIDs:
    #     if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
    #     elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    citations = Citation.get_by_aut(author) 
    actual_qp = QuoteParaphrase.get_actual_by_aut(author)
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
    
    prominence = ORCP('author',[author])
    C_P = [sorted(p[0].items(),key=lambda x:x[1],reverse=True) for p in prominence]
    QP_P = [sorted(p[1].items(),key=lambda x:x[1],reverse=True) for p in prominence]    
    
    return render_template('author.html',
                           author=author,
                        # sermons=aut_tcpIDs,
                        citations = citations,
                        actual_qp=actual_qp,
                        proximal = proximal,
                        C_P = C_P,
                        QP_P = QP_P
                        )

@bp.route('/pubyear/<pubyear>', methods=['POST','GET'])
def pubyear(pubyear):
    # aut_tcpIDs = Metadata.get_by_author(author)
    # for s in aut_tcpIDs:
    #     if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
    #     elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    citations = Citation.get_by_pubyear(pubyear) 
    actual_qp = QuoteParaphrase.get_actual_by_pubyear(pubyear)
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
    
    prominence = ORCP('pubyear',[pubyear])
    C_P = [sorted(p[0].items(),key=lambda x:x[1],reverse=True) for p in prominence]
    QP_P = [sorted(p[1].items(),key=lambda x:x[1],reverse=True) for p in prominence]    
    
    return render_template('pubyear.html',
                           pubyear=pubyear,
                        citations = citations,
                        actual_qp=actual_qp,
                        proximal = proximal,
                        C_P = C_P,
                        QP_P = QP_P
                        )

@bp.route('/subject_headings/<subject>', methods=['POST','GET'])
def subject_headings(subject):
    citations = Citation.get_by_subject(subject) 
    actual_qp = QuoteParaphrase.get_actual_by_subject(subject)
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
    
    prominence = ORCP('subjects',[subject])
    C_P = [sorted(p[0].items(),key=lambda x:x[1],reverse=True) for p in prominence]
    QP_P = [sorted(p[1].items(),key=lambda x:x[1],reverse=True) for p in prominence]    
    
    return render_template('subjects.html',
                           subject=subject,
                        citations = citations,
                        actual_qp=actual_qp,
                        proximal = proximal,
                        C_P = C_P,
                        QP_P = QP_P
                        )
    