import pandas as pd
import datetime as dt
import pathlib
import utils
import os



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
        http = utils.create_pool_manager()

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

                pdf_document, pdf_file_size, pdf_file_name = utils.get_pdf(url, http) 
                                                                                
                if pdf_document is None:
                    print(f"[!] Warning: There is no PDF to process because of an error for this url: {url}") 
                    skipped_urls.append({url})
                else:
                    print(f"\n---------------------------------------------")
                    print(f"Pulling metadata for PDF: {url}")
                    print(f"---------------------------------------------\n")

                    # todo: group, put in a class?
                    # images_count = utils.get_num_of_images_in_doc(pdf_document) 
                    links_in_pdf = utils.get_links(pdf_document)  
                    checked_urls = utils.check_url_status(links_in_pdf, http)
                    metadata = utils.get_metadata(pdf_document)  
                    
                    # class? 
                    current_url_metadata = [
                        url, 
                        metadata["format"], 
                        pdf_file_size, 
                        pdf_file_name,
                        pdf_document.page_count,
                        # images_count,
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

 
        utils.create_excel(metadata_list)
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