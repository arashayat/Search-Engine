from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import glob
import os
import csv
import time
import re



if __name__ == '__main__':

    parsed_pages = open('Parsed_pages.csv', 'w', encoding='UTF8', newline='')
    writer = csv.writer(parsed_pages)

    path = 'DataSetFor IR BS' # html pages directory

    counter = 0

    st = time.time()

    writer.writerow(['Index', 'URL', 'Title', 'Body']) # setting names for columns

    for filename in glob.glob(os.path.join(path, '*.xml')): # get every xml file

        print('parsing file: ' + filename)

        pages = ET.parse(filename)
        root = pages.getroot()
        for doc in root: # for each page in xml file

            soup = BeautifulSoup(doc.find('HTML').text, 'html.parser') # using beautifulsoup to parse the html part of page
            
            doc_url = doc.find('URL').text # parse url data
            
            try:
                doc_title = soup.find('title').get_text() # parse title data
                # doc_title = re.sub(r'[^\w]', ' ', doc_title)

                doc_title = ' '.join(doc_title.split()) # remove excess whitespaces
            except:
                doc_title = ''

            try:
                doc_body = soup.find('body').get_text() # parse body data
                # doc_body = re.sub(r'[^\w]', ' ', doc_body)

                doc_body = ' '.join(doc_body.split()) # remove excess whitespaces

            except:
                doc_body = ''
            


            writer.writerow([counter, doc_url, doc_title, doc_body])
            counter += 1
    
    ft = time.time()
    print('time spent to parse pages: ', '{:.2f}'.format(ft - st))
