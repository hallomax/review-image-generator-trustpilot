import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Trustpilot URL for Eventnet GmbH
TRUSTPILOT_URL = 'https://www.trustpilot.com/review/eventnet.de'

# Function to download Google Font and save locally
def download_font(font_url, file_path):
    response = requests.get(font_url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

# Google Fonts URLs
roboto_regular_url = "http://fonts.gstatic.com/s/roboto/v20/KFOmCnqEu92Fr1Me5WZLCzYlKw.ttf"
roboto_bold_url = "http://fonts.gstatic.com/s/roboto/v20/KFOlCnqEu92Fr1MmWUlfBBc9.ttf"

# Define font paths
roboto_regular_path = 'static/roboto_regular.ttf'
roboto_bold_path = 'static/roboto_bold.ttf'

# Download fonts and save them locally if they don't exist
if not os.path.exists(roboto_regular_path):
    download_font(roboto_regular_url, roboto_regular_path)
if not os.path.exists(roboto_bold_path):
    download_font(roboto_bold_url, roboto_bold_path)

def get_trustpilot_reviews(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rating = None
    total_reviews = None

    # Save the HTML to a file for debugging
    html_file_path = 'trustpilot_page.html'
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Saved HTML to {html_file_path}")

    # Extract the rating
    rating_tag = soup.find('p', {'data-rating-typography': 'true'})
    if rating_tag:
        rating = float(rating_tag.text.strip())
    
    # Extract the total number of reviews
    reviews_tag = soup.find('p', {'data-reviews-count-typography': 'true'})
    if reviews_tag:
        total_reviews_text = reviews_tag.text.strip()
        total_reviews = int(total_reviews_text.split()[0])  # Extract the number before the word "total"

    return rating, total_reviews

def draw_square(draw, x, y, size, fill):
    # Draw filled square
    draw.rectangle([x, y, x + size, y + size], fill=fill)

def draw_partial_square(draw, x, y, size, fill, percentage):
    # Draw partially filled square
    draw.rectangle([x, y, x + size * percentage, y + size], fill=fill)
    draw.rectangle([x + size * percentage, y, x + size, y + size], fill="#d7d7e2")

def create_review_image(rating, total_reviews):
    # Create a blank image with the specified background color
    bg_color = '#eceef0'
    image = Image.new('RGBA', (460, 154), bg_color)  # Working at a larger size for better quality
    draw = ImageDraw.Draw(image)

    # Load Trustpilot logo
    tp_logo_path = 'static/tplogo.png'  # Add your Trustpilot logo path here
    tp_logo = Image.open(tp_logo_path).convert("RGBA").resize((85, 85))
    image.paste(tp_logo, (25, 37), tp_logo)

    # Load star image
    tp_star_path = 'static/tp_star.png'  # Add your star image path here
    tp_star = Image.open(tp_star_path).convert("RGBA").resize((22, 22))  # Adjust the size as needed

    # Define fonts
    try:
        font_google = ImageFont.truetype(roboto_bold_path, 28)  # Font for "Trustpilot Bewertung"
        font_rating = ImageFont.truetype(roboto_bold_path, 40)  # Font for rating (5.0)
        font_reviews = ImageFont.truetype(roboto_regular_path, 20)  # Font for reviews text
    except IOError:
        font_google = ImageFont.load_default()
        font_rating = ImageFont.load_default()
        font_reviews = ImageFont.load_default()

    # Define texts
    text_google = "Trustpilot Bewertung"
    text_rating = f"{rating:.1f}"
    text_reviews = f"Basierend auf {total_reviews} Bewertungen"
    
    # Add texts to image
    draw.text((130, 23), text_google, font=font_google, fill="black")  # Position and style for "Trustpilot Bewertung"
    draw.text((130, 60), text_rating, font=font_rating, fill="#00ad72")  # Position and style for rating (5.0)
    draw.text((130, 112), text_reviews, font=font_reviews, fill="gray")  # Position and style for reviews text

    # Draw squares
    full_squares = int(rating)
    part_square = rating - full_squares
    x_offset = 208
    square_size = 30
    square_spacing = 38  # Define the spacing between squares
    square_color = "#00ad72"
    y_square_position = 68  # Adjusted y-coordinate for squares

    for _ in range(full_squares):
        draw_square(draw, x_offset, y_square_position, square_size, square_color)
        star_x_position = x_offset + (square_size - tp_star.width) // 2
        star_y_position = y_square_position + (square_size - tp_star.height) // 2
        image.paste(tp_star, (star_x_position, star_y_position), tp_star)
        x_offset += square_spacing  # Adjust spacing here

    if part_square > 0:
        draw_partial_square(draw, x_offset, y_square_position, square_size, square_color, part_square)
        star_x_position = x_offset + (square_size - tp_star.width) // 2
        star_y_position = y_square_position + (square_size - tp_star.height) // 2
        image.paste(tp_star, (star_x_position, star_y_position), tp_star)
        x_offset += square_spacing  # Adjust spacing here

    for _ in range(5 - full_squares - (1 if part_square > 0 else 0)):
        draw_square(draw, x_offset, y_square_position, square_size, "#d7d7e2")
        star_x_position = x_offset + (square_size - tp_star.width) // 2
        star_y_position = y_square_position + (square_size - tp_star.height) // 2
        image.paste(tp_star, (star_x_position, star_y_position), tp_star)
        x_offset += square_spacing  # Adjust spacing here

    # Resize image to desired size to apply antialiasing
    image = image.resize((230, 77), Image.Resampling.LANCZOS)

    # Save the image without rounded corners
    output_path = 'output.png'
    image.save(output_path)
    print(f"Image saved as {output_path}")

def create_empty_image():
    # Create a blank transparent image with the specified dimensions
    image = Image.new('RGBA', (230, 77), (255, 255, 255, 0))  # Transparent background
    # Save the image
    output_path = 'output.png'
    image.save(output_path)
    print(f"Empty image saved as {output_path}")

if __name__ == "__main__":
    rating, total_reviews = get_trustpilot_reviews(TRUSTPILOT_URL)
    if rating and total_reviews is not None:
        create_review_image(rating, total_reviews)  # Use the dynamic total_reviews value
    else:
        create_empty_image()
        print("Failed to retrieve reviews.")
