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
            print(f"[!!!] Failed to fetch PDF from {pdf_url} because of {pdf_response.status_code}")
       
        return pdf_document, pdf_response 
    
    except Exception as err:
        print(f"Error getting pdf: {err}")

def get_page_metadata(document, page, response, pdf_url, page_num, http, info_type):

    img_details = []
    url_status_details = []
    page_links = []

    metadata = document.metadata

    if response.headers.get("Content-Disposition") is None:
        pdf_file_name = pdf_url.split("/")[-1]
    else:
        pdf_file_name = response.headers.get("Content-Disposition").split("filename=")[1]
        
    if response.headers.get("Content-Length") is not None:
        pdf_file_size = response.headers['Content-Length']

    page_links = helpers.get_page_links(page, page_num)

    if len(page_links) >=1 and info_type is not None: # and the key for getting the links
        url_status_details = helpers.get_status(page_links, http)

    img_details = helpers.get_page_images(page, page_num)

    return metadata, pdf_file_name, pdf_file_size, page_links, url_status_details, img_details

def build_metadata_output(url, document, page, page_num, response, http, info_type = None):
    
    page_metadata_list = []  
    page_metadata_details = []
    url_status_details = []
    img_details = []

    img_counts = 0
    page_link_count = 0

    metadata, file_name, file_size, page_links, url_status_details, img_details = get_page_metadata(document, page, response, url, 
                                                                                                      page_num, http, info_type)
    
    for item in page_links:
        page_metadata_details.append(item) # list of dicts

    for item in url_status_details:
        page_metadata_details.append(item)
        page_link_count += 1

    for item in img_details:
        page_metadata_details.append(item)
        img_counts += 1
        
    for row in page_metadata_details:
        for k, v in row.items():
            try:
                if "Image" in v:
                    item_type = "Image"
                    item_detail = v
                else:
                    item_type = "Url"
                    item_detail = v
                
                page_metadata = [
                                url, 
                                metadata["format"], 
                                file_size, 
                                file_name,
                                document.page_count,
                                metadata["creationDate"],
                                metadata["modDate"],
                                metadata["title"],
                                len(metadata["title"]),
                                metadata["author"],
                                metadata["subject"],
                                metadata["keywords"],
                                page_num,
                                item_type,
                                item_detail
                            ] 
                
                page_metadata_list.append(page_metadata)
            except Exception as e:
                print(f"Error extracting URLs from pdf: {str(e)}")
    

    return page_metadata_list

def create_output(page_metadata_list):

    file_name = f"PDF_Metadata_{dt.datetime.today().strftime('%Y-%m-%d')}.xlsx"
    
    try:
        metadata_df = pd.DataFrame(page_metadata_list, columns=[
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
            "Page #",
            "Item Type",
            "Item Details",
        ])
    except Exception as e:
        print(f"Error extracting URLs from pdf: {str(e)}")

    # todo implement summary of all rows
    
    if os.path.exists(file_name):
        os.remove(file_name) 

    metadata_df.to_excel(file_name, sheet_name="PDF_Metadata", index=False)
