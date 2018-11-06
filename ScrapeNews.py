import urllib.request as URL
import xml.etree.ElementTree as ET
import boto3
import re
from boto3.dynamodb.conditions import Key, Attr
from bs4 import BeautifulSoup


def ScrapeNews(address):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
    table = dynamodb.Table('news')
    page = URL.urlopen(address)
    parsed = ET.parse(page)
    root = parsed.getroot()[0]

    for child in root.findall('item'):
        wp = URL.urlopen(child.find('link').text)
        soup = BeautifulSoup(wp, "lxml")
        iden = int(re.match('.*?([0-9]+)$', child.find('guid').text).group(1))
        response = table.query(
            KeyConditionExpression=Key('id').eq(iden)
        )
        items = response['Items']
        #print(items)

        # If it exists already, continue
        if (items != []):
            print("Already stored")
            userInput = input("Cancel?")
            if userInput == "y":
                return
            continue


        t1 = soup.find(class_='story-body__inner')
        if t1 == None:
            print("none", child.find('link').text)
            continue
        else:
            articleText = ""
            paragraphs = t1.findAll('p')
            for para in (paragraphs):
                articleText += str(para.renderContents())[2:-1]
                articleText += "\n"
            if articleText:
                # Write to db

                print(iden)
                table.put_item(
                    Item={
                    'id': iden,
                    'viewed': False,
                    'title':child.find('title').text,
                    'link': child.find('link').text,
                    'description': child.find('description').text,
                    'date': child.find('pubDate').text,
                    'articleText' : articleText#re.sub('<[^<]+?>', '', articleText)
                    }
                )
                print("Added: ", child.find('guid').text)
            else:
                print("articleText is empty")
