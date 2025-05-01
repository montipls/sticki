import requests
from bs4 import BeautifulSoup

base_url = "https://danball.fandom.com"
enemies_page = requests.get(f"{base_url}/wiki/List_of_enemies").text
soup = BeautifulSoup(enemies_page, "html.parser")

table = soup.find("table", attrs={"class": "wikitable sortable left"})
rows = table.find_all("tr")[1:]
enemies = [row.find("a") for row in rows if row.find("a")]
for enemy in enemies:
    print(enemy["title"])

if __name__ == "__main__":
    with open("enemies.html", "w") as file:
        file.write('<html><head><link rel="stylesheet" href="styles.css"></head><body>')
        file.write("<h1>Enemies</h1><ul>")
        for enemy in enemies:
            file.write(f'<li><a href=".{enemy["href"].replace("%", "%25")}.html" title="{enemy["title"]}">{enemy["title"]}</a></li>')
        file.write("</ul></body></html>")

    for index, enemy in enumerate(enemies):
        link = enemy["href"]
        response = requests.get(f"{base_url}{link}")
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        response.close()

        with open(f".{link}.html", "w") as file:
            file.write('<html><head><link rel="stylesheet" href="../styles.css"></head><body>')
            file.write(f'<h1>{enemy["title"]}</h1>')
            file.write('<h2>Drops</h2>')
            file.write('<ul>')
            
            drops = soup.find(string="Drops").parent.parent.find_next_sibling()
            items = drops.find_all("a")
            rates = drops.find_all("span")
            zipped = list(zip(items, rates))

            for item, rate in zipped:
                file.write(f'<li><a href="{base_url}{item["href"]}" title="{item["title"]}">{item["title"]}</a><br>{rate.string}</li>')


            file.write("</ul>")
            file.write("</body></html>")
            print(f"{index + 1}/{len(enemies)}")