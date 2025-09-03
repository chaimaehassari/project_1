from flask import Flask, jsonify, render_template
import requests, random
from db import get_connection, create_countries_table

app = Flask(__name__)


create_countries_table()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_countries', methods=['GET'])
def add_countries():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,flag,subregion,population"
    response = requests.get(url)
    countries = response.json()
    random_countries = random.sample(countries, 10)

    conn = get_connection()
    cur = conn.cursor()
    for country in random_countries:
        name = country['name']['common']
        capital = country['capital'][0] if 'capital' in country and country['capital'] else None
        flag = country.get('flag', None)
        subregion = country.get('subregion', None)
        population = country.get('population', None)

        cur.execute(
            "INSERT INTO countries (name, capital, flag, subregion, population) VALUES (%s,%s,%s,%s,%s)",
            (name, capital, flag, subregion, population)
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message":"10 pays ajoutés avec succès!"})

@app.route('/countries', methods=['GET'])
def list_countries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM countries ORDER BY id")
    countries = cur.fetchall()
    cur.close()
    conn.close()

    countries_list = []
    for c in countries:
        countries_list.append({
            "id": c[0],
            "name": c[1],
            "capital": c[2],
            "flag": c[3],
            "subregion": c[4],
            "population": c[5]
        })

    return jsonify(countries_list)

if __name__ == '__main__':
    app.run(debug=True)
