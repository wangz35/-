import os
import asyncio
from interactions import Client, Intents, listen, Embed,Color,File,Button, ButtonStyle, ActionRow
from interactions import slash_command, SlashContext, OptionType, slash_option
from PIL import Image, ImageDraw, ImageFont
from interactions.api.events import ButtonPressed,Component
import asyncio
import aiohttp
from mihomo import Language, MihomoAPI
from mihomo.models import StarrailInfoParsed
from mihomo.models.v1 import StarrailInfoParsedV1
from io import BytesIO
clientmihoyo = MihomoAPI(language=Language.CHS)
from dotenv import load_dotenv
load_dotenv()
my_secret = os.getenv("TOKEN")
client = Client(intents=Intents.DEFAULT)

def round_rectangle(top_left, bottom_right, radius=20, color = 'blue'):
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





async def v2(uid):
  data: StarrailInfoParsed = await clientmihoyo.fetch_user(uid, replace_icon_name_with_url=True)
  return data



@listen()
async def on_ready():
  print('We have logged in as', client.owner)
  print("------------------------------")



@slash_command(name="profile_uid", description="check star rail profile")
@slash_option(
    name="uid",
    description="Enter your UID for HSR",
    required=True,
    opt_type=OptionType.INTEGER
)
async def profile_uid(ctx: SlashContext, uid: int):
  await ctx.defer()
  try:
    print("profile request for uid")
    user_id = uid
    data = await v2(user_id)
    if data:
      signature_value = str(data.player.signature) if data.player.signature else "N/A"
      embed = Embed(
        title = data.player.name,
        description=signature_value,
        color=Color.random()
      )
      embed.set_thumbnail(data.player.avatar.icon)
      embed.add_field(name="UID", value = uid, inline=True)
      embed.add_field(name="等级", value = data.player.level, inline=True)
      embed.add_field(name="均衡等级", value = data.player.world_level, inline=True)
      embed.add_field(name="混沌回忆(当期）", value = data.player.forgotten_hall.memory_of_chaos, inline=True)
      embed.add_field(name="模拟宇宙", value = data.player.simulated_universes, inline=True)
      embed.add_field(name="好友数", value = data.player.friend_count, inline=True)
      embed.add_field(name="角色", value = data.player.characters, inline=True)
      embed.add_field(name="光锥", value = data.player.light_cones, inline=True)
      embed.add_field(name="成就", value = data.player.achievements, inline=True)
      image = await create_character_image(uid)
      image_path = f"{uid}_profile_image.png"
      image.save(image_path)
            
            # Send the image as a file attachment
      file = File(image_path, file_name=image_path)
      embed.set_image(url=f"attachment://{image_path}")
      buttons = [
        Button(style=ButtonStyle.BLUE, label=data.characters[0].name, custom_id=str(uid)+"_0"),
        Button(style=ButtonStyle.BLUE, label=data.characters[1].name, custom_id=str(uid)+"_1"),
        Button(style=ButtonStyle.BLUE, label=data.characters[2].name, custom_id=str(uid)+"_2"),
        Button(style=ButtonStyle.BLUE, label=data.characters[3].name, custom_id=str(uid)+"_3")
      ]
      action_row = ActionRow(buttons)
      await ctx.send(embeds=embed, file=file, components=buttons,ephemeral=True)
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
  await ctx.send(file = file, ephemeral=True)

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
        font = ImageFont.truetype("arial.ttf", 20)
        task = asyncio.create_task(download_image(session, char.preview))
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
        tracetasks =[]
        for each in char.trace_tree:
            tracelevels.append(each.level)
            tracetasks.append(asyncio.create_task(download_image(session, each.icon)))
        imgtraces = await asyncio.gather(*tracetasks)
        imgrelicinfolist = await asyncio.gather(*listis)
        imgrelics = await asyncio.gather(*relics)
        imgpreviews = await asyncio.gather(*previews)


        i = 0
        icondict = {}
        for each in imgrelicinfolist:
            icondict[iconname[i]] = each
            i+=1

        new_image.paste(imgpreviews[0], (0, 0))
        i = 30
        for j in range(7):
            imgtraces[j] = imgtraces[j].resize((50, 50))
            new_image.paste(imgtraces[j], (i, 450),imgtraces[j])
            circle_bbox = [i, 450, i+len(str(tracelevels[j]))*10, 450+len(str(tracelevels[j]))*10]
            draw.ellipse(circle_bbox, outline=(43, 45, 49), fill=(43, 45, 49))
            draw.text((i-2, 450-2),str(tracelevels[j]), font=ImageFont.truetype("arialbd.ttf", 20), fill=(255, 255, 255))
            i+=50
        #new_image.paste(round_rectangle((-10, -10), (100, 500),color=(0, 0, 128, 128)), (50, 550))
        x = 100
        y = 0
        for i in range(3):
            x+=300
            y+=50
            imgrelics[i] = imgrelics[i].resize((200, 200))
            new_image.paste(imgrelics[i], (x, 50))
            draw.text((x+20, 240), "+"+str(char.relics[i].level), font=font, fill=(255, 255, 255))
            yi = 0
            z = 0
            for each in relicinfo[i]:
                each = each.resize((40,40))
                if fieldlist[i][z] in ("atk", "crit_rate","spd","crit_dmg"):
                    draw.text((x+200 + 30, 56+yi), "+"+relicinfodata[i][z], font=font, fill=(255, 165, 0))
                else:
                    draw.text((x+200 + 30, 56+yi), "+"+relicinfodata[i][z], font=font, fill=(255, 255, 255))
                new_image.paste(each, (x+200-10, 50+yi))
                z+=1
                yi += 40
        x = 100
        y = 300
        for i in range(3):
            x+=300
            y+=50
            imgrelics[i+3] = imgrelics[i+3].resize((200, 200))
            new_image.paste(imgrelics[i+3], (x, 300))
            draw.text((x+20, 490), "+"+str(char.relics[i].level), font=font, fill=(255, 255, 255))
            yi = 0
            z = 0
            for each in relicinfo[i+3]:
                each = each.resize((40,40))
                if fieldlist[i+3][z] in ("atk", "crit_rate","spd","crit_dmg","sp_rate"):
                    draw.text((x+200 + 30, 306+yi), "+"+relicinfodata[i+3][z], font=font, fill=(255, 165, 0))
                else:
                    draw.text((x+200 + 30, 306+yi), "+"+relicinfodata[i+3][z], font=font, fill=(255, 255, 255))
                new_image.paste(each, (x+200-10, 300+yi))
                z+=1
                yi += 40
    icondict["hp"] = icondict["hp"].resize((50,50))
    new_image.paste(icondict["hp"], (50, 550))
    draw.text((120, 550), "+"+format(new["hp"], '.0f'), font=ImageFont.truetype("arial.ttf", 40), fill=(255, 255, 255))
    icondict["atk"] = icondict["atk"].resize((50,50))
    new_image.paste(icondict["atk"], (50, 600))
    draw.text((120, 600), "+"+format(new["atk"], '.0f'), font=ImageFont.truetype("arial.ttf", 40), fill=(255, 255, 255))
    icondict["def"] = icondict["def"].resize((50,50))
    new_image.paste(icondict["def"], (50, 650))
    draw.text((120, 650), "+"+format(new["def"], '.0f'), font=ImageFont.truetype("arial.ttf", 40), fill=(255, 255, 255))
    icondict["spd"] = icondict["spd"].resize((50,50))
    new_image.paste(icondict["spd"], (50, 700))
    draw.text((120, 700), "+"+format(new["spd"], '.1f'), font=ImageFont.truetype("arial.ttf", 40), fill=(255, 165, 0))
    icondict["crit_rate"] = icondict["crit_rate"].resize((50,50))
    new_image.paste(icondict["crit_rate"], (50, 750))
    draw.text((120, 750), "+"+format(new["crit_rate"], '.1f')+"%", font=ImageFont.truetype("arial.ttf", 40), fill=(255, 165, 0))
    icondict["crit_dmg"] = icondict["crit_dmg"].resize((50,50))
    new_image.paste(icondict["crit_dmg"], (50, 800))
    draw.text((120, 800), "+"+format(new["crit_dmg"], '.1f')+"%", font=ImageFont.truetype("arial.ttf", 40), fill=(255, 165, 0))
    yi = 550
    for eachset in char.relic_sets:
        content = eachset.name+"("+str(eachset.num)+"): "+eachset.desc
        if (len(content) >42):
            draw.text((450, yi), content[0:42],font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
            yi += 30
            draw.text((425, yi), content[42:],font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        else:
            draw.text((450, yi), content,font=ImageFont.truetype("simhei.ttf", 20), fill=(255, 255, 255))
        yi += 30
    new_image.paste(icondict["crit_dmg"], (50, 800))
    img2 = Image.new('RGB',(1350, 900))
    img3 = Image.new('RGB',(1350, 900),(43, 45, 49))
    img2.paste(img3,(0,0))
    box = round_rectangle((0, 0), (900, 350),color=(63, 65, 69, 200))
    img2.paste(box, (400, 525), box)
    img2.paste(new_image,(0,0), new_image)
    return img2


async def download_image(session, url):
    async with session.get(url) as response:
        return Image.open(BytesIO(await response.read()))

async def handle_error(ctx: SlashContext, error_message: str):
    embed = Embed(
        title = "Error",
        description=error_message,
        color=0xFF0000,
    )
    await ctx.send(embed=embed)


user_uid_mapping = {}


@slash_command(name="profile_user", description="check star rail profile")
@slash_option(
    name="user",
    description="Select a user in the server",
    required=True,
    opt_type=OptionType.USER
)
async def profile_user(ctx: SlashContext, user):
    try:
        print("profile request for user")
        # Use user.id to access the user's ID and then map it to the UID
        uid = user_uid_mapping.get(user.id)  # Use .get to avoid KeyError
        if uid is not None:
            await profile_uid(ctx, uid)  # Call profile_uid with UID
        else:
            await handle_error(ctx, "The user does not have a UID associated with them.")
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
            task = asyncio.create_task(download_image(session, char.light_cone.preview))
            light_cone.append(task)

        # 等待所有下载任务完成
        imgpreviews = await asyncio.gather(*previews)
        imglight_cones=await asyncio.gather(*light_cone)

        # 拼接图像，接下来的步骤和上面的示例相同
        total_width = sum(img.width for img in imgpreviews)
        max_height = max(img.height for img in imgpreviews)
        
        new_image = Image.new('RGBA', (total_width, max_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(new_image)
        font = ImageFont.truetype("arial.ttf", 40)  # 或者使用自定义字体
        x_offset = 0
        for i, img in enumerate(imgpreviews):
            new_image.paste(img, (x_offset, 0))
            level_rank_text = f"Lv.{data.characters[i].level} \nE{data.characters[i].eidolon}"
            light_cone_text = f"Lv.{data.characters[i].light_cone.level} \nS{data.characters[i].light_cone.superimpose}"
            draw.rectangle([x_offset, 0, x_offset+120, 110], fill=rectangle_color)
            draw.text((x_offset + 10, 10), level_rank_text, font=font, fill=(255, 255, 255))
            draw.rectangle([x_offset, 420, x_offset+120, 490], fill=rectangle_color)
            draw.text((x_offset + 10, 430-10), light_cone_text, font=ImageFont.truetype("arial.ttf", 30), fill=(255, 255, 255))
            light_cone_img = imglight_cones[i]
            light_cone_img = light_cone_img.resize((256, 300))
            light_cone_img = light_cone_img.rotate(-10, expand=True)

            # 计算贴图位置
            lc_x = x_offset + img.width - 250
            lc_y = 240  # 假设y_offset是400，这里可能需要调整

            new_image.paste(light_cone_img, (lc_x, lc_y), light_cone_img)
                    
            x_offset += img.width

    return new_image

@slash_command(name="register", description="register for yourself")
@slash_option(
    name="uid",
    description="Enter your UID for HSR",
    required=True,
    opt_type=OptionType.INTEGER
)
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
