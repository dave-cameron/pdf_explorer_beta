import fitz as pdfCrawler # PyMuPDF
import pandas as pd
import urllib3 as httpclient
import os
import datetime as dt
import helpers

def create_pool_manager():
    timeout = httpclient.Timeout(connect=2.0, read=2.0)
    http = httpclient.PoolManager(timeout=timeout)
    return http

def get_pdf(pdf_url, http):

    try:
        pdf_response = http.request("GET", pdf_url, retries = 5)
        
        if pdf_response.status == 200:
            pdf_document = pdfCrawler.open(stream=pdf_response.data, filetype="pdf")
        else:
            print(f"Failed to fetch PDF from {pdf_url} because of {pdf_response.status_code}")
       
        return pdf_document, pdf_response 
    
    except Exception as err:
        print(f"Error getting pdf: {err}")

def get_page_metadata(page, page_num, response, pdf_url, http):

        if response.headers.get("Content-Disposition") is None:
            print(f"[!] Could not find file name, so generating a file name from url now.")
            pdf_file_name = pdf_url.split("/")[-1]
        else:
            pdf_file_name = response.headers.get("Content-Disposition").split("filename=")[1]
            
        print(f"File name: {pdf_file_name}")
            
        # try to get page length
        if response.headers.get("Content-Length") is None:
            print("Length of document not available")
        else:
            pdf_file_size = response.headers['Content-Length']

        page_links = helpers.get_page_links(page, page_num)
        page_url_status_dict = {}

        if len(page_links) >=1:
            page_url_status_dict = helpers.get_status(page_links, http)
        
        img_details = {}
       # img_details = helpers.get_page_images(page)

        return pdf_file_name, pdf_file_size, page_url_status_dict, img_details

def build_metadata_output(url, page_count, page_num,file_name, pdf_file_size, metadata, metadata_details):
       
       page_metadata = [
                                url, 
                                metadata["format"], 
                                pdf_file_size, 
                                file_name,
                                page_count,
                                metadata["creationDate"],
                                metadata["modDate"],
                                metadata["title"],
                                len(metadata["title"]),
                                metadata["author"],
                                metadata["subject"],
                                metadata["keywords"],
                                page_num,
                                metadata_details["item_type"],
                                metadata_details["item"],
                                metadata_details["item_detail"]
                            ] 
       return page_metadata

def create_output(page_metadata):

    file_name = f"PDF_Metadata_{dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}.xlsx"

    metadata_df = pd.DataFrame(page_metadata, columns=[
        "Url", 
        "Format", 
        "File size",
        "File name",
        "Page count", 
        "Date Created", 
        "Date Modified", 
        "Title",
        "Title Length",
        "Author",
        "Subject",
        "Keywords",
        "page",
        "item_type",
        "item",
        "item_detail",
    ])

    if os.path.exists(file_name):
        os.remove(file_name) 

    metadata_df.to_excel(file_name, sheet_name="PDF_Metadata", index=False)