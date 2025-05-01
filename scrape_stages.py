import requests
from bs4 import BeautifulSoup

base_url = "https://danball.fandom.com"
stages_page = requests.get(f"{base_url}/wiki/Stage").text
soup = BeautifulSoup(stages_page, "html.parser")

table = soup.find("table", attrs={"class": "wikitable sortable col3r"})
rows = table.find_all("tr")[1:]
stages = [row.find("a") for row in rows if row.find("a")]

if __name__ == "__main__":
    with open("stages.html", "w") as file:
        file.write('<html><head><link rel="stylesheet" href="styles.css"></head><body>')
        file.write("<h1>Stages</h1><ul>")
        for stage in stages:
            file.write(f'<li><a href=".{stage["href"].replace("%", "%25")}.html" title="{stage["title"]}">{stage["title"]}</a></li>')
        file.write("</ul></body></html>")

    for stage in stages:
        link = stage["href"]
        response = requests.get(f"{base_url}{link}")
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        response.close()

        with open(f".{link}.html", "w") as file:
            file.write('<html><head><link rel="stylesheet" href="../styles.css"></head><body>')
            file.write(f'<h1>{stage["title"]}</h1>')
            file.write('<h2>Enemies</h2>')
            file.write('<ul>')
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
                            img = enemies.parent.find_next("a", attrs={"title": name}).find("img")
                            if not img:
                                img = enemies.parent.find_next("a", attrs={"title": next.string}).find("img")
                            print(f"{link}: {name}")
                            
                            if img["src"].startswith("data"):
                                img["src"] = f'{img["data-src"]}.png'
                            else:
                                img["src"] = f'{img["src"]}.png'

                            file.write("<li>")
                            file.write(f'<a href="..{href}.html" title="{name}">{str(img)}</a>')
                            file.write(f'<a href="..{href}.html" title="{name}">{name}</a> <br><br>')
                            file.write("</li>")
                        next = next.find_next_sibling()

            file.write("</ul>")
            file.write("</body></html>")