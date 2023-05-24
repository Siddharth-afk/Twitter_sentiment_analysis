from flask import Flask, redirect, url_for, request, render_template, jsonify
import pandas as pd
from textblob import TextBlob
import numpy as np
import re
import matplotlib.pyplot as plt
import emoji
import snscrape.modules.twitter as sntwitter

app = Flask(__name__)
save_directory = "C:/Users/gupta/Documents/finalYearProject(final)/projectfinal/src/images/"
plt.switch_backend('agg')

@app.route("/twitter", methods=['POST', 'GET'])
def test():
    posts = []
    data = request.json['data']
    for i, tweets in enumerate(sntwitter.TwitterSearchScraper(f"{data}").get_items()):
        if i > 100:
            break
        posts.append(tweets.content)

    df = pd.DataFrame([i for i in posts], columns = ["tweets"])

    def clean(text):
        text = emoji.demojize(text, delimiters=("", ""))
        text = re.sub(r'@[_a-zA-Z0-9]+',  '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT[\s]+', '', text)
        text = re.sub(r'https?:\/\/\S+', '', text)
        text = re.sub(r'_', ' ', text)
        text = re.sub(r'&amp;', 'and', text)

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
    plt.title("Bargraph")
    plt.xlabel("sentiment")
    plt.ylabel("counts")
    df['analysis'].value_counts().plot(kind = 'bar')
    plt.savefig(save_directory + 'bargraph')
    df['bargraph'] = save_directory + 'bargraph'

    #scatterplot of sentiment vs polarity
    plt.figure(figsize = (8, 6))
    for i in range(0, df.shape[0]):
        plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color = "blue")


    plt.title("Scatterplot")
    plt.xlabel("Polarity")
    plt.ylabel("Subjectivity")   
    plt.savefig(save_directory + 'scatterplot')
    df['scatterplot'] = save_directory + 'bargraph'

    ptweets = df[df.analysis == "positive"]
    ptweets = ptweets['tweets']
    perpos = round(len(ptweets)/df.shape[0] * 100, 1)

    df['perpos'] = perpos

    ntweets = df[df.analysis == "negative"]
    ntweets = ntweets['tweets']
    perneg = round(len(ntweets)/len(df) * 100, 1)

    df['perneg'] = perneg

    nettweets = df[df.analysis == "neutral"]
    nettweets = nettweets['tweets']
    pernet = round(len(nettweets)/len(df) * 100, 1)

    df['pernet'] = pernet

    return(df.to_json())

if __name__ == "__main__":
    app.run(debug=True)