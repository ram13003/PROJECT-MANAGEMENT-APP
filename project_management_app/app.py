from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'project_management_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.close()
    return render_template('index.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    if request.method == 'POST':
        project_number = request.form['project_number']
        title = request.form['title']
        description = request.form['description']
        profit = request.form['profit']
        time_taken = request.form['time_taken']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO projects (project_number, title, description, profit, time_taken) VALUES (%s, %s, %s, %s, %s)",
                    (project_number, title, description, profit, time_taken))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('index'))

@app.route('/optimize_projects', methods=['POST'])
def optimize_projects():
    max_time = int(request.form['max_time'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, project_number, title, profit, time_taken FROM projects")
    projects = cur.fetchall()
    cur.close()

    project_list = [(project['id'], project['project_number'], project['title'], project['profit'], project['time_taken']) for project in projects]
    selected_projects = knapsack(project_list, max_time)
    return render_template('index.html', projects=projects, selected_projects=selected_projects)

def knapsack(projects, max_time):
    n = len(projects)
    dp = [[0] * (max_time + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        project_id, project_number, project_title, profit, time_taken = projects[i-1]
        for w in range(1, max_time + 1):
            if time_taken <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-time_taken] + profit)
            else:
                dp[i][w] = dp[i-1][w]

    w = max_time
    selected_projects = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_projects.append(projects[i-1])
            w -= projects[i-1][4]

    return selected_projects

if __name__ == '__main__':
    app.run(debug=True, port=5001)
