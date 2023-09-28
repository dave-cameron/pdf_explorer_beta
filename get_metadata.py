import fitz as pdfCrawler # PyMuPDF
import requests as request
import pandas as pd # https://pandas.pydata.org/docs/getting_started/index.html 
from datetime import datetime as dt

# helper functions 
def get_pdf(pdf_url):

    try:
        # Download the PDF content from the URL
        response = request.get(pdf_url)

        if response.status_code != 200:
            print(f"Failed to fetch PDF from {pdf_url} because of {response.status_code}")
            return

        # Create a PDF document object
        pdf_document = pdfCrawler.open(stream=response.content, filetype="pdf")
        return pdf_document
    except Exception as err:
        print(f"Failed to fetch PDF from {pdf_url} because of {err}") 

def get_metadata(url):
    # probably could do a lot more more in this method
    print(pdf_document.metadata)
    return pdf_document.metadata

def get_images(pdf_document): #todo, to implement with PyMuPDF
    raise NotImplementedError # return dict of "has image bool, count"

def check_url_status(pdf_document, pdf_urls): #todo, to implement with PyMuPDF
    raise NotImplementedError # todo, return list of dict of key = url, value = url status 

def contains_image(pdf_document): 
    raise NotImplementedError # to implement with PyMuPDF

def create_excel(metadata_list):
    # using pandas, create dataframe to hold all the data 
    metadata_df = pd.DataFrame(metadata_list, columns=["Url", 
                                                       "Format", 
                                                       # "File size", # to implement 
                                                       "Page count", 
                                                       "Title", 
                                                        "Date Created", 
                                                        "Date Modified", 
                                                        "Author",
                                                        "Subject",
                                                        "Keywords",
                                                       # "URLs"  # i.e., https://www.someurl.com, statusError; https://www.someurl.com, status200; 
                                                       # "Has Image(s),"  # to implement
                                                       # "Image count",  # to implement
                                                       # "Meets 508" # to implement
                                        ])

    # create excel document
    # todo add check if file already exists
    # will save in local folder
    metadata_df.to_excel(f"PDF_Metadata_{dt.today().strftime('%Y-%m-%d')}.xlsx", sheet_name="PDF_Metadata", index=False)


if __name__ == "__main__":
    
    print(f"Starting process at {dt.today()}")
    print(f"Grabbing excel file...")
    
    # "wrap" your code in try, except, finally to catch errors so that you 1) can debug issues and 2) can ensure your program gracefully exits if it encounters an issue 
    try:

        # path to the excel file or excel file name if in path
        path_to_file = "CCTAN-internal_pdfs_20230914.xlsx"

        # get the excel file from a path and convert to dataframe?
        excel_df = pd.read_excel(path_to_file)

        # grab the 2nd row (the row with URLs) and convert to a list 
        url_list = excel_df.iloc[:,0].values.flatten().tolist()
        
        #initalize list to store metadata
        metadata_list = []
        missed_urls = []

        # keep track of how many have been iterated so far
        curr_url_count = 0 

        # iterate over all the URLs in the dataframe
        for item in url_list:
            
            if curr_url_count < 30:  # only look at the first 30 so we can refine 
                # get the PDF from the URL
                pdf_document = get_pdf(item)

                # check if nothing came back b/c of error 
                if pdf_document is None:
                    print(f"Error with current url: {item}")
                    missed_urls.append({item})
                else:
                    #grab the metadata from the PDF and 
                    metadata = get_metadata(pdf_document)
                    #add URL + relevant metadata to list
                    current_url_metadata = [
                                            item, 
                                            metadata["format"], 
                                            pdf_document.page_count,
                                            metadata["title"],
                                            metadata["creationDate"],
                                            metadata["modDate"],
                                            metadata["author"],
                                            metadata["subject"],
                                            metadata["keywords"],
                                            ]

                    #append the metadata for the current pdf url to the larger list of all PDFs/urls
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

    