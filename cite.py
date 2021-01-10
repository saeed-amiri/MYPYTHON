#!/usr/bin pyhton

"""
command:
if you want to creat new "bib" file:
    python cite.py <YOUR_LATEX>.aux
if you want to update the "bib" file:
    python cite.py <YOUR_LATEX>.bib
output:
<YOUR_LATEX>.bib

!first compile the latex file to produce the .aux file !
then run the python command
then compile the latex file again

read aux file
    get citations
    seperate citaion for normal and arxiv and book
    make url 
    get response
    seperate lines and edit:
        @ lable -> do
        title -> Capitalize
        authors -> get correct format of names
        journal -> hyperref with url
        pages -> correct if missing (not in this version!)
    replace the with updated ones
make the bibtex file

1) all the citation from one source should used with same label in the latex file.
2) I assumed the citation in .aux is in lines which satarted \citation{}, ex.:
    \citation{isbn:9780521392938,arxiv:2011.01070v1}
3) how to cite in the tex:
    - for normal journal use the "doi"  of the source ex.: \cite{10.1016/0039-6028(93)91022-h}
    - for arxiv papres use the arxiv's label ex.: \cite{arxiv:2011.01070v1}
    - for book use the ISBN of the book ex.: \cite{isbn:9780521392938} !! always check the bib for the book, especially the "authors"
    - combanition of cites is also possible: 
        \cite{isbn:9780521392938,arxiv:2011.01070v1,10.1016/0039-6028(93)91022-h,10.1088/0022-3719/16/9/005,isbn:9780122673511}
haven't tested it for the other styles of citation like: \citep ...

for others examples:
    http://www.thamnos.de/misc/look-up-bibliographical-information-from-an-arxiv-id/
    https://gist.github.com/jrsmith3/5513926

One modual should be installed for the books' bib: "isbnlib" [https://pypi.org/project/isbnlib/]
    use pip:
        pip install isbnlib
# updates:
    - using thread for downloading (now is around 10 times faster!!)
SAEED AMIRI
"""
import sys,re,requests,time,calendar
from contextlib import contextmanager
import concurrent.futures
# moduals for getting books' bibtex, it is easier then using "request"
from isbnlib import meta
from isbnlib.registry import bibformatters

start = time.perf_counter()

if len(sys.argv)==1: sys.exit(__doc__)

def do_and(authors) -> list:
  #counting number of authors, seperated by "and"
  and_count = authors.count(' and ')
  #if there is mpre then 1, replace them with "{,}" so latex will print them
  if and_count>1:
    authors=re.sub(' and','{,}',authors,count=and_count-1)
    authors=re.sub(' and','{,} and',authors,count=1)
  return(authors)

def do_firstname(authors) -> list:
  #make the names like: "FirstName MidelName(s) LastName" -> "F. M. LastName"
  comma = authors.count(',')-1
  #remove initat and trailing characters, also considering the umlats: \u00C0-\u017F
  authors = re.sub('[^\u00C0-\u017FA-Za-z0-9,]+', ' ', authors)
  #remove "and" and "author" and the trailing "c" from the list for now then will put them back
  #baring the names: rmoving "and"
  if comma >0:authors=re.sub('( and| and )','',authors)
  if comma==0:authors=re.sub('( and| and )',',',authors)
  #removing the "author" and/or trailing "c"
  authors=re.sub('(author| c ,)','',authors)
  #make a list of authors' names
  authors=" ".join(authors.split())
  #dropping the sapacces from the list
  authors=re.sub(', ',',',authors).split(',')
  authors=[author.strip() for author in authors if author]
  #doing "FirstName MidelName(s) LastName" -> "F. M1. M2. ... LastName"
  names = []
  for name in authors:
    author=[]
    #split the name 
    all=name.split(" ")
    #keep the first letter of all-name beside lastName
    for part in all[:-1]: author.append(f'{part[0]}.')
    #apoend the lastName
    author.append(f' {all[-1]}')
    #append the author to the others
    names.append("".join(author))
  if len(names)==1:authors = f'{names[0]}'
  #joining the name of the authors, if more then 1 by and
  elif len(names)>=2:authors = f'{" and ".join(names)}'
  spcial_char_map = {ord('ä'):'\\"a', ord('ü'):'\\"u', ord('ö'):'\\"o', ord('ß'):'\ss'}
  authors = authors.translate(spcial_char_map)
  return do_and(authors)

def pretty_title(title) -> list:
    #seperate the "title" make a list and capitalize them
    title = re.sub('^{','',title)
    title = [item.lower() if not "-" in item else item for item in title.split(" ")]
    title = [f'{{{item}}}' if "-" in item and len(item)>2 else item for item in title]
    title = [item.capitalize()  if i==0 else item for i,item in enumerate(title)]
    return  " ".join(title)

def make_dictionary(cite) -> dict:
    return {item.split("=")[0].strip():item.split("=")[1].strip() for item in cite if '=' in item}


@contextmanager
def open_file(fname, mode):
    try:
        f = open(fname,mode)
        yield f
    except FileNotFoundError: sys.exit(f"NO Such a FILE as '{fname}'")
    finally: f.close()

# first reading the "aux" tex output file
class Aux2Url:
    """
    readling 'aux' file, get 'doi' and make 'url'
    """
    def __init__(self, auxfile) -> None:
        self.auxfile = auxfile
    
    def read_aux(self) -> list:
        with open_file(self.auxfile, 'r') as aux:
            aux_lines = aux.readlines()
        aux_lines = [line.strip() for line in aux_lines if line.startswith("\citation")]
        #seperate citaion from multi citted 
        aux_lines = [re.sub('(\\\citation{|})','',line).split(",") for line in aux_lines]
        #remove the duplicates
        self.doi_list = list(set(cite.strip() for line in aux_lines for cite in line))
    
    def check_journals(self) -> list:
        self.read_aux()
        #lowering the letter cases, just in case!
        self.doi_list = [doi.lower() for doi in self.doi_list]
        #seperate the arXiv ones, since it has different headers
        self.arxiv = [doi for doi in self.doi_list if doi.startswith("arxiv")]
        # books which are cited with "isbn:"
        self.book = [isbn for isbn in self.doi_list if isbn.startswith("isbn")]
        #normal journals
        self.journals = [doi for doi in self.doi_list if doi not in self.arxiv or self.book]
        self.journals = [doi for doi in self.journals if '/' in doi]
        #if updating "bib" file
        self.arxiv = [doi for doi in self.arxiv if doi not in arxiv]
        self.book = [isbn for isbn in self.book if isbn not in book]
        self.journals = [doi for doi in self.journals if doi not in journals]

    def make_url(self) -> list:
        self.check_journals()
        # make "url" for both:
        self.arxiv = [f'http://export.arxiv.org/api/query?id_list={doi.split(":")[-1]}' for doi in self.arxiv]
        self.journals = [f'http://dx.doi.org/{doi}' for doi in self.journals]
        self.book = [isbn.split(":")[1] for isbn in self.book]
        return self.arxiv, self.journals, self.book

class RequestCite:
    """
    make the headers and request
    """
    def __init__(self)-> str:
        self.jrnl_header = {'accept':'application/x-bibtex'}
        self.arx_header = None
    
    def header(self, url, src) -> str:
        self.header = self.jrnl_header if src == 'journals' else self.arx_header
        # self.header = self.jrnl_header if src == 'journals' else self.arx_header
        print(f"Request for: {url}", file=sys.stderr)
    def do_request(self, url, src) -> str:
        self.header(url, src)
        self.r = requests.get(url,headers=self.header)
        if self.r.ok :
            self.r.encoding = 'utf-8'
            #return the text as a list
            return self.r.text.split('\n')
        else: 
            sys.exit(f'Wrong "{url}" or Busy server')

class Arxiv2bib:
    """
    make a citation like the one from other journlas
    """
    def __init__(self, url) -> list:
        self._cit = RequestCite()
        html = self._cit.do_request(url,'arxiv')
        self.html = [item.strip() for item in html]
        self.url = url
    def get_eprint(self) -> int:
        return self.url.split("=")[1]
    
    def  cock_strudel(self) -> str:
        return f'@misc{{arxiv:{self.get_eprint()},'    
        
    def get_title(self) -> list:
        i_index = [i for i,item in enumerate(self.html) if item.startswith('<title>')][0]
        f_index = [i for i,item in enumerate(self.html) if item.endswith('</title>') and i>=i_index][0]
        self.title = self.html[i_index:f_index+1]
        if len(self.title)>1:self.title = " ".join(self.title) 
        else:self.title=self.title[0]
        self.title = re.sub('</title>', "", re.sub('<title>', "", self.title))
        self.title = [item.lower()  if not "-" in item else item for item in self.title.split(" ")]
        self.title = [item.capitalize()  if i==0 else item for i,item in enumerate(self.title)]
        return  " ".join(self.title)

    def get_authors(self)-> list:
        self.authors = [re.sub('<name>','', name) for name in self.html if name.startswith('<name>') ]
        self.authors = [re.sub('</name>','', name) for name in self.authors ]
        self.authors = " , ".join(self.authors)
        return  do_firstname(self.authors)
    
    def get_date(self) -> int:
        self.year = [re.sub('<updated>','', item) for item in self.html if item.startswith("<updated>")][0]
        return  self.year.split("-")
    
    def get_category(self) -> str:
        # line breaking:
        # <category term="cond-mat.mtrl-sci" scheme="http://arxiv.org/schemas/atom"/>
        self.catag = [item.split("term=")[1].split(' ')[0] for item in self.html if item.startswith("<category term=")][0]
        return  self.catag.replace('"','')
    
    def make_dic(self) -> list:
        self._bib = {'title':f'{{{self.get_title()}}},', 
        'author':f'{{{self.get_authors()}}},',
        'year':f'{{{self.get_date()[0]}}},',
        'month':f'{{{calendar.month_abbr[int(self.get_date()[1])]}}},',
        'eprint':f'{{{self.get_eprint()}}},',
        'howpublished':f'{{arXiv}},',
        'note':f'{{\href{{https://arxiv.org/abs/{self.get_eprint()}}}{{{self.get_category()}}}}} '}
        self._bib = [f'{key} = {self._bib[key]}' for key in self._bib]
        self._bib.append("}")
        return self._bib
    def __str__(self) -> str:
        print(f'{self. cock_strudel()}')
        for item in self.make_dic():
            print(f'\t{item}')
        

class Jour2bib:
    """
    modifying bibtex from normal journals
    """
    def __init__(self, url) -> None:
        self._cit = RequestCite()
        html = self._cit.do_request(url,'journals')
        self.html = html
        self.url = url
        self.strudel = self.html[0].split("{")[0]
    
    def make_dic(self) -> dict:
        html = [item.strip() for item in self.html]
        return make_dictionary(html)
    # make "@article" with "doi" as the label for the bibtex
    def cock_strudel(self) -> str:
        self.doi = re.sub('}','',self.make_dic()["doi"])
        # self.paper = lambda paper: expression
        return f'{self.strudel}{self.doi}'
    # change capitalization of the title
    def get_title(self) -> list:
        self.title = self.make_dic()['title']
        return f'{{{pretty_title(self.title)}'
    # change the format of authors names
    def get_authors(self) -> list:
        self.authors = self.make_dic()['author']
        return f'{{{do_firstname(self.authors)}}},'
    # hyperref the journals
    def get_hyper_journal(self) -> str:
        # some papers or jouranls "bibtex" dosent have "url", its easier to make it!
        self.doi = re.sub('{|}|,|"',"",self.make_dic()['doi'])
        self.url = f"https://doi.org/{self.doi}"
        if self.strudel.split("@")[1]=='article':
            self.journal=self.make_dic()['journal'] 
            return f"{{\href{{{self.url}}}{self.journal}}}"
        else: 
            self.journal=self.make_dic()['publisher'][:-1]
            return f"{{\href{{{self.url}}}{self.journal}}},"

    def titlecase(self,s):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group(0).capitalize(), s)
    # updating the bibtex
    def update_bib(self) -> list:
        self.bib = self.make_dic()
        self.bib['author'] = self.get_authors()
        self.bib['title'] = self.get_title()
        if self.strudel.split("@")[1]=='article':
            self.bib['journal'] = self.get_hyper_journal()
        else:
            self.bib['publisher'] = self.get_hyper_journal()
        if 'year' in self.bib: 
            year = (re.sub('{|}|,|"','',self.bib['year']))
            self.bib['year'] = f'{{{year}}},'
        if 'month' in self.bib:
            self.bib['month'] = self.titlecase(self.bib['month'])
        self.bib = [f'{key} = {self.bib[key]}' for key in self.bib]
        self.bib.append("}")
        return self.bib
    # print bibtex
    def __str__(self) -> str :
        bib = self.update_bib()
        print(self.cock_strudel())
        for item in bib:
            print(f'\t{item}')


class Book2Bib:
    """
    get bib for books
    """
    def __init__(self, isbn) -> int:
        self.isbn = isbn
        print(f"Citting for isbn:{self.isbn}",file=sys.stderr)
    
    # now you can use the service
    def get_html(self):
        SERVICE = 'openl'
        self.bibtex = bibformatters['bibtex']
        return self.bibtex(meta(self.isbn, SERVICE))
    
    def make_dic(self) -> dict:
        self.html = self.get_html().split("\n")
        html = [item.strip() for item in self.html]
        return make_dictionary(html)
    # change capitalization of the title
    def get_title(self) -> list:
        self.title = self.make_dic()['title']
        return f'{{{pretty_title(self.title)}'
    def cock_strudel(self) -> str:
        return f'@book{{isbn:{self.isbn},'
    def get_authors(self) -> list:
        self.authors = self.make_dic()['author']
        return f'{{{do_firstname(self.authors)}}},'
    def update_bib(self) -> list:
        self.bib = self.make_dic()
        self.bib['author'] = self.get_authors()
        self.bib['title'] = self.get_title()
        self.bib['publisher']=f"{self.bib['publisher']},"
        self.bib['note'] = f'{{ISBN: {self.isbn}}},'
        self.bib = [f'{key} = {self.bib[key]}' for key in self.bib]
        self.bib.append("}")
        return self.bib
    def __str__(self) -> str:
        bib = self.update_bib()
        print(self.cock_strudel())
        for i in bib: 
            print(f'\t{i}')

class READBIB:
    """
    Reading excisting 'bib' file to update
    """
    def __init__(self, fname) -> None:
        self.fname = fname
        del fname

    def read_bib(self) -> list:
        with open_file(self.fname, 'r') as f:
            for line in f:
                if line.startswith('@'):
                    self.get_id(line)

    def get_id(self,line) -> str:
        self.line = line
        self.id = self.line.split("{")[1][:-2].strip()
        self.get_list(self.id)

    def get_list(self, id) -> list:
        if id.startswith('arxiv'): arxiv.append(id)
        elif id.startswith('isbn'): book.append(id)
        elif '/' in id: journals.append(id)
        else: pass

    def return_list(self) -> list:
        self.read_bib()
        return arxiv, journals, book

source = sys.argv[1].split(".")[0]
arxiv, journals, book = [],[],[]
if sys.argv[1].split(".")[1]=='aux':
    print(f"creating: {source}.bib",file=sys.stderr)
    bibfile = source.__add__('.bib')
    sys.stdout = open(bibfile,'w')
elif sys.argv[1].split(".")[1]=='bib':
    print(f"updating: {source}.bib",file=sys.stderr)
    bib = READBIB(sys.argv[1])
    arxiv, journals, book = bib.return_list()
    bibfile =sys.argv[1]
    sys.stdout = open(bibfile,'+a')

aux = Aux2Url(source.__add__('.aux'))
arxiv, journals, book = aux.make_url()

def get_arxiv (url) :
    t = Arxiv2bib(url)
    t.__str__()
def get_journals (url) :
    t = Jour2bib(url)
    t.__str__()
def get_book (isbn) :
    t = Book2Bib(isbn)
    t.make_dic()
    t.__str__()
with concurrent.futures.ThreadPoolExecutor() as executor:
    j_papers = executor.map(get_journals,journals)
    x_papers = executor.map(get_arxiv,arxiv)
    bok_isbn = executor.map(get_book,book)
sys.stdout = sys.__stdout__
finish = time.perf_counter()
print(f'\nDONE IN {finish-start:.3f} second(s)\n')
