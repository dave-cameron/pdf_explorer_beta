import fitz as pdfCrawler # PyMuPDF
import pandas as pd
import urllib3 as httpclient
import os
import datetime as dt
import pathlib


def create_pool_manager(): # todo pass in optional arguments to be pulled from config
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

def get_metadata(url):
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
        "Images count",
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

def get_num_of_images_in_doc(pdf_document): #todo, to implement with PyMuPDF
    
    image_count = 0
    for page_index in range(len(pdf_document)):
        
        try:
           image_list = pdf_document[page_index].get_images(full=True)
           
           if image_list:
               print(f"[+] Found a total of {len(image_list)} image(s) on page {page_index + 1}") # hack
               image_count += len(image_list)
           else:
               print(f"[!] No image(s) found on page {page_index + 1}") # hack

        except Exception as err:
           print(f"Exception getting image(s) dude error: {err}.\n")

    print(f"-------------------------")
    print(f"[+] Total # of images in this PDF: {image_count}\n")
    return image_count

if __name__ == "__main__":

    day = dt.datetime.today().strftime("%d/%m/%Y")
    time = dt.datetime.today().strftime("%H:%M:%S")

    print(f"\n---------------------------------------------")
    print(f"Starting the process at {time} on {day}")
    print(f"---------------------------------------------\n")
    

    file_name = "CCTAN_Public_PDFs.xlsx"
    parent_directory = pathlib.Path(__file__).parent.resolve()
    file_path = os.path.join(parent_directory, file_name)

    try:
        http = create_pool_manager()

        print(f"Getting the excel file and getting URLs:  {file_name}")
        excel_df = pd.read_excel(file_path)
        url_list = excel_df.iloc[:,0].values.flatten().tolist()  
        
        metadata_list = [] 
        skipped_urls = [] 

        curr_url_count = 1 
 
        for url in url_list:
            if curr_url_count <= 1: 

                print(f"\n---------------------------------------------")
                print(f"Currently processing PDF url #{curr_url_count}")
                print(f"Getting PDF information for: {url}")
                print(f"---------------------------------------------")

                pdf_document, pdf_file_size, pdf_file_name = get_pdf(url, http) 
                                                                                
                if pdf_document is None:
                    print(f"[!] Warning: There is no PDF to process because of an error for this url: {url}") 
                    skipped_urls.append({url})
                else:
                    print(f"\n---------------------------------------------")
                    print(f"Pulling metadata for PDF: {url}")
                    print(f"---------------------------------------------\n")

                    
                    images_count = get_num_of_images_in_doc(pdf_document) 
                    links_in_pdf = get_links(pdf_document)  
                    checked_urls = check_url_status(links_in_pdf, http)
                    metadata = get_metadata(pdf_document)  
                    
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

                    metadata_list.append(current_url_metadata)

                    curr_url_count += 1 

 
        create_excel(metadata_list)
        print("Created excel file.")


        if len(skipped_urls) < 1:
            print(f"[O] No URLs were skipped.")
        else:
            for url in skipped_urls:
                print(f"[!] Skipped URL: {url}")

    except Exception as err:
        print("Error extracting URLs from pdf: ", err)
    finally:
        print("Done.")