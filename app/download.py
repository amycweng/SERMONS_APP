from flask import render_template
from flask import request, redirect, url_for, Response
from .models.text import Text, Marginalia
from .models.reference import Citation, QuoteParaphrase
from .models.metadata import Metadata
from .lib import *
import re 
from flask import Blueprint
import csv,zipfile
from io import StringIO,BytesIO
bp = Blueprint('download', __name__)

@bp.route('/citations/download',methods=['POST'])
def download():
    if request.method == 'POST':
        label = request.form['item']
        if len(label) > 0: 
            if '.' in label: 
                citations = Citation.get_by_label(label)
            else: 
                citations = Citation.get_by_label(label + "%")
            print(len(citations), 'citations')
            segments,metadata,other_cited = {},{},{}
            book_counts,aut_counts,year_counts,links = {},{},{},{}
            actual_qp = {}
            verses = {}
            for c in citations: 
                meta = Metadata.get_by_tcpID(c.tcpID)[0]   
                if c.tcpID not in metadata:        
                    metadata[c.tcpID] = meta
                    book_counts[c.tcpID] = 0
                    phase = meta.phase
                    if phase == 2: links[c.tcpID] = f'https://quod.lib.umich.edu/e/eebo2/{c.tcpID}.0001.001?'
                    elif phase == 1: links[c.tcpID] = f'https://quod.lib.umich.edu/e/eebo/{c.tcpID}.0001.001?'
                    else: links[c.tcpID] = None
                book_counts[c.tcpID] += 1 

                if meta.pubyear not in year_counts: year_counts[meta.pubyear] = 0 
                year_counts[meta.pubyear] += 1 
                
                authors = Metadata.get_aut_by_tcpID(c.tcpID)
                for aut in authors: 
                    aut = aut[0]
                    if aut not in aut_counts: aut_counts[aut] = 0
                    aut_counts[aut] += 1 
                
                if c.tcpID not in segments: 
                    segments[c.tcpID] = {}
                
                if c.sidx not in segments[c.tcpID]:
                    segments[c.tcpID][c.sidx] = {}
                    text = Text.get_by_tcpID_sidx(c.tcpID,c.sidx)[0]
                    segments[c.tcpID][c.sidx]["In-Text"] = [text.tokens,f"{text.loc_type} {text.loc}",[]]
                    for n in Marginalia.get_by_tcpID_sidx(c.tcpID,c.sidx): 
                        segments[c.tcpID][c.sidx][f"Note {n.nidx}"] = [n.tokens,f"{text.loc_type} {text.loc}",[]]

                    for item in Citation.get_by_tcpID_sidx(c.tcpID,c.sidx): 
                        loc = item.loc
                        segments[c.tcpID][c.sidx][loc][-1].append(item.citation)
                        if 'Note' in loc: loc = 'Marginal'
                        item = item.citation.split("; ")
                        for i in item: 
                            if label in i: continue
                            if (i,loc) not in other_cited: other_cited[(i,loc)] = 0 
                            other_cited[(i,loc)] += 1 
                            if i in verses: continue
                            if '.' in i: 
                                verse_id = i + " (KJV)"
                                if 'Acts' in verse_id: verse_id = re.sub('Acts','Acts of the Apostles',verse_id)
                                elif 'Canticles' in verse_id: verse_id = re.sub('Canticles','Song of Solomon',verse_id)
                                verse = QuoteParaphrase.get_bible_verse(verse_id)
                                if verse is not None: 
                                    verses[i] = verse[0]
                                else:
                                    print(i) 
                                    verses[i] = None 
                            else: verses[i] = None 
                        

            book_counts = sorted(book_counts.items(),key = lambda x:x[1],reverse=True)
            aut_counts =  sorted(aut_counts.items(),key = lambda x:x[1],reverse=True)
            year_counts =  sorted(year_counts.items(),key = lambda x:x[1],reverse=True)
            other_cited = sorted(other_cited.items(),key=lambda x: (x[1], x[0][0],x[0][1]),reverse=True)
            
            meta_data = StringIO()
            meta_csv = csv.writer(meta_data)
            segment_data = StringIO()
            segment_csv = csv.writer(segment_data)
            aut_data = StringIO()
            aut_csv = csv.writer(aut_data)
            year_data = StringIO()
            year_csv = csv.writer(year_data)
            cited_data = StringIO()
            cited_csv = csv.writer(cited_data)

            meta_csv.writerow(['TCP ID',f'Number of Citations of {label}','Title','Authors','Publisher','Publication Place','Publication Year','Subject Headings','ESTC','STC','Link']) 
            aut_csv.writerow(['Author',f'Number of Citations of {label}'])
            segment_csv.writerow(['TCP ID','Index of Segment','Location','Page','Text (tokenized)','Parsed Citations'])
            year_csv.writerow(['Publication Year',f'Number of Citations of {label}'])
            cited_csv.writerow(['Citation','Location','Count','Full Text (KJV)'])

            for row in aut_counts: aut_csv.writerow(row)  
            for row in year_counts: year_csv.writerow(row) 
            for row in other_cited: cited_csv.writerow((row[0][0],row[0][1],row[1],verses[row[0][0]])) 
            for tcpID, count in book_counts:
                m = metadata[tcpID]  
                # print((tcpID, count,m.title, m.authors, m.publisher,m.pubplace,m.pubyear,m.subject_headings,m.estc,m.stc,links[tcpID]))
                meta_csv.writerow((tcpID, count,m.title, m.authors, m.publisher,m.pubplace,m.pubyear,m.subject_headings,m.estc,m.stc,links[tcpID]))
                for sidx in sorted(segments[tcpID]):
                    for loc in sorted(segments[tcpID][sidx]):
                        text, page, cited = segments[tcpID][sidx][loc] 
                        # print(tcpID,sidx,loc,page,"; ".join(cited))
                        segment_csv.writerow((tcpID,sidx,loc,page,text,"; ".join(cited)))

            headers = {
                "Content-Disposition": f"attachment; filename={label}.zip",
                "Content-Type": "application/zip",
            }
            zip_memory = BytesIO()
            with zipfile.ZipFile(zip_memory, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr(f"{label}_Sermons.csv", meta_data.getvalue())
                zip_file.writestr(f"{label}_Authors.csv", aut_data.getvalue())
                zip_file.writestr(f"{label}_Segments.csv", segment_data.getvalue())
                zip_file.writestr(f"{label}_Years.csv", year_data.getvalue())
                zip_file.writestr(f"{label}_OtherCitations.csv", cited_data.getvalue())
            
            return Response(zip_memory.getvalue(), headers=headers)
        
    return render_template('scriptural_index.html')

    