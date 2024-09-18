from flask import render_template,send_file,request
from flask_login import current_user
from io import BytesIO
from wordcloud import WordCloud 
import base64
from matplotlib.figure import Figure 
 
import re,json
from collections import Counter 

from .models.metadata import Metadata
from .models.reference import Citation, QuoteParaphrase
from .lib import * 
from flask import Blueprint
bp = Blueprint('index', __name__)
import os 
folder = os.getcwd()

@bp.route('/')
def about():
    return render_template('about.html')

@bp.route('/catalog', methods=['POST','GET'])
def index():
    sermons = Metadata.get_all()
    sermons_dict = {s.tcpID:s for s in sermons}
    search = None 
    pubplaces = Metadata.get_pubplace()
    pubplaces = {s[0]:s[1] for s in pubplaces} 
    for s in sermons: 
        # if s.subject_headings is not None: 
        #     s.subject_headings = "<br><br>".join(s.subject_headings.split("; "))
        if s.phase == 2: s.phase = f'https://quod.lib.umich.edu/e/eebo2/{s.tcpID}.0001.001?'
        elif s.phase == 1: s.phase = f'https://quod.lib.umich.edu/e/eebo/{s.tcpID}.0001.001?'
    if request.method == "POST": 
        search_sermons = []
        search = request.form["search"]
        results = Metadata.search_in_titles(search)
        for tcpID, score in results: 
            if score >= 0.1: 
                search_sermons.append(sermons_dict[tcpID])
        sermons = search_sermons

    return render_template('index.html',
                        sermons = sermons,
                        search=search,
                        pubplaces = pubplaces)


@bp.route('/metadata_visualization')
def visualize():
    # publication year 
    sermons = Metadata.get_all()
    years = [s.pubyear for s in sermons]
    x,y = [],[]
    date_counts = Counter(years)
    for date in sorted(date_counts): 
        if "?" in date: continue
        if "-" in date: 
            date = date.split("-")[0]
        x.append(int(date))
        y.append(date_counts[date])
    # fig = Figure(figsize=(15, 10))
    # ax = fig.subplots()
    # color='grey'
    # title='Sermons in EEBO-TCP'
    # xlabel= 'Year of Publication'
    # ylabel='Count of Sermons'
    # ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    # ax.bar(x,y,color=color)
    # ax.set_title(title, fontsize=20,fontdict={'family': 'serif'})
    # ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    # ax.set_xticks(np.arange(min(x), max(x)+1, 10.0))
    # ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'})
    # buf = BytesIO()
    # fig.savefig(buf, format="png")
    # data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # fig.clear()
    years = [(year,idx) for idx,year in enumerate(x)]
    num_sermons = y

    with open(f"{folder}/app/static/data/subjects.json","r") as file: 
        subjects = json.load(file) 
    wc_subjects = subjects[:502]  
    exclude = ["Sermons, English",
               "Early works to 1800"]
    wc_subjects = Counter({subject[0]:subject[1] for subject in wc_subjects if subject[0] not in exclude})
    
    # word_cloud = WordCloud(background_color = "white",font_path='Times New Roman', width=1200, height=800, max_words=2000,colormap=blue_cmap).generate_from_frequencies(wc_subjects)
    # img_buffer = BytesIO()
    # word_cloud.to_image().save(img_buffer, format="png")
    # data2 = base64.b64encode(img_buffer.getvalue()).decode("ascii")

    # authors
    author_counts = Metadata.get_author_counts()
    author_counts = sorted(author_counts,key = lambda x:x[1],reverse=True)
    # fig = Figure(figsize=(15, 10))
    # ax = fig.subplots()
    # color='grey'
    # title='Most Frequent Authors of Sermons in EEBO-TCP'
    # xlabel= 'Count of Sermons'
    # ylabel='Author'
    # x,y = [a[0] for a in author_counts][:25][::-1],[a[1] for a in author_counts][:25][::-1]
    # ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    # ax.barh(x,y,color=color)
    # ax.set_title(title, fontsize=20,fontdict={'family': 'serif'})
    # ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    # ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'},rotation=90)
    # fig.tight_layout()
    # buf = BytesIO()
    # fig.savefig(buf, format="png")
    # data3 = base64.b64encode(buf.getbuffer()).decode("ascii")
    # fig.clear()

    # publication place 
    pubplaces = Metadata.get_pubplace()
    pubplaces = {s[0]:s[1] for s in pubplaces}
    places = []
    london = []
    for s in sermons:
        if s.tcpID not in pubplaces: continue 
        place = pubplaces[s.tcpID]
        if place == "London":
            london.append('London')
        else: 
            london.append('Not London')
        
        places.append(place)
    places = sorted(Counter(places).items(),key = lambda x:x[1],reverse=True)

    # fig = Figure(figsize=(15, 8))
    # london_ax,ax= fig.subplots(1,2)
    # london = Counter(london)
    # colors_london = ['#1f77b4', '#4b9cd3'] 
    # london_ax.pie(london.values(), labels=london.keys(), autopct='%1.1f%%',textprops={'fontname':'Times New Roman','fontsize':20},colors=colors_london)
    # london_ax.axis('equal')
    # x,y = [],[]
    # x,y = [a[0] for a in places][1:26][::-1],[a[1] for a in places][1:26][::-1]
    # ax.pie(y, labels=x, autopct='%1.1f%%',textprops={'fontname':'Times New Roman','fontsize':10})
    # ax.axis('equal')
    # buf = BytesIO()
    # fig.savefig(buf, format="png")
    # data4 = base64.b64encode(buf.getbuffer()).decode("ascii")
    # fig.clear()

    # topic words 
    topics = Metadata.get_topics()
    all_topics = {}
    for tlist in topics.values(): 
        for t in tlist.split("; "): 
            if t not in all_topics: all_topics[t] = 0
            all_topics[t] += 1 
    topic_counts = sorted(all_topics.items(),key = lambda x:x[1],reverse=True)
    topic_counts = topic_counts[:502]
    topic_counts = Counter({t[0]:t[1] for t in topic_counts})
    # word_cloud = WordCloud(background_color = "white",font_path='Times New Roman', width=1200, height=800, max_words=2000,colormap=blue_cmap).generate_from_frequencies(topic_counts)
    # img_buffer = BytesIO()
    # word_cloud.to_image().save(img_buffer, format="png")
    # data_topics = base64.b64encode(img_buffer.getvalue()).decode("ascii")

    # sections 
    section_counts = Metadata.get_section_counts()
    section_counts = sorted(section_counts,key = lambda x:x[1],reverse=True)
    fig = Figure(figsize=(15, 5))
    ax = fig.subplots()
    # print(sum([s[1] for s in section_counts]))
    # x,y = [a[0] for a in section_counts][:10][::-1],[a[1] for a in section_counts][:10][::-1]
    # ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    # ax.barh(x,y,color=color)
    # ax.set_xlabel('Count of Sections', fontsize=15,fontdict={'family': 'serif'})
    # ax.set_ylabel('Section Title', fontsize=15,fontdict={'family': 'serif'},rotation=90)
    # fig.tight_layout()
    # buf = BytesIO()
    # fig.savefig(buf, format="png")
    # data_sections = base64.b64encode(buf.getvalue()).decode("ascii")

    return render_template('metadata.html', 
                        #    data=data, 
                        #    data2=data2,
                        #    data3=data3,
                        #    data4=data4,
                        #    data_topics=data_topics,
                        #    data_sections=data_sections,
                           section_counts=section_counts,
                           topics=topics,
                           years=years,
                           num_sermons=num_sermons,
                           author_counts=author_counts,
                           places=places,
                           subjects=subjects)


def visualize_dict_horizontal(title, xlabel, ylabel, dicts): 
    fig = Figure(figsize=(15, 8))
    ax, ax_QP = fig.subplots(1,2)
    color='grey'
    x,y = [],[]
    
    counts = sorted(dicts[0].items(), key=lambda x:x[1],reverse=True)
    for word,value in reversed(counts[:20]): 
        x.append(word)
        y.append(value)
    ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    ax.barh(x,y,color=color)
    ax.set_title("Citations", fontsize=15,fontdict={'family': 'serif'})
    ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'})
    
    x,y=[],[]
    counts = sorted(dicts[1].items(), key=lambda x:x[1],reverse=True)
    for word,value in reversed(counts[:20]): 
        x.append(word)
        y.append(value)
    ax_QP.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    ax_QP.barh(x,y,color=color)
    ax_QP.set_title("Quotes or\nParaphrases", fontsize=15,fontdict={'family': 'serif'})
    ax_QP.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()
    print(f"GRAPHED {title}")
    return data 


@bp.route('/index', methods=['POST','GET'])
def scriptural_index():
    citations = {}
    variants,verse_text = None, None 
    # with open(f"{folder}/app/static/data/verses.json") as file: 
    #     verse_ids = json.load(file)
    with open(f"{folder}/app/static/data/books_chapters.json") as file: 
        ___, books,chapters,_,__ = json.load(file)
    refs = []
    refs.extend(books)
    
    ref = None, None
    get_prominence = None 
    citing_entity = None 
    actual_qp = [] 
    proximal = None 
    book_vis,author_vis,pubplace_vis,pubyear_vis,subjects_vis = None, None,None,None,None
    metadata = {}
    tcpIDs, authors,pubplaces,pubyears,subjects = None, None,None,None,None
    tcpID_QP_meta = None 
    if request.method == 'POST':
        ref = request.form['item']
        get_prominence = request.form['get_prominence']
        citing_entity = request.form['citing_entity']
        print(citing_entity, get_prominence)
        if len(ref) > 0:  
            ref = ref.capitalize()
            if "." in ref:
                citations = Citation.get_by_label(ref)
                actual_qp = QuoteParaphrase.get_by_label(ref + " %")
            elif ref in books: 
                citations = Citation.get_by_label(ref + "%")
                actual_qp = QuoteParaphrase.get_by_label(ref + " %")
            else: # chapter 
                citations = Citation.get_by_label(ref)
                citations.extend(Citation.get_by_label(ref + ".%"))
                actual_qp = QuoteParaphrase.get_by_label(ref + ".%")
            variants = {}
            for c in citations: 
                orig = c.replaced.split(" ")
                if len(orig[0]) == 1: 
                    variants[" ".join(orig[:2])] = True 
                else: 
                    variants[orig[0]] = True 
            
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
            
            # VISUALIZTIONS 
            # marg, text, over_time = citation_over_time(citations,ref)
            print("BEGIN ORCP VIS")
            versions = ["(Douay-Rheims)","(Vulgate)","(Geneva)","(KJV)"] 
            def ORCP(etype,entities): 
                with open(f"{folder}/app/static/data/ORCP/{etype}_citations.json") as file: 
                    orcp_C = json.load(file)
                with open(f"{folder}/app/static/data/ORCP/{etype}_QP.json") as file: 
                    orcp_QP = json.load(file)
                ret = [{},{}]
                for e in entities: 
                    for dict in orcp_C: 
                        if e not in dict: continue 
                        if ref in dict[e]:  
                            ret[0][e] = round(dict[e][ref],4)
                    for dict in orcp_QP:
                        if e not in dict: continue 
                        for ver in versions: 
                            key = ref + f" {ver}"
                            if key in dict[e]:
                                ret[1][f"{e} {ver}"] = round(dict[e][key],4)
                print(f"FINISHED GETTING {etype} DATA")
                return ret
             
            authors = {} 
            pubplaces = {}
            subjects = {}
            tcpIDs = {c.tcpID:None for c in citations}
            tcpIDs.update({q.tcpID:None for q in actual_qp})
            if len(tcpIDs) >= 0: 
                metadata = {a.tcpID: a for a in Metadata.get_all() if a.tcpID in tcpIDs}
                all_info = Metadata.get_all_for_ORCP()
                for a in all_info: 
                    if a['tcpID'] in tcpIDs: 
                        authors[a['author']] = None 
                        pubplaces[a['pubplace']] = None 
                        subjects[a['subject_heading']] = None 
                pubyears = {a.pubyear: a.tcpID for a in metadata.values()}
                if citing_entity == "tcpIDs": 
                    tcpIDs = ORCP('tcpIDpub',tcpIDs)
                    tcpID_QP_meta = {item: item.split(" ")[0] for item in tcpIDs[1]}
                    book_vis = visualize_dict_horizontal(f'Publications', 'Prominence','TCP ID',tcpIDs)
                elif citing_entity == "Authors": 
                    authors = ORCP('author',authors)
                    author_vis = visualize_dict_horizontal(f'Authors','Prominence','Author',authors)
                elif citing_entity == "Subjects": 
                    subjects = ORCP('subjects',subjects)
                    subjects_vis = visualize_dict_horizontal(f'Subject headings','Prominence','Subject Heading',subjects)
                elif citing_entity == "Pubplace":
                    pubplaces = ORCP('pubplace',pubplaces)
                    pubplace_vis = visualize_dict_horizontal(f'Publication places','Prominence','Publication Place',pubplaces)
                elif citing_entity == "Pubyear": 
                    pubyears = ORCP('pubyear',pubyears)
                    pubyear_vis = visualize_dict_horizontal(f'Publication years','Prominence','Publication Year',pubyears)
    
    return render_template('scriptural_index.html',
                           refs=refs,
                           ref=ref,
                           get_prominence=get_prominence,
                           verse_text = verse_text,
                           actual_qp=actual_qp,
                           proximal=proximal,
                           books=books,
                           variants=variants, 
                         citations = citations,
                        
                            tcpIDs=tcpIDs,
                            tcpID_QP_meta=tcpID_QP_meta,
                           authors=authors,
                           pubplaces=pubplaces,
                           pubyears = pubyears,
                           subjects=subjects,
                           metadata=metadata,
                        
                           book_vis=book_vis,
                           author_vis=author_vis,
                           pubplace_vis = pubplace_vis,
                           pubyear_vis=pubyear_vis,
                           subjects_vis = subjects_vis)


# def parse_citations(citations, loc="all"): 
#     all_books = {}
#     all_chapters = {}
#     all_verses = {}
#     cited = []
#     for c in citations: 
#         for citation in c.citation.split("; "): 
#             if "-" in citation: 
#                 nums = re.findall(r"\d+",citation)
#                 bookchap = re.findall(r"^[ \w+]+\d+",citation)
#                 if len(bookchap) == 0: continue
#                 bookchap = bookchap[0]
#                 start, end = nums[-2],nums[-1]
#                 for num in range(int(start),int(end)+1):
#                     cited.append((f"{bookchap}.{num}",c.tcpID))
#             else: 
#                 cited.append((citation,c.tcpID))
#     for c, tcpID in cited:
#         c = c.split(" ")
#         if len(c[0]) == 1: 
#             book = f"{c[0]} {c[1]}"
#             ref = c[2]
#         else: 
#             book = c[0]
#             ref = c[1]
        
#         if book not in all_books: 
#             all_books[book] = []
#         all_books[book].append(tcpID)

#         ref = ref.split(".")
#         chapter = ref[0]
#         if '*' not in chapter and "^" not in chapter: 
#             key = f"{book} {chapter}"
#             if key not in all_chapters: 
#                 all_chapters[key] = []
#             all_chapters[key].append(tcpID)
#             if len(ref) == 2: 
#                 verse = ref[1]
#                 if '*' not in verse and "^" not in verse: 
#                     key = f"{book} {chapter}.{verse}"
#                     if key not in all_verses: 
#                         all_verses[key] = []
#                     all_verses[key].append(tcpID)
#     return all_books, all_chapters, all_verses

# def citation_over_time(citations, search):
#     sermons = Metadata.get_all()
#     tcpID_dates = {s.tcpID:s.pubyear for s in sermons}
#     results = {}
#     for c in citations: 
#         tcpID = c.tcpID 
#         date = tcpID_dates[tcpID]
#         if "?" in date: continue
#         if "-" in date: 
#             date = date.split("-")[0]
#         if 'In-Text' == c.loc: loc = 'In-Text'
#         else: loc = 'Marginal'
#         cited = []
#         for citation in c.citation.split("; "): 
#             if "-" in citation: 
#                 nums = re.findall(r"\d+",citation)
#                 bookchap = re.findall(r"^[ \w+]+\d+",citation)
#                 if len(bookchap) == 0: continue
#                 bookchap = bookchap[0]
#                 start, end = nums[-2],nums[-1]
#                 for num in range(int(start),int(end)+1):
#                     cited.append(f"{bookchap}.{num}")
#             else: cited.append(citation)
#         for citation in cited: 
#             if search in citation: 
#                 if date not in results: 
#                     results[date] = {}
#                 if tcpID not in results[date]: 
#                     results[date][tcpID] = [] 
#                 results[date][tcpID].append(loc)
#     return visualize_over_time(results,search)

# def visualize_over_time(results,search): 
#     marg, text = [],[]
#     sermons, years = [],[]
#     for date in sorted(results): 
#         marg_count, text_count = 0,0
#         num_sermons = 0
#         for locations in results[date].values(): 
#             num_sermons += 1 
#             locations = Counter(locations)
#             if "Marginal" in locations: 
#                 marg_count += locations["Marginal"]        
#             if "In-Text" in locations: 
#                 text_count += locations["In-Text"]
#         years.append(int(date))
#         marg.append(marg_count)
#         text.append(text_count)
#         sermons.append(num_sermons)

#     fig = Figure(figsize=(15, 10))
#     ax = fig.subplots()
#     ax.bar(years,marg,color="lightgrey",label="Marginal")
#     ax.bar(years,text,bottom=marg,color="darkgrey",label="In-Text")
#     if len(search) == 0: 
#         ax.set_title("All Known Citations Over Time",fontsize=20,fontdict={'family': 'serif'})
#     else: 
#         ax.set_title(f"All Known Citations Over Time of {search}",fontsize=20,fontdict={'family': 'serif'})
#         ax.scatter(years,sermons,color="black",label="Number of Books")
#     ax.set_xlabel("Publication Year", fontsize=15,fontdict={'family': 'serif'})
#     ax.set_ylabel("Frequency", fontsize=15,fontdict={'family': 'serif'})
#     ax.set_xticks(np.arange(min(years),max(years), 10.0))
#     ax.legend()
#     buf = BytesIO()
#     fig.tight_layout()
#     fig.savefig(buf, format="png")
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     fig.clear()
#     return marg, text, data 


# @bp.route('/citations_visualization',methods=['POST','GET'])
# def visualize_citations():
#     book_data,author_data,over_time = None, None,None
#     book=None
#     metadata = {}
#     tcpIDs, authors = None, None
#     books = get_books_citations()
#     data0,data,data2,data3 = None, None, None, None 
#     if request.method == 'POST':
#         book = request.form['item']
#         if len(book) > 0: 
#             if '.' in book: 
#                 citations = Citation.get_by_label(book)
#             else: 
#                 citations = Citation.get_by_label(book + "%")
#             marg, text, over_time = citation_over_time(citations,book)
#             tcpIDs = {}      
#             authors = {}      
#             for c in citations: 
#                 if c.tcpID not in tcpIDs: tcpIDs[c.tcpID] = [] 
#                 for item in c.citation.split("; "):
#                     tcpIDs[c.tcpID].append(item)
#             author_tcpIDs = Metadata.get_author_tcpIDs()
#             for a,t_list in author_tcpIDs: 
#                 for t in t_list.split("; "): 
#                     if t in tcpIDs: 
#                         if a not in authors: authors[a] = []
#                         authors[a].extend(tcpIDs[t])
#             x,y,book_data = visualize_dict_horizontal(f'Books with the Most Frequent Citations of {book}', 'Count of Citations','TCP ID',tcpIDs)
#             x,y,author_data = visualize_dict_horizontal(f'Authors with the Most Frequent Citations of {book}', 'Count of Citations','Author',authors)
#             all_meta = Metadata.get_all()
#             for a in all_meta: 
#                 if a.tcpID in tcpIDs: 
#                     metadata[a.tcpID] = a 
#             tcpIDs = {k:len(v) for k,v in tcpIDs.items()}
#             authors = {k:len(v) for k,v in authors.items()}
#         else: book = None 
    
#     if book is None: 
#         citations = Citation.get_all()
#         marg, text, data0 = citation_over_time(citations,'')

#         b, c, v = parse_citations(citations)
#         title='Most Frequent Citations of Books'
#         xlabel= 'Count of Citations'
#         ylabel='Book'
#         x,y,data = visualize_dict_horizontal(title,xlabel,ylabel,b) 

#         title='Most Frequent Citations of Chapters'
#         xlabel= 'Count of Citations'
#         ylabel='Chapter'
#         x,y,data2 = visualize_dict_horizontal(title,xlabel,ylabel,c)     

#         title='Most Frequent Citations of Verses'
#         xlabel= 'Count of Citations'
#         ylabel='Verse'
#         x,y,data3 = visualize_dict_horizontal(title,xlabel,ylabel,v)  

#     return render_template('citations.html',
#                            books=books,
#                            book=book,
#                            tcpIDs=tcpIDs,
#                            authors=authors,
#                            metadata=metadata,
#                            book_data=book_data,
#                            over_time=over_time,
#                            author_data=author_data, 
#                            data0=data0,
#                            data=data,
#                            data2=data2,
#                            data3=data3)