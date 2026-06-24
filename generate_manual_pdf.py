import os
import sys

def make_split_section(text_flowables, image_filename, workspace_dir, inch):
    img_path = os.path.join(workspace_dir, "doc", "images", image_filename)
    if os.path.exists(img_path):
        try:
            from reportlab.platypus import Table, TableStyle, Image as RLImage
            from reportlab.lib import colors
            
            img_widget = RLImage(img_path, width=1.85 * inch, height=3.52 * inch)
            
            # Nested table for Column 1 (Text flowables)
            text_table = Table([[f] for f in text_flowables], colWidths=[4.3 * inch])
            text_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            
            # Outer table side-by-side layout
            section_table = Table([[text_table, img_widget]], colWidths=[4.4 * inch, 2.1 * inch])
            section_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            return [section_table]
        except Exception as e:
            print(f"Warning embedding image {image_filename}: {e}")
    return text_flowables

def main():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
    except ImportError:
        print("Error: reportlab is not installed.")
        print("Please install it using: pip install reportlab")
        sys.exit(1)

    # Output file path in workspace root
    workspace_dir = r"E:\my project\ALLIA\FPA"
    output_filename = "user_manual.pdf"
    workspace_output = os.path.join(workspace_dir, output_filename)
    
    # Document Setup (Letter page has 8.5 x 11 inches)
    # 54pt margin = 0.75 inch. Total printable width = 7.0 inches.
    doc = SimpleDocTemplate(
        workspace_output,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Design Token Colors (Aligned with DESIGNS.md)
    primary_color = colors.HexColor('#1F4788')  # Deep Muted Slate Blue
    secondary_color = colors.HexColor('#0F172A')  # Slate 900
    accent_color = colors.HexColor('#00BCD4')  # Bright Cyan
    body_color = colors.HexColor('#334155')  # Slate 700
    border_color = colors.HexColor('#E2E8F0')  # Slate 200
    bg_light = colors.HexColor('#F8FAFC')
    
    # Typography Config
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=18
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=secondary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=14,
        textColor=body_color,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=body_style,
        fontSize=8.5,
        leading=12,
        spaceAfter=0
    )

    table_icon_style = ParagraphStyle(
        'TableIcon',
        parent=table_body_style,
        fontName='Helvetica-Bold',
        textColor=primary_color,
        alignment=1
    )

    story = []

    # Cover Banner (Accent Gradient bar simulated by nested Table)
    banner_text = Paragraph("<font color='white'><b>PANDUAN OPERASIONAL VISUAL</b></font>", ParagraphStyle('BText', parent=body_style, fontSize=9, alignment=1))
    banner_table = Table([[banner_text]], colWidths=[7.0 * inch])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))

    # Title Section
    story.append(Paragraph("Panduan Pengguna Lengkap: Tab Allia Finger", title_style))
    story.append(Paragraph("Sistem Pemindaian, Verifikasi, &amp; Analisis Kualitas Sidik Jari berbasis Pemrosesan Citra (OpenCV)", subtitle_style))
    story.append(Spacer(1, 10))

    # Bab 1: Akses Masuk & Beranda
    bab1_elements = [
        Paragraph("Bab 1: Akses Masuk (Login) &amp; Beranda", h1_style),
        Paragraph("<b>1.1 Login Pengguna:</b>", h2_style),
        Paragraph("Saat pertama kali membuka aplikasi, operator masuk menggunakan kredensial terdaftar:", body_style),
        Paragraph("&bull; Masukkan <b>Username</b> dan <b>Password</b> lembaga Anda.", bullet_style),
        Paragraph("&bull; Berikan centang pada kotak persetujuan Lisensi/Ketentuan.", bullet_style),
        Paragraph("&bull; Ketuk tombol melayang <b>'Masuk / Continue'</b>.", bullet_style),
        Paragraph("<b>1.2 Dashboard Utama:</b>", h2_style),
        Paragraph("Setelah masuk, Anda akan melihat sisa <b>Kredit Pemindaian Aktif</b> lembaga Anda. Kredit terpotong otomatis setiap kali satu laporan subjek berhasil diterbitkan.", body_style),
        Paragraph("Gunakan bilah navigasi bawah untuk berpindah tab:", body_style),
        Paragraph("&bull; <b>Beranda</b>: Statistik sesi, bento card, dan tombol scan baru.", bullet_style),
        Paragraph("&bull; <b>Sesi</b>: Daftar pemindaian yang berjalan atau tertunda.", bullet_style),
        Paragraph("&bull; <b>Tinjauan</b>: Antrean verifikasi sidik jari (khusus Admin).", bullet_style),
        Paragraph("&bull; <b>Riwayat</b>: Hasil laporan dan detail cetak sidik jari subjek.", bullet_style),
    ]
    story.extend(make_split_section(bab1_elements, "login_mockup.png", workspace_dir, inch))
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    # Bab 2: Sesi Pemindaian
    bab2_elements = [
        Paragraph("Bab 2: Sesi Pemindaian (Scan Session)", h1_style),
        Paragraph("Aplikasi menggunakan konsep <b>Sesi</b> untuk mengelompokkan 10 sidik jari subjek/klien secara aman:", body_style),
        Paragraph("<b>2.1 Membuat Sesi Baru:</b>", h2_style),
        Paragraph("Ketuk tombol terapung <b>'+ Mulai Pemindaian Baru'</b> di tab Beranda atau Sesi. Masukkan data identitas klien (Nama, ID, dll) lalu klik <b>'Buat Sesi'</b>.", body_style),
        Paragraph("<b>2.2 Melanjutkan Sesi Tertunda:</b>", h2_style),
        Paragraph("Jika baterai habis atau aplikasi tertutup, buka tab <b>Sesi</b>, temukan subjek dengan status draft/scanning, lalu klik <b>'Lanjutkan Pemindaian'</b> untuk melanjutkan dari jari terakhir.", body_style),
    ]
    
    # Collision callout text
    collision_text = (
        "<b>Pencegahan Tabrakan Akun (Collision Lock):</b> "
        "Satu sesi pemindaian dikunci ke satu perangkat aktif. Akses bersamaan pada "
        "sesi yang sama dari perangkat berbeda akan otomatis diblokir demi keamanan data."
    )
    p_collision = Paragraph(collision_text, ParagraphStyle('CollText', parent=body_style, fontSize=8.5, leading=12))
    t_collision = Table([[p_collision]], colWidths=[4.2 * inch])
    t_collision.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3.5, colors.HexColor('#EF4444')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    bab2_elements.append(Spacer(1, 6))
    bab2_elements.append(t_collision)
    
    story.extend(make_split_section(bab2_elements, "dashboard_mockup.png", workspace_dir, inch))
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    # Bab 3 & 4: Kamera & Kontrol Viewfinder
    bab3_4_elements = [
        Paragraph("Bab 3 &amp; 4: Alur Kamera &amp; Viewfinder Dashed", h1_style),
        Paragraph("<b>3.1 Wizard 10 Jari Berurutan:</b>", h2_style),
        Paragraph("Kamera akan memandu operator mengambil 10 sidik jari subjek dengan urutan: 5 jari tangan kanan (Ibu Jari s.d Kelingking), dilanjutkan 5 jari tangan kiri.", body_style),
        Paragraph("Posisikan <b>ujung jari</b> (bukan ruas tengah) tepat di dalam kotak panduan viewfinder.", body_style),
        Paragraph("<b>4.1 Panel Kontrol Kanan Atas:</b>", h2_style),
        Paragraph("Gunakan panel kontrol mengambang untuk meningkatkan ketajaman gambar:", body_style),
        Paragraph("&bull; <b>Senter/Torch (⚡)</b>: Aktifkan senter untuk memperjelas alur garis sidik jari.", bullet_style),
        Paragraph("&bull; <b>Transparansi (💧)</b>: Siklus overlay (Low: 0.05, Medium: 0.25, Standard: 0.45) jika layar terlalu gelap. Default dimulai dari tingkat **Low (0.05)** agar layar viewfinder terlihat jernih dan terang secara instan.", bullet_style),
        Paragraph("&bull; <b>Zoom Slider</b>: Gunakan zoom <b>1.8x - 2.0x</b> dengan jarak HP ke jari sekitar 10-15 cm untuk menghindari blur dan bayangan ponsel.", bullet_style),
        Paragraph("&bull; <b>Autofocus Manual</b>: Ketuk layar pada area jari untuk mengunci fokus lensa.", bullet_style),
    ]
    story.extend(make_split_section(bab3_4_elements, "camera_mockup.png", workspace_dir, inch))
    story.append(Spacer(1, 10))

    # Controls Table (Full width)
    table_data = [
        [
            Paragraph("Kontrol Kamera", table_header_style), 
            Paragraph("Ikon", table_header_style), 
            Paragraph("Manfaat Teknis (OpenCV)", table_header_style)
        ],
        [
            Paragraph("Siklus Transparansi", table_body_style),
            Paragraph("💧 (Tetes Air)", table_icon_style),
            Paragraph("Mengatur kegelapan overlay di sekitar panduan. Siklus: 0.05 (Default) &rarr; 0.45 &rarr; 0.25.", table_body_style)
        ],
        [
            Paragraph("Senter / Torch", table_body_style),
            Paragraph("⚡ (Senter)", table_icon_style),
            Paragraph("Pencahayaan konstan untuk mempertajam kontras guratan sidik jari subjek.", table_body_style)
        ],
        [
            Paragraph("Fokus Sentuh", table_body_style),
            Paragraph("Sentuh Layar", table_icon_style),
            Paragraph("Mengunci fokus lensa secara instan ke area sidik jari subjek. Otomatis reset dalam 3 detik.", table_body_style)
        ],
        [
            Paragraph("Zoom Kamera", table_body_style),
            Paragraph("Slider Bar", table_icon_style),
            Paragraph("Direkomendasikan 1.8x s.d 2.0x agar HP tidak terlalu dekat dan menghalangi cahaya senter.", table_body_style)
        ]
    ]

    control_table = Table(table_data, colWidths=[1.6 * inch, 1.1 * inch, 4.3 * inch])
    control_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light])
    ]))
    story.append(control_table)
    story.append(Spacer(1, 12))
    story.append(PageBreak())

    # Bab 5, 6 & 7: Evaluasi Kualitas & Cetak Detail
    bab5_7_elements = [
        Paragraph("Bab 5 &amp; 7: Evaluasi Kualitas &amp; Pratinjau Laporan", h1_style),
        Paragraph("<b>5.1 Evaluasi Kualitas Instan:</b>", h2_style),
        Paragraph("Setelah rana ditekan, aplikasi memotong gambar sidik jari secara otomatis sesuai panduan oval:", body_style),
        Paragraph("&bull; <b>Ikon Reload (Ulang)</b>: Membuang gambar dan kembali ke kamera jika buram.", bullet_style),
        Paragraph("&bull; <b>Ikon Centang (Gunakan)</b>: Mengunggah gambar ke server pemrosesan citra.", bullet_style),
        Paragraph("Jika algoritma OpenCV server mendeteksi kualitas buruk, unggahan ditolak dan kamera otomatis aktif kembali agar operator dapat mengambil ulang dengan cepat.", bullet_style),
        Paragraph("<b>6.1 Tinjauan Admin:</b>", h2_style),
        Paragraph("Sesi yang lengkap masuk antrean verifikasi Admin. Admin dapat menyetujui seluruh sesi atau meminta pengambilan ulang (retake) jari spesifik jika ada yang buram.", body_style),
        Paragraph("<b>7.1 Detail Sidik Jari Pasca-Laporan:</b>", h2_style),
        Paragraph("Setelah disetujui, operator mengeklik <b>'Buat Laporan'</b> (memotong 1 kredit) untuk menerbitkan PDF.", body_style),
        Paragraph("Operator dapat meninjau detail sidik jari subjek kapan saja di tab <b>Riwayat &rarr; Lihat Detail Sidik Jari</b>. Ketuk jari pada daftar bottom sheet untuk membuka pop-up pratinjau diperbesar beserta metrik pola dan ridge count.", body_style),
    ]
    story.extend(make_split_section(bab5_7_elements, "report_mockup.png", workspace_dir, inch))
    story.append(Spacer(1, 12))

    # Bab 8: FAQ (KeepTogether to prevent mid-FAQ page breaks)
    faq_story = []
    faq_story.append(Paragraph("Bab 8: Pertanyaan Umum (FAQ) &amp; Solusi Cepat", h1_style))
    faqs = [
        ("T: Mengapa kamera terlalu gelap saat pertama kali dibuka?", 
         "J: Aplikasi secara default menggunakan overlay gelap (Low: 0.05 opacity) di luar panduan untuk isolasi cahaya. Anda dapat mengubah kegelapan overlay dengan mengetuk ikon air (💧) di kanan atas."),
        ("T: Bagaimana cara mencegah hasil foto terdeteksi buram/blur?", 
         "J: Jaga jarak ponsel minimal 10 cm dari jari subjek. Atur zoom internal 1.8x s.d 2.0x and ketuk layar pada area jari untuk mengunci autofocus."),
        ("T: Saya tidak sengaja menutup aplikasi saat pemindaian berlangsung.", 
         "J: Semua jari yang sudah diunggah (centang hijau) aman di server. Cukup buka tab Sesi, klik subjek Anda, lalu klik 'Lanjutkan Pemindaian' untuk melanjutkan.")
    ]
    for q, a in faqs:
        faq_story.append(Paragraph(f"<b>{q}</b>", h2_style))
        faq_story.append(Paragraph(a, body_style))
        faq_story.append(Spacer(1, 3))
        
    story.append(KeepTogether(faq_story))

    # Build PDF
    doc.build(story)
    print(f"Success: PDF generated successfully at: {workspace_output}")

if __name__ == '__main__':
    main()
