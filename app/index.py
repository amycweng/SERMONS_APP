from flask import render_template,send_file
from io import BytesIO
from wordcloud import WordCloud 
import base64
from matplotlib.figure import Figure 
import numpy as np 
import re 
from collections import Counter 

from .models.metadata import Metadata

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

