import requests
import json
from bs4 import BeautifulSoup

base_url = "https://danball.fandom.com"
enemies_page = requests.get(f"{base_url}/wiki/List_of_enemies").text
soup = BeautifulSoup(enemies_page, "html.parser")

table = soup.find("table", attrs={"class": "wikitable sortable left"})
rows = table.find_all("tr")[1:]
enemies = [row.find("a") for row in rows if row.find("a")]

links = {}
drop_links = {}

for enemy in enemies:
    print(enemy["title"])

if __name__ == "__main__":
    with open("enemies.html", "w") as file:
        file.write('<html><head><link rel="stylesheet" href="styles.css"></head><body>')
        file.write("<h1>Enemies</h1><ul>")
        file.write('<a href="index.html" title="Home">Back (Home)</a><br><br><br>')
        for enemy in enemies:
            file.write(f'<li><a href=".{enemy["href"].replace("%", "%25")}.html" title="{enemy["title"]}">{enemy["title"]}</a></li>')
        file.write("</ul></body></html>")

    with open("links.json", "r") as file:
        links = json.loads(file.read())

    for index, enemy in enumerate(enemies):
        link = enemy["href"]
        response = requests.get(f"{base_url}{link}")
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        response.close()

        with open(f"{link[1:]}.html", "w") as file:
            file.write('<html><head><link rel="stylesheet" href="../styles.css"></head><body>')
            file.write('<a href="../index.html" title="Home">Back to home</a><br>')
            file.write(f'<h1>{enemy["title"]}</h1>')
            file.write('<h2>Drops</h2>')
            file.write('<ul>')
            
            drops = soup.find(string="Drops").parent.parent.find_next_sibling()
            items = drops.find_all("a", recursive=False)
            rates = drops.find_all("font", recursive=False)
            zipped = list(zip(items, rates))

            for item, rate_parent in zipped:
                rate = rate_parent.find("span")
                if not item["title"] in drop_links.keys():
                    drop_links[item["title"]] = [[enemy["title"], link, item["href"]]]
                else:
                    drop_links[item["title"]].append([enemy["title"], link, item["href"]])
                with open(f'{item["href"][1:]}.html', 'w') as f:
                    f.write('<html><head><link rel="stylesheet" href="../styles.css"></head><body>')
                    f.write('<a href="../index.html" title="Home">Back to home</a><br>')
                    f.write(f'<h1>{item["title"]}</h1>')
                    parent_enemies = drop_links[item["title"]]
                    f.write('<h2>Drops from:</h2><ul>')
                    for parent in parent_enemies:
                        f.write(f'<li><a href="{parent[1][6:]}.html" title="{parent[0]}">{parent[0]}</a></li>')
                file.write(f'<li><a href="{item["href"][6:].replace("%", "%25")}.html" title="{item["title"]}">{item["title"]}</a><br>({rate.string})</li>')

            file.write("</ul><h2>Found in:</h2><ul>")
            parent_stages = links[enemy["title"]]
            for parent in parent_stages:
                file.write(f'<li><a href="{parent[1][6:]}.html" title="{parent[0]}">{parent[0]}</a></li>')

            file.write("</ul>")
            file.write("</body></html>")
            print(f"{index + 1}/{len(enemies)}")
    
    with open("drop_links.json", "w") as file:
        file.write(json.dumps(drop_links, indent=4))