from flask import Flask, render_template, request, url_for, redirect
import boto3
import json
from collections import namedtuple
from boto3.dynamodb.conditions import Key, Attr
from ScrapeNews import ScrapeNews

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
table = dynamodb.Table('news')
app = Flask(__name__)


@app.before_first_request
def UpdateNews():
    # def run_job():#
    print("Doing update")
    ScrapeNews("http://feeds.bbci.co.uk/news/business/rss.xml?edition=uk")


    # thread = threading.Thread(target=run_job)
    # thread.start()


@app.route("/")
def main():
    latest_news_list = []
    allItems = table.scan(FilterExpression=Attr("viewed").eq(False))

    for item in allItems['Items']:
        latest_news_list.append(item)
    context = {'latest_news_list' : latest_news_list}
    return render_template('index.html', latest_news_list = latest_news_list)

@app.route("/test")
def LoadExperiencePage():
    return render_template('test.html')


@app.route('/MarkAsRead', methods=['GET', 'POST'])
def MarkAsRead():
    if request.method == "POST":
        try:
            iden = int(request.json['id'])
            response = table.update_item(
                Key={
                    'id': iden
                    },
                UpdateExpression="set viewed = :r",
                ExpressionAttributeValues={
                    ':r': True
                },
                ReturnValues="UPDATED_NEW"
            )
            return "successful"
        except Exception as e:
            return "error: "+str(e)


if __name__ == '__main__':
    app.run(debug=True)
