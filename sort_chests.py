import xml.etree.ElementTree as ET
import argparse


def sort_inventory(source,target,chest_name):
    tree = ET.parse(source)
    root = tree.getroot()
    inventory_list = []
    delete_list = []
    for i in range(len(list(root[1]))):
        location = root[1][i]
        location_name = location.find('name').text

        sort_dict = dict()
        objects = location.find('objects') # alle overworld objects, like buildinds, sprinklers, chests etc.
        for item in objects:
            value = item.find('value').find('Object')
            if value.find('DisplayName').text == chest_name: # yay a chest
                X = int(item.find('key').find('Vector2').find('X').text)
                Y = int(item.find('key').find('Vector2').find('Y').text)
                color = int(value.find('playerChoiceColor')[4].text)

                for it in value.find('items'): # all items in one chest
                    cur_item = it.find('DisplayName').text
                    stack = int(it.find('Stack').text)
                    quality = 'None' if it.find('quality') is None else int(it.find('quality').text)

                    if not it.find('type') is None: # this stuff is generally stackable
                        it_type = it.find('type').text
                        if it_type in ['Minerals','Fish','Basic','Seeds','Cooking','Crafting'] and cur_item != 'Sammler-Vogelscheuche': # Crafting is sketchy because of the rare crows
                            if (cur_item,quality) in sort_dict:
                                temp_it = sort_dict[(cur_item,quality)]
                                free_stack =  999-int(temp_it.find('Stack').text) #  maximal stacksize is 999
                                if free_stack >= stack: # all fit on the old stack
                                    temp_it.find('Stack').text = str(int(temp_it.find('Stack').text) + stack)
                                    temp_it.find('stack').text =  temp_it.find('Stack').text
                                    delete_list.append((value.find('items'),it)) # keep track of items that have been moved
                                else: # not all fit on the old stack
                                    temp_it.find('Stack').text = str(int(temp_it.find('Stack').text) + free_stack)
                                    temp_it.find('stack').text =  temp_it.find('Stack').text
                                    it.find('Stack').text = str(stack - free_stack)
                                    it.find('stack').text =  it.find('Stack').text                                                      
                            else:
                                sort_dict[(cur_item,quality)] = it
                    else: # non stackable stuff
                        pass
                    inventory_list.append({'DisplayName':cur_item,'quality':quality,'stack':stack,'location': location_name,'X' :X,'Y':Y,'color':color})

    # remove all the moved items 
    for chest, item in delete_list:
        chest.remove(item)

    tree.write(target)


    with open(target, 'r') as original: 
        data = original.read()
    with open(target, 'w') as fixed: 
        xmlstring = '<?xml version="1.0" encoding="utf-8"?><SaveGame xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
        fixed.write(xmlstring + data[len('<SaveGame xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'):])
    print('done')


parser = argparse.ArgumentParser(description='Export the contensts of your Stardew Valley chests into an html table.')
parser.add_argument('savefile', metavar='src', type=str, nargs=1,help='The location of your savefile.')
parser.add_argument('targetfile', metavar='dst', type=str, nargs=1,help='The location you want your table to be saved to.')
parser.add_argument('-chestname',metavar='cn',default='Kiste',nargs='?',help="Whatever chests are named in your savefile like 'Chest' or 'Kiste', depending on your language setting. Default is 'Kiste'.")


args = parser.parse_args()
if args.savefile and args.targetfile:
    sort_inventory(args.savefile[0],args.targetfile[0],args.chestname)
