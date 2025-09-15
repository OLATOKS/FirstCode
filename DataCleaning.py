import re
import pandas as pd 
import numpy as np
from textblob import TextBlob

FileCleaning = pd.read_csv("Reviews.csv", dtype=str)

for c in ("review_id", "review_text", "rating"):
    if c not in FileCleaning.columns:
        FileCleaning[c] = np.nan

str_cols = FileCleaning.select_dtypes(include=["object"]).columns
FileCleaning[str_cols]=FileCleaning[str_cols].apply(lambda col: col.str.strip())

FileCleaning["review_text"] = FileCleaning["review_text"].replace({"":np.nan})

FileCleaning["review_text"] = (FileCleaning["review_text"]
                               .astype(str).
                               replace("nan",np.nan).
                               where(FileCleaning["review_text"].notna(),None))

FileCleaning.loc[FileCleaning["review_text"].notna(),"review_text"] = (
    FileCleaning.loc[FileCleaning["review_text"].notna(),"review_text"]
    .str.replace(r"[^\x00-\x7F]+","", regex=True)
    .str.replace(r"\s+"," ",regex=True)
    .str.strip()
)

FileCleaning = FileCleaning.dropna(subset=["review_text"]).reset_index(drop=True)

TextNumMap ={
     "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

def parse_rating(val):
    
    if pd.isna(val):
        return np.nan
    s = str(val).strip().lower()
    
    s = re.sub(r"[^\w\.\-]", "", s)  
    if s == "":
        return np.nan
    
    if s in TextNumMap:
        return float(TextNumMap[s])
    
    try:
        return float(s)
    except Exception:
        return np.nan

FileCleaning["rating"] = FileCleaning["rating"].apply(parse_rating)

if FileCleaning["rating"].isnull().all():
    FileCleaning["rating"] = FileCleaning['rating'].fillna(0.0)
else:
    MeanRating = FileCleaning["rating"].mean()
    FileCleaning["rating"] = FileCleaning["rating"].fillna(round(MeanRating,2))

FileCleaning["rating"] =FileCleaning["rating"].round().astype(int)

def AnalyzeSentiment(text):
    blob = TextBlob(str(text))
    return blob.sentiment.polarity, blob.sentiment.subjectivity

FileCleaning["polarity"], FileCleaning["subjectivity"] = zip(*FileCleaning["review_text"].map(AnalyzeSentiment))

def SentiemntCategory(p):
    if p > 0.2:
        return "positive"
    elif p < -0.2:
        return "negative"
    else:
        return "Neutral"

FileCleaning["Sentiment"] =  FileCleaning["polarity"].apply(SentiemntCategory)

summary = (
    FileCleaning.groupby("Sentiment")
    .agg(
        ReviewsCount= ("review_id", "count"),
        AvgRating = ("rating", "mean"),
        AvgPolarity = ("polarity", "mean"),
    )
    .reset_index()
)

FileCleaning.to_csv("Cleaned_Analyzed_Reviews.csv",index=False)
summary.to_csv("Summary_By_sentiment.csv",index=False)

print("Saved: CleaningRevies.csv and the summary.csv \n the preview is below")
print(FileCleaning.head())
print("\nsummary is:")
print(summary)