import fitz as pdfCrawler # PyMuPDF
import pandas as pd
import urllib3 as httpclient
import os
import datetime as dt

def create_pool_manager():
    timeout = httpclient.Timeout(connect=2.0, read=2.0)
    http = httpclient.PoolManager(timeout=timeout)
    return http

def get_pdf(pdf_url, http):

    try:
        # Download the PDF content from the URL
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

def get_metadata(pdf_document):
    # probably could do a lot more more in this method
    return pdf_document.metadata

def get_links(pdf_document):

    page_count = pdf_document.page_count
    all_urls = []
    url_to_add = []

    print(f"\n---------------------------------------------")
    print(f"Finding URLs in current PDF")
    print(f"---------------------------------------------\n")

    for page_number in range(page_count):
       
        page = pdf_document.load_page(page_number)
        link_object = page.get_links()

        if len(link_object) < 1:
            print(f"[!] Found no URLs on {page_number + 1}.")  # todo: clean this hack up (+ 1 to page_number)
        else:
            for item in link_object:
                
                if item['uri'] in url_to_add:
                    print(f"[!] Already addded:{item['uri']}")        
                else:
                    print(f"[+] URL located on page {page_number + 1}: {item['uri']}")  
                    url_to_add.append(item['uri'])  
                    all_urls.append({f"{page_number + 1}" : item["uri"]})
                    
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
    
    for pdf_url_dict in pdf_urls: #todo need to fix this 
       
        try: 
            for item in pdf_url_dict: # please fix this 
                print(f"Checking status of url: {pdf_url_dict[item]}")
                response = http.request("GET", pdf_url_dict[item], retries = 5)
    
                if response.status == 200:
                    print(f"[+] URL status: {response.status}\n")
                else:
                    print(f"[!] URL status: {response.status}\n")

                url_dict[pdf_url_dict[item]] = f"URL status: {response.status}"
                
        except Exception as e:
            print(f"\n[!] Error getting pdf: {str(e)}\n")

    return url_dict

def create_excel(metadata_list):

    file_name = f"PDF_Metadata_{dt.datetime.today().strftime('%Y-%m-%d')}.xlsx"


    metadata_df = pd.DataFrame(metadata_list, columns=[
        "Url", 
        "Format", 
        "File size",
        "File name",
        "Page count", 
        # "Images count",
        "Date Created", 
        "Date Modified", 
        "Title", 
        "Author",
        "Subject",
        "Keywords",
        "URLs",  # {https://www.someurl.com: status 404,  https://www.someurl.com: status 200, ...} 
    ])
    

    if os.path.exists(file_name):
        os.remove(file_name) 

    metadata_df.to_excel(file_name, sheet_name="PDF_Metadata", index=False)
