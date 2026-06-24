import os
from PIL import Image, ImageDraw, ImageFont

def draw_phone_frame(draw, width, height, notch_width=110, notch_height=26, dark_mode=False):
    # Bezel shadow
    for i in range(8):
        draw.rounded_rectangle(
            [10 - i, 10 - i, width - 10 + i, height - 10 + i],
            radius=44,
            outline=(0, 0, 0, 10 + i * 2),
            width=1
        )
    # Bezel
    draw.rounded_rectangle(
        [10, 10, width - 10, height - 10],
        radius=40,
        fill=(18, 18, 18) if dark_mode else (30, 41, 59),
        outline=(51, 65, 85),
        width=4
    )
    # Inner screen
    draw.rounded_rectangle(
        [18, 18, width - 18, height - 18],
        radius=32,
        fill=(18, 18, 18) if dark_mode else (250, 250, 250),
        outline=(15, 23, 42) if dark_mode else (241, 245, 249),
        width=1
    )
    # Camera Notch
    draw.rounded_rectangle(
        [(width - notch_width) // 2, 18, (width + notch_width) // 2, 18 + notch_height],
        radius=12,
        fill=(15, 23, 42) if dark_mode else (15, 23, 42)
    )

def get_font(font_name="arial.ttf", size=14):
    try:
        return ImageFont.truetype(font_name, size)
    except IOError:
        return ImageFont.load_default()

def create_login_mockup(output_path):
    width, height = 420, 800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Phone
    draw_phone_frame(draw, width, height, dark_mode=False)
    
    # Fonts
    font_title = get_font(size=24)
    font_body = get_font(size=14)
    font_sub = get_font(size=11)
    
    # Colors
    primary = (31, 71, 136) # Deep Slate Blue #1F4788
    text_dark = (15, 23, 42)
    text_muted = (100, 116, 139)
    border_color = (226, 232, 240)
    
    # Brand logo placeholder
    draw.ellipse([width//2 - 32, 100, width//2 + 32, 164], fill=primary)
    draw.ellipse([width//2 - 20, 112, width//2 + 20, 152], fill=(255, 255, 255))
    # Fingerprint icon inside logo
    draw.arc([width//2 - 12, 120, width//2 + 12, 144], 0, 360, fill=primary, width=3)
    draw.arc([width//2 - 6, 126, width//2 + 6, 138], 0, 360, fill=primary, width=2)
    
    # Title
    draw.text((width//2, 190), "Allia Finger", fill=text_dark, font=font_title, anchor="mm")
    draw.text((width//2, 215), "Akses Masuk Operator Lembaga", fill=text_muted, font=font_sub, anchor="mm")
    
    # Input fields
    # Username Field
    draw.rounded_rectangle([40, 260, width-40, 310], radius=8, fill=(255, 255, 255), outline=border_color, width=1)
    draw.text((56, 275), "Username atau Email", fill=text_muted, font=font_body)
    
    # Password Field
    draw.rounded_rectangle([40, 330, width-40, 380], radius=8, fill=(255, 255, 255), outline=border_color, width=1)
    draw.text((56, 345), "Kata Sandi", fill=text_muted, font=font_body)
    # Password dots
    for i in range(6):
        draw.ellipse([width - 80 + i*8, 351, width - 74 + i*8, 357], fill=text_muted)
        
    # Checkbox licensing
    draw.rectangle([40, 410, 56, 426], fill=(255, 255, 255), outline=primary, width=2)
    # Checked symbol
    draw.line([44, 418, 48, 422], fill=primary, width=2)
    draw.line([48, 422, 53, 413], fill=primary, width=2)
    draw.text((66, 411), "Saya menyetujui Syarat & Ketentuan", fill=text_dark, font=font_sub)
    
    # Login Button (Floating style with elevation shadow)
    # Button shadow
    draw.rounded_rectangle([40, 462, width-40, 514], radius=26, fill=(31, 71, 136, 40))
    draw.rounded_rectangle([40, 460, width-40, 510], radius=25, fill=primary)
    draw.text((width//2, 485), "MASUK", fill=(255, 255, 255), font=font_body, anchor="mm")
    
    # Info footer
    draw.text((width//2, 700), "Versi Aplikasi v2.1.0", fill=text_muted, font=font_sub, anchor="mm")
    draw.text((width//2, 720), "Didukung oleh OpenCV & Computer Vision", fill=text_muted, font=font_sub, anchor="mm")
    
    img.save(output_path, "PNG")

def create_dashboard_mockup(output_path):
    width, height = 420, 800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Phone
    draw_phone_frame(draw, width, height, dark_mode=False)
    
    # Fonts
    font_title = get_font(size=20)
    font_body = get_font(size=13)
    font_sub = get_font(size=11)
    font_bold = get_font(size=14)
    
    # Colors
    primary = (31, 71, 136) # Deep Slate Blue #1F4788
    accent = (0, 188, 212) # Cyan #00BCD4
    text_dark = (15, 23, 42)
    text_muted = (100, 116, 139)
    bg_light = (248, 250, 252)
    
    # Welcome Operator
    draw.ellipse([40, 60, 72, 92], fill=primary)
    draw.text((56, 76), "O", fill=(255,255,255), font=font_bold, anchor="mm")
    draw.text((82, 64), "Selamat Datang,", fill=text_muted, font=font_sub)
    draw.text((82, 78), "Operator Lembaga A", fill=text_dark, font=font_bold)
    
    # Active Credit Card with Rich Gradients (drawn as multi-layered card)
    # Drawing gradient simulated bands
    card_top, card_bottom = 120, 240
    card_left, card_right = 36, width - 36
    
    # Shadow
    draw.rounded_rectangle([card_left, card_top+4, card_right, card_bottom+4], radius=16, fill=(31, 71, 136, 30))
    
    # Draw vertical bands to simulate gradient
    for y in range(card_top, card_bottom):
        ratio = (y - card_top) / (card_bottom - card_top)
        r = int(31 * (1 - ratio) + 0 * ratio)
        g = int(71 * (1 - ratio) + 188 * ratio)
        b = int(136 * (1 - ratio) + 212 * ratio)
        # Rounded rectangle clip approximation: draw horizontal lines
        draw.line([card_left+1, y, card_right-1, y], fill=(r, g, b))
        
    # Draw card border with round corners
    draw.rounded_rectangle([card_left, card_top, card_right, card_bottom], radius=16, outline=(255,255,255,80), width=1)
    
    # Card details
    draw.text((card_left+20, card_top+20), "KREDIT AKTIF LEMBAGA", fill=(255, 255, 255, 200), font=font_sub)
    draw.text((card_left+20, card_top+40), "150 Kredit", fill=(255, 255, 255), font=get_font(size=24))
    draw.text((card_left+20, card_top+85), "ID: L-8893A Allia Kids", fill=(255, 255, 255, 180), font=font_sub)
    
    # Statistics Bento Section
    draw.text((40, 275), "STATISTIK SESI AKTIF", fill=text_muted, font=font_sub)
    
    # Bento Card 1: Sesi
    draw.rounded_rectangle([40, 295, width//2 - 10, 385], radius=12, fill=bg_light, outline=(226, 232, 240), width=1)
    draw.ellipse([54, 308, 76, 330], fill=(219, 234, 254))
    # Icon replacement (Folder)
    draw.rectangle([60, 314, 70, 324], fill=primary)
    draw.text((54, 345), "12 Sesi", fill=text_dark, font=font_bold)
    draw.text((54, 362), "Pemindaian", fill=text_muted, font=font_sub)
    
    # Bento Card 2: Menunggu Tinjauan
    draw.rounded_rectangle([width//2 + 10, 295, width-40, 385], radius=12, fill=bg_light, outline=(226, 232, 240), width=1)
    draw.ellipse([width//2 + 24, 308, width//2 + 46, 330], fill=(255, 243, 205)) # Amber tint
    # Icon replacement (Clock)
    draw.ellipse([width//2 + 30, 314, width//2 + 40, 324], fill=(245, 158, 11))
    draw.text((width//2 + 24, 345), "2 Review", fill=text_dark, font=font_bold)
    draw.text((width//2 + 24, 362), "Menunggu Admin", fill=text_muted, font=font_sub)
    
    # Sesi Terbaru List
    draw.text((40, 420), "SESI AKTIF TERBARU", fill=text_muted, font=font_sub)
    
    # Sesi Item 1
    draw.rounded_rectangle([40, 440, width-40, 500], radius=10, fill=(255, 255, 255), outline=(241, 245, 249), width=1)
    draw.ellipse([52, 452, 80, 480], fill=(236, 253, 245)) # Green circle
    draw.text((61, 458), "JD", fill=(16, 185, 129), font=font_sub)
    draw.text((92, 452), "Jane Doe", fill=text_dark, font=font_bold)
    draw.text((92, 470), "Progress: 8 dari 10 jari selesai", fill=text_muted, font=font_sub)
    # Forward Chevron
    draw.line([width-65, 464, width-60, 470], fill=text_muted, width=2)
    draw.line([width-60, 470, width-65, 476], fill=text_muted, width=2)
    
    # Floating Action Button "Mulai Pemindaian Baru"
    fab_y = 620
    draw.rounded_rectangle([width//2 - 110, fab_y, width//2 + 110, fab_y + 48], radius=24, fill=(31, 71, 136, 40))
    draw.rounded_rectangle([width//2 - 110, fab_y-2, width//2 + 110, fab_y + 46], radius=24, fill=primary)
    draw.text((width//2, fab_y + 22), "+ Mulai Pemindaian Baru", fill=(255, 255, 255), font=font_bold, anchor="mm")
    
    # Bottom Navigation Bar
    nav_y = 724
    draw.rectangle([18, nav_y, width-18, height-18], fill=(255,255,255))
    draw.line([18, nav_y, width-18, nav_y], fill=(241, 245, 249), width=1)
    # Icons representation
    draw.text((width//5 * 1 - 10, nav_y+20), "Beranda", fill=primary, font=font_sub, anchor="mm")
    draw.text((width//5 * 2 - 5, nav_y+20), "Sesi", fill=text_muted, font=font_sub, anchor="mm")
    draw.text((width//5 * 3 + 5, nav_y+20), "Tinjauan", fill=text_muted, font=font_sub, anchor="mm")
    draw.text((width//5 * 4 + 10, nav_y+20), "Riwayat", fill=text_muted, font=font_sub, anchor="mm")
    
    img.save(output_path, "PNG")

def create_camera_mockup(output_path):
    width, height = 420, 800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Phone (Dark Mode Screen)
    draw_phone_frame(draw, width, height, dark_mode=True)
    
    # Fonts
    font_body = get_font(size=13)
    font_sub = get_font(size=11)
    font_bold = get_font(size=14)
    
    # Viewfinder Overlay: Dashed border
    view_x, view_y = width//2, height//2 - 50
    view_r = 110
    
    # Draw simulated fingerprint inside camera background
    draw.arc([view_x - 45, view_y - 65, view_x + 45, view_y + 25], 0, 360, fill=(40, 40, 40), width=3)
    draw.arc([view_x - 30, view_y - 50, view_x + 30, view_y + 10], 0, 360, fill=(50, 50, 50), width=3)
    draw.arc([view_x - 15, view_y - 35, view_x + 15, view_y - 5], 0, 360, fill=(60, 60, 60), width=3)
    
    # Dashed viewfinder (Dashed Oval approximation: 36 segments)
    import math
    for i in range(36):
        if i % 2 == 0:
            angle_start = i * 10
            angle_end = (i + 1) * 10
            draw.arc([view_x - 65, view_y - 85, view_x + 65, view_y + 45], angle_start, angle_end, fill=(52, 211, 153), width=2)
            
    # Camera UI Buttons (Right Column)
    ctrl_x = width - 56
    # Flash Button
    draw.ellipse([ctrl_x-16, 100, ctrl_x+16, 132], fill=(0,0,0,150), outline=(255,255,255,80), width=1)
    draw.text((ctrl_x, 116), "F", fill=(250, 204, 21), font=font_bold, anchor="mm")
    
    # Opacity Waterdrop Button
    draw.ellipse([ctrl_x-16, 148, ctrl_x+16, 180], fill=(0,0,0,150), outline=(255,255,255,80), width=1)
    draw.text((ctrl_x, 164), "💧", fill=(255,255,255), font=font_bold, anchor="mm")
    
    # Level indicator (e.g. 0.05 opacity text label next to opacity icon)
    draw.rectangle([ctrl_x - 65, 152, ctrl_x - 22, 176], fill=(0, 0, 0, 180))
    draw.text((ctrl_x - 43, 164), "Low 0.05", fill=(52, 211, 153), font=font_sub, anchor="mm")
    
    # Zoom Bar Slider
    draw.rounded_rectangle([50, height - 160, width-50, height - 146], radius=7, fill=(0,0,0,150))
    draw.line([70, height - 153, width-70, height - 153], fill=(255,255,255), width=2)
    # Active zoom thumb at 1.8x
    draw.ellipse([width//2 + 30, height - 161, width//2 + 46, height - 145], fill=(52, 211, 153))
    draw.text((width//2 + 38, height - 172), "1.8x", fill=(52, 211, 153), font=font_sub, anchor="mm")
    
    # Bottom Controls Row
    # Back
    draw.text((50, height - 85), "BATAL", fill=(255,255,255), font=font_bold)
    # Shutter Button
    draw.ellipse([width//2 - 28, height - 110, width//2 + 28, height - 54], fill=(255, 255, 255), outline=(52, 211, 153), width=4)
    # Label
    draw.text((width//2, height - 124), "TELUNJUK KANAN", fill=(52, 211, 153), font=font_bold, anchor="mm")
    
    img.save(output_path, "PNG")

def create_report_mockup(output_path):
    width, height = 420, 800
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Phone
    draw_phone_frame(draw, width, height, dark_mode=False)
    
    # Fonts
    font_title = get_font(size=18)
    font_body = get_font(size=13)
    font_sub = get_font(size=11)
    font_bold = get_font(size=14)
    
    # Colors
    primary = (31, 71, 136) # Deep Slate Blue #1F4788
    text_dark = (15, 23, 42)
    text_muted = (100, 116, 139)
    bg_light = (248, 250, 252)
    
    # Header
    draw.text((width//2, 60), "Detail Hasil Analisis", fill=text_dark, font=font_title, anchor="mm")
    draw.text((width//2, 80), "Subjek: Jane Doe (Perempuan)", fill=text_muted, font=font_sub, anchor="mm")
    
    # Quality score alert box (Green semantic banner)
    draw.rounded_rectangle([36, 100, width-36, 155], radius=10, fill=(236, 253, 245), outline=(167, 243, 208), width=1)
    # Check circle representation
    draw.ellipse([50, 117, 70, 137], fill=(16, 185, 129))
    draw.line([56, 127, 60, 131], fill=(255,255,255), width=2)
    draw.line([60, 131, 66, 123], fill=(255,255,255), width=2)
    draw.text((80, 112), "Skor Kualitas Rata-rata: 92.5%", fill=(6, 95, 70), font=font_bold)
    draw.text((80, 130), "Kualitas gambar sidik jari sangat baik & tajam", fill=(6, 95, 70), font=font_sub)
    
    # Download PDF Button
    draw.rounded_rectangle([36, 172, width-36, 222], radius=10, fill=(31, 71, 136))
    draw.text((width//2, 197), "Unduh Laporan Hasil (PDF)", fill=(255, 255, 255), font=font_bold, anchor="mm")
    
    # Fingerprint detail section trigger button
    draw.rounded_rectangle([36, 238, width-36, 288], radius=10, fill=(255, 255, 255), outline=primary, width=2)
    draw.text((width//2, 263), "Lihat Detail Sidik Jari", fill=primary, font=font_bold, anchor="mm")
    
    # Bottom sheet simulation (Open state showing 10 fingers list)
    sheet_y = 310
    # Semi-transparent overlay behind bottom sheet
    draw.rectangle([18, sheet_y, width-18, height-18], fill=(241, 245, 249))
    # Bottom Sheet outline
    draw.rounded_rectangle([18, sheet_y, width-18, height-18], radius=24, fill=(255, 255, 255), outline=(226, 232, 240), width=2)
    
    # Sheet handle drag bar
    draw.rounded_rectangle([width//2 - 20, sheet_y+8, width//2 + 20, sheet_y+14], radius=3, fill=(226, 232, 240))
    
    draw.text((36, sheet_y + 24), "Daftar Pemindaian 10 Jari Klien", fill=text_dark, font=font_bold)
    draw.text((36, sheet_y + 40), "Metrik ridge & pola per jari terdeteksi secara offline", fill=text_muted, font=font_sub)
    
    # Jari Row 1
    row1_y = sheet_y + 60
    draw.line([36, row1_y, width-36, row1_y], fill=(241, 245, 249), width=1)
    draw.ellipse([36, row1_y+10, 60, row1_y+34], fill=(16, 185, 129)) # Green status
    draw.text((48, row1_y+22), "1", fill=(255,255,255), font=font_sub, anchor="mm")
    draw.text((70, row1_y+12), "Ibu Jari Kanan (R-Thumb)", fill=text_dark, font=font_body)
    draw.text((70, row1_y+28), "Kualitas: 94.2% | Pola: Whorl | Ridge: 18", fill=text_muted, font=font_sub)
    
    # Jari Row 2
    row2_y = row1_y + 45
    draw.line([36, row2_y, width-36, row2_y], fill=(241, 245, 249), width=1)
    draw.ellipse([36, row2_y+10, 60, row2_y+34], fill=(16, 185, 129)) # Green status
    draw.text((48, row2_y+22), "2", fill=(255,255,255), font=font_sub, anchor="mm")
    draw.text((70, row2_y+12), "Telunjuk Kanan (R-Index)", fill=text_dark, font=font_body)
    draw.text((70, row2_y+28), "Kualitas: 91.8% | Pola: Loop | Ridge: 15", fill=text_muted, font=font_sub)
    
    # Jari Row 3 (Orange status - Cukup)
    row3_y = row2_y + 45
    draw.line([36, row3_y, width-36, row3_y], fill=(241, 245, 249), width=1)
    draw.ellipse([36, row3_y+10, 60, row3_y+34], fill=(245, 158, 11)) # Orange status
    draw.text((48, row3_y+22), "3", fill=(255,255,255), font=font_sub, anchor="mm")
    draw.text((70, row3_y+12), "Jari Tengah Kanan (R-Middle)", fill=text_dark, font=font_body)
    draw.text((70, row3_y+28), "Kualitas: 72.4% | Pola: Loop | Ridge: 12", fill=text_muted, font=font_sub)
    
    # Alert footer inside Bottom Sheet
    draw.text((width//2, height-50), "Ketuk baris jari untuk detail pola diperbesar", fill=text_muted, font=font_sub, anchor="mm")
    
    img.save(output_path, "PNG")

def main():
    workspace_dir = r"E:\my project\ALLIA\FPA"
    images_dir = os.path.join(workspace_dir, "doc", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    print("Generating Login mockup...")
    create_login_mockup(os.path.join(images_dir, "login_mockup.png"))
    print("Generating Dashboard mockup...")
    create_dashboard_mockup(os.path.join(images_dir, "dashboard_mockup.png"))
    print("Generating Camera mockup...")
    create_camera_mockup(os.path.join(images_dir, "camera_mockup.png"))
    print("Generating Report mockup...")
    create_report_mockup(os.path.join(images_dir, "report_mockup.png"))
    
    print(f"Mockups successfully generated in {images_dir}")

if __name__ == '__main__':
    main()
