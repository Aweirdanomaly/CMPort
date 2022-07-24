import requests
import pandas as pd
import numpy as np

id_list_URL="https://api.coingecko.com/api/v3/coins/list"


id_list = None

def make_IDList():
    global id_list
    r = requests.get(id_list_URL)
    id_list=pd.DataFrame(r.json())


def find_ID(ticker):
    id_found=id_list.loc[id_list["symbol"]==ticker]["id"]
    if len(id_found) != 1:
        print(f"{len(id_found)} ids were found for {ticker}!!!\
        we'll go with the first for now...")
        try:
            return id_found.values[0]
        except:
            return None
    else:
        return id_found.values[0]
        
def get_data(ids, days=365):
    g = lambda ids: "https://api.coingecko.com/api/v3/coins/"+ids+"/market_chart?vs_currency=USD&days="+str(days)+"&interval=daily"
    data={x:(np.array((requests.get(g(x)).json())["prices"])[:,1]) for x in ids}
    prices=pd.DataFrame(data)
    return prices


##TODO: Get returns, implement rest of midterm stuff

def parse_input(user_input):
    user_input=(user_input.replace(" ","").lower()).split(",")
    ids=[find_ID(ticker) for ticker in user_input]
    return ids



def main(tickers, days):
    user_input=tickers
    make_IDList()
    ids=parse_input(user_input)
    ####Get rid of nones (aka tickers with no id found)
    ids=list(filter(None, ids))
    ####
    prices=get_data(ids, int(days))
    #print(prices)
    return prices


if __name__ == "__main__":
    print("Running as called")
    main("BTC,ETH,ADA",365)


