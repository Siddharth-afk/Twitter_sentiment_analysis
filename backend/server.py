from flask import Flask, redirect, url_for, request, render_template, jsonify
import pandas as pd
from textblob import TextBlob
import numpy as np
import re
import matplotlib.pyplot as plt
import emoji
import snscrape.modules.twitter as sntwitter

app = Flask(__name__)
 
""" #members api routes

@app.route("/members")
def members():
    return{"members": []} """

@app.route("/twitter", methods=['POST', 'GET'])
def test():
    posts = []
    data = request.json['data']
    for i, tweets in enumerate(sntwitter.TwitterSearchScraper(f"{data}").get_items()):
        if i > 10:
            break
        posts.append(tweets.content)

    df = pd.DataFrame([i for i in posts], columns = ["tweets"])

    def clean(text):
        text = emoji.demojize(text, delimiters=("", ""))
        text = re.sub(r'@[_a-zA-Z0-9]+',  '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT[\s]+', '', text)
        text = re.sub(r'https?:\/\/\S+', '', text)

        return text
    
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity

    def getAnalysis(score):
        if score < 0:
            return "negative"
        elif score == 0:
            return "neutral"
        else:
            return "positive"
        
    
    
    df["tweets"] = df["tweets"].apply(clean)
    df['Subjectivity'] = df['tweets'].apply(getSubjectivity)
    df['Polarity'] = df['tweets'].apply(getPolarity)
    df['analysis'] = df['Polarity'].apply(getAnalysis)
    sortedDF = df.sort_values(by = ['Polarity'], ascending=False, ignore_index=True)
    
    #bar graph plot
    df['analysis'].value_counts()
    plt.title("sentiment analysis")
    plt.xlabel("sentiment")
    plt.ylabel("counts")
    df['analysis'].value_counts().plot(kind = 'bar')
    plt.savefig('bargraph', bbox_inches='tight', pad_inches=0.3, transparent=False)

    #scatterplot of sentiment vs polarity
    plt.figure(figsize = (8, 6))
    for i in range(0, df.shape[0]):
        plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color = "blue")

    plt.title("scatterplot")
    plt.xlabel("polarity")
    plt.ylabel("subjectivity")   
    plt.savefig('scatterplot')

    return(df.to_json())


if __name__ == "__main__":
    app.run(debug=True)