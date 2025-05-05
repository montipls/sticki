from scraper import *


def write_header(file, wiki: bool = True) -> None:
    file.write(f'<html><head><link rel="stylesheet" href="{"../" if wiki else ""}styles.css"></head><body>')
    file.write(f'<p><a href="{"../" if wiki else ""}index.html" title="Home">Home</a> • <a href="{"../" if wiki else ""}stages.html" title="Stages">Stages</a> • <a href="{"../" if wiki else ""}enemies.html" title="Enemies">Enemies</a> • <a href="{"../" if wiki else ""}weapons.html" title="Weapons">Weapons</a> • <a href="{"../" if wiki else ""}compo_items.html" title="Compo Items">Compo Items</a></p><br>')


def write_trailer(file) -> None:
    file.write('</body></html>')


def write_stat_entry(file, name: str, data: str, link: str = None) -> None:
    file.write(f'<p class="stat">{name}: {f'<a href="{link}">' if link else ""}{data}{'</a>' if link else ""}</p>')


def main():
    links = {}

    item_names = [weapon["name"] for group in get_weapon_list().values() for weapon in group]
    item_names.extend(compo["name"] for group in get_compo_item_list().values() for compo in group)

    with open("stages.html", "w") as file:
        write_header(file, wiki=False)
        file.write('<h1>Stages</h1><ul>')

        for stage in get_stage_list():
            print(stage["name"])

            # link every stage html
            file.write(f'<li><a href="{anchor(stage, jump=True)}" title={stage["name"]}>{stage["name"]}</a></li>')

            # create html file for each stage
            with open(f_link(stage), "w") as stage_file:
                write_header(stage_file)
                stage_file.write(f'<h1>{stage["name"]}</h1>')
                stage_file.write('<h2>Enemies</h2><ul>')

                enemies = get_stage_enemy_list(stage["link"])
                enemy_count = len(enemies)
                for ei, enemy in enumerate(enemies):
                    stage_file.write(f'<li><a href="{anchor(enemy)}" title="{enemy["name"]}">{enemy["name"]}</a></li>')

                    # create html file for each enemy
                    with open(f_link(enemy), "w") as enemy_file:
                        write_header(enemy_file)
                        enemy_file.write(f'<h1>{enemy["name"]}</h1>')
                        enemy_file.write('<h2>General information</h2>')

                        stats = get_enemy_stats(enemy["link"])
                        
                        location = stats["location"]
                        write_stat_entry(enemy_file, "Location", location["name"], link=anchor(location))
                        
                        strength_data = stats["strength"]
                        strength = ", ".join(strength_data) if len(strength_data) > 0 else "-"
                        write_stat_entry(enemy_file, "Strength", strength)

                        weakness_data = stats["weakness"]
                        weakness = ", ".join(weakness_data) if len(weakness_data) > 0 else "-"
                        write_stat_entry(enemy_file, "Weakness", weakness)

                        exp_data = stats["exp"]
                        exp = f'{exp_data["amount"]} at LV {exp_data["lv"]}'
                        write_stat_entry(enemy_file, "EXP", exp)

                        gold = stats["gold"]
                        write_stat_entry(enemy_file, "Gold", gold)

                        enemy_file.write(f'<h2>Item drops</h2><ul class="stat">')

                        drops = stats["drops"]
                        if len(drops) == 0:
                            enemy_file.write('<li><i>none</i></li>')
                            write_trailer(enemy_file)
                            continue
                        
                        linked_items = links.keys()
                        for drop in drops:
                            item = drop["item"]
                            rate = drop["rate"]

                            if item["name"] == "Onigiri":
                                enemy_file.write(f'<li>{item["name"]} ({rate})</li>')
                                continue

                            if item["name"] not in item_names:
                                item["name"] = item["name"][:-2]
                                item["link"] = item["link"][:-2]

                            content = f'<a href="{anchor(item)}" title="{item["name"]}">{item["name"]}</a>'
                            enemy_file.write(f'<li>{content} ({rate})</li>')

                            if item["name"] in linked_items:
                                links[item["name"]].append({"enemy": enemy, "stage": stage})
                            else:
                                links[item["name"]] = [{"enemy": enemy, "stage": stage}]
                    
                        write_trailer(enemy_file)
                    print(f"{ei + 1}/{enemy_count}")

                stage_file.write('</ul>')
                write_trailer(stage_file)

        file.write('</ul>')
        write_trailer(file)

    with open("links.json", "w") as file:
        file.write(json.dumps(links, indent=4))

    
def create_enemy_list():
    with open('enemies.html', "w") as file:
        write_header(file, wiki=False)
        file.write('<h1>Enemies</h1><ul>')
        
        for enemy in get_enemy_list():
            file.write(f'<li><a href="{anchor(enemy, jump=True)}" title="{enemy["name"]}">{enemy["name"]}</a></li>')
        
        file.write("</ul>")
        write_trailer(file)


def create_item_list():
    with open('weapons.html', "w") as file:
        write_header(file, wiki=False)
        file.write('<h1>Weapons</h1><ul>')
        
        weapons = get_weapon_list()
        for class_ in weapons.keys():
            file.write(f'<li><h2>{class_}</h2><ul>')

            for weapon in weapons[class_]:
                file.write(f'<li><a href="{anchor(weapon, jump=True)}" title="{weapon["name"]}">{weapon["name"]}</a></li>')
            file.write("</ul></li>")
        
        file.write("</ul>")
        write_trailer(file)

    with open('compo_items.html', "w") as file:
        write_header(file, wiki=False)
        file.write('<h1>Compo Items</h1><ul>')
        
        compo_items = get_compo_item_list()
        for type in compo_items.keys():
            file.write(f'<li><h2>{type}</h2><ul>')

            for compo_item in compo_items[type]:
                file.write(f'<li><a href="{anchor(compo_item, jump=True)}" title="{compo_item["name"]}">{compo_item["name"]}</a></li>')
            file.write("</ul></li>")
        
        file.write("</ul>")
        write_trailer(file)


def initialize_item_pages():
    with open("links.json", "r") as file:
        links = json.loads(file.read())

    weapons = [weapon for group in get_weapon_list().values() for weapon in group]
    for weapon in weapons:
        with open(f_link(weapon), "w") as file:
            write_header(file, wiki=True)
            file.write(f'<h1>{weapon["name"]}</h1>')

            try:
                item_links = links[weapon["name"]]
                file.write(f'<h2>Drops by</h2><ul>')
                for link in item_links:
                    enemy = link["enemy"]
                    stage = link["stage"]
                    file.write(f'<li><a href="{anchor(enemy)}" title="{enemy["name"]}">{enemy["name"]}</a> (<a href="{anchor(stage)}" title="{stage["name"]}">{stage["name"]}</a>)</li>')
                file.write("</ul>")
            except KeyError:
                file.write(f'<h2>Default weapon</h2>')
            
            write_trailer(file)

    compo_items = [compo_item for group in get_compo_item_list().values() for compo_item in group]
    for compo_item in compo_items:
        with open(f_link(compo_item), "w") as file:
            write_header(file, wiki=True)
            file.write(f'<h1>{compo_item["name"]}</h1>')
            file.write(f'<h2>Drops by</h2><ul>')

            item_links = links[compo_item["name"]]
            for link in item_links:
                enemy = link["enemy"]
                stage = link["stage"]
                file.write(f'<li><a href="{anchor(enemy)}" title="{enemy["name"]}">{enemy["name"]}</a> (<a href="{anchor(stage)}" title="{stage["name"]}">{stage["name"]}</a>)</li>')
            
            file.write("</ul>")
            write_trailer(file)

if __name__ == "__main__":
    initialize_item_pages()