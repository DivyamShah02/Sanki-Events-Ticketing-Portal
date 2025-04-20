from PIL import Image, ImageDraw, ImageFont

# Load the image
image = Image.open("pass.png")  # Replace with your PNG file

# Create a drawing object
draw = ImageDraw.Draw(image)

# Define the text and font
text = "John Doe"
font = ImageFont.truetype("arial.ttf", 100)  # Ensure 'arial.ttf' is available or use another font

# Position of text (adjust as needed)
text_position = (250, 990)  # Change this to place the text where needed

# Text color (RGB)
text_color = (255, 0, 0)  # Red color

# Add text to image
draw.text(text_position, text, fill=text_color, font=font)

# Save the image
image.save("output.png")

# Show the modified image
image.show()
