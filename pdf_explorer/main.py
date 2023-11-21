import pandas as pd
import datetime as dt
import pathlib
import utils
import os
import timeit

def main():
    
    start_time = dt.datetime.now()
    print(f"Starting process: {start_time}")
    
    start = timeit.default_timer()
    file_name = "CCTAN_Public_PDFs.xlsx"
    parent_directory = pathlib.Path(__file__).parent.resolve()
    file_path = os.path.join(parent_directory, file_name)

    final_output_rows = []
    temp_output_rows = []
    skipped_urls = []
    worked_pdf = []

    try:
        http = utils.create_pool_manager()

        print(f"[--->] Working file: {file_name}\n")

        excel_df = pd.read_excel(file_path)
        init_url_list = excel_df.iloc[:,0].values.flatten().tolist()  
        curr_url_count = 1
 
        for url in init_url_list:  
            if curr_url_count <= len(init_url_list) and url not in worked_pdf: 
                    worked_pdf.append(url)

                    print(f"[--->] Currently processing PDF #{curr_url_count}")
                    print(f"[--->] PDF name: {url}")

                    pdf_document, pdf_response = utils.get_pdf(url, http) 
                                                                                    
                    if pdf_document is None:
                        print(f"[!!!] Warning: There is no PDF to process because of an error for this url: {url}") 
                        skipped_urls.append({url})
                    else:
                        for page_num in range(pdf_document.page_count):
                            current_page = pdf_document.load_page(page_num)
                            friendly_page_num = page_num + 1

                            print(f"\n[----->] Processing page: {friendly_page_num}") 
                            temp_output_rows = utils.build_metadata_output(url, pdf_document, current_page, friendly_page_num, pdf_response, http, info_type=None)
                            final_output_rows.extend(temp_output_rows)
                    
                    duration = timeit.default_timer() - start
                    print(f"\n*****Time elapsed: {duration}\n")
                    curr_url_count += 1 

        utils.create_output(final_output_rows)
        print("Created excel file.")

        if len(skipped_urls) < 1:
            print(f"[O] No URLs were skipped.")
        else:
            for url in skipped_urls:
                print(f"[!] Skipped URL: {url}")
        
        duration = timeit.default_timer() - start
        end_time = dt.datetime.now()

        print(f"\n[!!!!] Ending processs")
        print(f"Start time: {start_time} | End time: {end_time}")
        print(f"Time elapsed: {duration}")

    except Exception as e:
        print(f"Error extracting URLs from pdf: {str(e)}")
    finally:
        print("Done.")

if __name__ == "__main__":
    # sys args
    main()
   

    