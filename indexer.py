import os.path
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh import scoring
from whoosh import qparser

# Please see the main() function that utilizes all the helper functions to print p@10

# Set up index and schema
if not os.path.exists("index"):
    os.mkdir("index")
schema = Schema(title=TEXT(stored=True), content=TEXT)
ix = create_in("index", schema)
ix = open_dir("index")

def _openAndParse(path):
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

def _addParsedDocsToIndex():
    parsedDocs = _openAndParse("./med/MED.ALL")
    writer = ix.writer()
    for document in parsedDocs:
        title = document[0]
        content = document[1]
        writer.add_document(title=title, content=content)
    writer.commit()

def _runQuery(querystring):
    savedResults = []
    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        query = QueryParser('content', ix.schema, group=qparser.OrGroup).parse(querystring)
        results = searcher.search(query)
        for result in results:
            savedResults.append(result.get("title"))
        return savedResults

def _getRelevantDocList():
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


def _getPrecisionAtTen(queries, queryIdWithRelevantDocs):
    pAtTen = {}
    for query in queries:
        queryId = query[0]
        content = query[1]
        results = _runQuery(content)
        knownRelevantResults = queryIdWithRelevantDocs[queryId]
        relevantDocsInTopTenResults = 0
        for result in results:
            if result in knownRelevantResults:
                relevantDocsInTopTenResults += 1
        pAtTen[queryId] = relevantDocsInTopTenResults / 10.0
    return pAtTen

# This function does the following:
# 1. Index the docs from MED.ALL
# 2. queryIdWithRelevantDocs: Makes a dictionary with queryId as key and array of documentIds
# 3. queries: Get a list of queries along with the query id
# 4. precisionAtTen: Queries the index with queries from MED.QRY and checks how many of the first ten docs are relevant
def main():
    _addParsedDocsToIndex()
    queryIdWithRelevantDocs = _getRelevantDocList()
    queries = _openAndParse("./med/MED.QRY")
    precisionsAtTen = _getPrecisionAtTen(queries, queryIdWithRelevantDocs)

    print("=============")
    print("Query id | P@10 ")
    for queryId, pAtTen in precisionsAtTen.items():
        print(str(queryId) + ": " + str(pAtTen))

main()
