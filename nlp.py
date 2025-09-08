import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import pprint

nltk.download('punkt',quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet',quiet=True)
nltk.download('omw-1.4',quiet=True)


Text = input("Input your text to see some magic:")

Tokens = word_tokenize(Text,)

ps = PorterStemmer()
Stem = [ps.stem(w) for w in Tokens]

Lem = WordNetLemmatizer()
Lemz = [Lem.lemmatize(w) for w in Tokens]


Blob = TextBlob(Text)
Sentiment = Blob.sentiment

Outcome = {
    'Tokens':Tokens,
    'Stems' : Stem,
    'Lemmas': Lemz,
    "Sentiment" : {
        'Polarity' : Sentiment.polarity,
        'Subjectivity' : Sentiment.subjectivity
    }
}
pprint.pprint(Outcome, width=100)

