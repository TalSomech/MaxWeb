import logging

import networkx as nx
from flask import request, render_template
import gspread
from flask_example.algorithms.Maximum_weight_cycle_packing_approximation_algorithm import \
    Maximum_weight_cycle_packing_approximation_algorithm
from flask_example.algorithms.maximum_weight_cycle_packing import maximum_weight_cycle_packing

from flask_example import app

logger = logging.getLogger()



@app.route('/')
def myhome():
    return render_template('home.html')


@app.route('/approximate')
def approximate():
    return render_template('approximate.html')


@app.route('/exact')
def exact():
    return render_template('exact.html')


@app.route('/Spread/')
def Spread():
    url = request.args.get('url')
    algo = request.args.get('algo')
    logger.info("url=", url)
    logger.info("algo=", algo)
    print("url=", url)
    print("algo=", algo)
    error = None
    try:
        account = gspread.service_account("credentials.json")
        print("account=", account)
        spreadsheet = account.open_by_url(url)
        print(spreadsheet.url)
    except gspread.exceptions.APIError:
        error = "Google Spreadsheet API error! Please verify that you shared your spreadsheet with the above address."
    # except gspread.exceptions.NoValidUrlKeyFound:
    #     error = "Google Spreadsheet could not find a key in your URL! Please check that the URL you entered points to a valid spreadsheet."
    except gspread.exceptions.SpreadsheetNotFound:
        error = "Google Spreadsheet could not find the spreadsheet you entered! Please check that the URL points to a valid spreadsheet."
    except gspread.exceptions.NoValidUrlKeyFound:
        return render_template(f'Spread.html', algo=algo,
                               url="https://docs.google.com/spreadsheets/d/1TkMFytSMkXmwEpSbTi85h5wYH6rdiJN64ZYo4ld2Iks")
    except Exception as e:
        error = type(e).__name__ + "! Please check your URL and try again."
    if error is not None:
        print("error=", error)
        return render_template(f'home.html', error=error)
    else:
        return render_template(f'Spread.html', algo=algo, url=url)


@app.route('/Run/', methods=['GET'])
def Run():
    account = gspread.service_account("credentials.json")
    k = int(request.args.get('k'))

    url = request.args.get('url')
    algo = request.args.get('algo')
    if k > 3:
        error = "ERROR:Only Supports k<=3 currently."
        return render_template(f'Spread.html', algo=algo, url=url, error=error)
    spreadsheet = account.open_by_url(url)
    graph_sheet = spreadsheet.get_worksheet(0)
    graph = nx.DiGraph()
    i = 1
    while True:
        node1 = graph_sheet.cell(i, 1).numeric_value
        node2 = graph_sheet.cell(i, 2).numeric_value
        weight = graph_sheet.cell(i, 3).numeric_value
        if node1 is None or node2 is None:
            break
        else:
            graph.add_edge(node1, node2, weight=weight)
            i += 1
    if algo == "Exact":
        ans = maximum_weight_cycle_packing(graph, k)
    else:
        ans = Maximum_weight_cycle_packing_approximation_algorithm(graph, k)
    try:
        output = spreadsheet.get_worksheet(1)
        spreadsheet.del_worksheet(output)
    except:
        pass
    output = spreadsheet.add_worksheet(title="Output", rows=len(ans)+1, cols=2)
    for i, cyc in enumerate(ans, start=1):
        strd=""
        for t in ans[i-1]:
            strd=strd+str(t)+','
        output.update_cell(i, 1, strd)
    return render_template(f'Spread.html', algo=algo, url=url)
