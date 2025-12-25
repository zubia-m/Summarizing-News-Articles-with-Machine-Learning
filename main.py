from flask import Flask, render_template, request, redirect, url_for
from textblob import TextBlob
from newspaper import Article
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        data = {}

        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            # -------- Author fallback --------
            author = ", ".join(article.authors) if article.authors else None
            if not author:
                soup = BeautifulSoup(article.html, "html.parser")
                meta_author = soup.find("meta", {"name": "author"})
                if meta_author and meta_author.get("content"):
                    author = meta_author.get("content")
            author = author or "Not provided by source"

            publish_date = article.publish_date or "Not provided by source"

            analysis = TextBlob(article.text)
            polarity = analysis.polarity
            subjectivity = analysis.subjectivity

            sentiment = (
                "Positive" if polarity > 0 else
                "Negative" if polarity < 0 else
                "Neutral"
            )

            data = {
                "title": article.title or "N/A",
                "authors": author,
                "date": publish_date,
                "summary": article.summary or "Summary not available.",
                "polarity": round(polarity, 2),
                "subjectivity": round(subjectivity, 2),
                "sentiment": sentiment
            }

            # Store result temporarily in session-like redirect
            return render_template("index.html", data=data)

        except Exception as e:
            return render_template("index.html", data={"error": str(e)})

    # -------- GET request (page load / reload) --------
    return render_template("index.html", data={})

if __name__ == "__main__":
    app.run(debug=True)
