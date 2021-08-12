from flask import Flask,render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/index')
def home():
    return index()

@app.route('/movie')
def movie():
    movielist = []
    conn = sqlite3.connect('movie.db')
    cur = conn.cursor()
    sql = '''
        select * from movie250
    '''
    data = cur.execute(sql)
    for item in data:
        movielist.append(item)
    cur.close()
    conn.close()
    return render_template('movie.html',movielist = movielist)

@app.route('/analysis')
def rating_score():
    rating = []
    num_of_rating = []
    rank_rating = []
    rate_gross = []
    meta = []
    num_of_meta = []
    rank_meta = []
    meta_gross = []
    rating_meta = []
    gross_rank = []

    conn = sqlite3.connect('movie.db')
    cur = conn.cursor()
    sql1 = '''
        SELECT rating,count(rating) FROM movie250
        GROUP BY rating
    '''
    sql2 = '''
        SELECT rating,id FROM movie250
    '''
    sql3 = '''
        SELECT rating,gross FROM movie250
        WHERE gross <> ' '
    '''
    sql4 = '''
        SELECT meta_score,count(meta_score) FROM movie250
        GROUP BY meta_score
        ORDER BY meta_score DESC
    '''
    sql5 = '''
        SELECT meta_score,id FROM movie250
        WHERE meta_score <> ' '
        '''
    sql6 = '''
        SELECT meta_score,gross FROM movie250
        WHERE meta_score <> ' ' AND gross <> ' '
    '''
    sql7 = '''
        SELECT rating, meta_score FROM movie250
        WHERE meta_score <> ' ' AND rating <> ' '
    '''
    sql8 = '''
        SELECT id,gross FROM movie250
        WHERE gross <> ' '
    '''

    data = cur.execute(sql1)
    for item in data:
        rating.append(item[0])
        num_of_rating.append(item[1])

    data = cur.execute(sql2)
    for item in data:
        rank_rating.append(list(item))

    data = cur.execute(sql3)
    for item in data:
        rate_gross.append(list(item))

    data = cur.execute(sql4)
    for item in data:
        if item[0]==' ':
            continue
        meta.append(item[0])
        num_of_meta.append(item[1])

    data = cur.execute(sql5)
    for item in data:
        rank_meta.append(list(item))

    data = cur.execute(sql6)
    for item in data:
        meta_gross.append(list(item))

    data = cur.execute(sql7)
    for item in data:
        rating_meta.append(list(item))

    data = cur.execute(sql8)
    for item in data:
        gross_rank.append(list(item))

    cur.close()
    conn.close()
    return render_template('analysis.html',
                           rating=rating,num_of_rating=num_of_rating,
                           rank_rating=rank_rating,
                           rate_gross=rate_gross,
                           meta=meta,num_of_meta=num_of_meta,
                           rank_meta=rank_meta,
                           meta_gross=meta_gross,
                           rating_meta=rating_meta,
                           gross_rank=gross_rank)

@app.route('/word')
def word():
    return render_template('word.html')

@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == "__main__":
    app.run()