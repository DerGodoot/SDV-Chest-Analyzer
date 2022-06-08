import xml.etree.ElementTree as ET
import pandas as pd
import argparse

def RGBAfromInt(argb_int):
    red =  argb_int & 255
    green = (argb_int >> 8) & 255
    blue =   (argb_int >> 16) & 255
    alpha = (argb_int >> 24) & 255
    return (red, green, blue, alpha/255)

#TODO: Pass the color columns as an additional parameter to make final table cleaner
def chest_color(row):
    backgroundcolor ='background-color: rgba' + str(RGBAfromInt(row.color)) 
    return pd.Series(backgroundcolor,row.index)

#https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
def text_color(row):
    r,g,b,_ = RGBAfromInt(row.color)
    textcolor = 'color: rgb(0,0,0)' if (0.299 * r + 0.587 * g + 0.114 * b)/255 > 0.5 else 'color: rgb(255,255,255)'
    return pd.Series(textcolor ,row.index)

# Put the contents of all chests into a dataframe
def get_chest_inventory(savefile,chest_name):
    tree = ET.parse(savefile)
    root = tree.getroot()
    inventory_list = []
    for i in range(len(list(root[1]))):
        location = root[1][i]
        location_name = location.find('name').text

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
                    inventory_list.append({'DisplayName':cur_item,'quality':quality,'stack':stack,'location': location_name,'X' :X,'Y':Y,'color':color})
    df = pd.DataFrame(inventory_list)
    df['quality'] = df['quality'].apply(lambda x: 'iridium' if x ==4  else ('gold' if x == 2 else ('silver' if x==1 else ('normal' if x == 0 else x))))
    
    return df


parser = argparse.ArgumentParser(description='Export the contensts of your Stardew Valley chests into an html table.')
parser.add_argument('savefile', metavar='src', type=str, nargs=1,help='The location of your savefile.')
parser.add_argument('targetfile', metavar='dst', type=str, nargs=1,help='The location you want your table to be saved to.')
parser.add_argument('-chestname',metavar='cn',default='Kiste',nargs='?',help="Whatever chests are named in your savefile like 'Chest' or 'Kiste', depending on your language setting. Default is 'Kiste'.")


args = parser.parse_args()
if args.savefile and args.targetfile:
    df = get_chest_inventory(args.savefile[0],args.chestname)
    df.style.apply(chest_color, axis=1).apply(text_color,axis=1).to_html(args.targetfile[0])
