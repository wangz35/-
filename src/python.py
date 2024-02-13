import os
import asyncio
from interactions import Client, Intents, listen, Embed, Color, File, Button, ButtonStyle, ActionRow, slash_command, SlashContext, OptionType, slash_option
from PIL import Image, ImageDraw, ImageFont,ImageEnhance, ImageFilter
from interactions.api.events import ButtonPressed, Component
import asyncio
import aiohttp
from mihomo import MihomoAPI, Language
from mihomo.models import StarrailInfoParsed
from mihomo.models.v1 import StarrailInfoParsedV1
from io import BytesIO

clientmihoyo = MihomoAPI(language=Language.CHS)
from dotenv import load_dotenv

load_dotenv()
my_secret = os.getenv("TOKEN")
client = Client(intents=Intents.DEFAULT)
command_called = {}

def round_rectangle(top_left, bottom_right, radius=20, color='blue'):
  """
    Draw a rounded rectangle with the given top-left and bottom-right coordinates.

    Parameters:
    - top_left: A tuple (x, y) for the top left corner.
    - bottom_right: A tuple (x, y) for the bottom right corner.
    - radius: The radius of the rounded corner.

    Returns:
    - An Image object with the drawn rounded rectangle.
    """
  width = bottom_right[0] - top_left[0]
  height = bottom_right[1] - top_left[1]

  # Create a new image with transparent background
  rounded_rect = Image.new('RGBA', (width, height), (255, 0, 0, 0))
  draw = ImageDraw.Draw(rounded_rect)

  # Draw four rectangles and four circles to make a rounded rectangle
  draw.rectangle((radius, 0, width - radius, height), fill=color)
  draw.rectangle((0, radius, width, height - radius), fill=color)
  draw.pieslice((0, 0, 2 * radius, 2 * radius), 180, 270, fill=color)
  draw.pieslice((width - 2 * radius, 0, width, 2 * radius),
                270,
                360,
                fill=color)
  draw.pieslice((0, height - 2 * radius, 2 * radius, height),
                90,
                180,
                fill=color)
  draw.pieslice((width - 2 * radius, height - 2 * radius, width, height),
                0,
                90,
                fill=color)

  return rounded_rect


async def v2(uid):
  data: StarrailInfoParsed = await clientmihoyo.fetch_user(
      uid, replace_icon_name_with_url=True)
  return data


@listen() 
async def on_ready():
  print('We have logged in as', client.owner)
  print("------------------------------")


@slash_command(name="profile_uid", description="check star rail profile")
@slash_option(name="uid",
              description="Enter your UID for HSR",
              required=True,
              opt_type=OptionType.INTEGER)
async def profile_uid(ctx: SlashContext, uid: int):
  await ctx.defer()
  try:
    print("profile request for uid")
    user_id = uid
    data = await v2(user_id)
    if data:
      signature_value = str(
          data.player.signature) if data.player.signature else "N/A"
      embed = Embed(title=data.player.name,
                    description=signature_value,
                    color=Color.random())
      embed.set_thumbnail(data.player.avatar.icon)
      embed.add_field(name="UID", value=uid, inline=True)
      embed.add_field(name="等级", value=data.player.level, inline=True)
      embed.add_field(name="均衡等级", value=data.player.world_level, inline=True)
      if data.player.forgotten_hall != None:
        embed.add_field(name="混沌回忆(当期）",
                        value=data.player.forgotten_hall.memory_of_chaos,
                        inline=True)
      embed.add_field(name="模拟宇宙",
                      value=data.player.simulated_universes,
                      inline=True)
      embed.add_field(name="好友数", value=data.player.friend_count, inline=True)
      embed.add_field(name="角色", value=data.player.characters, inline=True)
      embed.add_field(name="光锥", value=data.player.light_cones, inline=True)
      embed.add_field(name="成就", value=data.player.achievements, inline=True)
      image, charnum = await create_character_image(uid)
      print("creating_character_image")
      image_path = f"{uid}_profile_image.png"
      image.save(image_path)

      # Send the image as a file attachment
      file = File(image_path, file_name=image_path)
      embed.set_image(url=f"attachment://{image_path}")
      buttons = [
          Button(style=ButtonStyle.BLUE,
                 label=data.characters[index].name,
                 custom_id=str(uid) + "_"+str(index)) for index in range(charnum)
      ]
      action_row = ActionRow(buttons)
      await ctx.send(embeds=embed,
                     file=file,
                     components=buttons,
                     ephemeral=True)
    else:
      await handle_error(ctx, "No profile data found for the provided UID.")
  except Exception as e:
    await handle_error(ctx, f"An unexpected error occurred: {str(e)}")


@listen(Component)
async def on_click(event: Component):
  ctx = event.ctx
  await ctx.defer()
  custom_id = ctx.custom_id
  uid = custom_id[:-2]
  image = await v3(uid, int(custom_id[-1:]))
  image_path = f"{uid}_profile_image.png"
  image.save(image_path)
  file = File(image_path, file_name=image_path)
  await ctx.send(file=file, ephemeral=True)


async def v3(uid, index):
    data: StarrailInfoParsed = await clientmihoyo.fetch_user(uid, replace_icon_name_with_url=True)
    async with aiohttp.ClientSession() as session:
        previews = []#立绘
        relics = []#遗器
        relicinfo = []
        relicinfodata = []
        fieldlist = []
        char = data.characters[index]
        new_image = Image.new('RGBA', (1350, 900))
        draw = ImageDraw.Draw(new_image)
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
        eidolon_tasklist = []
        for each in char.eidolon_icons:
            task = asyncio.create_task(download_image(session, each))
            eidolon_tasklist.append(task)
        task = asyncio.create_task(download_image(session, char.portrait))
        previews.append(task)
        for relic in char.relics:
            relicinfolist = []
            infodata = []
            infoname = []
            task = asyncio.create_task(download_image(session, relic.icon))
            relics.append(task)
            task = asyncio.create_task(download_image(session, relic.main_affix.icon))
            relicinfolist.append(task)
            infodata.append(relic.main_affix.displayed_value)
            infoname.append(relic.main_affix.field)
            for each in relic.sub_affixes:
                infodata.append(each.displayed_value)
                infoname.append(each.field)
                task = asyncio.create_task(download_image(session, each.icon))
                relicinfolist.append(task)
            relicinfodata.append(infodata)
            fieldlist.append(infoname)
            imgrelicinfolist = await asyncio.gather(*relicinfolist)
            relicinfo.append(imgrelicinfolist)
        pathtask = [asyncio.create_task(download_image(session, char.path.icon))]
        elementtask = [asyncio.create_task(download_image(session, char.element.icon))]
        new = {}
        taskicon = {}
        for each in char.additions:
                    if each.is_percent:
                        new[each.field] = each.value*100
                    else:
                        new[each.field] = each.value
                    taskicon[each.field] = each.icon
        for each in char.attributes:
            if each.field  in new:
                if each.is_percent:
                    new[each.field] += each.value*100
                else:
                    new[each.field] += each.value
            else:
                if each.is_percent:
                    new[each.field] = each.value*100
                else:
                    new[each.field] = each.value
                taskicon[each.field] = each.icon
        listis = []
        iconname = []
        for each in taskicon:
            listis.append(asyncio.create_task(download_image(session, taskicon[each])))
            iconname.append(each)
        tracelevels =[]
        tracemaxlevels = []
        tracetasks =[]
        lightconetask = []
        if char.light_cone:
            lightconetask.append(asyncio.create_task(download_image(session, char.light_cone.preview)))
        for each in char.trace_tree:
            tracelevels.append(each.level)
            tracemaxlevels.append(each.max_level)
            tracetasks.append(asyncio.create_task(download_image(session, each.icon)))
        imgtraces = await asyncio.gather(*tracetasks)
        imgrelicinfolist = await asyncio.gather(*listis)
        imgrelics = await asyncio.gather(*relics)
        imgpreviews = await asyncio.gather(*previews)
        imgeidolon_icons = await asyncio.gather(*eidolon_tasklist)
        imgpath = await asyncio.gather(*pathtask)
        imgelement = await asyncio.gather(*elementtask)
        imglightcone = await asyncio.gather(*lightconetask)

        i = 0
        icondict = {}
        for each in imgrelicinfolist:
            icondict[iconname[i]] = each
            i+=1

        small_path = imgpath[0].resize((60, 60))
        imgelement[0] = imgelement[0].resize((60, 60))
        new_image.paste(small_path, (20, 30))
        new_image.paste(imgelement[0], (20, 90))
        large_path = imgpath[0].resize((350, 350))
        r, g, b, a = large_path.split()
        enhancer = ImageEnhance.Brightness(a)
        faded_a = enhancer.enhance(0.15)
        faded_icon = Image.merge('RGBA', (r, g, b, faded_a))
        new_image.paste(faded_icon, (300, 540))
        for j in range(7):
            imgtraces[j] = imgtraces[j].resize((50, 50))
            x = 0
            y = 0
            text = ""
            if j == 0:
                x = 320
                y = 700
                text = "普攻"
            elif j == 1:
                x = 400
                y = 650
                text = "终结技"
            elif j == 2:
                x = 480
                y = 700
                text = "战技"
            elif j == 3:
                x = 400
                y = 750
                text = "天赋"
            elif j == 4:
                x = 300
                y = 550
            elif j == 5:
                x = 400
                y = 550
            else:
                x = 500
                y = 550
            x += 50

            circle_bbox = [x-1, y, x-1+50, y+50]
            if j in (4,5,6):
                if char.trace_tree[j].level == 0:
                    draw.ellipse(circle_bbox, outline=(255, 255, 255, 100), fill=(43, 45, 49, 255),width = 2)
                    r, g, b, a = imgtraces[j].split()
                    enhancer = ImageEnhance.Brightness(a)
                    faded_a = enhancer.enhance(0.2)
                    faded_icon = Image.merge('RGBA', (r, g, b, faded_a))
                    new_image.paste(faded_icon, (x, y),faded_icon)
                else:
                    draw.ellipse(circle_bbox, outline=(255, 255, 255, 200), fill=(43, 45, 49, 255),width = 2)
                    new_image.paste(imgtraces[j], (x, y),imgtraces[j])
            else:
                draw.ellipse(circle_bbox, outline=(255, 255, 255, 200), fill=(43, 45, 49, 255),width = 2)
                new_image.paste(imgtraces[j], (x, y),imgtraces[j])
            string = str(char.trace_tree[j].level)+"/"+str(char.trace_tree[j].max_level)
            draw.text((x+30-len(string)/2*10, y+50),string, font=ImageFont.truetype("simhei.ttf", 15), fill=(255, 255, 255))
            draw.text((x+20-len(text)*5, y+70),text, font=ImageFont.truetype("simhei.ttf", 15), fill=(255, 255, 255))

        i = 30
        eidolonlevel = char.eidolon
        for j in range(eidolonlevel):
            imgeidolon_icons[j] = imgeidolon_icons[j].resize((50, 50))
            circle_bbox = [i-1, 450, i-1+50, 450+50]
            draw.ellipse(circle_bbox, outline=(255, 255, 255, 200), fill=(43, 45, 49, 255),width = 2)
            new_image.paste(imgeidolon_icons[j], (i, 450),imgeidolon_icons[j])
            i+=60

        for j in range(6-eidolonlevel):
            imgeidolon_icons[j+eidolonlevel] = imgeidolon_icons[j+eidolonlevel].resize((50, 50))
            r, g, b, a = imgeidolon_icons[j+eidolonlevel].split()
            enhancer = ImageEnhance.Brightness(a)
            faded_a = enhancer.enhance(0.2)
            faded_icon = Image.merge('RGBA', (r, g, b, faded_a))
            circle_bbox = [i-1, 450, i-1+50, 450+50]
            draw.ellipse(circle_bbox, outline=(255, 255, 255, 100), fill=(43, 45, 49, 255),width = 2)
            slash_start = (circle_bbox[0]+8, circle_bbox[1]+8)
            slash_end = (circle_bbox[2]-8, circle_bbox[3]-8)
            draw.line([slash_start, slash_end], fill=(255, 255, 255, 100), width=3)
            new_image.paste(faded_icon, (i, 450),faded_icon)
            i+=60
        #new_image.paste(round_rectangle((-10, -10), (100, 500),color=(0, 0, 128, 128)), (50, 550))
        x = 100
        y = 0
        font2 = ImageFont.truetype("DejaVuSans.ttf", 16)
        j = 0
        for i in range(len(imgrelics)):
            if char.relics[j].id %10 == 1:
                x = 400
                y = 50
            elif char.relics[j].id %10 == 2:
                x = 700
                y = 50
            elif char.relics[j].id %10 == 3:
                x = 1000
                y = 50
            elif char.relics[j].id %10 == 4:
                x = 400
                y = 300
            elif char.relics[j].id %10 == 5:
                x = 700
                y = 300
            elif char.relics[j].id %10 == 6:
                x = 1000
                y = 300
            color = (0,191,255, 255)
            if char.relics[j].rarity == 3:
                color = (0,191,255, 255)
            elif char.relics[j].rarity == 4:
                color = (138,43,226, 255)
            else:
                color = (255, 165, 0, 255)
            box = round_rectangle((0, 0), (300, 250),border_color=color, fill_color = (25, 25, 40, 160))
            new_image.paste(box, (x, y-25))
            imgrelics[i] = imgrelics[i].resize((200, 200))
            new_image.paste(imgrelics[i], (x, y),imgrelics[i])
            draw.text((x+20, y+190), "+"+str(char.relics[j].level), font=font, fill=(255, 255, 255))
            draw.line([(x+205-10, y),(x+205-10, y+200)],fill="white", width=1)
            yi = 0
            z = 0
            for each in relicinfo[i]:
                each = each.resize((40,40))
                if fieldlist[i][z] in ("atk", "crit_rate","spd","crit_dmg"):
                    draw.text((x+200 + 28, y+6+yi), "+"+relicinfodata[i][z], font=font2, fill=(255, 165, 0))
                else:
                    draw.text((x+200 + 28, y+6+yi), "+"+relicinfodata[i][z], font=font2, fill=(255, 255, 255))
                new_image.paste(each, (x+200-10, y+yi),each)
                z+=1
                yi += 40
            j+= 1
    icondict["hp"] = icondict["hp"].resize((50,50))
    new_image.paste(icondict["hp"], (50, 550))
    draw.text((120, 550), "+"+format(new["hp"], '.0f'), font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 255, 255))
    icondict["atk"] = icondict["atk"].resize((50,50))
    new_image.paste(icondict["atk"], (50, 600))
    draw.text((120, 600), "+"+format(new["atk"], '.0f'), font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 255, 255))
    icondict["def"] = icondict["def"].resize((50,50))
    new_image.paste(icondict["def"], (50, 650))
    draw.text((120, 650), "+"+format(new["def"], '.0f'), font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 255, 255))
    icondict["spd"] = icondict["spd"].resize((50,50))
    new_image.paste(icondict["spd"], (50, 700))
    draw.text((120, 700), "+"+format(new["spd"], '.1f'), font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 165, 0))
    icondict["crit_rate"] = icondict["crit_rate"].resize((50,50))
    new_image.paste(icondict["crit_rate"], (50, 750))
    draw.text((120, 750), "+"+format(new["crit_rate"], '.1f')+"%", font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 165, 0))
    icondict["crit_dmg"] = icondict["crit_dmg"].resize((50,50))
    new_image.paste(icondict["crit_dmg"], (50, 800))
    draw.text((120, 800), "+"+format(new["crit_dmg"], '.1f')+"%", font=ImageFont.truetype("DejaVuSans.ttf", 40), fill=(255, 165, 0))
    yi = 550
    for eachset in char.relic_sets:
        content = eachset.name+"("+str(eachset.num)+"): "+eachset.desc
        if (len(content) >30):
            draw.text((450+200, yi), content[0:35],font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
            yi += 30
            draw.text((425+200, yi), content[35:],font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        else:
            draw.text((450+200, yi), content,font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        yi += 30
    if char.light_cone:
        light_cone_img = imglightcone[0].resize((int(200*0.85), 200))
        new_image.paste(light_cone_img, (650, 700),light_cone_img)
        draw.text((860, 730), char.light_cone.name,font=ImageFont.truetype("simhei.ttf", 30), fill=(255, 255, 255))
        rank = ""
        if char.light_cone.superimpose == 1:
            rank = "I"
        elif char.light_cone.superimpose == 2:
            rank = "II"
        elif char.light_cone.superimpose == 3:
            rank = "III"
        elif char.light_cone.superimpose == 4:
            rank = "IV"
        elif char.light_cone.superimpose == 5:
            rank = "V"
        img = create_circle_with_text(rank, (30, 30), circle_radius=15, font_size=20)
        new_image.paste(img, (860, 770),img)
        draw.text((950, 770), "Lv."+str(char.light_cone.level)+"/"+str(char.light_cone.max_level),font=ImageFont.truetype("simhei.ttf", 30), fill=(255, 255, 255))



        hpimg = icondict["hp"].resize((20, 20))
        new_image.paste(hpimg, (860, 840))
        draw.text((860+25, 840), char.light_cone.attributes[0].displayed_value,font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        atkimg = icondict["atk"].resize((20, 20))
        draw.text((960+25, 840), char.light_cone.attributes[1].displayed_value,font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        new_image.paste(atkimg, (960, 840))
        defimg = icondict["def"].resize((20, 20))
        draw.text((1060+25, 840), char.light_cone.attributes[2].displayed_value,font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        new_image.paste(defimg, (1060, 840))



    img2 = Image.new('RGB',(1350, 900))

    img3 = Image.open('background.png')
    imgpreviews[0] = imgpreviews[0].resize((int(imgpreviews[0].width/2), int(imgpreviews[0].height/2)))
    img3.paste(imgpreviews[0], (200-int(imgpreviews[0].width/2), 300-int(imgpreviews[0].height/2)),imgpreviews[0])
    img3 = blur_area(img3, (0, 500, 1350, 900))
    img2.paste(img3)
    img2.paste(new_image,(0,0), new_image)
    draw = ImageDraw.Draw(img2)
    return img2


def create_circle_with_text(text, image_size=(200, 200), circle_radius=80, font_size=20):
    """
    Create an image with a black circle and a text string centered inside the circle.

    :param text: String to be written inside the circle.
    :param image_size: Tuple (width, height) for the size of the image.
    :param circle_radius: Radius of the black circle.
    :param font_size: Font size of the text.
    :return: PIL Image object with the drawn circle and text.
    """
    # Create an image with white background
    img = Image.new('RGBA', image_size, color=(255,255,255,0))

    # Initialize the drawing context with the image as background
    draw = ImageDraw.Draw(img)

    # Load a font
    try:
        font=ImageFont.truetype("simhei.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate width and height of the text to be inserted
    text_width = font_size/2*len(text)
    text_height = font_size

    # Calculate the x,y coordinates of the text
    text_x = (image_size[0] - text_width) / 2
    text_y = (image_size[1] - text_height) / 2

    # Calculate the x,y coordinates of the circle
    circle_x = image_size[0] / 2
    circle_y = image_size[1] / 2

    # Draw a black circle
    draw.ellipse((circle_x - circle_radius, circle_y - circle_radius, 
                  circle_x + circle_radius, circle_y + circle_radius), outline='black', fill='black')

    # Draw the text in black, centered inside the circle
    if text == "V":
        draw.text((text_x, text_y), text, font=font, fill="yellow")
    else:
        draw.text((text_x, text_y), text, font=font, fill='white')

    return img

def round_rectangle(top_left, bottom_right, radius=20, border_color='yellow', fill_color='blue', border_width=3):
    """
    Draw a rounded rectangle with the given top-left and bottom-right coordinates, a border color, and a fill gradient.
    
    Parameters:
    - top_left: A tuple (x, y) for the top left corner.
    - bottom_right: A tuple (x, y) for the bottom right corner.
    - radius: The radius of the rounded corner.
    - border_color: The color of the border.
    - fill_color: The start and end colors of the gradient fill (tuple of two color tuples).
    - border_width: The width of the border.
    
    Returns:
    - An Image object with the drawn rounded rectangle.
    """
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]
    
    # Create a new image with transparent background
    rounded_rect = Image.new('RGBA', (width, height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(rounded_rect)
    
    # Outer rounded rectangle (border)
    
    # Apply a gradient fill

    outer_rect_coords = (0, 0, width, height)
    for i in range(border_width):
        draw.rounded_rectangle(outer_rect_coords, radius+i, outline=border_color)
        outer_rect_coords = (outer_rect_coords[0] + 1, outer_rect_coords[1] + 1, outer_rect_coords[2] - 1, outer_rect_coords[3] - 1)
    
    # Inner rounded rectangle (fill)
    inner_rect_coords = (border_width, border_width, width - border_width, height - border_width)
    draw.rounded_rectangle(inner_rect_coords, radius, fill=fill_color)
    
    return rounded_rect


def rounded_rectangle(top_left, bottom_right, radius=20, color = 'blue'):
    """
    Draw a rounded rectangle with the given top-left and bottom-right coordinates.
    
    Parameters:
    - top_left: A tuple (x, y) for the top left corner.
    - bottom_right: A tuple (x, y) for the bottom right corner.
    - radius: The radius of the rounded corner.
    
    Returns:
    - An Image object with the drawn rounded rectangle.
    """
    width = bottom_right[0] - top_left[0]
    height = bottom_right[1] - top_left[1]
    
    # Create a new image with transparent background
    rounded_rect = Image.new('RGBA', (width, height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(rounded_rect)
    
    # Draw four rectangles and four circles to make a rounded rectangle
    draw.rectangle((radius, 0, width - radius, height), fill=color)
    draw.rectangle((0, radius, width, height - radius), fill=color)
    draw.pieslice((0, 0, 2 * radius, 2 * radius), 180, 270, fill=color)
    draw.pieslice((width - 2 * radius, 0, width, 2 * radius), 270, 360, fill=color)
    draw.pieslice((0, height - 2 * radius, 2 * radius, height), 90, 180, fill=color)
    draw.pieslice((width - 2 * radius, height - 2 * radius, width, height), 0, 90, fill=color)
    
    return rounded_rect

def blur_area(image, box_coordinates):
    """
    Apply a blur effect to a specific area of an image.

    :param image_path: Path to the image file.
    :param box_coordinates: A tuple of four integers (left, upper, right, lower) that define the
                            region of the image to blur.
    :return: A PIL Image object with the specified area blurred.
    """
    # Open the original image
    # Crop the area defined by box_coordinates from the original image
    blur_area = image.crop(box_coordinates)
    blurred_area = blur_area.filter(ImageFilter.GaussianBlur(radius=5))
    image.paste(blurred_area, box_coordinates)
    # Apply the blur filter to the cropped part

    # Paste the blurred area back onto the original image

    return image




@slash_command(name="maintenance_reminder", description="check star rail api server status")
async def maintenance_reminder(ctx: SlashContext):
    embed1 = Embed(
      title="Notice:开服了, 冲刺冲刺",
      color=0xFF0000,
      )
    embed2 = Embed(
      title="Notice: HSR服务器维护中",
      color=0xFF0000,
      )
    embederror = Embed(
      title="Notice: 这个命令已经被调用过了。",
      color=0xFF0000,
      )
    if command_called.get(ctx.channel_id, False):
        await ctx.send(embed = embederror, ephemeral=True)
        return
    else:
        command_called[ctx.channel_id] = True
    await ctx.defer()
    send = 0
    while True:
        try:
            await v2(602236308)
            await ctx.send(embed = embed1)
            await asyncio.sleep(10)
            command_called[ctx.channel_id] = False
            break
        except Exception as e:
            if send == 0:
              file = File("herta-kurukuru.gif", file_name="herta-kurukuru.gif")
              embed2.set_image(url=f"attachment://herta-kurukuru.gif")
              send+= 1
              await ctx.send(embed = embed2, file = file)
            print(f"v2 failed with {e}")

async def download_image(session, url):
  async with session.get(url) as response:
    return Image.open(BytesIO(await response.read()))


async def handle_error(ctx: SlashContext, error_message: str):
  embed = Embed(
      title="Error",
      description=error_message,
      color=0xFF0000,
  )
  await ctx.send(embed=embed)


user_uid_mapping = {}


@slash_command(name="profile_user", description="check star rail profile")
@slash_option(name="user",
              description="Select a user in the server",
              required=True,
              opt_type=OptionType.USER)
async def profile_user(ctx: SlashContext, user):
  try:
    print("profile request for user")
    # Use user.id to access the user's ID and then map it to the UID
    uid = user_uid_mapping.get(user.id)  # Use .get to avoid KeyError
    if uid is not None:
      await profile_uid(ctx, uid)  # Call profile_uid with UID
    else:
      await handle_error(ctx,
                         "The user does not have a UID associated with them.")
  except Exception as e:
    await handle_error(ctx, f"An unexpected error occurred: {str(e)}")


async def create_character_image(uid):
  data = await v2(uid)
  rectangle_color = (128, 128, 128)

  async with aiohttp.ClientSession() as session:
    # 异步下载所有的Eidolon图标和图标
    previews = []
    light_cone = []
    for char in data.characters:
      task = asyncio.create_task(download_image(session, char.preview))
      previews.append(task)
      if char.light_cone:
        task = asyncio.create_task(
          download_image(session, char.light_cone.preview))
        light_cone.append(task)

    # 等待所有下载任务完成
    imgpreviews = await asyncio.gather(*previews)
    imglight_cones = await asyncio.gather(*light_cone)

    # 拼接图像，接下来的步骤和上面的示例相同
    total_width = sum(img.width for img in imgpreviews)
    max_height = max(img.height for img in imgpreviews)

    new_image = Image.new('RGBA', (total_width, max_height),
                          (43, 45, 49, 0))
    draw = ImageDraw.Draw(new_image)
    font = ImageFont.truetype("DejaVuSans.ttf", 40)  # 或者使用自定义字体
    x_offset = 0
    j = 0
    for i, img in enumerate(imgpreviews):
      new_image.paste(img, (x_offset, 0))
      level_rank_text = f"Lv.{data.characters[i].level} \nE{data.characters[i].eidolon}"
      if data.characters[i].light_cone:
        light_cone_text = f"Lv.{data.characters[i].light_cone.level} \nS{data.characters[i].light_cone.superimpose}"
      draw.rectangle([x_offset, 0, x_offset + 120, 110], fill=rectangle_color)
      draw.text((x_offset + 10, 10),
                level_rank_text,
                font=font,
                fill=(255, 255, 255))
      if data.characters[i].light_cone:
        draw.rectangle([x_offset, 420, x_offset + 120, 490],
                      fill=rectangle_color)
        draw.text((x_offset + 10, 430 - 10),
                  light_cone_text,
                  font=ImageFont.truetype("DejaVuSans.ttf", 30),
                  fill=(255, 255, 255))
        light_cone_img = imglight_cones[j]
        light_cone_img = light_cone_img.resize((256, 300))
        light_cone_img = light_cone_img.rotate(-10, expand=True)
        j+= 1

      # 计算贴图位置
        lc_x = x_offset + img.width - 250
        lc_y = 240  # 假设y_offset是400，这里可能需要调整

        new_image.paste(light_cone_img, (lc_x, lc_y), light_cone_img)

      x_offset += img.width

  return new_image, j


@slash_command(name="register", description="register for yourself")
@slash_option(name="uid",
              description="Enter your UID for HSR",
              required=True,
              opt_type=OptionType.INTEGER)
async def register(ctx: SlashContext, uid: int):
  try:
    print("register request for uid")
    if ctx.author in user_uid_mapping.keys():
      pass
    user_uid_mapping[ctx.author.id] = uid
    await profile_uid(ctx, uid)
  except Exception as e:
    await handle_error(ctx, f"An unexpected error occurred: {str(e)}")


client.start(my_secret)
