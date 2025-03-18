import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
from django.conf import settings

def generate_pass(ticket_id, name):
    # pass_image_path = "Vaayu'24 Pronite Pass.png"
    pass_image_path = os.path.join(settings.BASE_DIR, "static/assets/img/Vaayu'24 Pronite Pass.png")

    base_img = Image.open(pass_image_path)

    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(ticket_id)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill="black", back_color="white").convert("RGBA")
    
    qr_size = (330, 330)  
    qr_img = qr_img.resize(qr_size)
    
    qr_position = (163, 125)  
    base_img.paste(qr_img, qr_position, qr_img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)  
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(base_img)

    text_position = (200, 500)  
    text_color = (255, 255, 255)  

    text_bg_position = (140, 310, 460, 360)  
    
    draw.rectangle(text_bg_position)  

    draw.text(text_position, name, font=font, fill=text_color)

    buffer = BytesIO()
    base_img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
