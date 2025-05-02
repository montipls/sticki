import json

drop_links = {}

if __name__ == "__main__":
    with open("drop_links.json", "r") as file:
        drop_links = dict(json.loads(file.read()))
    
    with open("items.html", "w") as file:
        file.write('<html><head><link rel="stylesheet" href="styles.css"></head><body>')
        file.write("<h1>Enemies</h1><ul>")
        file.write('<a href="index.html" title="Home">Back (Home)</a><br><br><br>')
        for name, data in drop_links.items():
            href = data[0][2]
            file.write(f'<li><a href=".{href.replace("%", "%25")}.html" title="{name}">{name}</a></li>')
        file.write("</ul></body></html>")