#!/usr/bin/python3

import json
import csv
#import urllib2
import requests
import sys

""" 
%prog [inputfile] [outputfile]]
Provided a file of OCLC numbers, return ISBN(s)
"""
# From the Hathi API documentation: https://www.hathitrust.org/bib_api
# In the simplest case, to retrieve volume information based on a single identifier, the following syntax would be used:

# http://catalog.hathitrust.org/api/volumes/brief/<id type>/<id value>.json
# http://catalog.hathitrust.org/api/volumes/full/<id type>/<id value>.json

# The difference between a brief and full API request is that complete MARC-XML is returned in a full response.

hURL_brief = 'http://catalog.hathitrust.org/api/volumes/brief/oclc/'
hURL_full = 'http://catalog.hathitrust.org/api/volumes/full/oclc/'

oNum = ''
hStub = '.json'

class codesList:
    def __init__(self, fh):
        self.codeFile = fh
    def listed(self):
        lines = [] #    
        for line in self.codeFile.readlines():
            lines.append(line.strip())
        return lines

def print_status(numcodes, totalNum, msg): #progress indicator
    """status printing utility for long-running scripts"""
    print('Record: {} / {} {:>20}\r'.format(numcodes, totalNum, msg), end='\r'),
    sys.stdout.flush()  

def lookup(url):
    try:
        h_response = requests.get(url)
        txtResult = h_response.text
        jsonResult = json.loads(txtResult)
        return jsonResult
    except AttributeError as e:
        print('AttributeError: {} \n url: {}'.format(e,url))
        return ""
    except TypeError as e:
        print('TypeError: {} \n url: {}'.format(e,url))
        return ""
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return ""

def get_hathi_rec_report(oclc_num, h_result):
    """Accept a dictionary of hathi fields and return a list
    that includes catalog url, item url, and rights"""
    # Hathi data consists of records and items. A record is a description 
    # of a bibliographic entity (a book, serial, etc.)
    # An item is a physical volume that was scanned. 
    # Each item belongs to a single record, 
    # but a single record (e.g., the record for the journal Nature) 
    # may have many items associated with it.
    records = h_result['records']
    items = h_result['items']
    csv_rows=[]
    for item in items:
        # each item is a dictionary with fields:
        # enumcron, fromRecord, htid, itemURL, lastUpdate, orig, rightsCode, usRightsString
        #see: https://catalog.hathitrust.org/api/volumes/brief/oclc/1019548.json
        # print('\n item url: {} \n rights: {}'.format(item['itemURL'], item['usRightsString']))
        for record in records:
            if record == item['fromRecord']:
                csv_row = [oclc_num, records[record]['recordURL'],item['itemURL'],item['usRightsString']]
                csv_rows.append(csv_row)
    return csv_rows

def search(lCodes): 
    numo=len(lCodes)
    csv_rows = []
    for i,oclc_num in enumerate(lCodes): # Iterate through the codes
        print_status(i,numo,oclc_num)
        hReq = hURL_brief+oclc_num+hStub
        queryResult = lookup(hReq)
        csv_row = get_hathi_rec_report(oclc_num, queryResult)            
        #print(csv_row)
        if len(csv_row)>0:
            csv_rows.append(csv_row)
    return csv_rows

if __name__ == "__main__":        
    fileIn = sys.argv[1] #                          get the text data to process
    fileOut = sys.argv[2]    #                      put results here
    with open(fileIn,'r') as inputF, open(fileOut,'w', newline='') as outputF:
        csvw = csv.writer(outputF,delimiter=',', quotechar='"')  # csv writing machine
        csvw.writerow(['OCLCNUM','Hathi_catalog_entry','hathi_item_url', 'rights'])
        codeList = codesList(inputF) #                prep a list object
        codes = codeList.listed() #                    read file into a list, whitespace removed    
        results = search(codes) #                      DO THE ACTUAL LOOKUPS  
        for row in results:
            for r in row:
                csvw.writerow(r)
