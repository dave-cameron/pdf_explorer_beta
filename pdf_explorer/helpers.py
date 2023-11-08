
def get_page_links(page, page_number):

    all_urls = []
    url_to_add = []

    print(f"\n---------------------------------------------")
    print(f"Finding URLs in current PDF")
    print(f"---------------------------------------------\n")

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
        print(f"[!] Found no URLs on page {page_number + 1}\n")
    else:
        print(f"[+] Found {len(all_urls)} URL(s) on page {page_number + 1}\n")
        
    return all_urls

def get_status(pdf_urls, http):
    
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

def get_page_images(page):
   raise NotImplementedError
