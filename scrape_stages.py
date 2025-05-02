import requests
import json
from bs4 import BeautifulSoup

base_url = "https://danball.fandom.com"
stages_page = requests.get(f"{base_url}/wiki/Stage").text
soup = BeautifulSoup(stages_page, "html.parser")

table = soup.find("table", attrs={"class": "wikitable sortable col3r"})
rows = table.find_all("tr")[1:]
stages = [row.find("a") for row in rows if row.find("a")]

links = {}

if __name__ == "__main__":
    with open("stages.html", "w") as file:
        file.write('<html><head><link rel="stylesheet" href="styles.css"></head><body>')
        file.write("<h1>Stages</h1><ul>")
        file.write('<a href="index.html" title="Home">Back (Home)</a><br><br><br>')
        for stage in stages:
            file.write(f'<li><a href="{stage["href"][1:].replace("%", "%25")}.html" title="{stage["title"]}">{stage["title"]}</a></li>')
        file.write("</ul></body></html>")

    for index, stage in enumerate(stages):
        link = stage["href"]
        response = requests.get(f"{base_url}{link}")
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        response.close()

        with open(f"{link[1:]}.html", "w") as file:
            file.write('<html><head><link rel="stylesheet" href="../styles.css"></head><body>')
            file.write('<a href="../index.html" title="Home">Back to home</a><br>')
            file.write(f'<h1>{stage["title"]}</h1>')
            file.write('<a href="../stages.html" title="Stages">Back (Stages)</a><br>')
            file.write('<h2>Enemies</h2><ul>')
            for h2 in soup.find_all("h2"):
                if "Drops" in h2.text:
                    next = h2.find_next_sibling()
                    while next and next.name != "h2":
                        if next.name == "ul":
                            name = next.find("a")["title"]
                            href = next.find("a")["href"]
                            enemies = soup.find("span", attrs={"id": "Enemies", "class": "mw-headline"})
                            if not enemies:
                                enemies = soup.find("span", attrs={"id": "Enemy", "class": "mw-headline"})
                            if not name in links.keys():
                                links[name] = [[stage["title"], link]]
                            else:
                                links[name].append([stage["title"], link])

                            file.write("<li>")
                            file.write(f'<a href="{href[6:]}.html" title="{name}">{name}</a>')
                            file.write("</li>")
                        next = next.find_next_sibling()

            file.write("</ul></body></html>")
        print(f"{index + 1}/{len(stages)}")

    with open("links.json", "w") as file:
        file.write(json.dumps(links, indent=4))