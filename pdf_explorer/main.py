import pandas as pd
import datetime as dt
import pathlib
import utils
import os

def main():
    
    #can be build file function 
    day = dt.datetime.today().strftime("%d/%m/%Y")
    time = dt.datetime.today().strftime("%H:%M:%S")
    
    file_name = "CCTAN_Public_PDFs.xlsx"
    parent_directory = pathlib.Path(__file__).parent.resolve()
    file_path = os.path.join(parent_directory, file_name)

    metadata_list = [] 
    skipped_urls = []
    worked_pdf = []

    print(f"\n---------------------------------------------")
    print(f"Starting the process at {time} on {day}")
    print(f"---------------------------------------------\n")
    
    try:
        http = utils.create_pool_manager()

        print(f"Getting the excel file and getting URLs:  {file_name}")

        excel_df = pd.read_excel(file_path)
        init_url_list = excel_df.iloc[:,0].values.flatten().tolist()  
        
        curr_url_count = 1
 
        for url in init_url_list:
            if curr_url_count <= 31: 
                if url in worked_pdf:
                    print("duplicate")
                else:
                    worked_pdf.append(url)
            
                    print(f"\n---------------------------------------------")
                    print(f"Currently processing PDF url #{curr_url_count}")
                    print(f"---------------------------------------------\n")

                    pdf_document, pdf_response = utils.get_pdf(url, http) 
                                                                                    
                    if pdf_document is None:
                        print(f"[!] Warning: There is no PDF to process because of an error for this url: {url}") 
                        skipped_urls.append({url})
                    else:
                        print(f"\n---------------------------------------------")
                        print(f"Getting metadata for PDF: {url}")
                        print(f"---------------------------------------------\n")

                        for page_num in range(pdf_document.page_count):
    
                            current_page = pdf_document.load_page(page_num)
                            pdf_file_name, pdf_file_size, url_details, img_details = utils.get_page_metadata(current_page, page_num, pdf_response, url, http)  
                            # combined_metadata_details = url_details.extend(img_details)
                            
                            # class? 
                            print(f"Build page object for page {page_num + 1}")
                            # for item in combined_details
                                # metadata_item = utils.build_metadata_output(pdf_file_name, pdf_file_size, pdf_document.metadata, metadata_detail)
                                # metadata_list.append(metadata_item)

                        curr_url_count += 1 

        # utils.create_output(metadata_list)
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

if __name__ == "__main__":
    # sys args
    main()
   

    