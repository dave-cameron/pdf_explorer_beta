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
from PIL import Image # may not need this but keeping just in case

# helper functions  
# create http session manager
def create_pool_manager():
    timeout = Timeout(connect=2.0, read=10.0)
    http = PoolManager(timeout=timeout)

    return http

def get_pdf(pdf_url, http):

    try:
        # Download the PDF content from the URL
        response = http.request("GET", pdf_url, retries = 5)
        
        if response.headers.get("Content-Disposition") is None:
            print("No Content Disposition that has file name so creating file name from URL")
            pdf_file_name = pdf_url.split("/")[-1]
        else:
            pdf_file_name = response.headers.get("Content-Disposition").split("filename=")[1]
            
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
    print(pdf_document.metadata)
    return pdf_document.metadata

def get_urls(pdf_document, url_pattern):

    # Initialize a list to store the URLs found in the PDF
    found_urls = []
    page_count = pdf_document.page_count

    # Loop through each page in the PDF
    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()
        
        # cleaned_page_text = clean_text(page_text)

        # Find all URLs on the page using the regular expression
        urls_in_pdf = set(re.findall(url_pattern, page_text))   # use set to remove duplicates (i.e., find all unique elements)

        # Add the found URLs to the list
        found_urls.extend(urls_in_pdf)
        print(f"Number of urls found on page {page_number + 1}: {len(urls_in_pdf)}") # todo: clean this hack up

    return found_urls

def check_url_status(pdf_urls, http):
    
    url_dict = {}

   
    for url in pdf_urls:
        
        try:
            print(f"Checking status of url: {url}")
            response = http.request("GET", url, retries = 5)
            url_dict[url] = f"URL status: {response.status}"

        except httpclient.exceptions.NewConnectionError as err:
            print(f"Connection failed on {url} due to NewConnectionError: {err}.")
        except httpclient.exceptions.ReadTimeoutError as err:
            print(f"Connection failed on {url} due to ReadTimeoutError: {err}.")
        except httpclient.exceptions.TimeoutError as err:
            print(f"Connection failed on {url} due to TimeoutError: {err}.")
        except httpclient.exceptions.NameResolutionError as err:
            print(f"Connection failed on {url} due to NameResolutionError: {err}.")
        except Exception as err:
            print(f"Error getting pdf: {err}")

    return url_dict

def create_excel(metadata_list):

    file_name = f"PDF_Metadata_{dt.today().strftime('%Y-%m-%d')}.xlsx"

    # using pandas, create dataframe to hold all the data 
    metadata_df = pd.DataFrame(metadata_list, columns=["Url", 
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
               print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
               image_count += len(image_list)
           else:
               print(f"[!] No images found on page {page_index}")

        except Exception as err:
           print(f"Exception getting images dude error: {err}.")

    print("Total images in this PDF: ", image_count)
    return image_count

if __name__ == "__main__":
    
    print(f"Starting process at {dt.today()}")
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" # does not work for aliases (i.e., "Click here!"), does not handle line breaks
    
    # path to the excel file or excel file name if in path
    path_to_file = "CCTAN-internal_pdfs_20230914.xlsx"

    # "wrap" your code in try, except, finally to catch errors so that you 1) can debug issues and 2) can ensure your program gracefully exits if it encounters an issue 
    try:
        # create the httpclient
        http = create_pool_manager()

        # get the excel file from a path and convert to dataframe?
        print(f"Grabbing excel file {path_to_file}")
        excel_df = pd.read_excel(path_to_file)

        # grab the 2nd row (the row with URLs) and convert to a list 
        url_list = excel_df.iloc[:,0].values.flatten().tolist()
        
        #initalize list to store metadata
        metadata_list = []
        missed_urls = [] # PDF URLs that are broken or have issues so we can't analyze their contents

        # keep track of how many have been iterated so far
        curr_url_count = 1 

        # iterate over all the URLs in the dataframe
        for url in url_list:
            
            if curr_url_count <= 1:  # only look at the first 'n' so we can refine 
                
                # get the PDF, file size, file name
                print(f"Working PDF #{curr_url_count}")
                print(f"Getting PDF for: {url}")
                pdf_document, pdf_file_size, pdf_file_name = get_pdf(url, http)

                # check if nothing came back b/c of error 
                if pdf_document is None:
                    print(f"Error with current url: {url}")
                    missed_urls.append({url})
                else:
                    print(f"Pulling metadata for PDF: {url}")
                    # get images
                    images_count = get_num_of_images_in_doc(pdf_document)
                    # get urls from page
                    pdf_urls = get_urls(pdf_document, url_pattern)
                    checked_urls = check_url_status(pdf_urls, http)
                    # grab the metadata from the PDF and 
                    metadata = get_metadata(pdf_document)
                    
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
        print("Created excel file")
        print("Missed URLs: ")

        for item in missed_urls:
            print({item})

    except Exception as err:
        # print the error message so we know what happened and can try to fix the issue= (e.g., typo in the pdf_url)
        print("Error extracting URLs from pdf: ", err)
    # if there is an error, capture the error message 
    finally:
        print("Done.")

    