import os.path
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh import scoring

# Set up index and schema
if not os.path.exists("index"):
    os.mkdir("index")
schema = Schema(title=TEXT(stored=True), content=TEXT)
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

def runQuery(querystring):
    savedResults = []
    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        query = QueryParser('content', ix.schema).parse(querystring)
        results = searcher.search(query)
        for result in results:
            savedResults.append(result.get("title"))
        return savedResults

def getRelevantDocList():
    queryIdWithRelevantDocs = {}
    with open("./med/MED.REL") as relDocs:
        for line in relDocs:
            strippedLine = line.rstrip().split(" ")
            queryId = strippedLine[0]
            documentId = strippedLine[2]
            if queryId in queryIdWithRelevantDocs:
                queryIdWithRelevantDocs[queryId] = queryIdWithRelevantDocs[queryId] + [documentId]
            else:
                queryIdWithRelevantDocs[queryId] = [documentId]
        return queryIdWithRelevantDocs


def getPrecisionAtTen(queries, queryIdWithRelevantDocs):
    pAtTen = {}
    for query in queries:
        queryId = query[0]
        content = query[1]
        results = runQuery(content)
        pAtTen[queryId] = len(results)
    return pAtTen

addParsedDocsToIndex()
queryIdWithRelevantDocs = getRelevantDocList()
queries = openAndParse("./med/MED.QRY")
precisionsAtTen = getPrecisionAtTen(queries, queryIdWithRelevantDocs)
for p in precisionsAtTen.values():
    print(p)