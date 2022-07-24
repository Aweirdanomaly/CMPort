import pandas as pd
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from scipy.optimize import minimize
import random

rf=0.015/12 #Assumed here to be about 1.5%


def draw_graph_two(returns):
    cryptos = returns.columns
    fig, ax = plt.subplots(figsize=(7, 5))
    #Function for getting random hex color code 
    def get_color():
        r = lambda: random.randint(0,255)
        return ('#%02X%02X%02X' % (r(),r(),r()))

    #Get a color for each crypto
    colors = [get_color() for x in returns.columns]
    #Plot each crypto
    for (cryptos, color) in zip(cryptos, colors):
        ax.scatter(x=np.sqrt(returns.cov().loc[cryptos, cryptos]),
            y=returns.mean().loc[cryptos], label=cryptos,
            s=50, color=color)
        
    #Plot the risk free rate
    ax.scatter(x=0, y=rf, label="RF", s=50, color="black")
    #Parameters for setting how the graph looks
    ax.set_xlim(-0.005, 0.105)
    ax.set_ylim(-0.002, 0.012)
    ax.set_xlabel("Monthly Standard Deviation")
    ax.set_ylabel("Monthly Expected Return")
    ax.legend()
    return fig


def draw_graph(returns):
    def get_color():
        r = lambda: random.randint(0,255)
        return ('#%02X%02X%02X' % (r(),r(),r()))
    cryptos = returns.columns
    rw_df = pd.DataFrame(data=None)

    coins_num=len(returns.columns)
    for coin in range(len(returns.columns)-1):
        rw_df.loc[:, coin] = np.random.normal(1/coins_num, 1/coins_num, 10000)
        
    rw_df.loc[:, len(returns.columns)-1] = 1 - rw_df.sum(axis=1)
    
    mu_df = returns.mean()
    cov_df = returns.cov()
    mu=mu_df.values
    cov=cov_df.values

    # Compute the expected return of the portfolio for each random set.
    random_portfolio_df = rw_df.dot(mu).to_frame("R_P")
    # Compute the variance and then the standard deviation of the portfolio for each random set.
    random_portfolio_df.loc[:, "Var"] = np.sum(rw_df.dot(cov) * rw_df, axis=1)
    random_portfolio_df.loc[:, "SD"] = np.sqrt(random_portfolio_df.loc[:, "Var"])

    
    
    no_stocks = len(mu)

    def min_variance(mu, cov, desired_ret):

        # Compute the variance
        def variance(weights):
            return np.dot(weights, np.dot(cov, weights))
        # Check that the weights sum up to 1
        def check_sum(weights):
            return np.sum(weights) - 1
        # Check that the return of the portfolio is the desired return.
        def check_return(weights):
            return np.dot(mu.T, weights) - desired_ret

        # Write down the constraints as equality constraints.
        cons = ({"type": "eq", "fun": check_sum},
                {"type": "eq", "fun": check_return})
        # We are guessing a purposely wrong initial guess.
        init_guess = [-10 for _ in range(no_stocks)]
        # Run the minimiziation
        results = minimize(variance, init_guess, tol=1e-9, constraints=cons)
        w = results.x
        # Assert that the optimization converged. Otherwise, throw an error.
        assert results.success, "Optimization did not converge for ." + \
            str(desired_ret)
        # Return the desired return and variance of the appropriate portfolio.
        return [desired_ret, variance(w), w]


    # Finding the efficient frontier
    desired_rets = np.linspace(-.2, 0.18/12, 300)
    frontier = [min_variance(mu, cov, desired_ret)
                for desired_ret in desired_rets]

    frontier_df = pd.DataFrame(data=frontier, columns=["ER", "Var", "Weights"])
    frontier_df.loc[:, "SD"] = np.sqrt(frontier_df.loc[:, "Var"])
    
    #graphing
    fig, ax = plt.subplots(figsize=(9, 6))

    frontier_df.plot.line(x="SD", y="ER", color="black", ax=ax, label="Frontier")

    #Get a color for each crypto
    colors = [get_color() for x in returns.columns]

    # Plot the different portfolios as a scatter plot.
    random_portfolio_df.plot.scatter(x="SD", y="R_P", s=1, color="gray", ax=ax)

    cryptos = returns.columns
    for (cryptos, color) in zip(cryptos, colors):
        ax.scatter(x=np.sqrt(cov_df.loc[cryptos, cryptos]),\
                y=mu_df.loc[cryptos], label=cryptos, s=70, color=color, marker="o")

    # Incldue the risk-free rate.
    ax.scatter(x=0, y=rf, label="RF", s=70, color="black", marker="o")

    ax.set_xlim(-0.005, 0.105)
    ax.set_ylim(-0.008, 0.012)
    ax.set_xlabel("Monthly Standard Deviation")
    ax.set_ylabel("Monthly Expected Return")

    ax.legend()
    
    frontier_df.loc[:, "SR"] = (frontier_df.loc[:, "ER"] - rf) / frontier_df.loc[:, "SD"]
    weights = frontier_df.loc[frontier_df["SR"] == np.max(frontier_df["SR"]), "Weights"].values

    norms=sum([abs(weights[0][j]) if (weights[0][j] < 0) else weights[0][j] for j in range(len((returns.columns)))])

    final=[(returns.columns[j], weights[0][j]/norms) for j in range(len(returns.columns))]
    final_df=pd.DataFrame(data=final,columns=["Cryptocurrency","Proportion Invested"])
    return fig, final_df

