import fitz as pdfCrawler # PyMuPDF
import requests
import re


def extract_urls_from_pdf(pdf_url):
    # Download the PDF content from the URL
    response = requests.get(pdf_url)

    if response.status_code != 200:
        print(f"Failed to fetch PDF from {pdf_url}")
        return

    # Create a PDF document object
    pdf_document = pdfCrawler.open(stream=response.content, filetype="pdf")

    # Get the total page count
    total_pages = pdf_document.page_count

    # Get the dimensions of the first page (assuming all pages have the same dimensions)
    first_page = pdf_document.load_page(0)
    page_width = first_page.bound().width
    page_height = first_page.bound().height

    # Create a regular expression to find URLs in the PDF content
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # Initialize a list to store the URLs found in the PDF
    found_urls = []

    # Loop through each page in the PDF
    for page_number in range(total_pages):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()

        # Find all URLs on the page using the regular expression
        urls_on_page = re.findall(url_pattern, page_text)

        # Add the found URLs to the list
        found_urls.extend(urls_on_page)

    return found_urls, total_pages, (page_width, page_height)


if __name__ == "__main__":
    pdf_url = "https://childcareta.acf.hhs.gov/sites/default/files/new-occ/resource/files/SBRG_Capacity%20Building%20Self%20Assessment%20Tool%202023_0.pdf"  # Replace with your PDF URL
    urls, total_pages, dimensions = extract_urls_from_pdf(pdf_url)

    print(f"Total Pages: {total_pages}")
    print(f"Page Dimensions (width, height): {dimensions[0]} x {dimensions[1]} points")

    if urls:
        print("\nURLs found in the PDF:")
        for url in urls:
            print(url)
    else:
        print("\nNo URLs found in the PDF.")
