import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import webbrowser
import math

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def CreatePost(groups, numLines, length, leaf, index):
    #if only one page
    if len(groups) == 1:
        text = " " + groups[0]

        # Creating Blue Box
        W, H = (1000, 1000)
        img = Image.new('RGB', (W, H), color=(40, 116, 174))
        draw = ImageDraw.Draw(img)


        # Drawing bruin tea logo
        draw.text((106, 375), text, fill=(255, 255, 255), align='left', font=font)
        draw.text((337, 125), 'bruin tea', fill=(255, 255, 255), align='center', font=logo_font)

        #Printing Quotation Marks
        pixel_height = 39
        if numLines == 1:
            last_char_coordinates = (length + 106, pixel_height*(numLines - 1)+ 375)
        else:
            last_char_coordinates = (length + 106 - 2 - 18, pixel_height*(numLines - 1)+ 375)
        draw.text(last_char_coordinates, '"', fill=(255,204,51), align='left', font=font)
        draw.text((106, 375), '"', fill=(255,204,51), align='left', font=font)


        # Create blue block to block out the "i" dot
        bblock = Image.new('RGBA', (20, 10), color=(40, 116, 174, 255))  # RGBA format with alpha channel
        img.paste(bblock, (454, 138), bblock)


        bblock = Image.new('RGBA', (20, 34), color=(255, 255, 255, 255))  # RGBA format with alpha channel

        # Paste the leaf image onto the original image
        img.paste(leaf, (434, 118), leaf)

        # Save the final image
        img_path = f"confessions/confession{index+1}.png"
        #img_path = "/Users/TommyTan/Downloads/bruin_tea/Bruin_Tea/output_image.png"
        img.save(img_path)
        print(f"Image saved to {img_path}")

        # Open the final image in the default web browser
        webbrowser.open(img_path)

    elif len(groups) == 2:
        pg1 = " " + groups[0]
        pg2 = groups[1]

        # Creating Blue Box for pg 1 and pg 2
        W, H = (1000, 1000)
        img1 = Image.new('RGB', (W, H), color=(40, 116, 174))
        draw = ImageDraw.Draw(img1)
        
        img2 = Image.new('RGB', (W, H), color=(40, 116, 174))
        draw2 = ImageDraw.Draw(img2)

        # Drawing bruin tea logo
        draw.text((106, 375), pg1, fill=(255, 255, 255), align='left', font=font)
        draw2.text((106, 375), pg2, fill=(255, 255, 255), align='left', font=font)

        draw.text((337, 125), 'bruin tea', fill=(255, 255, 255), align='center', font=logo_font)
        draw2.text((337, 125), 'bruin tea', fill=(255, 255, 255), align='center', font=logo_font)

        #Printing Quotation Marks
        draw.text((106, 375), '"', fill=(255,204,51), align='left', font=font)

        pixel_height = 39
        last_char_coordinates = (length + 106 - 2 - 18, pixel_height*(numLines - 1)+ 375)
        draw2.text(last_char_coordinates, '"', fill=(255,204,51), align='left', font=font)
        


        # Create blue block to block out the "i" dot
        bblock = Image.new('RGBA', (20, 10), color=(40, 116, 174, 255))  # RGBA format with alpha channel
        img1.paste(bblock, (454, 138), bblock)
        img2.paste(bblock, (454, 138), bblock)


        bblock = Image.new('RGBA', (20, 34), color=(255, 255, 255, 255))  # RGBA format with alpha channel

        # Paste the leaf image onto the original image
        img1.paste(leaf, (434, 118), leaf)
        img2.paste(leaf, (434, 118), leaf)

        img1_path = f"confessions/confession{i+1}_1.png"
        img1.save(img1_path)
        print(f"Image saved to {img1_path}")
        
        img2_path = f"confessions/confession{i+1}_2.png"
        img2.save(img2_path)
        print(f"Image saved to {img2_path}")

        # Open the final image in the default web browser
        webbrowser.open(img1_path)
        webbrowser.open(img2_path)
def AddNewLines(text, font, imgW=1080):
    outputtext = text

    groups = []
    lines = []
    line = ""
    numLines = 0
    #38 characters per line
    for word in text.split():
        test_line = line + word 

        # Check if the test line fits within the specified width
        if ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(test_line, font=font) <= 760:
            line = test_line + " "
        else:
            lines.append(line.strip())
            numLines += 1
            if numLines == 16:
                page = "\n".join(lines)
                groups.append(page)
                lines.clear()
                numLines == 0

            line = word + " "

    # Add the remaining line
    length = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(line, font=font)
    lines.append(line.strip())
    page = "\n".join(lines)
    groups.append(page)
    numLines = len(lines)

    return groups, numLines, length


#Extracting data from Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('bruin_tea_credentials.json', scope)
client = gspread.authorize(credentials)

sheet = client.open("UCLA Confessions (Responses)").sheet1

confessions = np.array(sheet.col_values(2))
status = np.array(sheet.col_values(3))

# Set font
font = ImageFont.truetype("JetBrainsMono-Bold.ttf", size=34)
logo_font = ImageFont.truetype("JetBrainsMono-Bold.ttf", size=60)

# Load the leaf image
leaf = Image.open('leaf.png')

#for i in range(0,0):
for i in range(2,len(confessions)):
    if(i < len(status)):
        if(status[i] == ""):
            text = confessions[i]
            groups, numLines, length = AddNewLines(text,font)
            text = " " + text
            sheet.update_cell(i+1, 3, "yes")
            CreatePost(groups, numLines, length, leaf, i)
    else:
        text = confessions[i]
        groups, numLines, length = AddNewLines(text,font)
        text = " " + text
        sheet.update_cell(i+1, 3, "yes")
        CreatePost(groups, numLines, length, leaf, i)

#text = "Cody Lejang is happy "
#groups, numLines, length = AddNewLines(text,font)
#CreatePost(groups, numLines, length, leaf, 113)
#print(f"numLines is: {numLines}")
#print(f"length is: {length}")

print("the end")