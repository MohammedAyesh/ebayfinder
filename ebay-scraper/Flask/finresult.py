from pathlib import Path
import pandas as pd
import google.generativeai as genai

# Install the package if not already installed
# pip install google-generativeai
def printresponse():
    # Configure the API key
    genai.configure(api_key="")

    # Set up the model configuration
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

    system_instruction = """
    You will be given a list of products. You will remove all outliers in the list like accessories to the product.
    You will then return by index the product with the maximum Price,
    the one with the lowest price, and what is the best deal for your money.
    Prioritize used products that offer the lowest value for what is a working product. That is your only consideration
    Keep in mind that price is the most important factor when considering what is the best deal. Do not consider a brand new product unless it is better priced than used.
    Do not consider any for parts products.
    If the specific model is given, make sure to filter out all the other models even if they are very similar.
    You will be told what the actual product is so you can remove any outliers.
    Finally, you will return 5 other recommended products by index
    Your final line of text will return first the index of the best deal product, then the indexes of the 5 other recommended products in the following format:
    034 067 012 044 078 101
    """

    # Initialize the model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                generation_config=generation_config,
                                system_instruction=system_instruction)

    # Function to extract content from an Excel file and convert to a list of strings
    def extract_excel_data(file_path: str) -> list[str]:
        df = pd.read_excel(file_path)
        data_str_list = df.astype(str).values.flatten().tolist()
        return data_str_list

    # Define the file path to your Excel file
    excel_file_path = r'C:\Users\meesh\Downloads\EbayScrap\Ebay Scraper\scrapfly-scrapers\ebay-scraper\results\ebay_data.xlsx'

    # Create the prompt parts with data from the Excel file

    prompt_parts = [
    "Meta Quest 3\n\n",
    #*extract_pdf_pages("<path>/document0.pdf"),
    "\n## Meta Quest 3 Analysis:\n\n**Highest Price:**\n\n* **Index 69:** Used Meta Quest 3 128GB VR Headset w/ Elite Strap And Carrying Case for **$524.99**.  This is likely overpriced due to the inclusion of accessories.\n\n**Lowest Price:**\n\n* **Index 1:** New Listing Meta Quest 3 for **$400.00** in Pre-Owned condition.  While this is the lowest price, the condition and lack of details in the listing may be concerning.\n\n**Best Deal:**\n\n*  Index 1: This is the best priced one and is in Pre-Owned Condition.\n001, 045, 078, 098, 102, 033\n\nApple pro 6th generation\n",
    #*extract_pdf_pages("<path>/document1.pdf"),
    "\n## Apple iPad Pro 6th Generation Analysis: \n\nBased on the provided eBay data, I have filtered listings for other iPad models, iPads with accessories bundled in, and \"For Parts\" items. Here's a summary:\n\n**Highest Price:**\n\n* **Index 101:** New Apple 12.9\" iPad Pro 6th Gen M2 2TB Wi-Fi + 5G Cellular Unlocked Space Gray for **$1,699.99**. This is a brand new, high-end configuration with maximum storage and cellular connectivity, explaining the top price.\n\n**Lowest Price:**\n\n* **Index 29:** Apple iPad 6th Gen 32GB - Wi-Fi Only -  Very Good for **$117.00**. This is a regular iPad 6th gen, not the Pro model, with lower storage capacity and in refurbished condition.\n\n**Best Deal:**\n\n*  **Index 31:** Apple iPad Pro 6th Gen. 256GB, Wi-Fi, 12.9in - Space Gray. **$700.00**. This is the one of the best priced Ipad Pro but has 256 Gb instead of the slightly lower priced 128Gb model available at index 33\n\nMake sure to only list iPad Pro's and not any other model. You should not have included the the regular ipad\n\n\n031, 005, 028, 068, 012, 038\n\n\niPhone 11 Pro Max Unlocked\n\n",
    #*extract_pdf_pages("<path>/document2.pdf"),
    "\n\n\n## iPhone 11 Pro Max Unlocked Analysis: \n\nI've filtered out listings that weren't for the iPhone 11 Pro Max, locked phones, those bundled with accessories, and \"For Parts\" items. \n\n**Highest Price:**\n\n* **Index 55:** Apple iPhone 11 PRO MAX 64GB 256GB 512GB (UNLOCKED) ⚫🟠🔋 100% BATTERY🔋❖SEALED❖ for **$444.95**.  This is a brand new, sealed unit, justifying the higher cost.\n\n**Lowest Price:**\n\n* **Index 59:** 【Lowest Price Online】Apple iPhone 11 Pro Max 64G/256G- 6.5-inch screen-Unlocked for **$79.70** from China. The extremely low price and origin raise concerns about authenticity and condition.\n\n**Best Deal:**\n\n* **Index 25:** Apple iPhone 11 Pro Max - A2161 - 256GB - Space Gray (None - Unlocked)  (s17248) for **$264.11**. This offers a good balance of storage space (256GB) and price, assuming the condition is acceptable based on the seller's description.\n",
    #*extract_pdf_pages("<path>/document3.pdf"),
    "\n#\n025, 044, 078, 013, 090, 047\n## Ember Mug 2 Analysis:\n\nI've filtered the listings to only include Ember Mug 2 models, excluding those with accessories, \"For Parts\" items, and listings for other Ember products (like the travel mug).\n\n**Highest Price:**\n\n* **Index 23:** Ember Mug2 Smart Temperature Controlled Cup 14OZ IPX7 LED Stainless Steel Copper for **$134**. This is a brand new, stainless steel mug with extra features, justifying its high price.\n\n**Lowest Price:**\n\n* **Index 2:** Ember Temperature Control Smart Mug 2 10 oz. Smartphone Control 1.5 Hr Battery for **$34**. This is a used mug in Pre-Owned condition, which explains its lower price.\n\n**Best Deal:**\n\n* **Index 2:**  The used Ember Mug 2 for $34 is the best deal for your money. Even though it's pre-owned, it's significantly cheaper than other listings for new Ember mugs and offers the same functionality. The lower capacity (10oz) might be a consideration, but it's still a good deal for a working, used Ember Mug 2. \n002, 056, 078, 011, 012, 045\n",
    #*extract_pdf_pages("<path>/document4.pdf"),
    "\n## Xbox Series S Analysis:\n\nI've filtered out listings that weren't for the Xbox Series S, listings for other consoles (Series X, One X), bundles with accessories, and \"For Parts\" items.\n\n**Highest Price:**\n\n* **Index 2:** Xbox Series S - 1TB (Black) for **$349**. This listing is for a brand new Series S with 1TB of storage, justifying its higher price compared to the standard 512GB model.\n\n**Lowest Price:**\n\n* **Index 22:** New Listing for **$79**.  This is a used console with no information about its condition, making it a risky purchase.\n\n**Best Deal:**\n\n* **Index 6:** Microsoft Xbox Series S 512GB Video Game Console - White for **$172**. This is a used console in Pre-Owned condition, offering a significant discount compared to brand new listings. It's the best deal because it's a working, used console at a lower price than other used options.\n\n006, 032, 067, 001, 089, 055\n",
        *extract_excel_data(excel_file_path),
    ]
    response = model.generate_content(prompt_parts)
    
    return(response.text)

print(printresponse())