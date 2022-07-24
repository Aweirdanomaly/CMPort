from flask import Flask, render_template, make_response, request, url_for
import os
import time
import numpy as np
import pandas as pd

from io import BytesIO
import matplotlib.pyplot as plt, mpld3

from prices import main
from graphs import draw_graph



app = Flask(__name__)

def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)

def stats():
  main()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
      context = { 'server_time': format_server_time() }
      template=render_template("index.html")
      response = make_response(template)
      response.headers["Cache-Control"] ="public, max-age=300, s-maxage=600"
      return response
    elif request.method == "POST":
      try:
        prices= main(request.form["tickers"], request.form["days"])
        returns = np.log(prices).diff().dropna()
        fig, final =draw_graph(returns)
        
        mu_df=returns.mean().to_frame()
        mu_df["Average Price"]=prices.mean()
        mu_df.rename(columns={0:"Average daily return"},inplace=True)
        
        return make_response(render_template("index.html",
        corr=returns.corr().to_html(),
        cov=returns.cov().to_html(),
        fig=mpld3.fig_to_html(fig),
        final=final.to_html(index=False),
        mu_df=mu_df.to_html()))
      except:
        return "Something messed up"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))