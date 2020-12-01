#importing several libraries
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import math
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import re
import requests
import csv
import random
import json


#define a function for marley spoon google web scraping
def marley_spoon_google_scrape():
    #Open a new web browser
    driver = webdriver.Chrome()

    #Open the web page that we want open and log in.
    url = 'https://www.google.com/maps/place/Martha+%26+Marley+Spoon/@40.7533395,-73.9950754,17z/data=!4m7!3m6!1s0x89c259ad70388de5:0xcb304a760cebd2e2!8m2!3d40.7533395!4d-73.9928867!9m1!1b1'
    driver.get(url)

    num_reviews = 900
    num_iter_rounded = math.ceil((num_reviews-8) / 10)

    #define an inner function to derive the actual date from the relative date
    def rel_date_converter(i):
        if re.search("day", i):
            if i[0] == 'a':
                d = date.today() - relativedelta(days=1)
            else:
                d = date.today() - relativedelta(days=1*int(i[:1]))

            review_date_list.append(d)

        if re.search("month", i):
            if i[0] == 'a':
                d = date.today() - relativedelta(months=1)
            else:
                d = date.today() - relativedelta(months=1*int(i[:1]))

            review_date_list.append(d)

        if re.search("week", i):
            if i[0] == 'a':
                d = date.today() - relativedelta(weeks=1)
            else:
                d = date.today() - relativedelta(weeks=1*int(i[0:1]))

            review_date_list.append(d)

        if re.search("year", i):
            if i[0] == 'a':
                d = date.today() - relativedelta(weeks=52)
            else:
                d = datetime.today() - timedelta(weeks=52*int(i[0:1]))

            review_date_list.append(d)

        if re.search("hour", i):
            if i[0] == 'a':
                d = date.today() - relativedelta(hours=1)
            else:
                d = date.today() - relativedelta(hours=int(i[:1]))

            review_date_list.append(d)

    #Scroll down on the Google Maps review page 
    for i in range(num_iter_rounded):
        scrollable_div = driver.find_element_by_css_selector(
        'div.section-layout.section-scrollbox.scrollable-y.scrollable-show'
                         )
        driver.execute_script(
                   'arguments[0].scrollTop = arguments[0].scrollHeight', 
                    scrollable_div
                   )
        time.sleep(2)

    #Load the review data in a beautiful soup object
    response = bs(driver.page_source, 'html.parser')
    rlist = response.find_all('div', class_='section-review-content')

    #load the reviews in lists
    id_list = []
    user_list = []
    review_list = []
    rating_list = []
    rel_date_list = []
    review_date_list = []
    date_scraped_list = []

    for r in rlist:
        id_r = r.find('button', 
                  class_='section-review-action-menu')['data-review-id']
        id_list.append(id_r)

        username = r.find('div', 
                          class_='section-review-title').find('span').text
        user_list.append(username)

        try:
            review_text = r.find('span', class_='section-review-text').text
            review_list.append(review_text)
        except Exception:
            review_text = None

        rating = r.find('span', class_='section-review-stars')['aria-label']
        rating_list.append(rating)

        rel_date = r.find('span', class_='section-review-publish-date').text
        rel_date_list.append(rel_date)

        rel_date_converter(rel_date)

        date_scraped_list.append(date.today())

    #Create a pandas data frame from the review data and export it to CSV
    review_data = pd.DataFrame()

    review_data["User_Name"] = user_list
    review_data["Id"] = id_list
    review_data["Review"] = review_list
    review_data["rating_list"] = rating_list
    review_data["Review_Date"] = review_date_list
    review_data['Relative_Date'] = rel_date_list
    review_data["Date_Scraped"] = date_scraped_list

    review_data.to_csv('marleyspoon_reviews.csv')


#define a function for blue apron consumer affairs web scraping
def blue_apron_consumeraffairs_scrape():

    #user defined function to scrape the fields of the review we are interested in
    #and store them in a dictionary
    def scrape_one_page(reviews,csvwriter):
        for review in reviews:
            dictionary_reviews = {}
            username = review.find('strong', attrs={'class':'rvw-aut__inf-nm'}).string
            rating = review.find_all('meta')[1].get('content')
            date = review.find('span', attrs={'class': 'ca-txt-cpt'}).get_text()
            content = review.find('div',attrs={'class' : 'rvw-bd'}).get_text()
            dictionary_reviews['Username'] = username
            dictionary_reviews['Rating'] = rating
            dictionary_reviews['Date'] = date
            dictionary_reviews['Review'] = content
            review_writer.writerow(dictionary_reviews.values())

    #Here I created a list with all the URL to scrape
    url_list = ['https://www.consumeraffairs.com/food/blue-apron.html']
    for i in range(2,4,1):
         url_list.append('https://www.consumeraffairs.com/food/blue-apron.html?page='+str(i))

    #Created a csv file to save the reviews scraped
    with open('blueapron.csv','w',encoding = 'utf-8',newline='') as csvfile:
         review_writer = csv.writer(csvfile)
         review_writer.writerow(['reviewUsername', 'reviewRating', 'reviewDate','reviewText'])
         for index, url in enumerate(url_list):
             #here I requested to open the different URLs \
             #and created an objet with all the information from each page.
             response = requests.get(url).text
             soup = bs(response, 'html.parser')
             #this is to find all the div reviews in the website
             reviews = soup.find_all('div', attrs={'class':'rvw js-rvw'})
             #called the function that scrapes the username, rating and review 
             scrape_one_page(reviews,review_writer)
             #randomsleep to avoid getting banned from the server
             time.sleep(random.randint(1,3))
             print('Finished page' + str(index + 1))

         csvfile.close()

#define a function for hello fresh consumer affairs web scraping
def hello_fresh_consumeraffairs_scrape():

    #user defined function to scrape the fields of the review we are interested in
    #and store them in a dictionary
    def scrape_one_page(reviews,csvwriter):
        for review in reviews:
            dictionary_reviews = {}
            username = review.find('strong', attrs={'class':'rvw-aut__inf-nm'}).string
            rating = review.find_all('meta')[1].get('content')
            date = review.find('span', attrs={'class': 'ca-txt-cpt'}).get_text()
            content = review.find('div',attrs={'class' : 'rvw-bd'}).get_text()
            dictionary_reviews['Username'] = username
            dictionary_reviews['Rating'] = rating
            dictionary_reviews['Date'] = date
            dictionary_reviews['Review'] = content
            review_writer.writerow(dictionary_reviews.values())

    #Here I created a list with all the URL to scrape
    url_list = ['https://www.consumeraffairs.com/food/hellofresh.html']
    for i in range(2,39,1):
         url_list.append('https://www.consumeraffairs.com/food/hellofresh.html?page='+str(i))

    #Created a csv file to save the reviews scraped
    with open('hellofresh.csv','w',encoding = 'utf-8',newline='') as csvfile:
         review_writer = csv.writer(csvfile)
         review_writer.writerow(['reviewUsername', 'reviewRating', 'reviewDate','reviewText'])
         for index, url in enumerate(url_list):
             #here I requested to open the different URLs and created an objet with all the information from each page.
             response = requests.get(url).text
             soup = bs(response, 'html.parser')
             #this is to find all the div reviews in the website
             reviews = soup.find_all('div', attrs={'class':'rvw js-rvw'})
             #called the function that scrapes the username, rating and review 
             scrape_one_page(reviews,review_writer)
             #randomsleep to avoid getting banned from the server
             time.sleep(random.randint(1,3))
             print('Finished page' + str(index + 1))

         csvfile.close()



#define a function for blue apron trust pilot web scraping
def blue_apron_trustpilot_scrape():
    #input the url link for Blue Apron reviews on Trust Pilot
    url = 'https://www.trustpilot.com/review/blueapron.com'
    new_name = [] 
    new_date = [] 
    rating = []
    new_heading = []
    new_review =[]
    user_review_heading = [] 
    user_review = []
    time_post =[] 
    user_name = []

    #Create a loop to find reviews from all pages. 
    for i in range(1,70):
        i = url + '?page=' + str(i)
        r = requests.get(i)
        soup = bs(r.content, 'lxml')    

    #Code to find star ratings 
    for i in soup.find_all('div',{'class':'review-card'}): 
        star_rating=i.find('div',{'class':'star-rating star-rating--medium'})
        per_rating = star_rating.find('img').get('alt')
        rating.append(per_rating)

    #Code to find user name    
    for i in soup.find_all('div',{'class':'review-card'}): 
        name=i.find('div',{'class':'consumer-information__details'})
        per_name = name.find('div')
        user_name.append(per_name)

    #Code to clean user_name column:
    for each in user_name:
        new_each = str(each).replace('<div class="consumer-information__name" v-pre="">', '')
        new_each = new_each.replace("</div>","")
        new_name.append(new_each.strip())

    #Code to find headings of each user review
    for i in soup.find_all('div',{'class':'review-content__body'}): 
        review_heading = i.find('h2',{'class':'review-content__title'})
        per_heading = review_heading.find("a")
        user_review_heading.append(per_heading)

    #Code to clean user_review heading:
    for each in user_review_heading:
        new_each = str(each).replace('<a class="link link--large link--dark"', '').replace("target': 'Single review', 'name': 'review-title'", "")
        new_each = new_each.replace("</a>","").replace('data-track-link=', '')
        new_each1 = new_each.replace("{'}", "").replace('href="/reviews/',"").replace('""', "").replace('"', "")
        new_heading.append(new_each1)

    #Code to find review:
    for i in soup.find_all('div',{'class':'review-card'}): 
        review = i.find('div',{'class':'review-content__body'})
        per_review = review.find('p')
        user_review.append(per_review)

    #Code to clean review column:
    for each in user_review:
        new_each = str(each).replace('<p class="review-content__text">', '')
        new_each = new_each.replace("</p>","")
        new_review.append(new_each.strip())

    #Code to fnd date and time of the post:
    for i in soup.find_all('div',{'class':'review-content-header'}): 
        time = i.find('div',{'class':'review-content-header__dates'})
        per_time = time.find('script')
        time_post.append(per_time)

    #Code to clean the time column:
    for each in time_post:
        new_each = str(each).replace('<script data-initial-state="review-dates"', '')
        new_each = new_each.replace('type="application/json"', '').replace('"updatedDate":null,"reportedDate":null}','').replace('</script>',"").replace('<review-dates :published-date="publishedDate" :reported-date="reportedDate" :updated-date="updatedDate"></review-dates>', "")
        new_each1 = new_each.replace('{"publishedDate":"', "").replace(">","").replace('",','')
        new_date.append(new_each1)    

    #Code to convert the output to csv file.
    import csv

    fields =['Number', 'Name', 'Date Posted', 'Time Posted', 'Rating Star', 'Rating Type', 'Review ID', "Review Heading", 'Review'] 

    rows = [[str(i+1), 
            new_name[i], 
            str(new_date[i].split('T')[0].strip()), str(new_date[i].split('T')[1].strip()), 
            str(rating[i].split(':')[0].strip()), str(rating[i].split(':')[1].strip()), 
            str(new_heading[i].split('>')[0].strip()), str(new_heading[i].split('>')[1].strip()), 
            new_review[i]] for i in range(len(rating))]

    with open ('Blue Apron.csv', 'w', newline ='', encoding ='utf-8') as file:
        write = csv.writer(file) 
        write.writerow(fields) 
        write.writerows(rows) 


#define a function for hello fresh trust pilot web scraping
def hello_fresh_trustpilot_scrape():
    #input the url link for Hello Fresh reviews on Trust Pilot
    url = 'https://www.trustpilot.com/review/hellofresh.com'
    new_name = [] 
    new_date = [] 
    rating = []
    new_heading = []
    new_review =[]
    user_review_heading = [] 
    user_review = []
    time_post =[] 
    user_name = []

    #Create a loop to find reviews from all pages. 
    for i in range(1,900):
        i = url + '?page=' + str(i)
        r = requests.get(i)
        soup = bs(r.content, 'lxml')    

    #Code to find star ratings 
    for i in soup.find_all('div',{'class':'review-card'}): 
        star_rating=i.find('div',{'class':'star-rating star-rating--medium'})
        per_rating = star_rating.find('img').get('alt')
        rating.append(per_rating)

    #Code to find user name   
    for i in soup.find_all('div',{'class':'review-card'}): 
        name=i.find('div',{'class':'consumer-information__details'})
        per_name = name.find('div')
        user_name.append(per_name)

    #Code to clean user_name column:
    for each in user_name:
        new_each = str(each).replace('<div class="consumer-information__name" v-pre="">', '')
        new_each = new_each.replace("</div>","")
        new_name.append(new_each.strip())

    #Code to find headings of each user review 
    for i in soup.find_all('div',{'class':'review-content__body'}): 
        review_heading = i.find('h2',{'class':'review-content__title'})
        per_heading = review_heading.find("a")
        user_review_heading.append(per_heading)

    #Code to clean user_review heading:
    for each in user_review_heading:
        new_each = str(each).replace('<a class="link link--large link--dark"', '').replace("target': 'Single review', 'name': 'review-title'", "")
        new_each = new_each.replace("</a>","").replace('data-track-link=', '')
        new_each1 = new_each.replace("{'}", "").replace('href="/reviews/',"").replace('""', "").replace('"', "")
        new_heading.append(new_each1)

    #Code to find review:
    for i in soup.find_all('div',{'class':'review-card'}): 
        review = i.find('div',{'class':'review-content__body'})
        per_review = review.find('p')
        user_review.append(per_review)

    #Code to clean review column:
    for each in user_review:
        new_each = str(each).replace('<p class="review-content__text">', '')
        new_each = new_each.replace("</p>","")
        new_review.append(new_each.strip())

    #Code to fnd date and time of the post:
    for i in soup.find_all('div',{'class':'review-content-header'}): 
        time = i.find('div',{'class':'review-content-header__dates'})
        per_time = time.find('script')
        time_post.append(per_time)

    #Code to clean the time column:
    for each in time_post:
        new_each = str(each).replace('<script data-initial-state="review-dates"', '')
        new_each = new_each.replace('type="application/json"', '').replace('"updatedDate":null,"reportedDate":null}','').replace('</script>',"").replace('<review-dates :published-date="publishedDate" :reported-date="reportedDate" :updated-date="updatedDate"></review-dates>', "")
        new_each1 = new_each.replace('{"publishedDate":"', "").replace(">","").replace('",','')
        new_date.append(new_each1)    

    #Code to convert the output to csv file.
    import csv

    fields =['Number', 'Name', 'Date Posted', 'Time Posted', 'Rating Star', 'Rating Type', 'Review ID', "Review Heading", 'Review'] 

    rows = [[str(i+1), 
            new_name[i], 
            str(new_date[i].split('T')[0].strip()), str(new_date[i].split('T')[1].strip()), 
            str(rating[i].split(':')[0].strip()), str(rating[i].split(':')[1].strip()), 
            str(new_heading[i].split('>')[0].strip()), str(new_heading[i].split('>')[1].strip()), 
            new_review[i]] for i in range(len(rating))]

    with open ('Hello Fresh.csv', 'w', newline ='', encoding ='utf-8') as file:
        write = csv.writer(file) 
        write.writerow(fields) 
        write.writerows(rows)




#define a function for marley spoon trust pilot web scraping
def marley_spoon_trustpilot_scrape():
    #input the url link for Marley Spoon reviews on Trust Pilot
    url = 'https://www.trustpilot.com/review/marleyspoon.com'
    new_name = [] 
    new_date = [] 
    rating = []
    user_review_heading = []
    time_post = []
    new_heading = []
    new_review =[]
    new_date = []
    user_name = []

    #Create a loop to find reviews from all pages. 
    for i in range(1,70):
        i = url + '?page=' + str(i)
        r = requests.get(i)
        soup = bs(r.content, 'lxml')    

    #Code to find star ratings 
    for i in soup.find_all('div',{'class':'review-card'}): 
        star_rating=i.find('div',{'class':'star-rating star-rating--medium'})
        per_rating = star_rating.find('img').get('alt')
        rating.append(per_rating)

    #Code to find user name    
    for i in soup.find_all('div',{'class':'review-card'}): 
        name=i.find('div',{'class':'consumer-information__details'})
        per_name = name.find('div')
        user_name.append(per_name)

    #Code to clean user_name column:
    for each in user_name:
        new_each = str(each).replace('<div class="consumer-information__name" v-pre="">', '')
        new_each = new_each.replace("</div>","")
        new_name.append(new_each.strip())

    #Code to find headings of each user review
    for i in soup.find_all('div',{'class':'review-content__body'}): 
        review_heading = i.find('h2',{'class':'review-content__title'})
        per_heading = review_heading.find("a")
        user_review_heading.append(per_heading)

    #Code to clean user_review heading:
    for each in user_review_heading:
        new_each = str(each).replace('<a class="link link--large link--dark"', '').replace("target': 'Single review', 'name': 'review-title'", "")
        new_each = new_each.replace("</a>","").replace('data-track-link=', '')
        new_each1 = new_each.replace("{'}", "").replace('href="/reviews/',"").replace('""', "").replace('"', "")
        new_heading.append(new_each1)

    #Code to find review:
    user_review = [] 
    for i in soup.find_all('div',{'class':'review-card'}): 
        review = i.find('div',{'class':'review-content__body'})
        per_review = review.find('p')
        user_review.append(per_review)

    #Code to clean review column:
    for each in user_review:
        new_each = str(each).replace('<p class="review-content__text">', '')
        new_each = new_each.replace("</p>","")
        new_review.append(new_each.strip())

    #Code to fnd date and time of the post:
    for i in soup.find_all('div',{'class':'review-content-header'}): 
        time = i.find('div',{'class':'review-content-header__dates'})
        per_time = time.find('script')
        time_post.append(per_time)

    #Code to clean the time column:
        for each in time_post:
            new_each = str(each).replace('<script data-initial-state="review-dates"', '')
            new_each = new_each.replace('type="application/json"', '').replace('"updatedDate":null,"reportedDate":null}','').replace('</script>',"").replace('<review-dates :published-date="publishedDate" :reported-date="reportedDate" :updated-date="updatedDate"></review-dates>', "")
            new_each1 = new_each.replace('{"publishedDate":"', "").replace(">","").replace('",','')
            new_date.append(new_each1)    

    #Code to convert the output to csv file.
    import csv

    fields =['Number', 'Name', 'Date Posted', 'Time Posted', 'Rating Star', 'Rating Type', 'Review ID', "Review Heading", 'Review'] 

    rows = [[str(i+1), 
            new_name[i], 
            str(new_date[i].split('T')[0].strip()), str(new_date[i].split('T')[1].strip()), 
            str(rating[i].split(':')[0].strip()), str(rating[i].split(':')[1].strip()), 
            str(new_heading[i].split('>')[0].strip()), str(new_heading[i].split('>')[1].strip()), 
            new_review[i]] for i in range(len(rating))]

    with open ('Marley Spoon.csv', 'w', newline ='', encoding ='utf-8') as file:
        write = csv.writer(file) 
        write.writerow(fields) 
        write.writerows(rows) 

