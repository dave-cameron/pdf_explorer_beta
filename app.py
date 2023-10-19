# start by calling all the libraries and packages needed to execute the script into the environment - kind of like JavaScript?
# QUESTION: where do these imports come from? do you need to designate these specficially or do they get added automatically?

import io
import fitz as pdfCrawler # PyMuPDF
import requests as request
import pandas as pd # https://pandas.pydata.org/docs/getting_started/index.html 
import urllib3 as httpclient
import re # regex
import os.path

from os import path
from urllib3 import Timeout, PoolManager 
from datetime import datetime as dt

# ?? is a "helper function" as commented below a term with specific meaning or just a general term?
# helper functions  
# create http session manager
def create_pool_manager():
    timeout = Timeout(connect=2.0, read=10.0)
    http = PoolManager(timeout=timeout)

    return http


# this defines a METHOD to be used named get_pdf
def get_pdf(pdf_url, http):

    try:
        # Download the PDF content from the URL and give it 5 chances to connect
        response = http.request("GET", pdf_url, retries = 5)
        
        if response.headers.get("Content-Disposition") is None:
            print(f"[!] Could not find file name, so generating a file name now.")
            pdf_file_name = pdf_url.split("/")[-1]
        else:
            pdf_file_name = response.headers.get("Content-Disposition").split("filename=")[1]
            
        print(f"File name: {pdf_file_name}")
            
        # try to get page length
        if response.headers.get("Content-Length") is None:
            print("Length of document not available")
        else:
            pdf_file_size = response.headers['Content-Length']

        if response.status != 200:
            print(f"Failed to fetch PDF from {pdf_url} because of {response.status_code}")
            return
        
        # Create a PDF document object
        pdf_document = pdfCrawler.open(stream=response.data, filetype="pdf")
        return pdf_document, pdf_file_size, pdf_file_name, 
    
    except httpclient.exceptions.NewConnectionError as err:
        print(f"Connection failed on {pdf_url} due to NewConnectionError: {err}.")
    except httpclient.exceptions.ReadTimeoutError as err:
        print(f"Connection failed on {pdf_url} due to ReadTimeoutError: {err}.")
    except Exception as err:
        print(f"Error getting pdf: {err}")

def get_metadata(url):
    # probably could do a lot more more in this method
    return pdf_document.metadata

def get_urls(pdf_document, url_pattern):

    # Initialize a list to store the URLs found in the PDF
    all_urls = []
    page_count = pdf_document.page_count

    print(f"\n---------------------------------------------")
    print(f"Finding URLs in current PDF")
    print(f"---------------------------------------------\n")

    # Loop through each page in the PDF
    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()
        
        # cleaned_page_text = clean_text(page_text)

        # Find all URLs on the page using the regular expression
        urls_on_page = set(re.findall(url_pattern, page_text))   # use set to remove duplicates (i.e., find all unique elements)

        # if no urls print found no urls, 
        if len(urls_on_page) < 1:
            print(f"[!] Found a total of {len(urls_on_page)} url(s) on page {page_number + 1}.")  # todo: clean this hack up (+ 1 to page_number)
        else:
            all_urls.extend(urls_on_page) # else add urls to list 
            print(f"[+] Found a total of {len(urls_on_page)} url(s) on page {page_number + 1}.") # and print # of urls found on page 

    print (f"---------------------------------------------")

    if len(all_urls) < 1:
        print(f"[!] Found no URLs in PDF\n")
    else:

        print(f"[+] Found {len(all_urls)} URL(s) in PDF\n")
        
    return all_urls

def check_url_status(pdf_urls, http):
    
    url_dict = {}

    print(f"\n---------------------------------------------")
    print(f"Checking status of URLs in PDF")
    print(f"---------------------------------------------\n")

    for url in pdf_urls:
        
        try:
            print(f"Checking status of url: {url}")
            response = http.request("GET", url, retries = 5)
    
            if response.status == 200:
                print(f"[+] URL status: {response.status}\n")
            else:
                print(f"[!] URL status: {response.status}\n")

            url_dict[url] = f"URL status: {response.status}"

        except httpclient.exceptions.NewConnectionError as e:
            print(f"\n[!] Connection failed on {url} due to NewConnectionError: {str(e)}.\n")
        except httpclient.exceptions.ReadTimeoutError as e:
            print(f"\n[!] Connection failed on {url} due to ReadTimeoutError: {str(e)}.\n")
        except httpclient.exceptions.TimeoutError as e:
            print(f"\n[!] Connection failed on {url} due to TimeoutError: {str(e)}.\n")
        except httpclient.exceptions.NameResolutionError as e:
            print(f"\n[!] Connection failed on {url} due to NameResolutionError: {str(e)}.\n")
        except Exception as e:
            print(f"\n[!] Error getting pdf: {str(e)}\n")

    return url_dict

def create_excel(metadata_list):

    file_name = f"PDF_Metadata_{dt.today().strftime('%Y-%m-%d')}.xlsx"

    # using pandas, create dataframe to hold all the data 
    metadata_df = pd.DataFrame(metadata_list, columns=[
        "Url", 
        "Format", 
        "File size",
        "File name",
        "Page count", 
        "Images count",
        "Date Created", 
        "Date Modified", 
        "Title", 
        "Author",
        "Subject",
        "Keywords",
        "URLs",  # {https://www.someurl.com: status 404,  https://www.someurl.com: status 200, ...} 
        # "Meets 508" # to implement
    ])
    
    # todo add check if file already exists, might be unsafe 
    if path.isfile(file_name):
        
        os.remove(file_name) # delete file
        # create excel document
        # will save in local folder
        metadata_df.to_excel(file_name, sheet_name="PDF_Metadata", index=False)

def get_num_of_images_in_doc(pdf_document): #todo, to implement with PyMuPDF
    
    image_count = 0
    for page_index in range(len(pdf_document)):
        
        try:
           image_list = pdf_document[page_index].get_images(full=True)
           
           # printing number of images found in this page
           if image_list:
               print(f"[+] Found a total of {len(image_list)} image(s) on page {page_index}")
               image_count += len(image_list)
           else:
               print(f"[!] No image(s) found on page {page_index}")

        except Exception as err:
           print(f"Exception getting image(s) dude error: {err}.\n")

    print(f"---------------------------------------------")
    print(f"[+] Total # of images in this PDF: {image_count}\n")
    return image_count

# ******************************************
# >>> THIS IS WHERE THE OUTPUT WILL BEGIN WHEN THIS RUNS <<<<
# ******************************************
if __name__ == "__main__":

    day = dt.today().strftime("%d/%m/%Y")
    time = dt.today().strftime("%H:%M:%S")

    print(f"\n---------------------------------------------")
    print(f"Starting the process at {time} on {day}")
    print(f"---------------------------------------------\n")

    URL_PATTERN = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" # does not work for aliases (i.e., "Click here!"), does not handle line breaks
    
    # path to the excel file or excel file name if in path
    path_to_file = "CCTAN-internal_pdfs_20230914.xlsx"

    # "wrap" your code in try, except, finally to catch errors so that you 1) can debug issues and 2) can ensure your program gracefully exits if it encounters an issue 
    try:
        # create the httpclient
        http = create_pool_manager()

        print(f"Getting the excel file and getting URLs:  {path_to_file}")
        excel_df = pd.read_excel(path_to_file)
        url_list = excel_df.iloc[:,0].values.flatten().tolist()  # grab the 2nd column (the column with URLs) and convert to a list 
        
        metadata_list = [] # created this to hold all of the metadata from the PDF url 
        skipped_urls = [] # PDF URLs that are broken or have issues so we can't analyze their contents

        # create a counter to keep track of how many URLs from the Excel spreadsheet we have looked at so far, starting with the first one
        curr_url_count = 1 

        # for each url in the list of URLs we took from the Excel spreasheet:
        for url in url_list:
            
            if curr_url_count <= 1:  # only look at the first URL so we can test
                
                # get the PDF, file size, file name
                print(f"\n---------------------------------------------")
                print(f"Currently processing PDF url #{curr_url_count}")
                print(f"Getting PDF information for: {url}")
                print(f"---------------------------------------------")

                pdf_document, pdf_file_size, pdf_file_name = get_pdf(url, http) # in the get_pdf function, pass in the url and http. 
                                                                                # this will return the pdf document, file size (bytes) and file name

                # check if nothing came becaise of an error 
                if pdf_document is None:
                    print(f"[!] Warning: There is no PDF to process because of an error for this url: {url}") 
                    skipped_urls.append({url})
                else:
                    print(f"\n---------------------------------------------")
                    print(f"Pulling metadata for PDF: {url}")
                    print(f"---------------------------------------------\n")

                    
                    images_count = get_num_of_images_in_doc(pdf_document) # get images 
                    pdf_urls = get_urls(pdf_document, URL_PATTERN)  # get urls from page
                    checked_urls = check_url_status(pdf_urls, http) # get all statuses of urls found in PDF
                    metadata = get_metadata(pdf_document)  # return metadata from the PDF
                    
                    # add URL + relevant metadata to list
                    current_url_metadata = [
                        url, 
                        metadata["format"], 
                        pdf_file_size, 
                        pdf_file_name,
                        pdf_document.page_count,
                        images_count,
                        metadata["creationDate"],
                        metadata["modDate"],
                        metadata["title"],
                        metadata["author"],
                        metadata["subject"],
                        metadata["keywords"],
                        checked_urls,
                    ]
                    # append the metadata for the current pdf url to the larger list of all PDFs/urls
                    metadata_list.append(current_url_metadata)

                curr_url_count += 1 # add 1 more to count 

        # create the final Excel file with all metadata from all PDFs
        create_excel(metadata_list)
        print("Created excel file.")

        #to do: create summary
        if len(skipped_urls) < 1:
            print(f"[O] No URLs were skipped.")
        else:
            for url in skipped_urls:
                print(f"[!] Skipped URL: {url}")

    except Exception as err:
        # print the error message so we know what happened and can try to fix the issue= (e.g., typo in the pdf_url)
        print("Error extracting URLs from pdf: ", err)
    # if there is an error, capture the error message 
    finally:
        print("Done.")

    