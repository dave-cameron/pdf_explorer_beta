
def get_page_links(page, page_number): 

    url_details_list = []
    cleaned_list = []

    link_list = page.get_links()
    
    for item in link_list:
        if "uri" in item: 
            try:
                if "http" in item["uri"] and item["uri"] not in cleaned_list:
                    cleaned_list.append(item["uri"])
            except Exception as e:
                print(f"\n[!!!] Error getting pdf: {str(e)}\n")
        
    # print (f"---------------------------------------------\n")
    if len(cleaned_list) < 1:
        print(f"[+++++] Found no URL(s) on page {page_number}") 
    else:
        print(f"[+++++] Found {len(cleaned_list)} URL(s) on page {page_number}")
        for item in cleaned_list:
            try:
                url_details_list.append({f"{page_number}" : item})
            except Exception as e:
                print(f"\n[!!!] Error getting pdf: {str(e)}")
   
    return url_details_list

def get_status(pdf_urls, http):
    
    url_status_details = []
    
    for pdf_url_dict in pdf_urls: #todo need to fix this 
        try: 
            for item in pdf_url_dict: # please fix this 
                response = http.request("GET", pdf_url_dict[item], retries = 5)
                url_status_details.append({f"{pdf_url_dict[item]} : URL status: {response.status}"})
                
        except Exception as e:
            print(f"\n[!!!!!] Error getting pdf: {str(e)}\n")

    return url_status_details

def get_page_images(page, page_number):
    image_details_list = []

    img_list = page.get_image_info()

    if len(img_list) < 1:
        print(f"[!!!!!] Found no images on {page_number}.") 
    else:
       print(f"[+++++] Found {len(img_list)} img(s) on {page_number}")

       for item in img_list:
           try:
           # print(f"[+++++] Found 1 img on {page_number + 1} of size: {item['size']}, with height: {item['height']} and width: {item['width']}")
            image_details_list.append({f"{page_number}" : f"Image information: size: {item['size']}, height: {item['height']}, width: {item['width']}"}) # list of dicts
           except Exception as e:
               print(f"\n[!!!!!] Error getting pdf: {str(e)}\n")
    return image_details_list