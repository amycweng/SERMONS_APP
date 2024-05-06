from flask import render_template,send_file,request
from io import BytesIO
from wordcloud import WordCloud 
import base64
from matplotlib.figure import Figure 
import numpy as np 
import re 
from collections import Counter 

from .models.metadata import Metadata
from .models.reference import Citation, QuoteParaphrase

from flask import Blueprint
bp = Blueprint('index', __name__)

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    grey_value = int(150 - font_size)  
    grey_value = max(50, min(grey_value, 200))  
    return "rgb({0}, {0}, {0})".format(grey_value)


@bp.route('/')
def index():
    sermons = Metadata.get_all()
    return render_template('index.html',
                        sermons = sermons)
    
@bp.route('/metadata_visualization')
def visualize():
    # publication year 
    fig = Figure(figsize=(15, 10))
    ax = fig.subplots()
    color='grey'
    title='Sermons in EEBO-TCP'
    xlabel= 'Year of Publication'
    ylabel='Count of Sermons'
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
    ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    ax.bar(x,y,color=color)
    ax.set_title(title, fontsize=20,fontdict={'family': 'serif'})
    ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    ax.set_xticks(np.arange(min(x), max(x)+1, 10.0))
    ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'})
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()
    years = [(year,idx) for idx,year in enumerate(x)]
    num_sermons = y

    subjects = []
    exclude = ['Sermons, English','Bible','17th century','Sermons','Early works to 1800','16th century']
    for s in sermons: 
        words = s.subject_headings.split("; ")
        for w in words: 
            if w == "No Keywords": continue
            if w.strip(".") not in exclude: 
                if w != 'O.T.' and w!= 'N.T.': 
                    w = w.strip(".")
                subjects.append(w)
    subjects = Counter(subjects)
    word_cloud = WordCloud(background_color = "white",font_path='Times New Roman', width=1200, height=800, max_words=2000,color_func=grey_color_func).generate_from_frequencies(subjects)
    img_buffer = BytesIO()
    word_cloud.to_image().save(img_buffer, format="png")
    subjects = sorted(subjects.items(),key = lambda x:x[1],reverse=True)
    data2 = base64.b64encode(img_buffer.getvalue()).decode("ascii")

    # authors
    fig = Figure(figsize=(15, 10))
    ax = fig.subplots()
    color='grey'
    title='Most Frequent Authors of Sermons in EEBO-TCP'
    xlabel= 'Count of Sermons'
    ylabel='Author'
    author_counts = Metadata.get_author_counts()
    author_counts = sorted(author_counts,key = lambda x:x[1],reverse=True)
    x,y = [a[0] for a in author_counts][:25][::-1],[a[1] for a in author_counts][:25][::-1]
    ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    ax.barh(x,y,color=color)
    ax.set_title(title, fontsize=20,fontdict={'family': 'serif'})
    ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'},rotation=90)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data3 = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()

    # publication place 
    places = []
    london = []
    for s in sermons: 
        found = False
        if re.search(r"London|Londini|Londres|Londo n|london|Londom|Londoon|londun",s.pubplace):
            london.append('London')
            places.append('London')
            found=True
        else: 
            london.append('Not London')
        if re.search(r"Oxon|Oxford",s.pubplace):
            places.append('Oxford')
            found=True
        if re.search('Boston',s.pubplace):
            places.append('Boston')
        if not found: 
            places.append(s.pubplace)
    
    fig = Figure(figsize=(15, 8))
    london_ax,ax= fig.subplots(1,2)
    london = Counter(london)
    london_ax.pie(london.values(), labels=london.keys(), autopct='%1.1f%%',textprops={'fontname':'Times New Roman','fontsize':20})
    london_ax.axis('equal')
    
    x,y = [],[]
    places = sorted(Counter(places).items(),key = lambda x:x[1],reverse=True)
    x,y = [a[0] for a in places][1:26][::-1],[a[1] for a in places][1:26][::-1]
    ax.pie(y, labels=x, autopct='%1.1f%%',textprops={'fontname':'Times New Roman','fontsize':10})
    ax.axis('equal')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data4 = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()

    return render_template('metadata.html', 
                           data=data, 
                           data2=data2,
                           data3=data3,
                           data4=data4,
                           years=years,
                           num_sermons=num_sermons,
                           author_counts=author_counts,
                           places=places,
                           subjects=subjects)

def parse_citations(citations, loc="all"): 
    all_books = {}
    all_chapters = {}
    all_verses = {}
    for c in citations:
        tcpID = c.tcpID 
        cited = c.citation 
        cited = cited.split("; ")
        for c in cited: 
            c = c.split(" ")
            if len(c[0]) == 1: 
                book = f"{c[0]} {c[1]}"
                ref = c[2]
            else: 
                book = c[0]
                ref = c[1]
            
            if book not in all_books: 
                all_books[book] = []
            all_books[book].append(tcpID)

            ref = ref.split(".")
            chapter = ref[0]
            if '*' not in chapter and "^" not in chapter: 
                key = f"{book} {chapter}"
                if key not in all_chapters: 
                    all_chapters[key] = []
                all_chapters[key].append(tcpID)
                if len(ref) == 2: 
                    verse = ref[1]
                    if '*' not in verse and "^" not in verse: 
                        key = f"{book} {chapter}.{verse}"
                        if key not in all_verses: 
                            all_verses[key] = []
                        all_verses[key].append(tcpID)
    return all_books, all_chapters, all_verses

def visualize_dict_horizontal(title, xlabel, ylabel, dict): 
    fig = Figure(figsize=(15, 10))
    ax = fig.subplots()
    color='grey'
    x,y = [],[]
    dictionary = {k:len(v) for k,v in dict.items() }
    counts = sorted(dictionary.items(), key=lambda x:x[1],reverse=True)
    for word,freq in reversed(counts[:25]): 
        x.append(word)
        y.append(freq)
    ax.tick_params(axis='both', which='major', labelsize=12, labelfontfamily='serif')  # Set fontsize to 12 for both x and y ticks
    ax.barh(x,y,color=color)
    ax.set_title(title, fontsize=20,fontdict={'family': 'serif'})
    ax.set_xlabel(xlabel, fontsize=15,fontdict={'family': 'serif'})
    ax.set_ylabel(ylabel, fontsize=15,fontdict={'family': 'serif'})
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()
    return x, y, data 

def citation_over_time(citations, search):
    sermons = Metadata.get_all()
    tcpID_dates = {s.tcpID:s.pubyear for s in sermons}
    results = {}
    for c in citations: 
        tcpID = c.tcpID 
        date = tcpID_dates[tcpID]
        cited = c.citation
        if 'In-Text' == c.loc: loc = 'In-Text'
        else: loc = 'Marginal'
        for citation in cited.split("; "): 
            if search in citation: 
                if date not in results: 
                    results[date] = {}
                if tcpID not in results[date]: 
                    results[date][tcpID] = [] 
                results[date][tcpID].append(loc)
    return visualize_over_time(results,search)

def visualize_over_time(results,search): 
    marg, text = [],[]
    sermons, years = [],[]
    for date in sorted(results): 
        marg_count, text_count = 0,0
        num_sermons = 0
        for locations in results[date].values(): 
            num_sermons += 1 
            locations = Counter(locations)
            if "Marginal" in locations: 
                marg_count += locations["Marginal"]        
            if "In-Text" in locations: 
                text_count += locations["In-Text"]
        years.append(int(date))
        marg.append(marg_count)
        text.append(text_count)
        sermons.append(num_sermons)

    fig = Figure(figsize=(15, 10))
    ax = fig.subplots()
    ax.bar(years,marg,color="lightgrey",label="Marginal")
    ax.bar(years,text,bottom=marg,color="darkgrey",label="In-Text")
    ax.scatter(years,sermons,color="black",label="Number of Books")
    if len(search) == 0: 
        ax.set_title("All Known Citations Over Time",fontsize=20,fontdict={'family': 'serif'})
    ax.set_xlabel("Publication Year", fontsize=15,fontdict={'family': 'serif'})
    ax.set_ylabel("Frequency", fontsize=15,fontdict={'family': 'serif'})
    ax.set_xticks(np.arange(min(years),max(years), 5.0))
    ax.legend()
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig.clear()
    return marg, text, data 

def get_books_citations():
    books = {}
    citations = Citation.get_all()
    for c in citations: 
        c = c.citation.split("; ")[0].split(".")[0]
        c = c.split(" ")[:-1]
        books[" ".join(c)] = True 
    return sorted(list(books.keys()))


@bp.route('/citations',methods=['POST','GET'])
def visualize_citations():
    book_data,author_data,over_time = None, None,None
    book=None
    tcpIDs, authors = None, None
    books = get_books_citations()
    if request.method == 'POST':
        book = request.form['book']
        if len(book) > 0: 
            citations = Citation.get_by_label(book + "%")
            marg, text, over_time = citation_over_time(citations,book)
            tcpIDs = {}      
            authors = {}      
            for c in citations: 
                if c.tcpID not in tcpIDs: tcpIDs[c.tcpID] = [] 
                for item in c.citation.split("; "):
                    tcpIDs[c.tcpID].append(item)
            author_tcpIDs = Metadata.get_author_tcpIDs()
            for a,t_list in author_tcpIDs: 
                for t in t_list.split("; "): 
                    if t in tcpIDs: 
                        if a not in authors: authors[a] = []
                        authors[a].extend(tcpIDs[t])
            x,y,book_data = visualize_dict_horizontal(f'Books with the Most Frequent Citations of {book}', 'Count of Citations','TCP ID',tcpIDs)
            x,y,author_data = visualize_dict_horizontal(f'Authors with the Most Frequent Citations of {book}', 'Count of Citations','Author',authors)
            tcpIDs = {k:len(v) for k,v in tcpIDs.items()}
            authors = {k:len(v) for k,v in authors.items()}
    citations = Citation.get_all()
    marg, text, data0 = citation_over_time(citations,'')

    b, c, v = parse_citations(citations)
    title='Most Frequent Citations of Books'
    xlabel= 'Count of Citations'
    ylabel='Book'
    x,y,data = visualize_dict_horizontal(title,xlabel,ylabel,b) 

    title='Most Frequent Citations of Chapters'
    xlabel= 'Count of Citations'
    ylabel='Chapter'
    x,y,data2 = visualize_dict_horizontal(title,xlabel,ylabel,c)     

    title='Most Frequent Citations of Verses'
    xlabel= 'Count of Citations'
    ylabel='Verse'
    x,y,data3 = visualize_dict_horizontal(title,xlabel,ylabel,v)  

    return render_template('citations.html',
                           books=books,
                           book=book,
                           tcpIDs=tcpIDs,
                           authors=authors,
                           book_data=book_data,
                           over_time=over_time,
                           author_data=author_data, 
                           data0=data0,
                           data=data,
                           data2=data2,
                           data3=data3)

