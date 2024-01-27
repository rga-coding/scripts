

"""
# Filename: run_selenium.py
"""

# Run selenium and chrome driver to scrape data from cloudbytes.dev
import json
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def prayer_times():
    # hicri = [
    #     (1, "Muharrem"),
    #     (2, "Safer"),
    #     (3, "Rebî'ül-evvel"),
    #     (4, "Rebî'ül-âhir"),
    #     (5, "Cemâziyel evvel"),
    #     (6, "Cemâziyel âhir"),
    #     (7, "Receb"),
    #     (8, "Şâban"),
    #     (9, "Ramazan"),
    #     (11, "Şevval"),
    #     (12, "Zilka'de"),
    #     (13, "Zilhicce"),
    # ]

    miladi = {
        "Ocak": ("1", "Ocak", "January"),
        "Şubat": ("2", "Şubat", "February"),
        "Mart": ("3", "Mart", "March"),
        "Nisan": ("4", "Nisan", "April"),
        "Mayıs": ("5", "Mayıs", "May"),
        "Haziran": ("6", "Haziran", "June"),
        "Temmuz": ("7", "Temmuz", "July"),
        "Ağustos": ("8", "Ağustos", "August"),
        "Eylül": ("9", "Eylül", "September"),
        "Ekim": ("10", "Ekim", "October"),
        "Kasım": ("11", "Kasım", "November"),
        "Aralık": ("12", "Aralık", "December"),
    }
    # Setup chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")

    # # Set path to chrome/chromedriver as per your configuration
    # homedir = os.path.expanduser("~")
    # chrome_options.binary_location = f"{homedir}/chrome_browser/chrome-linux64/chrome"
    # webdriver_service = Service(f"{homedir}/chrome_browser/chromedriver-linux64/chromedriver")

    # Choose Chrome Browser
    # browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    browser = webdriver.Chrome(options=chrome_options)

    # Get page
    browser.get("https://namazvakitleri.com.tr/sehir/1616/houthalen-namaz-vakitleri")

    # Accept cookies
    cookies = None
    while not cookies:
        try:
            cookies = browser.find_element(By.CLASS_NAME, "fc-button-label")
        except NoSuchElementException:
            pass
        else:
            cookies.click()
    date_and_monthly_click = browser.find_element(By.CLASS_NAME, "css-1hr40ic")
    month_hicri, month_miladi = [
        d.split(' ')[1].capitalize()
        for d in date_and_monthly_click.find_element(By.CLASS_NAME, "chakra-stack").text.split('\n/\n')
    ]

    # Monthly
    date_and_monthly_click.find_element(By.CLASS_NAME, "chakra-icon").click()

    # daily_prayings_header = browser.find_element(By.CLASS_NAME, "css-1l6fx3q").text.split(' ')
    daily_prayings_header = ["imsak", "gunes", "oglen", "ikindi", "aksam", "yatsi"]

    month_prayer_times_table = browser.find_element(By.CLASS_NAME, "chakra-table").find_element(By.XPATH, 'tbody')
    month_prayer_times_table_elems = month_prayer_times_table.find_elements(By.XPATH, 'tr')
    month, year = month_prayer_times_table_elems[0].text.split(' ')

    prayer_times = {year: {miladi[month_miladi][0].zfill(2): {}}}
    for table_elem in month_prayer_times_table_elems[1:]:
        if table_elem.text == '':
            continue
        elif len(table_elem.text.split(' ')) == 2:
            # End of the month
            break
        month_day, weekday, times_str = table_elem.text.split('\n')
        times_lst = times_str.split(' ')
        times_str = times_str.replace(' ', ', ')
        prayer_times[year][miladi[month_miladi][0].zfill(2)].update({
            month_day.zfill(2): {
                "miladi": month_miladi,
                "hicri": month_hicri,
                "day": month_day.zfill(2),
                "weekday": weekday,
                "prayer_times": {
                    "times_str": times_str,
                    **dict(zip(daily_prayings_header, times_lst)),
                }
            }
        })
    browser.quit()

    save_to_json(prayer_times)


def save_to_json(prayer_times):

    with open('/mnt/c/Users/rga/Dropbox/prayer_times.json', 'r') as f:
        data = json.load(f)

    for year in prayer_times.keys():
        if not data.get(year):
            data.update(prayer_times)
            break
        for monthly in prayer_times[year].keys():
            if not data[year].get(monthly):
                data[year].update(prayer_times[year])
                break

    with open('/mnt/c/Users/rga/Dropbox/prayer_times.json', 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    prayer_times()
