# INCLUDE THE NECESSARY LIBRARIES

# Please install requests (pip install requests) if not installed
# Request library is for connecting to the https
import requests

import urllib.request
import urllib.error

# Regular expression for searching text
import re

# For reading/writing unicode files (UTF-8)
import codecs 

# For parse HTML document
from bs4 import BeautifulSoup 
 
import sys



def get_next_10_pages(input_text):
    """   
    # This function is the main function to begin with 
    # It does 2 things:
    
    # 1. Start with the root page, and get all the entries in the root page
    
    # 2. It will get next 10 pages, and for each page, get all the entries associated with that page
    #    Page number 11 will be next 10 pages    
    #    Get the next 10 pages. Which is equivalent to click on next 10 pages in the last table row.
    #    Normally, the last entry id is dgrMeetingResult$_ctl44$_ctl11
    #    And this function is called recursively untill the end.
     
    :param input_text: is the html page return by the function request.post
    :return: 
    """

    # Regex to find __VIEWSTATE
    # view state_re = re.compile('id=\"__VIEWSTATE\" value=\"[^\"]+\"')
    
    # 1. Get all entries in this page
    # get_all_entries_in_page(input_text)
    
    # 2. Get all entries for all parent pages except the next 10 pages
    get_all_pages(input_text)


def get_all_pages(input_text):
    """
    START NEXT FUNCTION
    Go to each page and get the detail record
    :param input_text: is the html page return by the function request.post
    :return: 
    """

    # Regex to find __VIEWSTATE
    view_state_re = re.compile('id=\"__VIEWSTATE\" value=\"[^\"]+\"')
    # Regex to find detail-link IDs

    pages_re = re.compile('__doPostBack\(\'dgrMeetingResult\$_ctl44+\$_ctl\d{1,10}\'')

    # Find __VIEWSTATE
    m = view_state_re.search(input_text)
    if m is None:
        print("Error: __VIEWSTATE not found")
        quit()
    else:
        # Extract the view state string including id="__VIEWSTATE"...
        vs = m.group()
        # vs =m
        # Extract __VIEWSTATE value
        vs = vs[24:-1]
        print("VIEWSTATE found")
        
        # Find all detail-link IDs
        # pages = pages_re.finditer(r.text)

        pages = pages_re.findall(input_text)

        print("Number of pages: %d" % len(pages))

        if pages is None:
            print("No detail pages found")
            quit()
            
        else:
            no_pages = len(pages)
            # Iterate through all links
            for i in range(0, (no_pages-1)):
                id = pages[i]
                # id = page.group()
                id = id[14:-1]
                print("Processing %s" % id)




                
                # Open the detail URL
               
                page_detail = requests.post(url_link, data={id: '','__VIEWSTATE': vs})

                if page_detail.status_code == requests.codes.ok:

                    # Get page number
                    page_no_text = get_current_page_number(page_detail.text)

                    # Get all entries for one parent page
                    get_all_entries_in_page(page_detail.text)
                    
                    # Save data of parent htlm
                    # fo = codecs.open("parents//page_"+ page_no_text+ str(i)+".html", "wb", "utf-8")
                    # fo.write(page_detail.text)
                    # fo.close()
                    
                    print("Page number: %s" % page_no_text)
                else:
                    print("Detail page for %s returns status code %d" % (id, page_detail.status_code))
                    
            # If it's not the end of the list, there are at least 10 more pages
            if is_last_page(input_text) == 0:
                id = pages[no_pages-1]
                # id = page.group()
                id = id[14:-1]
                print("Next 10 pages %s" % id)
                
                page_detail = requests.post(url_link, data={id: '', '__VIEWSTATE': vs})
                
                # Recursive call next 10 pages
                get_next_10_pages(page_detail.text)


def get_all_entries_in_page(input_text):
    """
    Get all entries for one company
    :param input_text: 
    :return: 
    """

    # Regex to find __VIEWSTATE
    viewstate_re = re.compile('id=\"__VIEWSTATE\" value=\"[^\"]+\"')
    # Regex to find detail-link IDs
    
    # Regex to find detail-link IDs
    link_re = re.compile('__doPostBack\(\'dgrMeetingResult\$_ctl[0-9]+\$lnkIssuerName\'')
 
    # Find __VIEWSTATE
    m = viewstate_re.search(input_text)
    
    # Get page number
    page_no_text = get_current_page_number(input_text)
    
    if page_no_text is None:
        print("Invalid page number!")
        return None
    
    if m is None:
        print("Error: __VIEWSTATE not found")
        quit()
    else:
        
        # Save data of parent HTML
        fo = codecs.open("parents//page_" + page_no_text + ".html", "wb", "utf-8")
        fo.write(input_text)
        fo.close()

        # Extract the viewstate string including id="__VIEWSTATE"...
        vs = m.group()
        # Extract __VIEWSTATE value
        vs = vs[24:-1]
        print("VIEWSTATE found")
        
        # Find all detail-link IDs
        links = link_re.finditer(input_text)
        if links is None:
            print("No detail links found")
            quit()
        else:
            file_id = 0
            # Iterate through all links
            
            for l in links:
                id = l.group()
                id = id[14:-1]
                print("Processing %s" % id)
                # Open the detail URL
                rdetail = requests.post(url_link, data={id: '', '__VIEWSTATE': vs})
                if rdetail.status_code == requests.codes.ok:
                    # Process detail-page here
                    # For now, write the page to a text file
                    fo = codecs.open("html//page"+page_no_text + "_no_" + str(file_id) + ".html", "wb", "utf-8")
                    fo.write(rdetail.text)
                    fo.close()
                    file_id = file_id + 1
                    
                    print("Process page: %s id = %d" % (page_no_text, file_id))
                else:
                    print("Detail page for %s returns status code %d" % (id, rdetail.status_code))
   

def get_current_page_number(input_text):
    """
    Get current page number
    :param input_text: 
    :return: 
    """
    start_row = re.search(r'<tr class="DGR_PAGER">', input_text, re.MULTILINE)
    #start_row = re.search(r'<tr class="DGR_ITEM">', input_text, re.MULTILINE)

    if start_row is None:
        print("Cannot find start of row")
        return ""
    else:
        # Start of the <tr> table row tag
        start_index = start_row.span()[0]
        
        end_row = re.search('</tr>', input_text[start_index:len(input_text)], re.MULTILINE)
        
        if end_row is None:
            print("Cannot find end of row")
            return ""
        else:
            # Get the end index of the table row tag
            end_index = start_index + end_row.span()[1]
            
            # HTML information of the last row
            html_row = input_text[start_index:end_index]
            
            # Put it in to BeutifulSoup object
            soup = BeautifulSoup(html_row, "lxml")
            
            # Current page, don't have the active link, but only span tag
            tb_span = soup.find_all("span")
            
            # If not foud return empty
            if tb_span is None:
                print("Cannot find span tag")
                return ""
            else:
                # First item only
                page_no_text = tb_span[0].text.strip()
                
                return page_no_text


def is_last_page(input_text):
    """
    START NEXT FUNCTION
    :param input_text: 
    :return: 
            1 if the last page is not "...", or it is a number page number 343 or something
            0 if last page is "...", which means there are at least 10 more pages
    """
    
    start_row = re.search(r'<tr class="DGR_PAGER">', input_text, re.MULTILINE)
    
    if start_row is None:
        print("Cannot find start of row")
        return ""
    else:
        # Start of the <tr> table row tag
        start_index = start_row.span()[0]
        
        end_row = re.search('</tr>', input_text[start_index:len(input_text)], re.MULTILINE)
        
        if end_row is None:
            print("Cannot find end of row")
            return ""
        else:
            # Get the end index of the table row tag
            end_index = start_index + end_row.span()[1]
            
            # HTML information of the last row
            html_row = input_text[start_index:end_index]
            
            # Put it in to BeautifulSoup object
            soup = BeautifulSoup(html_row, "lxml")
            
            # Current page, don't have the active link, but only span tag
            tb_pages = soup.find_all("a")
            
            # If not found return empty
            if tb_pages is None:
                print("Cannot find span tag")
                return 1
            else:
                # First item only
                no_pages = len(tb_pages)
                
                if no_pages == 0:
                    return 1
                
                else:
                    last_page_text = tb_pages[no_pages-1].text.strip()
                    
                    if last_page_text == "...":
                        return 0
                    else:
                        return 1             


def main(__url_link):
    """
    Main entry point function
    :param __url_link: url link
    :return: 
    """
    # Request the document, will go to root page
    r = requests.get(__url_link)

    # r = urllib.request.urlopen(__url_link)

    # Call the recursive function to get all data
    get_next_10_pages(r.text)



if __name__ == '__main__':
    """
    Main program start here
    """
    # Check argument  - No argument
    if len(sys.argv) == 1:
        # First argument should be from base data folder
        # __from_base_folder = sys.argv[1]

        # Link to the website - default
        url_link = 'https://viewpoint.glasslewis.net/webdisclosure/search.aspx?glpcustuserid=AIM118'
        # Call the main function
        main(url_link)

    # If have the second argument
    if len(sys.argv) == 2:
        # Get the link
        url_link = sys.argv[1]
        # Call the main function
        main(url_link)
    else:
        print("Invalid arguments")
        print("Use   : python glass_lewis.py ")
        print("Or use: python glass_lewis.py url_link")
