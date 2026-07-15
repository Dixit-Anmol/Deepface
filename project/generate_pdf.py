import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_pdf():
    # Setup directories
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "final_geeta.pdf")
    
    # Locate Windows Devanagari font to correctly render Sanskrit/Hindi glyphs
    font_name = "Helvetica"
    font_paths = [
        "C:\\Windows\\Fonts\\nirmala.ttf",
        "C:\\Windows\\Fonts\\mangal.ttf",
        "C:\\Windows\\Fonts\\kokila.ttf",
        "C:\\Windows\\Fonts\\utsah.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont('Devanagari', p))
                font_name = 'Devanagari'
                break
            except Exception:
                continue
                
    # Build Document layout
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
                            
    styles = getSampleStyleSheet()
    
    # Custom styles mapping the Devanagari Font
    shloka_style = ParagraphStyle(
        'ShlokaStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=16,
        spaceAfter=10
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        leading=22,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    story = []
    
    # Add title and guide description
    story.append(Paragraph("Srimad Bhagavad Gita - Chapter 16", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 16: Daivasura Sampad Vibhaga Yoga (The Divine and Demoniac Natures)", shloka_style))
    story.append(Spacer(1, 15))
    
    # ----------------------------------------------------
    # Verse 1-3 (Divine Qualities)
    # ----------------------------------------------------
    story.append(Paragraph("<b>[Verse 1-3]</b>", shloka_style))
    story.append(Paragraph("श्रीभगवानुवाच<br/>"
                           "अभयं सत्त्वसंशुद्धिर्ज्ञानयोगव्यवस्थितिः ।<br/>"
                           "दानं दमश्च यज्ञश्च स्वाध्यायस्तप आर्जवम् ॥ १ ॥<br/>"
                           "अहिंसा सत्यमक्रोधस्त्यागः शान्तिरपैशुनम् ।<br/>"
                           "दया भूतेष्वलोलुप्त्वं मार्दवं ह्रीरचापलम् ॥ २ ॥<br/>"
                           "तेजः क्षमा धृतिः शौचमद्रोहो नातिमानिता ।<br/>"
                           "भवन्ति सम्पदं दैवीमभिजातस्य भारत ॥ ३ ॥", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hindi Translation:</b>", shloka_style))
    story.append(Paragraph("श्री भगवान ने कहा— हे भरतवंशी अर्जुन! निर्भयता, अन्तःकरण की शुद्धि, ज्ञान और योग में दृढ़ स्थिति, दान, इंद्रियों पर नियंत्रण, यज्ञ, स्वाध्याय (वेदाध्ययन), तपस्या, सरलता, अहिंसा, सत्य, क्रोध न करना, त्याग, मानसिक शांति, निंदा न करना, जीवों के प्रति दया, आसक्तिहीनता, कोमलता, लज्जा, अकृत्रिमता, तेज, क्षमा, धैर्य, शुद्धि, द्रोह न करना तथा अहंकाररहित होना— ये सभी दिव्य गुण (दैवी संपदा) हैं, जो दैवी संपदा को लेकर उत्पन्न हुए व्यक्ति में पाए जाते हैं।", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>English Translation:</b>", shloka_style))
    story.append(Paragraph("The Supreme Lord said: Fearlessness, purity of mind, steadfastness in spiritual knowledge, charity, control of the senses, performance of sacrifice, study of the sacred scriptures, austerity, straightforwardness, nonviolence, truthfulness, freedom from anger, renunciation, peacefulness, restraint from speaking ill of others, compassion for all living beings, freedom from avarice, gentleness, modesty, freedom from fickleness, vigor, forgiveness, fortitude, cleanliness, and freedom from malice and egotism—these are the qualities of those born with a divine nature (Daivi Sampad).", shloka_style))
    story.append(Spacer(1, 20))
    
    # ----------------------------------------------------
    # Verse 4 (Demoniac Qualities)
    # ----------------------------------------------------
    story.append(Paragraph("<b>[Verse 4]</b>", shloka_style))
    story.append(Paragraph("दम्भो दर्पोऽभिमानश्च क्रोधः पारुष्यमेव च ।<br/>"
                           "अज्ञानं चाभिजातस्य पार्थ सम्पदमासुरीम् ॥ ४ ॥", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hindi Translation:</b>", shloka_style))
    story.append(Paragraph("हे पार्थ! पाखंड, घमंड, अभिमान, क्रोध, कठोरता और अज्ञान— ये सब आसुरी संपदा (दानवी स्वभाव) लेकर उत्पन्न हुए मनुष्य के लक्षण हैं।", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>English Translation:</b>", shloka_style))
    story.append(Paragraph("Hypocrisy, pride, arrogance, anger, harshness, and ignorance—these are the marks of those who are born with demoniac qualities (Asuri Sampad).", shloka_style))
    story.append(Spacer(1, 20))
    
    # ----------------------------------------------------
    # Verse 5 (Destiny of the Qualities)
    # ----------------------------------------------------
    story.append(Paragraph("<b>[Verse 5]</b>", shloka_style))
    story.append(Paragraph("दैवी सम्पद्विमोक्षाय निबन्धायासुरी मता ।<br/>"
                           "मा शुचः सम्पदं दैवीमभिजातौऽसि पाण्डव ॥ ५ ॥", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hindi Translation:</b>", shloka_style))
    story.append(Paragraph("दैवी संपदा मोक्ष (मुक्ति) के लिए और आसुरी संपदा बंधन (संसार चक्र) के लिए मानी जाती है। हे पाण्डव पुत्र अर्जुन! तुम शोक मत करो, क्योंकि तुम दैवी संपदा को लेकर ही उत्पन्न हुए हो।", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>English Translation:</b>", shloka_style))
    story.append(Paragraph("The divine qualities lead to liberation, while the demoniac qualities lead to bondage. Do not grieve, O Pandava, for you are born with divine qualities.", shloka_style))
    story.append(Spacer(1, 20))

    # ----------------------------------------------------
    # Verse 21 (Gates of Hell)
    # ----------------------------------------------------
    story.append(Paragraph("<b>[Verse 21]</b>", shloka_style))
    story.append(Paragraph("त्रिविधं नरकस्येदं द्वारं नाशनमात्मनः ।<br/>"
                           "कामः क्रोधस्तथा लोभस्तस्मादेतत्त्रयं त्यजेत् ॥ २१ ॥", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Hindi Translation:</b>", shloka_style))
    story.append(Paragraph("नरक के तीन द्वार हैं जो आत्मा का विनाश (अधोगति) करने वाले हैं— काम (वासना), क्रोध और लोभ। इसलिए मनुष्य को इन तीनों का त्याग कर देना चाहिए।", shloka_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>English Translation:</b>", shloka_style))
    story.append(Paragraph("There are three gates leading to the hell of self-destruction—lust, anger, and greed. Therefore, one must abandon these three.", shloka_style))
    story.append(Spacer(1, 20))
    
    # Callback to draw page decorations (headers, footers, page numbers) to verify extraction filters
    def add_page_decorations(canvas, doc):
        canvas.saveState()
        # Top Header line
        canvas.setFont(font_name, 9)
        canvas.drawString(72, 750, "Srimad Bhagavad Gita - Adhyay 16 Study Guide")
        canvas.setStrokeColorRGB(0.7, 0.7, 0.7)
        canvas.setLineWidth(0.5)
        canvas.line(72, 742, 540, 742)
        
        # Bottom Footer line & Page Number
        canvas.line(72, 55, 540, 55)
        canvas.drawString(72, 42, "Confidential - For Personal Study Only")
        canvas.drawRightString(540, 42, f"Page {doc.page}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    print(f"Generated test PDF successfully at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
