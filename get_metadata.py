import fitz as pdfCrawler # PyMuPDF
import requests
import re 
# from pypdf import PdfReader as pdr # py -m pip install pypdf 
# from io import BytesIO as stream # used to stream PDF

# to do - implement PDFMetadata class
class PDFMetaData:
    def __init__(self, pdfObject):
        self.format = ""
        self.title = ""
        self.author = ""
        self.subject = ""
        self.keywords = ""
        self.creator = ""
        self.created_date = ""
        self.mod_date = ""
        self.fonts = [] # list
        self.urls = {} # url, whether url is broken or good
        self.length = 0
        self.has_img = False
        self.image_count = 0 
        self.page_count = 0

    def get_page_count(self):
        return NotImplementedError

# get the PDF first
def get_pdf(response, pdf_url):

    if response.status_code != 200:
        print(f"Failed to fetch PDF from {pdf_url}")
        return

    # else create a PDF document object
    pdf_document = pdfCrawler.open(stream=response.content, filetype="pdf")
    
    return pdf_document.metadata

if __name__ == "__main__":
    
    pdf_url = "https://childcareta.acf.hhs.gov/sites/default/files/new-occ/resource/files/SBRG_Capacity%20Building%20Self%20Assessment%20Tool%202023_0.pdf"  # Replace with your PDF URL
    all_metadata = [] # pdf, object 
   
    # wrap in try / except / finally to catch errors that may happen
    try:
        # get the response back 
        response = requests.get(pdf_url)
        # create new method, "get_pdf" to open the PDF
        currentPDF = get_pdf(response, pdf_url)

        # now get the metadata from the current PDF
        # but want to implement a cleaner way to do this later on 

        metadata = {} # dictionary to hold relevant metadata
        print(currentPDF is dict)

        for item in currentPDF: # all the values in the metadata dictionary
            print(item) # print out each item
      
    # if there is an error, capture the error message 
    except Exception as err: 
    # print the error message so we know what happened and can try to fix the issue= (e.g., typo in the pdf_url)
        print("Error extracting URLs from pdf: ", err)
    finally:
        print("Done.")

    