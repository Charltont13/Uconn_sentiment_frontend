from google.cloud import datastore
import plotly.graph_objs as go
from plotly.offline import plot

def data_plot_summary(kind='Banks', ticker=None, sector=None, startmonth=None, endmonth=None):
    # Initialize the Datastore client
    client = datastore.Client()

    # Cleaning up the tickers and putting them into a list
    clean_tickers = []

    if "," in ticker:
        ticker = ticker.split(",")
        for t in ticker:
            clean_tickers.append(t.strip().upper())

    else:
        clean_tickers.append(ticker.strip().upper())

    # Cleaning up the sectors and putting them into a list
    clean_sectors = []

    if "," in sector:
        sector = sector.split(",")
        for s in sector:
            clean_tickers.append(s.strip().upper())

    else:
        clean_sectors.append(sector.strip().upper())



    # Create a query to fetch entities from the Datastore
    query = client.query(kind=kind)
    query.order = ['YahooTicker']

    # Fetch the data
    try:
        entities = list(query.fetch())
    
    except:
        return 429

    # Prepare the data for plotting
    keyword_period_scores = {}

    # Filter entities after fetching
    if "BANKS" in clean_sectors:
        filtered_entities = entities
    else:
        filtered_entities = [e for e in entities if e['YahooTicker'] in clean_tickers]

    for entity in filtered_entities:
        period = entity['Period']
        category = entity['YahooTicker'] + ": " + entity['Category']
        score = entity['Score']

        if period[0] == "Q":
            quarter = period[1]
            period = period[2:]

            period = period + "Q" + quarter

        else:
            period = period

        if category not in keyword_period_scores:
            keyword_period_scores[category] = {}

        if period in keyword_period_scores[category]:
            keyword_period_scores[category][period].append(score)
        else:
            keyword_period_scores[category][period] = [score]

    title = ""

    for ticker in clean_tickers:
        title = title + ticker + ", "

    # Prepare the Plotly graph
    fig = go.Figure()

    for category, period_scores in keyword_period_scores.items():
        unique_periods = sorted(period_scores.keys())
        average_scores = [sum(scores) / len(scores)
                        for scores in period_scores.values()]

        # Create a trace for each keyword
        fig.add_trace(go.Scatter(
            x=unique_periods,
            y=average_scores,
            mode='lines+markers',
            name=category
        ))

    fig.update_layout(
        title=f'Sentiment Scores over Time by Category for tickers {title}',
        xaxis_title='Period',
        yaxis_title='Average Sentiment Score',
        legend_title='Categories',
        xaxis=dict(tickangle=45),
        yaxis_range=[-1, 1]
    )

    # Return HTML div
    return plot(fig, include_plotlyjs=True, output_type='div')
