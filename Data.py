import pandas as Pd 
from textblob import TextBlob

CsvReading = Pd.read_csv("Reviews.csv")

print("Preview of the data:\n",CsvReading.head())

def Sentiment_Analyzer(text):
    Text = TextBlob(text)
    return Text.sentiment.polarity, Text.sentiment.subjectivity

CsvReading['polarity'],CsvReading['subjectivity'] = zip(*CsvReading["review_text"].map(Sentiment_Analyzer))

print("\n Reviews with sentiment analysis")

print(CsvReading)
CsvReading.to_csv("analyzed_reviews.csv",index=False)
print("\n Results saved to analyzed_reviews.csv")