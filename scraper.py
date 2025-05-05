from typing import Any

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

import json


FANDOM_URL = "https://danball.fandom.com"
WEAPON_FOR_CLASS = {
    "Boxer": "Gloves",
    "Gladiator": "Swords",
    "Sniper": "Bows",
    "Magician": "Orbs",
    "Priest": "Staffs (I refuse to call it staves)",
    "Gunner": "Guns",
    "Whipper": "Whips",
    "Angel": "Rings"
}


def get_class_list() -> list[dict[str, str]]:
    classes_page = requests.get(f"{FANDOM_URL}/wiki/Class").text
    soup = BeautifulSoup(classes_page, "html.parser")

    ref = soup.find("table", attrs={"class": "navbar1"})
    next_link = ref.find("table").find("tr").find_next_sibling().find("td")
    
    classes = []
    while True:
        class_ = next_link.find("b").find("a")
        classes.append({"name": class_.string, "link": class_["href"]})
        next_link = next_link.find_next_sibling()
        if not next_link:
            break
        next_link = next_link.find_next_sibling()

    return classes
    

def get_stage_list() -> list[dict[str, str]]:
    stages_page = requests.get(f"{FANDOM_URL}/wiki/Stage").text
    soup = BeautifulSoup(stages_page, "html.parser")

    table = soup.find("table", attrs={"class": "wikitable sortable col3r"})
    rows = table.find_all("tr")[1:]

    stages = []
    for row in rows:
        stage = row.find("a")
        if stage:
            stages.append({"name": stage["title"], "link": stage["href"]})

    return stages


def get_enemy_list() -> list[dict[str, str]]:
    enemies_page = requests.get(f"{FANDOM_URL}/wiki/List_of_enemies").text
    soup = BeautifulSoup(enemies_page, "html.parser")
    
    table = soup.find("table", attrs={"class": "wikitable sortable left"})
    rows = table.find_all("tr")[1:]

    enemies = []
    for row in rows:
        enemy = row.find("a")
        if enemy:
            enemies.append({"name": enemy["title"], "link": enemy["href"]})
            
    return enemies


def get_compo_item_list() -> dict[str, list[dict[str, str]]]:
    compo_page = requests.get(f"{FANDOM_URL}/wiki/Compo_item").text
    soup = BeautifulSoup(compo_page, "html.parser")

    header: Tag = soup.find_all("h2")[1]
    next_div = header.find_next_sibling("div")

    lists = {}
    while next_div and next_div.name == "div":
        ref = next_div.find("ul").find("li")
        group = ref.find("a").string.strip()
        items = ref.find("ul").find_all("a")

        item_list = []
        for item in items:
            item_list.append({"name": item["title"], "link": item["href"]})

        lists[group] = item_list
        next_div = next_div.find_next_sibling("div")
    
    return lists


def get_weapon_list() -> dict[str, list[dict[str, str]]]:
    lists = {}
    for group in get_class_list():
        group_page = requests.get(f"{FANDOM_URL}{group["link"]}").text
        soup = BeautifulSoup(group_page, "html.parser")

        table = soup.find("span", string="Weapons", attrs={"class": "mw-headline"}).find_next("table", attrs={"class": "wikitable"})

        items = []
        for row in table.find_all("tr"):
            for item in row.find_all("td"):
                weapon = item.find("a", recursive=False)
                if weapon:
                    items.append({"name": weapon["title"], "link": weapon["href"]})
        
        lists[WEAPON_FOR_CLASS[group["name"]]] = items

    return lists


def get_stage_enemy_list(stage_link: str) -> list[dict[str, str]]:
    stage_page = requests.get(f"{FANDOM_URL}{stage_link}").text
    soup = BeautifulSoup(stage_page, "html.parser")

    header = soup.find("span", attrs={"id": "Drops"}).parent
    next_sibling = header.find_next_sibling()

    enemy_list = []
    while next_sibling and next_sibling.name != "h2":
        if next_sibling.name == "ul":
            enemy_anchor = next_sibling.find("a")
            enemy_list.append({"name": enemy_anchor["title"], "link": enemy_anchor["href"]})

        next_sibling = next_sibling.find_next_sibling()
    return enemy_list


def get_enemy_stats(enemy_link: str) -> dict[str, Any]:
    enemy_page = requests.get(f"{FANDOM_URL}{enemy_link}").text
    soup = BeautifulSoup(enemy_page, "html.parser")

    ref = soup.find("table", attrs={"class": "SR_enemy_experience"})
    table = ref.find_next_sibling().find("table").find("tbody")
    headers: list[Tag] = table.find_all("th")[1:]

    data = {}
    lv = "err"
    for header in headers:
        name = header.string if header.string else header.find().string
        name = name.strip().replace(":", "").lower()
        stat = header.find_next_sibling("td")
        
        if name == "location":
            location = stat.find("a")
            entry = {
                "name": location["title"],
                "link": location["href"]
            }
            data[name] = entry

        if name in ["strength", "weakness"]:
            entry = [s.string.strip() for s in stat.find_all("span")]
            data[name] = entry

        if name == "lv":
            lv = stat.string.strip()

        if name == "exp":
            exp = stat.string.strip()
            entry = {
                "amount": exp,
                "lv": lv
            }
            data[name] = entry
        
        if name == "gold":
            entry = stat.string.strip()
            data[name] = entry

        if name == "drops":
            data[name] = []
            items = stat.find_all("a")
            for item in items:
                rate = item.find_next_sibling().find().string.strip()
                entry = {
                    "item": {
                        "name": item["title"],
                        "link": item["href"]
                    },
                    "rate": rate
                }
                data[name].append(entry)
    
    return data


def anchor(pack: dict[str], jump: bool = False) -> str:
    link = pack["link"][1:] if jump else pack["link"][6:]
    link = link.replace("%", "%25")
    return f'{link}.html'


def f_link(pack: dict[str], jump: bool = True) -> str:
    link = pack["link"][1:] if jump else pack["link"][6:]
    return f'{link}.html'