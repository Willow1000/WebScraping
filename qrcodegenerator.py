from PIL import Image, ImageDraw
import qrcode

def make_rounded_corner_logo(logo_path, size, corner_radius):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.LANCZOS)

    # Create rounded corner mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size, size), radius=corner_radius, fill=255)

    # Apply mask to logo
    rounded_logo = Image.new("RGBA", (size, size))
    rounded_logo.paste(logo, (0, 0), mask)
    return rounded_logo

def qr_code_generator(link,logo_path):
    qr = qrcode.QRCode(
        version=1,  # controls the size of the QR
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # more error correction = better for logos
        box_size=10,
        border=4,
    )

    qr.add_data(link)
    qr.make(fit=True)
    # Load the QR code
    img = qr.make_image(fill_color="#0A84FF", back_color="transparent").convert('RGB')

    # Load your logo
    logo = Image.open(logo_path)

    # Calculate logo size
    qr_width, qr_height = img.size
    logo_size = int(qr_width * 0.25)
    # logo = logo.resize((logo_size, logo_size))
    logo = make_rounded_corner_logo(logo_path,logo_size,20)

    # Paste logo onto the QR
    pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

    img.save("qr_with_logo.png")
    img.show()

if __name__ == "__main__":
    link = input("Enter the link: ").strip()
    logo_path = input('Enter absolute path to the logo: ').strip()
    qr_code_generator(link,logo_path)
    print("done")