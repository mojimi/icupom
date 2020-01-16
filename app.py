from flask import Flask, request, render_template, session
from uuid import uuid4
from ifoodcrawler import IfoodCrawler
import os

app = Flask(__name__)
app.secret_key = uuid4().hex

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            raise ValueError('argument is not a string of number')
        
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/query", methods=['POST'])
def query():
    data = request.form
    session['latitude'] = data['latitude']
    session['longitude'] = data['longitude']
    session['zip_code'] = data['zip_code']
    crawler = IfoodCrawler()
    restaurants = crawler.coupon_query(data['latitude'], data['longitude'], data['zip_code'], num(data['delivery_fee_max']), num(data['min_price']), num(data['max_price']))
    return render_template('query.html', restaurants=restaurants)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

