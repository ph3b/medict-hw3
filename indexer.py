import os.path
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser

# Set up index and schema
if not os.path.exists("index"):
    os.mkdir("index")
schema = Schema(title=TEXT, content=TEXT)
ix = create_in("index", schema)
ix = open_dir("index")

def openAndParse(path):
    rawDocs = open(path, "r")
    
    formattedDocs = []
    title = None
    content = ""
    
    for index, line in enumerate(rawDocs.readlines()):
        strippedLine = line.rstrip()
        
        if ".I" in strippedLine:
        
            if title != None:
                formattedDocs.append([unicode(title), unicode(content)])
        
            title = strippedLine.split(" ")[1]
            content = ""

        elif ".W" not in strippedLine:
            content += strippedLine

    return formattedDocs

def addParsedDocsToIndex():
    parsedDocs = openAndParse("./med/MED.ALL")
    writer = ix.writer()

    for document in parsedDocs:
        title = document[0]
        content = document[1]
        writer.add_document(title=title, content=content)
    
    writer.commit()

def query(querystring):
    with ix.searcher() as searcher:
        query = QueryParser('content', ix.schema).parse(unicode(querystring))
        results = searcher.search(query)
        for result in results:
            print(result)

addParsedDocsToIndex()
query("heart")