from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
import requests

def generate_pass(ticket_id, name, qr_size, qr_position, text_position, pass_path):    
    response = requests.get(pass_path)
    img_data = BytesIO(response.content)
    base_img = Image.open(img_data)

    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(ticket_id)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill="black", back_color="white").convert("RGBA")
    
    # qr_size = (475, 475)  
    qr_img = qr_img.resize(qr_size)
    
    # qr_position = (380, 620)  # (w, h)
    base_img.paste(qr_img, qr_position, qr_img)
    font = ImageFont.load_default(size=70)
    draw = ImageDraw.Draw(base_img)

    # text_position = (370, 1120)
    text_color = (0, 0, 0)  

    draw.text(text_position, name, font=font, fill=text_color)

    buffer = BytesIO()
    base_img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
