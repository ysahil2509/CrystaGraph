"""
Script to generate a highly polished, professional 10-slide academic presentation (.pptx)
for B.Tech Project-4: 'CrystaGraph: AI-Driven Material Knowledge Mining from Scientific Tables'
BML Munjal University, Department of Computer Science & Engineering.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Initialize Presentation with 16:9 Widescreen dimensions
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6] # completely blank slide layout

# Color Palette Constants
COLOR_BG_WHITE = RGBColor(255, 255, 255)
COLOR_BG_SOFT = RGBColor(248, 250, 252) # #F8FAFC
COLOR_BG_CARD = RGBColor(241, 245, 249) # #F1F5F9
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
COLOR_CARD_ACCENT_BG = RGBColor(224, 242, 254) # #E0F2FE

COLOR_NAVY_DARK = RGBColor(15, 23, 42) # #0F172A
COLOR_PRIMARY_BLUE = RGBColor(30, 61, 89) # #1E3D59
COLOR_CYAN_ACCENT = RGBColor(2, 132, 199) # #0284C7
COLOR_TEAL_ACCENT = RGBColor(0, 168, 150) # #00A896
COLOR_MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
COLOR_TEXT_DARK = RGBColor(30, 41, 59) # #1E293B
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_AMBER = RGBColor(217, 119, 6) # #D97706
COLOR_PURPLE = RGBColor(124, 58, 237) # #7C3AED

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

def set_slide_background(slide, color=COLOR_BG_SOFT):
    """Sets a clean solid background color for the slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, category: str, title: str, subtitle: str = None):
    """Adds a standardized professional academic header banner to content slides."""
    # Category Pill Tag
    cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.4), Inches(0.32))
    cat_box.fill.solid()
    cat_box.fill.fore_color.rgb = COLOR_CARD_ACCENT_BG
    cat_box.line.color.rgb = COLOR_CYAN_ACCENT
    cat_box.line.width = Pt(1)
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.name = FONT_HEADING
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN_ACCENT
    p_cat.alignment = PP_ALIGN.CENTER

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.6))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    # Subtitle if provided
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.35))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = COLOR_MUTED_TEXT

    # Subtle horizontal divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.7), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER

def add_footer(slide, slide_num: int, citation: str = None):
    """Adds a standard academic footer with project attribution and optional citation."""
    # Bottom divider
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.01))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_CARD_BORDER
    div.line.color.rgb = COLOR_CARD_BORDER

    # Footer Text Left
    foot_left = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(6.5), Inches(0.4))
    tf_l = foot_left.text_frame
    p_l = tf_l.paragraphs[0]
    p_l.text = "CrystaGraph: AI-Driven Material Knowledge Mining | BML Munjal University — Project-4"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(9.5)
    p_l.font.color.rgb = COLOR_MUTED_TEXT

    # Citation if provided in center/left
    if citation:
        cite_box = slide.shapes.add_textbox(Inches(5.0), Inches(6.95), Inches(5.8), Inches(0.4))
        tf_c = cite_box.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = f"Source: {citation}"
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(9)
        p_c.font.italic = True
        p_c.font.color.rgb = COLOR_CYAN_ACCENT
        p_c.alignment = PP_ALIGN.RIGHT

    # Slide Number Right
    foot_right = slide.shapes.add_textbox(Inches(11.0), Inches(6.95), Inches(1.533), Inches(0.4))
    tf_r = foot_right.text_frame
    p_r = tf_r.paragraphs[0]
    p_r.text = f"Slide {slide_num} of 10"
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(9.5)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_PRIMARY_BLUE
    p_r.alignment = PP_ALIGN.RIGHT

def create_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER, border_width=1):
    """Creates a stylized background card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

# ==============================================================================
# SLIDE 1 — TITLE SLIDE
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, COLOR_BG_WHITE)

# Decorative top-right technical accent badge
accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
accent_bar.line.fill.background()

# Hero Banner Card
hero_card = create_card(s1, Inches(0.8), Inches(0.6), Inches(11.733), Inches(3.2), bg_color=COLOR_PRIMARY_BLUE, border_color=None)

# Tag inside hero
tag_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.9), Inches(3.8), Inches(0.35))
tag_shape.fill.solid()
tag_shape.fill.fore_color.rgb = RGBColor(14, 116, 144) # dark cyan
tag_shape.line.color.rgb = COLOR_CYAN_ACCENT
tag_shape.line.width = Pt(1)
tf_tag = tag_shape.text_frame
p_t = tf_tag.paragraphs[0]
p_t.text = "B.TECH CSE — PROJECT-4 RESEARCH PROPOSAL"
p_t.font.name = FONT_HEADING
p_t.font.size = Pt(10)
p_t.font.bold = True
p_t.font.color.rgb = COLOR_WHITE
p_t.alignment = PP_ALIGN.CENTER

# Main Title
title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.35), Inches(10.9), Inches(1.3))
tf_title = title_box.text_frame
tf_title.word_wrap = True
p_main = tf_title.paragraphs[0]
p_main.text = "CrystaGraph: AI-Driven Material Knowledge\nMining from Scientific Tables"
p_main.font.name = FONT_HEADING
p_main.font.size = Pt(28)
p_main.font.bold = True
p_main.font.color.rgb = COLOR_WHITE

# Subtitle
sub_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.75), Inches(10.9), Inches(0.6))
tf_sub = sub_box.text_frame
p_sub = tf_sub.paragraphs[0]
p_sub.text = "Comprehensive Literature Review, Research Gap Analysis & Proposed Methodology"
p_sub.font.name = FONT_BODY
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = COLOR_CARD_ACCENT_BG

# Group Members Section Card
mem_card = create_card(s1, Inches(0.8), Inches(4.0), Inches(6.8), Inches(2.6), bg_color=COLOR_BG_CARD, border_color=COLOR_CARD_BORDER)

mem_title = s1.shapes.add_textbox(Inches(1.1), Inches(4.15), Inches(6.2), Inches(0.35))
p_mt = mem_title.text_frame.paragraphs[0]
p_mt.text = "PROJECT TEAM MEMBERS"
p_mt.font.name = FONT_HEADING
p_mt.font.size = Pt(11)
p_mt.font.bold = True
p_mt.font.color.rgb = COLOR_PRIMARY_BLUE

# Member pills grid (2x2)
members = [
    ("Sahil Yadav", "230860"),
    ("Ayush Yadav", "230517"),
    ("Nitin Yadav", "230771"),
    ("Ghoda", "2306969")
]
for idx, (m_name, m_roll) in enumerate(members):
    col_idx = idx % 2
    row_idx = idx // 2
    m_left = Inches(1.1 + col_idx * 3.1)
    m_top = Inches(4.6 + row_idx * 0.9)
    
    p_box = create_card(s1, m_left, m_top, Inches(2.9), Inches(0.75), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
    tb = s1.shapes.add_textbox(m_left + Inches(0.1), m_top + Inches(0.08), Inches(2.7), Inches(0.6))
    tf_m = tb.text_frame
    p1 = tf_m.paragraphs[0]
    p1.text = f"• {m_name}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_DARK
    
    p2 = tf_m.add_paragraph()
    p2.text = f"   Roll No: {m_roll}"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10)
    p2.font.color.rgb = COLOR_MUTED_TEXT

# Institution & Department Card Right
inst_card = create_card(s1, Inches(7.8), Inches(4.0), Inches(4.733), Inches(2.6), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)

inst_tb = s1.shapes.add_textbox(Inches(8.1), Inches(4.3), Inches(4.133), Inches(2.0))
tf_inst = inst_tb.text_frame
tf_inst.word_wrap = True

pi1 = tf_inst.paragraphs[0]
pi1.text = "ACADEMIC INSTITUTION"
pi1.font.name = FONT_HEADING
pi1.font.size = Pt(10)
pi1.font.bold = True
pi1.font.color.rgb = COLOR_CYAN_ACCENT

pi2 = tf_inst.add_paragraph()
pi2.text = "BML Munjal University"
pi2.font.name = FONT_HEADING
pi2.font.size = Pt(18)
pi2.font.bold = True
pi2.font.color.rgb = COLOR_NAVY_DARK
pi2.space_before = Pt(4)

pi3 = tf_inst.add_paragraph()
pi3.text = "Department of Computer Science & Engineering\nSchool of Engineering & Technology\nAcademic Year: 2025–2026"
pi3.font.name = FONT_BODY
pi3.font.size = Pt(11.5)
pi3.font.color.rgb = COLOR_TEXT_DARK
pi3.space_before = Pt(6)

add_footer(s1, 1)

# ==============================================================================
# SLIDE 2 — BACKGROUND & MOTIVATION
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_BG_SOFT)
add_header(s2, "Context & Motivation", "Background & Motivation", "The Critical Need for Automated Knowledge Mining from Tabular Scientific Literature")

# Left Column Card: Scientific Table Wealth
c1 = create_card(s2, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8), bg_color=COLOR_WHITE)
tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.2), Inches(4.5))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "Materials Literature Goldmine in Tables"
p.font.name = FONT_HEADING
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

p = tf1.add_paragraph()
p.text = "Materials science research generates a massive volume of empirical data. Over 80% of experimental measurements are published inside tables rather than text:"
p.font.name = FONT_BODY
p.font.size = Pt(11.5)
p.font.color.rgb = COLOR_TEXT_DARK
p.space_before = Pt(6)

items = [
    ("Material Names & Phases", "e.g., Ti-6Al-4V, BaTiO3, LiFePO4, high-entropy alloys"),
    ("Chemical Compositions", "Elemental & oxide mass/atomic fractions (wt.%, at.%, mol%)"),
    ("Target Properties", "Yield strength, hardness, density, dielectric constant, Tc"),
    ("Numerical Values & Units", "Quantitative data with scientific units (MPa, GPa, g/cm³, K)"),
    ("Experimental Conditions", "Sintering temperatures, strain rates, dopant concentrations")
]
for title_item, desc_item in items:
    p = tf1.add_paragraph()
    p.text = f"• {title_item}: "
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)
    # Add non-bold description
    p_run = p.add_run()
    p_run.text = desc_item
    p_run.font.bold = False
    p_run.font.color.rgb = COLOR_MUTED_TEXT

# Right Column Top Card: Current Bottlenecks
c2 = create_card(s2, Inches(6.7), Inches(1.9), Inches(5.833), Inches(2.7), bg_color=COLOR_WHITE)
tb2 = s2.shapes.add_textbox(Inches(6.9), Inches(2.05), Inches(5.4), Inches(2.4))
tf2 = tb2.text_frame
tf2.word_wrap = True

p = tf2.paragraphs[0]
p.text = "Key Challenges in Table Mining"
p.font.name = FONT_HEADING
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

challenges = [
    "High Literature Volume: Millions of papers published in heterogeneous layouts.",
    "Complex Topology: Multi-row headers, spanning cells (morerows, colspans).",
    "Manual Bottleneck: Human extraction is slow, costly, and error-prone.",
    "Implicit Relations: Compositions in Table 1 and properties in Table 2 are unlinked.",
    "Data Silos: Information is hard to search, cross-reference, and compare across papers."
]
for ch in challenges:
    p = tf2.add_paragraph()
    p.text = f"⚠ {ch}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(3)

# Right Column Bottom Card: Core Transformation Concept
c3 = create_card(s2, Inches(6.7), Inches(4.75), Inches(5.833), Inches(1.95), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb3 = s2.shapes.add_textbox(Inches(6.9), Inches(4.85), Inches(5.4), Inches(1.75))
tf3 = tb3.text_frame
tf3.word_wrap = True

p = tf3.paragraphs[0]
p.text = "CORE TRANSFORMATION PARADIGM"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

p = tf3.add_paragraph()
p.text = "Scientific Papers  ➔  Tables  ➔  Structured Knowledge  ➔  Knowledge Graph"
p.font.name = FONT_HEADING
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY_DARK
p.space_before = Pt(3)

p = tf3.add_paragraph()
p.text = "“Materials-domain NLP research such as MatSciBERT demonstrates the importance of domain-specific language understanding for materials information extraction.”"
p.font.name = FONT_BODY
p.font.size = Pt(9.5)
p.font.italic = True
p.font.color.rgb = COLOR_TEXT_DARK
p.space_before = Pt(4)

add_footer(s2, 2, "Gupta et al., npj Computational Materials (2022)")

# ==============================================================================
# SLIDE 3 — PROBLEM STATEMENT
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, COLOR_BG_SOFT)
add_header(s3, "Problem Definition", "Problem Statement & Research Questions", "Addressing the Technical Bottlenecks of Unstructured Tabular Materials Data")

# Top Highlight Card: Formal Problem Statement
c_top = create_card(s3, Inches(0.8), Inches(1.9), Inches(11.733), Inches(1.4), bg_color=COLOR_PRIMARY_BLUE, border_color=None)
tb_top = s3.shapes.add_textbox(Inches(1.1), Inches(2.05), Inches(11.1), Inches(1.1))
tf_top = tb_top.text_frame
tf_top.word_wrap = True

p = tf_top.paragraphs[0]
p.text = "FORMAL PROBLEM STATEMENT"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_CARD_ACCENT_BG

p = tf_top.add_paragraph()
p.text = "“Scientific materials knowledge is distributed across research papers and is frequently presented in heterogeneous tables containing compositions, properties, units and experimental information. Extracting, linking and exploring this information across multiple papers remains challenging.”"
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(3)

# 6 Key Obstacles Grid (3 columns x 2 rows)
obstacles = [
    ("1. Heterogeneous Table Formats", "Different publishers use varied XML/HTML schemas (Elsevier, JATS, standard HTML) with complex spanning cells."),
    ("2. Entity Alias Diversity", "Material names appear as trade codes (Ti-6Al-4V), acronyms (LFP, PZT), or chemical stoichiometry (LiFePO4)."),
    ("3. Mixed Headers & Embedded Units", "Table columns combine property names, fractions (wt.%, mol%), and physical units (MPa, g/cm³) in single text headers."),
    ("4. Implicit Multi-Table Relationships", "Compositions reported in Table 1 and mechanical properties in Table 2 for the same alloy are not explicitly linked."),
    ("5. Query & Comparison Barriers", "Researchers cannot easily search across multi-paper tables to compare property trade-offs or alloy performance."),
    ("6. Siloed Research Tooling", "Existing methods focus on isolated extraction algorithms without an integrated end-user exploration platform.")
]

for idx, (ob_title, ob_desc) in enumerate(obstacles):
    col = idx % 3
    row = idx // 3
    left = Inches(0.8 + col * 3.98)
    top = Inches(3.45 + row * 1.55)
    
    card_ob = create_card(s3, left, top, Inches(3.78), Inches(1.45), bg_color=COLOR_WHITE)
    tb_ob = s3.shapes.add_textbox(left + Inches(0.12), top + Inches(0.08), Inches(3.54), Inches(1.3))
    tf_o = tb_ob.text_frame
    tf_o.word_wrap = True
    
    p = tf_o.paragraphs[0]
    p.text = ob_title
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE
    
    p = tf_o.add_paragraph()
    p.text = ob_desc
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2)

# Central Research Question Callout Banner
c_rq = create_card(s3, Inches(0.8), Inches(5.15), Inches(11.733), Inches(1.55), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT, border_width=1.5)
tb_rq = s3.shapes.add_textbox(Inches(1.1), Inches(5.25), Inches(11.1), Inches(1.35))
tf_rq = tb_rq.text_frame
tf_rq.word_wrap = True

p = tf_rq.paragraphs[0]
p.text = "🎯 CORE RESEARCH QUESTION"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

p = tf_rq.add_paragraph()
p.text = "“How can AI-based techniques be used to extract, structure, link and visualize material knowledge from scientific tables across multiple research papers?”"
p.font.name = FONT_HEADING
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY_DARK
p.space_before = Pt(3)

add_footer(s3, 3)

# ==============================================================================
# SLIDE 4 — LITERATURE REVIEW: EXISTING RESEARCH
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, COLOR_BG_SOFT)
add_header(s4, "Literature Review", "Literature Review: State-of-the-Art Research", "Evolution from Domain NLP and Table Extractors to GNNs and Knowledge Graphs (2022–2025)")

# 6 Key Papers Timeline Layout (2 rows of 3 cards with connecting headers)
papers_lit = [
    {
        "year": "2022",
        "title": "MatSciBERT",
        "authors": "Gupta et al. (2022)",
        "focus": "Domain-Specific Materials Language Model",
        "desc": "Pretrained BERT on large materials science literature corpus. Demonstrates importance of domain embeddings for materials entity recognition.",
        "tag": "Domain NLP"
    },
    {
        "year": "2023",
        "title": "Zhang et al.",
        "authors": "Zhang et al., Digital Discovery (2023)",
        "focus": "Integrated Text & Table Mining",
        "desc": "Pioneered pipeline combining textual paragraph mining with heuristic tabular data extraction for specific materials science publication sets.",
        "tag": "Text + Tables"
    },
    {
        "year": "2024",
        "title": "Materials Tetrahedron",
        "authors": "Digital Discovery Perspective (2024)",
        "focus": "Knowledge Distribution Challenges",
        "desc": "Highlights how composition, crystal structure, synthesis processing, and properties are deeply fragmented across scientific literature.",
        "tag": "Informatics"
    },
    {
        "year": "2024/25",
        "title": "MaTableGPT",
        "authors": "Yi et al. (2024/2025)",
        "focus": "LLM/GPT-Based Table Extraction",
        "desc": "Investigates prompt-based LLM extractors for parsing material tables. Flexible across layouts but faces token cost and hallucination constraints.",
        "tag": "LLM Prompting"
    },
    {
        "year": "2025",
        "title": "MatSKRAFT",
        "authors": "Hira et al. (2025)",
        "focus": "Constraint-Driven GNN Extraction",
        "desc": "Graph-based representation enforcing structural & stoichiometric constraints via GNNs for composition-property extraction from research tables.",
        "tag": "GNN & Rules"
    },
    {
        "year": "2025",
        "title": "Dreger et al.",
        "authors": "Dreger et al., Adv. Intell. Syst. (2025)",
        "focus": "LLM-Assisted Knowledge Graphs",
        "desc": "Converts scientific tables into structured knowledge graphs using LLMs and ontology mapping. Tested on focused heterogeneous collections.",
        "tag": "Knowledge Graph"
    }
]

for idx, p_info in enumerate(papers_lit):
    col = idx % 3
    row = idx // 3
    left = Inches(0.8 + col * 3.98)
    top = Inches(1.9 + row * 2.35)
    
    card_p = create_card(s4, left, top, Inches(3.78), Inches(2.2), bg_color=COLOR_WHITE)
    
    # Year Badge
    badge = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.15), top + Inches(0.12), Inches(0.8), Inches(0.28))
    badge.fill.solid()
    badge.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    badge.line.fill.background()
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = p_info["year"]
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(9)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Tag Badge Right
    tag_b = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(2.45), top + Inches(0.12), Inches(1.18), Inches(0.28))
    tag_b.fill.solid()
    tag_b.fill.fore_color.rgb = COLOR_CARD_ACCENT_BG
    tag_b.line.color.rgb = COLOR_CYAN_ACCENT
    tag_b.line.width = Pt(0.75)
    tf_tb = tag_b.text_frame
    p_tb = tf_tb.paragraphs[0]
    p_tb.text = p_info["tag"]
    p_tb.font.name = FONT_HEADING
    p_tb.font.size = Pt(8.5)
    p_tb.font.bold = True
    p_tb.font.color.rgb = COLOR_CYAN_ACCENT
    p_tb.alignment = PP_ALIGN.CENTER

    # Text Box
    tb = s4.shapes.add_textbox(left + Inches(0.12), top + Inches(0.42), Inches(3.54), Inches(1.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = p_info["title"]
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    p = tf.add_paragraph()
    p.text = p_info["focus"]
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL_ACCENT
    p.space_before = Pt(1)

    p = tf.add_paragraph()
    p.text = p_info["desc"]
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2)

# Bottom Takeaway Box
c_bot = create_card(s4, Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.42), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb_bot = s4.shapes.add_textbox(Inches(1.0), Inches(6.47), Inches(11.3), Inches(0.38))
tf_bot = tb_bot.text_frame
p = tf_bot.paragraphs[0]
p.text = "📈 Literature Trend: Domain-specific NLP (2022) ➔ Text/Table Mining (2023) ➔ LLM Extraction (2024) ➔ Graph-based GNNs (2025) ➔ Knowledge Graphs (2025)."
p.font.name = FONT_BODY
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

add_footer(s4, 4, "Gupta et al. (2022) | Zhang et al. (2023) | Hira et al. (2025)")

# ==============================================================================
# SLIDE 5 — LITERATURE REVIEW COMPARISON TABLE
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_BG_SOFT)
add_header(s5, "Literature Analysis", "Literature Review Comparison", "Comparative Matrix of Existing Materials Information Extraction Methodologies")

# Create Table Shape
rows = 6
cols = 6
top_t = Inches(1.9)
left_t = Inches(0.8)
width_t = Inches(11.733)
height_t = Inches(4.3)

table_shape = s5.shapes.add_table(rows, cols, left_t, top_t, width_t, height_t)
table = table_shape.table

# Set Column Widths
table.columns[0].width = Inches(1.6) # Research
table.columns[1].width = Inches(0.9) # Year
table.columns[2].width = Inches(1.8) # Technique
table.columns[3].width = Inches(1.3) # Input
table.columns[4].width = Inches(3.3) # Main Contribution
table.columns[5].width = Inches(2.833) # Limitation / Gap

headers = ["Research Work", "Year", "Core Technique", "Input Modality", "Main Contribution", "Identified Limitation / Gap"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

table_data = [
    ("MatSciBERT\n(Gupta et al.)", "2022", "Domain-Specific\nBERT Model", "Scientific Text\n(Literature)", "Pioneered materials-domain language representations for NLP entity recognition.", "Primarily focused on narrative text; lacks 2D structural awareness of tables."),
    ("Zhang et al.", "2023", "NLP + Heuristic\nTable Extraction", "Text + Research\nTables", "Combined text and tabular extraction for materials literature mining.", "Specific extraction pipeline; lacks general interactive exploration and graph querying."),
    ("MaTableGPT\n(Yi et al.)", "2024/25", "Prompt-Based\nGPT / LLMs", "Materials\nTables", "Flexible zero-shot extraction across diverse scientific table layouts.", "Inference cost, output formatting variance, and potential LLM hallucinations."),
    ("MatSKRAFT\n(Hira et al.)", "2025", "Constraint-Driven\nGNNs + Rules", "Scientific\nTables", "Large-scale composition and property extraction using graph constraints.", "Research-oriented complex pipeline; lacks integrated user-facing exploration platform."),
    ("Dreger et al.", "2025", "LLM + Rule-Based\nKnowledge Graph", "Materials\nTables", "Converts tabular materials data into structured semantic knowledge graphs.", "Evaluated on relatively small table set; limited multi-paper synthesis and discovery.")
]

for row_idx, row_content in enumerate(table_data):
    for col_idx, cell_value in enumerate(row_content):
        cell = table.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE if row_idx % 2 == 0 else COLOR_BG_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = cell_value
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = COLOR_TEXT_DARK
        if col_idx == 0:
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY_DARK

# Bottom Takeaway Card
c_take = create_card(s5, Inches(0.8), Inches(6.3), Inches(11.733), Inches(0.55), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb_t = s5.shapes.add_textbox(Inches(0.95), Inches(6.32), Inches(11.4), Inches(0.5))
tf_t = tb_t.text_frame
tf_t.word_wrap = True
p = tf_t.paragraphs[0]
p.text = "💡 Research Takeaway: Existing works provide strong individual components. CrystaGraph focuses on integrating multi-paper extraction, structured relational storage, relationship linking, and interactive graph exploration into a unified platform."
p.font.name = FONT_BODY
p.font.size = Pt(9.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

add_footer(s5, 5)

# ==============================================================================
# SLIDE 6 — RESEARCH GAP
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_BG_SOFT)
add_header(s6, "Research Opportunity", "Identified Research Gaps", "Bridging Isolated Extraction Modules with an Integrated Multi-Paper Knowledge Platform")

# 5 Gap Cards (Left Side 5 Gaps)
gaps = [
    ("1. Fragmented Extraction Approaches", "Current research concentrates on isolated individual tasks—either pure text extraction, isolated table parsing, or standalone graph schemas without an end-to-end bridge."),
    ("2. Lack of Multi-Paper Synthesis", "Limited ability in existing pipelines to aggregate, cross-reference, and deduplicate material compositions and properties across a multi-paper corpus."),
    ("3. Absence of User-Centric Exploration", "Research-oriented extraction scripts lack intuitive, accessible graphical user interfaces for materials scientists and student researchers."),
    ("4. Unlinked Entity-Property Knowledge", "Material compositions in Table 1 and experimental properties in Table 2 within the same paper often remain unlinked in isolated tables."),
    ("5. Missing End-to-End Workflow", "Need for a seamless pipeline: Raw XML/PDF ➔ Table Extraction ➔ Entity Normalization ➔ Relation Linking ➔ SQLite Store ➔ Knowledge Graph ➔ UI.")
]

left_card = create_card(s6, Inches(0.8), Inches(1.9), Inches(6.8), Inches(4.85), bg_color=COLOR_WHITE)
tb_g = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(6.4), Inches(4.6))
tf_g = tb_g.text_frame
tf_g.word_wrap = True

p = tf_g.paragraphs[0]
p.text = "Identified Gaps in Current Literature"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

for title_gap, desc_gap in gaps:
    p = tf_g.add_paragraph()
    p.text = f"• {title_gap}: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)
    
    pr = p.add_run()
    pr.text = desc_gap
    pr.font.bold = False
    pr.font.size = Pt(9.5)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Right Side: Visual Contrast Card (Existing vs CrystaGraph Proposed)
right_top = create_card(s6, Inches(7.8), Inches(1.9), Inches(4.733), Inches(2.3), bg_color=COLOR_BG_CARD, border_color=COLOR_CARD_BORDER)
tb_rt = s6.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.333), Inches(2.1))
tf_rt = tb_rt.text_frame
tf_rt.word_wrap = True

p = tf_rt.paragraphs[0]
p.text = "CURRENT RESEARCH LANDSCAPE"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

cur_items = ["• Isolated text NLP models", "• Single-paper table extractors", "• Complex CLI-only research scripts", "• Disconnected property measurements"]
for ci in cur_items:
    p = tf_rt.add_paragraph()
    p.text = ci
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2)

# Right Bottom: CrystaGraph Solution Card
right_bot = create_card(s6, Inches(7.8), Inches(4.35), Inches(4.733), Inches(2.4), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT, border_width=1.5)
tb_rb = s6.shapes.add_textbox(Inches(8.0), Inches(4.45), Inches(4.333), Inches(2.2))
tf_rb = tb_rb.text_frame
tf_rb.word_wrap = True

p = tf_rb.paragraphs[0]
p.text = "CRYSTAGRAPH PROPOSED PARADIGM"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

prop_items = ["✔ Multi-Paper Automated Table Ingestion", "✔ Associative Composition-Property Linking", "✔ Structured Relational SQLite Knowledge Base", "✔ Interactive NetworkX / Plotly Graph Explorer", "✔ Web-Based Streamlit Analytics Platform"]
for pi in prop_items:
    p = tf_rb.add_paragraph()
    p.text = pi
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(2)

add_footer(s6, 6)

# ==============================================================================
# SLIDE 7 — OBJECTIVES
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_BG_SOFT)
add_header(s7, "Project Scope", "Project Objectives", "Four Core Architectural Pillars of the CrystaGraph Mining Platform")

# 4 Pillars Grid (2x2)
pillars = [
    {
        "title": "1. DATA INGESTION & PARSING",
        "color": COLOR_PRIMARY_BLUE,
        "accent": COLOR_CARD_ACCENT_BG,
        "objectives": [
            "Ingest multiple authentic scientific research XML/PDF papers.",
            "Detect and parse complex XML table nodes (<ce:table>, <tgroup>, <tbody>).",
            "Resolve multi-row headers and spanning cells (morerows, namest/nameend).",
            "Preserve table captions, footers, and experimental test conditions."
        ]
    },
    {
        "title": "2. AI & ENTITY MINING",
        "color": COLOR_TEAL_ACCENT,
        "accent": RGBColor(230, 255, 250),
        "objectives": [
            "Identify material entity names, alloys, formulas, and trade codes.",
            "Extract chemical compositions and fraction units (wt.%, at.%, mol%).",
            "Extract mechanical, thermal, electrical, and electrochemical properties.",
            "Standardize numerical values, scientific exponents, and units (MPa, GPa, g/cm³)."
        ]
    },
    {
        "title": "3. KNOWLEDGE LINKING & STORAGE",
        "color": COLOR_PURPLE,
        "accent": RGBColor(245, 243, 255),
        "objectives": [
            "Associatively link composition profiles with measured property values.",
            "Map inter-table relationships within the same research document.",
            "Design and populate a structured relational SQLite knowledge base.",
            "Construct a multi-relational NetworkX Knowledge Graph (Paper➔Table➔Mat➔Prop)."
        ]
    },
    {
        "title": "4. PLATFORM & VISUALIZATION",
        "color": COLOR_CYAN_ACCENT,
        "accent": COLOR_CARD_ACCENT_BG,
        "objectives": [
            "Develop an interactive multi-page Streamlit web platform.",
            "Provide real-time search across materials, compositions, and properties.",
            "Render interactive 2D/3D knowledge graph visualizers with Plotly.",
            "Enable structured data downloads in standardized CSV and JSON formats."
        ]
    }
]

for idx, p_info in enumerate(pillars):
    col = idx % 2
    row = idx // 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.9 + row * 2.4)
    
    card_pil = create_card(s7, left, top, Inches(5.78), Inches(2.25), bg_color=COLOR_WHITE)
    
    # Pillar Header Ribbon
    ribbon = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.12), top + Inches(0.12), Inches(5.54), Inches(0.35))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = p_info["accent"]
    ribbon.line.color.rgb = p_info["color"]
    ribbon.line.width = Pt(1)
    tf_rib = ribbon.text_frame
    p = tf_rib.paragraphs[0]
    p.text = p_info["title"]
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = p_info["color"]
    p.alignment = PP_ALIGN.CENTER

    # Content
    tb_c = s7.shapes.add_textbox(left + Inches(0.15), top + Inches(0.5), Inches(5.48), Inches(1.65))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    for o_idx, obj in enumerate(p_info["objectives"]):
        p = tf_c.paragraphs[0] if o_idx == 0 else tf_c.add_paragraph()
        p.text = f"✔ {obj}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_before = Pt(2)

add_footer(s7, 7)

# ==============================================================================
# SLIDE 8 — PROPOSED METHODOLOGY
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_BG_SOFT)
add_header(s8, "System Architecture", "Proposed Methodology & Pipeline", "10-Stage End-to-End Workflow from Scientific XML Papers to Knowledge Graph & Web UI")

# 10 Stages Process Flow (2 rows of 5 cards with sequence numbers)
stages = [
    ("Stage 1", "Scientific Papers", "Elsevier / JATS XML multi-paper input"),
    ("Stage 2", "XML Parsing", "Extract title, DOI, abstract, sections"),
    ("Stage 3", "MIT Table Extractor", "Parse tgroup, thead, tbody, spans"),
    ("Stage 4", "Table Normalization", "Unicode cleaning & formula preservation"),
    ("Stage 5", "Composition Mining", "Extract wt%, at%, mol% & oxides"),
    ("Stage 6", "Property Extraction", "Mine values & normalize units (MPa)"),
    ("Stage 7", "Relation Linking", "Map composition-property pairs"),
    ("Stage 8", "SQLite Database", "Persist indexed relational schema"),
    ("Stage 9", "Knowledge Graph", "Construct multi-relational network"),
    ("Stage 10", "Streamlit UI", "Interactive dashboard & analytics")
]

for idx, (st_num, st_title, st_desc) in enumerate(stages):
    col = idx % 5
    row = idx // 5
    left = Inches(0.8 + col * 2.38)
    top = Inches(1.9 + row * 2.1)
    
    card_st = create_card(s8, left, top, Inches(2.23), Inches(1.95), bg_color=COLOR_WHITE)
    
    # Step Number Pill
    st_pill = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.1), top + Inches(0.1), Inches(2.03), Inches(0.28))
    st_pill.fill.solid()
    st_pill.fill.fore_color.rgb = COLOR_PRIMARY_BLUE if row == 0 else COLOR_TEAL_ACCENT
    st_pill.line.fill.background()
    tf_sp = st_pill.text_frame
    p = tf_sp.paragraphs[0]
    p.text = st_num.upper()
    p.font.name = FONT_HEADING
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.alignment = PP_ALIGN.CENTER

    tb_st = s8.shapes.add_textbox(left + Inches(0.08), top + Inches(0.42), Inches(2.07), Inches(1.45))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True

    p = tf_st.paragraphs[0]
    p.text = st_title
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    p = tf_st.add_paragraph()
    p.text = st_desc
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_MUTED_TEXT
    p.space_before = Pt(2)

# Research Extension Note at Bottom
c_ext = create_card(s8, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.7), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb_ext = s8.shapes.add_textbox(Inches(1.0), Inches(6.18), Inches(11.3), Inches(0.65))
tf_ext = tb_ext.text_frame
tf_ext.word_wrap = True

p = tf_ext.paragraphs[0]
p.text = "🔬 Foundation vs. Extension Scope:"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

p = tf_ext.add_paragraph()
p.text = "• Project 3 Foundation: Understood and executed the base MatSKRAFT preprocessing scripts on small sample inputs.\n• Project 4 / CrystaGraph: Extending the framework to multi-paper corpora, relation linking, SQLite persistence, and Streamlit platform."
p.font.name = FONT_BODY
p.font.size = Pt(9.5)
p.font.color.rgb = COLOR_TEXT_DARK

add_footer(s8, 8)

# ==============================================================================
# SLIDE 9 — DATASET, TECHNOLOGY & EXPECTED OUTPUT
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_BG_SOFT)
add_header(s9, "Technical Stack & Deliverables", "Dataset, Technology Stack & Expected Outputs", "Execution Foundation and Planned Deliverables for CrystaGraph")

# 3 Column Layout: Dataset | Tech Stack | Expected Output
col_w = Inches(3.78)

# Col 1: Dataset
c_d = create_card(s9, Inches(0.8), Inches(1.9), col_w, Inches(4.85), bg_color=COLOR_WHITE)
tb_d = s9.shapes.add_textbox(Inches(0.95), Inches(2.05), col_w - Inches(0.3), Inches(4.5))
tf_d = tb_d.text_frame
tf_d.word_wrap = True

p = tf_d.paragraphs[0]
p.text = "1. TARGET DATASET"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

d_points = [
    ("Initial Target Corpus", "10 real peer-reviewed scientific papers in standard Elsevier/JATS XML format."),
    ("Materials Domains", "Titanium alloys, battery cathodes, piezoelectric ceramics, high-entropy alloys, bioactive glasses, superconductors, SOFCs, SMAs."),
    ("Extracted Fields", "Paper ID, DOI, Table ID, Caption, Material Name, Composition (wt.%, at.%), Property Name, Numerical Value, Standardized Unit, Footnote Conditions.")
]
for dp_t, dp_b in d_points:
    p = tf_d.add_paragraph()
    p.text = f"• {dp_t}: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)
    pr = p.add_run()
    pr.text = dp_b
    pr.font.bold = False
    pr.font.size = Pt(9.5)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Col 2: Technology Stack
c_t = create_card(s9, Inches(4.78), Inches(1.9), col_w, Inches(4.85), bg_color=COLOR_WHITE)
tb_t = s9.shapes.add_textbox(Inches(4.93), Inches(2.05), col_w - Inches(0.3), Inches(4.5))
tf_t = tb_t.text_frame
tf_t.word_wrap = True

p = tf_t.paragraphs[0]
p.text = "2. TECHNOLOGY STACK"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL_ACCENT

t_points = [
    ("Core Programming", "Python 3.11+, Pandas, NumPy, scikit-learn"),
    ("AI / NLP Models", "MatSKRAFT research foundation, MatSciBERT tokenization, regex ontology parsers"),
    ("Data Storage", "SQLite3 relational database, structured JSON / CSV records"),
    ("Graph & Visualization", "NetworkX graph engine, Plotly Express & Graph Objects"),
    ("Web Platform", "Streamlit multi-page interactive web framework")
]
for tp_t, tp_b in t_points:
    p = tf_t.add_paragraph()
    p.text = f"• {tp_t}: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)
    pr = p.add_run()
    pr.text = tp_b
    pr.font.bold = False
    pr.font.size = Pt(9.5)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Col 3: Expected Output
c_o = create_card(s9, Inches(8.76), Inches(1.9), col_w, Inches(4.85), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb_o = s9.shapes.add_textbox(Inches(8.91), Inches(2.05), col_w - Inches(0.3), Inches(4.5))
tf_o = tb_o.text_frame
tf_o.word_wrap = True

p = tf_o.paragraphs[0]
p.text = "3. EXPECTED DELIVERABLES"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

o_points = [
    "Clean extracted scientific table DataFrames preserving multi-row spans.",
    "Structured composition fraction records (wt.%, at.%, mol%).",
    "Standardized property measurement database with canonical SI units.",
    "Linked composition-property relational knowledge triples.",
    "Interactive NetworkX / Plotly Materials Knowledge Graph.",
    "Multi-page Streamlit exploration platform with CSV/JSON export engine."
]
for op in o_points:
    p = tf_o.add_paragraph()
    p.text = f"✔ {op}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)

add_footer(s9, 9)

# ==============================================================================
# SLIDE 10 — EXPECTED CONTRIBUTION & FUTURE SCOPE
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, COLOR_BG_WHITE)
add_header(s10, "Impact & Vision", "Expected Contribution & Future Scope", "Bridging Tabular Scientific Literature with Graph Exploration and AI Discovery")

# Left Column Card: Expected Contributions
c_c1 = create_card(s10, Inches(0.8), Inches(1.9), Inches(5.7), Inches(3.4), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
tb_c1 = s10.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.3), Inches(3.1))
tf_c1 = tb_c1.text_frame
tf_c1.word_wrap = True

p = tf_c1.paragraphs[0]
p.text = "Expected Research Contributions"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

contribs = [
    "Multi-Paper Ingestion: Automated table extraction across multi-paper corpora.",
    "Structured Knowledge Store: Transforms chaotic XML tables into clean relational database.",
    "Relation Linking: Discovers implicit cross-table composition-property mappings.",
    "Knowledge Graph Representation: Connects Paper➔Table➔Material➔Property relations.",
    "User-Centric Platform: Empowers researchers to query, visualize, and export data."
]
for cb in contribs:
    p = tf_c1.add_paragraph()
    p.text = f"✔ {cb}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(3)

# Right Column Card: Future Research Scope
c_c2 = create_card(s10, Inches(6.8), Inches(1.9), Inches(5.733), Inches(3.4), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
tb_c2 = s10.shapes.add_textbox(Inches(7.0), Inches(2.05), Inches(5.3), Inches(3.1))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True

p = tf_c2.paragraphs[0]
p.text = "Future Scope & Roadmaps"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL_ACCENT

futures = [
    "Corpus Scaling: Expand from 10 papers to 100+ and 1,000+ open-access publications.",
    "Native PDF Parsing: Integrate vision-based table transformers (e.g., Table-Transformer).",
    "Hybrid LLM + GNN: Combine prompt-based LLMs with graph neural network reasoning.",
    "Downstream ML Prediction: Train regression models directly on mined knowledge graph.",
    "Automated Validation: Add confidence scoring and automated stoichiometric checking."
]
for ft in futures:
    p = tf_c2.add_paragraph()
    p.text = f"🚀 {ft}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(3)

# Bottom Concluding Message Banner
c_final = create_card(s10, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.3), bg_color=COLOR_PRIMARY_BLUE, border_color=None)
tb_final = s10.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.1), Inches(1.1))
tf_final = tb_final.text_frame
tf_final.word_wrap = True

p = tf_final.paragraphs[0]
p.text = "CONCLUDING VISION"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = COLOR_CARD_ACCENT_BG

p = tf_final.add_paragraph()
p.text = "“CrystaGraph extends research-oriented material information extraction toward an integrated environment for multi-paper knowledge extraction, relationship discovery and interactive exploration.”"
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(3)

add_footer(s10, 10, "BML Munjal University — Department of Computer Science & Engineering")

# Save Presentation
output_path = os.path.join(PROJECT_ROOT, "CrystaGraph_Project4_Presentation.pptx")
prs.save(output_path)
print(f"[SUCCESS] Presentation generated successfully at: {output_path}")
