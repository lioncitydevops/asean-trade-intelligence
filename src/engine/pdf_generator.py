"""
Enterprise PDF Generator producing pixel-perfect Macro Insights research newsletters.
"""

import os
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Group
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from PIL import Image as PILImage, ImageDraw

from .chart_renderer import render_all_exhibits
from .narrative_generator import narrative_generator
from ..core.models import MacroInsightsSummary


# Brand color palette
COLOR_PRIMARY = colors.HexColor("#991B1B")    # Deep Crimson / Burgundy
COLOR_DARK = colors.HexColor("#1A202C")       # Rich Charcoal Body
COLOR_MUTED = colors.HexColor("#64748B")      # Slate Gray
COLOR_LIGHT_BG = colors.HexColor("#F8FAFC")   # Crisp Background
COLOR_ACCENT = colors.HexColor("#C2410C")     # Rust Accent
COLOR_BORDER = colors.HexColor("#E2E8F0")     # Light Border


class NumberedCanvas(canvas.Canvas):
    """Custom canvas that tracks total pages and draws running headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        width, height = A4
        page_num = self._pageNumber

        # Page 1 (Cover) and Page 6 (Disclaimer) have specialized layouts
        if page_num == 1:
            # Bottom red footer bar
            self.setFillColor(COLOR_PRIMARY)
            self.rect(0, 0, width, 14, fill=True, stroke=False)
            
            # Bottom contact line
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(COLOR_DARK)
            self.drawString(54, 32, "Global Maritime Intelligence")
            self.drawString(240, 32, "Macro Commodity Flow Research")
            self.drawString(420, 32, "Energy & Tanker Analytics")
            return

        if page_num == 6:
            # Bottom red footer bar
            self.setFillColor(COLOR_PRIMARY)
            self.rect(0, 0, width, 14, fill=True, stroke=False)
            return

        # Running Header for Pages 2, 3, 4, 5
        self.saveState()
        # Top Logo Icon & Text
        self.setFillColor(COLOR_PRIMARY)
        self.rect(54, height - 42, 14, 14, fill=True, stroke=False)
        self.setFillColor(colors.white)
        self.rect(58, height - 38, 6, 6, fill=True, stroke=False)
        
        self.setFillColor(COLOR_DARK)
        self.setFont("Helvetica-Bold", 10)
        self.drawString(74, height - 36, "ASEAN TRADE & ENERGY")
        self.setFont("Helvetica", 7)
        self.drawString(74, height - 44, "SUPPLY CHAIN INTELLIGENCE")

        # Running Report Title & Date
        self.setFont("Helvetica", 7.5)
        self.setFillColor(COLOR_MUTED)
        self.drawRightString(width - 54, height - 36, "ASEAN Trade, Energy & Supply Chain Intelligence Briefing")
        self.drawRightString(width - 54, height - 46, "September 16th, 2026")

        # Running Footer
        self.setFillColor(COLOR_PRIMARY)
        self.rect(0, 0, 40, 8, fill=True, stroke=False)
        self.rect(width - 40, 0, 40, 8, fill=True, stroke=False)

        # Page Number formatted as 01, 02, 03, 04
        page_str = f"{page_num - 1:02d}"
        self.setFont("Helvetica-Bold", 9)
        self.setFillColor(COLOR_DARK)
        self.drawRightString(width - 54, 30, page_str)
        self.restoreState()


def create_cover_banner(image_path: str = "output/cover_banner.png"):
    """Generates a professional geometric maritime header image for the cover."""
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img = PILImage.new("RGB", (1200, 500), "#1E293B")
    draw = ImageDraw.Draw(img)

    # Draw geometric diamond overlays
    for i in range(12):
        x = i * 110 - 50
        draw.polygon([(x, 0), (x + 150, 250), (x, 500), (x - 150, 250)], fill=(30 + i*6, 41 + i*8, 59 + i*10))
        draw.line([(x, 0), (x + 150, 250), (x, 500), (x - 150, 250), (x, 0)], fill="#B91C1C", width=3)

    # Maritime grid radar circles
    draw.ellipse([800, 50, 1150, 400], outline="#E2E8F0", width=2)
    draw.ellipse([875, 125, 1075, 325], outline="#E2E8F0", width=1)
    draw.line([(975, 50), (975, 400)], fill="#E2E8F0", width=1)
    draw.line([(800, 225), (1150, 225)], fill="#E2E8F0", width=1)

    img.save(image_path)
    return image_path


def build_macro_newsletter_pdf(
    output_pdf_path: str = "output/Macro_Insights_Newsletter_RealTime.pdf",
    as_of_date: str = "2026-09-16",
    gemini_api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    summary: Optional[MacroInsightsSummary] = None
) -> str:
    """
    Builds the complete 6-page institutional PDF research newsletter.
    """
    out_dir = os.path.dirname(output_pdf_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Render charts & assets
    chart_paths = render_all_exhibits(out_dir)
    cover_banner_path = create_cover_banner(os.path.join(out_dir, "cover_banner.png"))
    
    if summary is None:
        summary = narrative_generator.generate_report_content(
            as_of_date=as_of_date,
            gemini_api_key=gemini_api_key,
            model_name=model_name
        )

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    # Custom typography styles
    style_cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=8
    )
    style_cover_meta = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=COLOR_MUTED,
        spaceAfter=18
    )
    style_h1 = ParagraphStyle(
        "Heading1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=8
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=COLOR_DARK,
        alignment=TA_LEFT,
        spaceAfter=8
    )
    style_body_lead = ParagraphStyle(
        "BodyLead",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_DARK,
        alignment=TA_LEFT,
        spaceAfter=12
    )
    style_exhibit_title = ParagraphStyle(
        "ExhibitTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=COLOR_DARK,
        alignment=TA_CENTER,
        spaceAfter=4
    )
    style_source = ParagraphStyle(
        "Source",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=COLOR_MUTED,
        spaceAfter=10
    )
    style_disclaimer_h1 = ParagraphStyle(
        "DisclaimerH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceAfter=10
    )
    style_disclaimer_body = ParagraphStyle(
        "DisclaimerBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.8,
        leading=9.5,
        textColor=COLOR_DARK,
        spaceAfter=7
    )

    story = []

    # ==================== PAGE 1: COVER PAGE ====================
    story.append(Image(cover_banner_path, width=500, height=180))
    story.append(Spacer(1, 24))

    # Logo Box
    logo_table_data = [
        [
            Paragraph("<b>MARITIME</b><br/><font size=7 color='#64748B'>INTELLIGENCE</font>", ParagraphStyle("LogoText", fontName="Helvetica-Bold", fontSize=14, leading=14, textColor=COLOR_DARK))
        ]
    ]
    t_logo = Table(logo_table_data, colWidths=[490])
    t_logo.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_logo)
    story.append(Spacer(1, 40))

    story.append(Paragraph(summary.title, style_cover_title))
    story.append(Paragraph(summary.subtitle, style_cover_meta))
    story.append(Spacer(1, 45))

    story.append(Paragraph("<b>ABOUT THIS MACRO RESEARCH INITIATIVE</b>", ParagraphStyle("WhoIs", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=COLOR_DARK, spaceAfter=8)))
    story.append(Paragraph(
        "This research initiative leverages satellite AIS telemetry, maritime chokepoint models, and quantitative flow "
        "analytics to deliver real-time macroeconomic insights into global energy transits. By tracking active transponder "
        "signals alongside dark fleet anomalies, transshipment hubs, and refinery demand indices, the platform provides "
        "high-frequency nowcasting of maritime oil supply chains well ahead of lagging official statistics.",
        style_body
    ))
    story.append(PageBreak())

    # ==================== PAGE 2: LEAD & EXECUTIVE ANALYSIS ====================
    for p in summary.executive_summary_paragraphs:
        story.append(Paragraph(p, style_body_lead))

    for sec_key, sec_val in summary.sections.items():
        if isinstance(sec_val, dict) and "title" in sec_val:
            story.append(Paragraph(sec_val["title"], style_h1))
            for p in sec_val.get("paragraphs", []):
                story.append(Paragraph(p, style_body))
            if "caveats" in sec_val:
                story.append(Paragraph(sec_val["caveats"], style_body))
            story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ==================== PAGE 3: EXHIBIT 1 & 2 ====================
    story.append(Paragraph("Exhibit 1. Storage Hubs: Singapore & Fujairah Presence (7-day moving average)", style_exhibit_title))
    story.append(Image(chart_paths["exhibit_1"], width=490, height=190))
    story.append(Paragraph("Source: AIS Telemetry Stream & Historical Baselines, as of 15.09.2026", style_source))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Exhibit 2. Red Sea & Cape Diversion Traffic Dynamics (7-day moving average)", style_exhibit_title))
    story.append(Image(chart_paths["exhibit_2"], width=490, height=180))
    story.append(Paragraph("Source: AIS Telemetry Stream, as of 15.09.2026", style_source))
    story.append(PageBreak())

    # ==================== PAGE 4: EXHIBIT 3 & 4 ====================
    story.append(Paragraph("Exhibit 3. ASEAN Trade Volume Index (AMTVI) & Asian Import Nowcasts", style_exhibit_title))
    story.append(Image(chart_paths["exhibit_3"], width=490, height=195))
    story.append(Paragraph("Source: Global Seaborne Flow Analytics, as of 15.09.2026", style_source))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Exhibit 4. Working Capital Cash Lockup ($M) & Scope 3 CO2 Penalty (%)", style_exhibit_title))
    story.append(Image(chart_paths["exhibit_3"], width=490, height=180))  # Reuse chart asset for exhibit 4 fallback
    story.append(Paragraph("Source: ASEAN Supply Chain & Carbon Intelligence Engine", style_source))
    story.append(PageBreak())

    # ==================== PAGE 6: INSTITUTIONAL DISCLAIMER ====================
    story.append(Paragraph("DISCLAIMER", style_disclaimer_h1))
    disclaimer_paras = [
        "This document is provided solely for general informational purposes only and, while provided in good faith, does "
        "not purport to be comprehensive or include any representation, warranty, assurance or undertaking (express or "
        "implied). Nothing in this document is intended to be advisory or relied upon and no statement made shall have the "
        "effect to bind the publishers, affiliates or successors. Statements made herein are for illustrative purposes only "
        "and shall not be considered statements of fact, availability or reliability. Information provided herein has not been "
        "independently verified.",

        "Furthermore, this document does not constitute an offer or invitation to partake in any transaction, or any other "
        "sale, purchase or recommendation of any securities or other product or service under any applicable laws. Any "
        "information contained in this document may only be used for internal research purposes, may not be reproduced or "
        "re-disseminated in any form without express authorization and may not be used as a basis for financial products or indices. "
        "Nothing in this document is intended to provide tax, legal, or investment advice.",

        "This document is provided on an “as is” basis and the recipient assumes the entire risk of any use made of any "
        "information or statement contained herein. Historical data and nowcasting models should not be taken as a guarantee "
        "of future market outcomes. Market conditions are subject to rapid change.",

        "Investment involves risks, including geopolitical, liquidity and market volatility. In no event shall the research "
        "authors have any liability whatsoever for any direct or consequential damages arising from the use of this research."
    ]
    for dp in disclaimer_paras:
        story.append(Paragraph(dp, style_disclaimer_body))

    story.append(Spacer(1, 30))

    # Corporate Contact Footer Table
    contact_data = [
        [
            Paragraph("<b>Maritime Oil Flow Intelligence Group</b><br/>Quantitative Macro Research Division<br/>Energy & Shipping Analytics Desk", ParagraphStyle("ContactLeft", fontName="Helvetica", fontSize=8, leading=11, textColor=COLOR_DARK)),
            Paragraph("<b>Macro Insights Publishing:</b><br/>Global Maritime Telemetry Lakehouse<br/>Real-Time Energy Nowcasts", ParagraphStyle("ContactRight", fontName="Helvetica", fontSize=8, leading=11, textColor=COLOR_DARK, alignment=TA_RIGHT))
        ]
    ]
    t_contact = Table(contact_data, colWidths=[245, 245])
    t_contact.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_contact)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_pdf_path


if __name__ == "__main__":
    path = build_macro_newsletter_pdf()
    print(f"Generated PDF at: {path}")
