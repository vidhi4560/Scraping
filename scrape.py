from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
from lxml import html
import csv


data_file = "countries.csv"


def get_country_data():
    site_base_url = "https://www.numbeo.com/"
    site_url = site_base_url + "quality-of-life/"

    site_response = requests.get(site_url)

    soup = BeautifulSoup(site_response.text, 'html.parser')
    table = soup.find("table", class_="related_links")
    tr_elements = table.contents
    tr_elements = tr_elements[0]
    countries = []
    for tr_element in tr_elements.findChildren("td"):
        for a in tr_element.findChildren("a"):
            a_val = {}
            a_val["href"] = a["href"]
            a_val["country"] = a.string
            countries.append(a_val)

    with open(data_file, "w+") as csvfile:
        fieldnames = ["country", "parameter", "value", "rating"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for country in countries:
            print("Getting data for {}".format(country["country"]))
            # make a request to the country's page and get data
            country_url = site_url + country["href"]
            r = requests.get(country_url)

            content = html.fromstring(r.content)
            table = content.xpath("/html/body/div[1]/table")[0]

            # iterate over the table, get all text_data for every <td>
            for row in table.getchildren():
                row_val = []
                for td in row.getchildren():
                    # replace \n and special characters
                    td_text = td.text_content().replace("\n", "").replace("\xa0", "").replace("\u0192", "").replace("?", "").replace(":", "").strip()
                    row_val.append(td_text)
                if len(row_val) == 3:
                    writer.writerow({"country": country["country"], "parameter": row_val[0], "value": row_val[1], "rating": row_val[2]})


def process():
    user_menu_for_parameters = {
        "1": "Purchasing Power Index",
        "2": "Safety Index",
        "3": "Health Care Index",
        "4": "Climate Index",
        "5": "Cost of Living Index",
        "6": "Property Price to Income Ratio",
        "7": "Traffic Commute Time Index",
        "8": "Pollution Index",
        "9": "Quality of Life Index"
    }

    parameter_index = raw_input('''
    Parameters :
           1. Purchasing Power Index
           2. Safety Index
           3. Health Care Index
           4. Climate Index
           5. Cost of Living Index
           6. Property Price to Income Ratio
           7. Traffic Commute Time Index
           8. Pollution Index
           9. Quality of Life Index
    Select an option (enter the number to select a option): ''')

    user_menu_for_rating = {
        "1": "Very Low",
        "2": "Low",
        "3": "Moderate",
        "4": "High",
        "5": "Very High",
    }

    rating_index = raw_input('''
    Rating :
            1. Very Low
            2. Low
            3. Moderate
            4. High
            5. Very High
    Select an option (enter the number to select a option): ''')

    result_list = []

    with open(data_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['parameter'] == user_menu_for_parameters.get(parameter_index) and row['rating'] == user_menu_for_rating.get(rating_index):
                result_list.append((row["country"], row["value"]))

    result = sorted(result_list, key=lambda x: float(x[1]), reverse=True)
    print("Following countries (with values) match your criteria:\n")
    for item in result[:5]:
        print("{} ({})\n".format(item[0], item[1]))


if __name__ == "__main__":
    process()
