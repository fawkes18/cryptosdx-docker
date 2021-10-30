from logging import debug
from flask.templating import render_template
import pymysql 
from app import app 
from flask import json, jsonify
from flask import flash, request

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/api/cryptoinfo", methods=["GET"])
def get_crypto_info():
    try:
        conn = pymysql.connect(
        host="twitter-database.csjjaxtjezsr.eu-central-1.rds.amazonaws.com",
        user="admin",
        password="knappima18",
        database="twitter_sentiment")

        cur = conn.cursor(pymysql.cursors.DictCursor)
        select_meta_info_query = """select 
                                        table1.coin as coin,
                                        table1.ticker as ticker,
                                        table2.sentiment as current_sentiment,
                                        table3.sentiment as today_sentiment,
                                        table4.sentiment as weekly_sentiment,
                                        table5.sentiment as monthly_sentiment,
                                        table6.price as price,
                                        table7.return_today as daily_return
                                    from crypto_price_data.crypto_tickers table1
                                    join twitter_sentiment.current_sentiment table2 on table1.coin=table2.coin
                                    join crypto_price_data.daily_returns table8 on table1.coin=table8.coin
                                    join twitter_sentiment.today_sentiment table3 on table1.coin=table3.coin
                                    join twitter_sentiment.weekly_sentiment table4 on table1.coin=table4.coin
                                    join twitter_sentiment.monthly_sentiment table5 on table1.coin=table5.coin
                                    join crypto_price_data.current_prices table6 on table1.coin=table6.coin
                                    join crypto_price_data.daily_returns table7 on table1.coin=table7.coin"""

        cur.execute(select_meta_info_query)
        rows = cur.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp

    except Exception as e:
        print(e)
    finally:
        conn.close()
        cur.close()


@app.route("/<string:coin>")
def coin_landing_page(coin):
    return render_template(f"{coin}.html")


@app.route("/api/sentiment_price_history/<string:coin>", methods=["GET"])
def get_coin_history(coin):
    try:
        conn = pymysql.connect(
        host="twitter-database.csjjaxtjezsr.eu-central-1.rds.amazonaws.com",
        user="admin",
        password="knappima18",
        database="twitter_sentiment")

        cur = conn.cursor(pymysql.cursors.DictCursor)
        select_sentiment_price_query = f"""
                                        select 
                                        table_1.date_str,
                                        table_1.return,
                                        table_2.sentiment
                                        from crypto_price_data.{coin}_historic table_1 
                                        join twitter_sentiment.results table_2 on table_1.date_str=table_2.date_str
                                        and table_1.coin=table_2.coin
                                        where table_2.sentiment is not null
                                        """
        cur.execute(select_sentiment_price_query)
        rows = cur.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        conn.close()
        cur.close()                    
        

@app.route("/api/sentiment/<string:coin>")
def sentiment(coin):
    try:
        conn = pymysql.connect(
        host="twitter-database.csjjaxtjezsr.eu-central-1.rds.amazonaws.com",
        user="admin",
        password="knappima18",
        database="twitter_sentiment")

        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(f"SELECT * FROM results WHERE coin='{coin}'")
        rows = cur.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        conn.close()
        cur.close()

@app.route("/api/metainfo/<string:coin>")
def get_sentiment_meta(coin):
    try:
        conn = pymysql.connect(
        host="twitter-database.csjjaxtjezsr.eu-central-1.rds.amazonaws.com",
        user="admin",
        password="knappima18",
        database="twitter_sentiment")

        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = f'''
            select 
                crypto_price_data.current_prices.price,
                crypto_price_data.daily_returns.return_today,
                twitter_sentiment.current_sentiment.sentiment as current_sentiment,
                twitter_sentiment.today_sentiment.sentiment as today_sentiment,
                twitter_sentiment.weekly_sentiment.sentiment as weekly_sentiment
                from twitter_sentiment.current_sentiment,
                    crypto_price_data.daily_returns,
                    crypto_price_data.current_prices,
                    twitter_sentiment.weekly_sentiment,
                    twitter_sentiment.today_sentiment
            where twitter_sentiment.current_sentiment.coin = "{coin}"
            and crypto_price_data.current_prices.coin="{coin}"
            and crypto_price_data.daily_returns.coin="{coin}"
            and twitter_sentiment.today_sentiment.coin="{coin}"
            and twitter_sentiment.weekly_sentiment.coin="{coin}"'''
        cur.execute(sql)
        rows = cur.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        conn.close()
        cur.close()

@app.route("/")
def show_chart():
    return render_template("chart.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")

#