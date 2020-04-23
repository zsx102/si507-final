from flask import Flask, render_template, request
import sqlite3
import plotly.graph_objects as go

app = Flask(__name__)

def get_colleges():
    conn = sqlite3.connect('Final_Project.sqlite')
    cur = conn.cursor()
    query = 'SELECT Id, Name, City, State from Colleges'
    results = cur.execute(query).fetchall()
    conn.close()
    return results

def get_results(sort_by, sort_order, college_id):
    conn = sqlite3.connect('Final_Project.sqlite')
    cur = conn.cursor()
    if sort_by == 'rating':
        sort_column = 'Rating'
    elif sort_by == 'price':
        sort_column = 'AvgPrice'
    else:
        sort_column = 'Distance'
    
    query = f'''SELECT Name, Rating, AvgPrice, Distance, Category FROM 
    BUSINESSES WHERE CollegeId={college_id} ORDER BY {sort_column} {sort_order}'''
    results = cur.execute(query).fetchall()
    conn.close()
    return results


@app.route('/')
def index():
    results = get_colleges()
    return render_template('index.html', results=results)

@app.route('/results', methods=['POST'])
def results():
    sort_by = request.form['sort']
    sort_order = request.form['order']
    college_id = request.form['college']
    results = get_results(sort_by, sort_order, college_id)
    plot_results = request.form.get('plot', False)
    if plot_results:
        arr = ['rating', 'price', 'distance']
        x_vals = [r[0] for r in results]
        y_vals = [r[arr.index(sort_by) + 1] for r in results]
        bars_data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=bars_data)
        div = fig.to_html(full_html=False)
        return render_template('plot.html', plot_div=div)
    else:
        return render_template('results.html', sort=sort_by, order=sort_order, results=results)


if __name__ == '__main__':
    app.run(debug=True)