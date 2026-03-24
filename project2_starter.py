# SI 201 HW4 (Library Checkout System)
# Your name: Kikii Park, Anna Browne
# Your student id: 36180469, 56505997
# Your email: parkpark@umich.edu, aobrowne@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    results = []

    # find all listing cards by their title div
    title_divs = soup.find_all("div", attrs={"data-testid": "listing-card-title"})

    for div in title_divs:
        title = div.get_text()

        # id looks like "title_1944564", so only get the numbers
        div_id = div.get("id", "")
        match = re.search(r"title_(\d+)", div_id)

        if match:
            listing_id = match.group(1)
            results.append((title, listing_id))

    return results





    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    html_path = os.path.join("html_files", f"listing_{listing_id}.html")
    
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    page_text = soup.get_text(" ", strip=True)

    # 1. policy_number (regex from <li>)

    policy_number = None
    for li in soup.find_all("li"):
        li_text = li.get_text(" ", strip=True)
        match = re.search(r"Policy number:\s*(.+)", li_text)
        if match:
            raw_policy = match.group(1).strip()
            if "pending" in raw_policy.lower():
                policy_number = "Pending"
            elif "exempt" in raw_policy.lower():
                policy_number = "Exempt"
            else:
                policy_number = raw_policy
            break


    # 2. host_type 
   
    host_type = "regular"  

    host_span = soup.find("span", class_="_1mhorg9", attrs={"aria-hidden": "false"})
    if host_span:
        if "Superhost" in host_span.get_text():
            host_type = "Superhost"


    # 3. host_name (from <h2>)


    host_name = None
    host_h2 = soup.find("h2", attrs={"elementtiming": "LCP-target"})
    if host_h2:
        # Normalize whitespace to remove \xa0 and extra spaces
        clean_text = " ".join(host_h2.get_text().split())
        match = re.search(r"hosted by\s+(.+)$", clean_text)
        if match:
            host_name = match.group(1).strip()



    # 4. room_type (from<h2>)

    room_type = "Entire Room"  
    host_h2 = soup.find("h2", attrs={"elementtiming": "LCP-target"})
    if host_h2:
        # Normalize whitespace to remove \xa0 and extra spaces
        clean_text = " ".join(host_h2.get_text().split())

        if "Private" in clean_text:
            room_type = "Private Room"
        elif "Shared" in clean_text:
            room_type = "Shared Room"
    

    
    # 5. location_rating
    location_rating = 0.0

    # 1) Find the div that acts as the label for "Location"
    location_label = soup.find("div", class_="_y1ba89", string="Location")

    if location_label:
        # 2) Find the rating div that follows the label
       
        rating_div = location_label.find_next("div", class_="_7pay")
        
        if rating_div and rating_div.has_attr("aria-label"):
            aria_label = rating_div["aria-label"] # "4.9 out of 5.0"
            
            # 3) Extract the number using regex
            match = re.search(r"(\d\.\d)", aria_label)
            if match:
                location_rating = float(match.group(1))




    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }



    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listing_results = load_listing_results(html_path)
    listing_details = get_listing_details(html_path)
    listing_database = []

    for listing in listing_details:
        listing_tuple = (listing['policy_number'], listing['host_type'], listing['host_name'], listing['room_type'], listing['location_rating'])
        for list in listing_results:
            if list[1] == listing:
                listing_tuple += list
                listing_database.append(listing_tuple)
    
    print(listing_database)
    return listing_database


    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").

        self.assertEqual(len(self.listings),18)
        self.assertEqual(self.listings[0],("Loft in Mission District", "1944564"))
        # print(self.listings)


    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        my_list = []
        for id in html_list:
            detail_dict = get_listing_details(id)
            my_list.append(detail_dict)
        print(detail_dict)



        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        
        self.assertEqual(my_list[0]["467507"]["policy_number"],"STR-0005349")

        self.assertEqual(my_list[2]["1944564"]["host_type"],"Superhost")
        self.assertEqual(my_list[2]["1944564"]["room_type"],"Entire Room")

        self.assertEqual(my_list[2]["1944564"]["location_rating"],4.9)
        
        

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        # for result in self.detailed_data:
        #     self.assertEqual(len(result), 7)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        # self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        pass
        # os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    # detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    # output_csv(detailed_data, "airbnb_dataset.csv")
    pass

if __name__ == "__main__":
    # main()
    unittest.main(verbosity=2)