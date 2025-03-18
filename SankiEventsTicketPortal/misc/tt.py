from PIL import Image, ImageDraw, ImageFont
import qrcode

# Load the event pass image
pass_image_path = "Vaayu'24 Pronite Pass.png"  # Your uploaded pass image
output_path = "Updated_Pass.png"  # Output file path

# Function to generate and add QR code to the pass
def generate_pass(link, name):
    # Load the pass image
    base_img = Image.open(pass_image_path)
    
    # Generate the QR code
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(link)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill="black", back_color="white").convert("RGBA")
    
    # Resize QR code to fit in the designated area
    qr_size = (330, 330)  # Adjust as per requirement
    qr_img = qr_img.resize(qr_size)
    
    # Paste QR code on the pass
    qr_position = (163, 125)  # Adjust (x, y) coordinates based on where the QR should go
    base_img.paste(qr_img, qr_position, qr_img)

    # Load a font for the text
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # Adjust font size as needed
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(base_img)

    # Position for text replacement
    text_position = (200, 500)  # Adjust the coordinates as needed
    text_color = (255, 255, 255)  # White color

    # Remove old text by drawing a rectangle over it
    text_bg_position = (140, 310, 460, 360)  # Background rectangle coordinates
    # draw.rectangle(text_bg_position, fill=(118, 31, 227))  # Matching background color
    draw.rectangle(text_bg_position)  # Matching background color

    # Add new text
    draw.text(text_position, name, font=font, fill=text_color)

    # Save the updated pass
    base_img.save(output_path)
    print(f"Updated pass saved to {output_path}")

# Example usage
generate_pass("https://www.dynamiclabz.net/", "Dynamic Labz")
