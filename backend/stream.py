from asyncio.windows_events import NULL
import streamlit as st
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import emoji
import snscrape.modules.twitter as sntwitter
#from datatime import date
plt.style.use('fivethirtyeight')

st.image('https://th.bing.com/th?id=OIP.P3GJZi8Z-DGPx1JS3u5yOgHaGl&w=265&h=235&c=8&rs=1&qlt=90&o=6&dpr=1.3&pid=3.1&rm=2', width=150)
st.title("Stock Market Sentiment Analysis on Twitter")

name = st.text_input("Enter Stock name!")
post = []
if(name != ""):
    #st.text(name + " since:2023-01-01 until:2023-04-10")
    for i, tweets in enumerate(sntwitter.TwitterSearchScraper(name).get_items()):
        if i > 1000:
            break

        post.append(tweets.content)


    df = pd.DataFrame([i for i in post], columns = ["tweets"])
    st.subheader("most recent tweet: ")
    st.text(str(df['tweets'][0]))

    def clean(text):
        text = re.sub(r'@[_a-zA-Z0-9]+',  '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT[\s]+', '', text)
        text = re.sub(r'https?:\/\/\S+', '', text)
        text = emoji.demojize(text, delimiters=("", ""))

        return text

    df['tweets'] = df['tweets'].apply(clean)


    #getting subjectivity
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    #getting polarity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity

    df['Subjectivity'] = df['tweets'].apply(getSubjectivity)
    df['Polarity'] = df['tweets'].apply(getPolarity)

    def getAnalysis(score):
        if score < 0:
            return "negative"
        elif score == 0:
            return "neutral"
        else:
            return "positive"

    df['analysis'] = df['Polarity'].apply(getAnalysis)

    #showing positive and negative tweets:
    sortedDF = df.sort_values(by = ['Polarity'], ascending=False, ignore_index=True)

    pos, neg = st.columns(2)

    with pos:
        st.subheader("Most Positive Tweets:")
        for i in range(0, 5):
            st.caption(str(sortedDF['tweets'][i]))


    posdf = pd.DataFrame(columns=['tweet', 'polarity'])
    for i in range(0, sortedDF.shape[0]):
        if sortedDF['analysis'][i] == "negative":
            posdf = posdf.append({'tweet':sortedDF['tweets'][i], 'polarity': sortedDF['Polarity'][i]}, ignore_index=True)

    with neg:
        st.subheader("Most Negative Tweets:")
        negtw = posdf.sort_values(by=['polarity'], ignore_index=True)
        for i in range(0, 5):
            st.caption(str(negtw['tweet'][i]))

    #bar chart

    st.subheader("Bar chart")
    st.caption("Representation of positive, negative and neutral tweets.")

    df['analysis'].value_counts()
    plt.title("sentiment analysis")

    plt.xlabel("sentiment")
    plt.ylabel("counts")

    df['analysis'].value_counts().plot(kind = 'bar')
    st.pyplot(plt)

    #scatter plot of sentiment vs polarity

    st.subheader('Subjectivity vs Polarity')
    st.caption("this gives us a representation of how subjective our tweet is and whether its consider positive or negative (polarity).")

    plt.figure(figsize = (8, 6))
    for i in range(0, df.shape[0]):
        plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color = "blue")

    plt.title("sentiment analysis")
    plt.xlabel("polarity")
    plt.ylabel("subjectivity")
    st.pyplot(plt)

    #percentage of positive and negative tweets:
    ptweets = df[df.analysis == "positive"]
    ptweets = ptweets['tweets']
    perpos = round(len(ptweets)/df.shape[0] * 100, 1)

    ntweets = df[df.analysis == "negative"]
    ntweets = ntweets['tweets']
    perneg = round(len(ntweets)/len(df) * 100, 1)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Percentage of positive tweets:\n" + str(perpos) + "%")

    with col2:
        st.subheader("Percentage of negative tweets:\n" + str(perneg) + "%")