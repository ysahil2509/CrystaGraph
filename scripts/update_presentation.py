"""
Script to generate the updated, submission-ready 12-slide academic PowerPoint presentation (.pptx)
for B.Tech Project-4: 'CrystaGraph: AI-Driven Material Knowledge Mining from Scientific Tables'
BML Munjal University, Department of Computer Science & Engineering.
Includes:
- Exact requested Literature Review Comparison Table
- Detailed 'Why Not Just Use an AI Chatbot?' comparison & USP
- What is New & Updated from Project 3
- Real experimental results, validation accuracy & ML benchmarks (R²=0.88-0.997)
- Embedded uploaded CrystaGraph Architecture Diagram (assets/crystagraph_architecture.jpg)
- Comprehensive feature showcases of the Streamlit application
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ARCH_IMG_PATH = os.path.join(PROJECT_ROOT, "assets/crystagraph_architecture.jpg")

# Initialize Presentation with 16:9 Widescreen dimensions
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

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
COLOR_GREEN = RGBColor(22, 163, 74) # #16A34A
COLOR_RED_ALERT = RGBColor(220, 38, 38) # #DC2626

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

TOTAL_SLIDES = 12

def set_slide_background(slide, color=COLOR_BG_SOFT):
    """Sets a clean solid background color for the slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, category: str, title: str, subtitle: str = None):
    """Adds a standardized professional academic header banner to content slides."""
    # Category Pill Tag
    cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(3.6), Inches(0.3))
    cat_box.fill.solid()
    cat_box.fill.fore_color.rgb = COLOR_CARD_ACCENT_BG
    cat_box.line.color.rgb = COLOR_CYAN_ACCENT
    cat_box.line.width = Pt(1)
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.name = FONT_HEADING
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_CYAN_ACCENT
    p_cat.alignment = PP_ALIGN.CENTER

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.55))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    # Subtitle if provided
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.32))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_MUTED_TEXT

    # Subtle horizontal divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.65), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_CARD_BORDER
    line.line.color.rgb = COLOR_CARD_BORDER

def add_footer(slide, slide_num: int, citation: str = None):
    """Adds a standard academic footer with project attribution and optional citation."""
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.01))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_CARD_BORDER
    div.line.color.rgb = COLOR_CARD_BORDER

    foot_left = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(6.8), Inches(0.4))
    tf_l = foot_left.text_frame
    p_l = tf_l.paragraphs[0]
    p_l.text = "CrystaGraph: AI-Driven Material Knowledge Mining | BML Munjal University — Project-4"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(9)
    p_l.font.color.rgb = COLOR_MUTED_TEXT

    if citation:
        cite_box = slide.shapes.add_textbox(Inches(5.0), Inches(6.95), Inches(5.8), Inches(0.4))
        tf_c = cite_box.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = f"Source: {citation}"
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(8.5)
        p_c.font.italic = True
        p_c.font.color.rgb = COLOR_CYAN_ACCENT
        p_c.alignment = PP_ALIGN.RIGHT

    foot_right = slide.shapes.add_textbox(Inches(11.0), Inches(6.95), Inches(1.533), Inches(0.4))
    tf_r = foot_right.text_frame
    p_r = tf_r.paragraphs[0]
    p_r.text = f"Slide {slide_num} of {TOTAL_SLIDES}"
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

# Top Decorative Accent Bar
accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
accent_bar.line.fill.background()

# Hero Banner Card
hero_card = create_card(s1, Inches(0.8), Inches(0.55), Inches(11.733), Inches(3.25), bg_color=COLOR_PRIMARY_BLUE, border_color=None)

# Tag inside hero
tag_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.85), Inches(4.3), Inches(0.35))
tag_shape.fill.solid()
tag_shape.fill.fore_color.rgb = RGBColor(14, 116, 144)
tag_shape.line.color.rgb = COLOR_CYAN_ACCENT
tag_shape.line.width = Pt(1)
tf_tag = tag_shape.text_frame
p_t = tf_tag.paragraphs[0]
p_t.text = "B.TECH CSE — PROJECT-4 EVALUATION & SUBMISSION"
p_t.font.name = FONT_HEADING
p_t.font.size = Pt(9.5)
p_t.font.bold = True
p_t.font.color.rgb = COLOR_WHITE
p_t.alignment = PP_ALIGN.CENTER

# Main Title
title_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(10.9), Inches(1.3))
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
p_sub.text = "Comprehensive Literature Review, Proposed Architecture & Prototype Implementation"
p_sub.font.name = FONT_BODY
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = COLOR_CARD_ACCENT_BG

# Group Members Section Card
mem_card = create_card(s1, Inches(0.8), Inches(4.0), Inches(6.8), Inches(2.65), bg_color=COLOR_BG_CARD, border_color=COLOR_CARD_BORDER)

mem_title = s1.shapes.add_textbox(Inches(1.1), Inches(4.15), Inches(6.2), Inches(0.35))
p_mt = mem_title.text_frame.paragraphs[0]
p_mt.text = "PROJECT TEAM MEMBERS"
p_mt.font.name = FONT_HEADING
p_mt.font.size = Pt(11)
p_mt.font.bold = True
p_mt.font.color.rgb = COLOR_PRIMARY_BLUE

# Member pills grid (2x2)
members = [
    ("Sahil Yadav", "230860", "Architecture & Preprocessing Lead"),
    ("Ayush Yadav", "230517", "Property & ML Prediction Lead"),
    ("Nitin Yadav", "230771", "Database & Streamlit UI Platform"),
    ("Ghoda", "2306969", "Material NLP & Composition Extraction")
]
for idx, (m_name, m_roll, m_role) in enumerate(members):
    col_idx = idx % 2
    row_idx = idx // 2
    m_left = Inches(1.1 + col_idx * 3.1)
    m_top = Inches(4.55 + row_idx * 0.95)
    
    p_box = create_card(s1, m_left, m_top, Inches(2.9), Inches(0.82), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
    tb = s1.shapes.add_textbox(m_left + Inches(0.1), m_top + Inches(0.06), Inches(2.7), Inches(0.7))
    tf_m = tb.text_frame
    p1 = tf_m.paragraphs[0]
    p1.text = f"• {m_name}"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(11.5)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_DARK
    
    p2 = tf_m.add_paragraph()
    p2.text = f"   Roll: {m_roll} | {m_role}"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = COLOR_MUTED_TEXT

# Institution & Department Card Right
inst_card = create_card(s1, Inches(7.8), Inches(4.0), Inches(4.733), Inches(2.65), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)

inst_tb = s1.shapes.add_textbox(Inches(8.1), Inches(4.25), Inches(4.133), Inches(2.1))
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
pi2.space_before = Pt(3)

pi3 = tf_inst.add_paragraph()
pi3.text = "Department of Computer Science & Engineering\nSchool of Engineering & Technology\nCourse: Project-4 (Capstone Stage)\nAcademic Year: 2025–2026"
pi3.font.name = FONT_BODY
pi3.font.size = Pt(11)
pi3.font.color.rgb = COLOR_TEXT_DARK
pi3.space_before = Pt(5)

add_footer(s1, 1)

# ==============================================================================
# SLIDE 2 — BACKGROUND & MOTIVATION
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, COLOR_BG_SOFT)
add_header(s2, "Context & Motivation", "Background & Motivation", "The Critical Need for Automated Knowledge Mining from Tabular Scientific Literature")

# Left Column Card: Scientific Table Wealth
c1 = create_card(s2, Inches(0.8), Inches(1.85), Inches(5.6), Inches(4.85), bg_color=COLOR_WHITE)
tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.55))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "Materials Literature Goldmine in Tables"
p.font.name = FONT_HEADING
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

p = tf1.add_paragraph()
p.text = "Materials science research produces a vast amount of empirical data. Over 80% of experimental measurements are published inside tables rather than narrative text:"
p.font.name = FONT_BODY
p.font.size = Pt(11)
p.font.color.rgb = COLOR_TEXT_DARK
p.space_before = Pt(5)

items = [
    ("Material Names & Phases", "Alloys, ceramics, superconductors (e.g., Ti-6Al-4V, BaTiO3, LiFePO4)."),
    ("Chemical Compositions", "Stoichiometry & fractions (wt.%, at.%, mol%) across multiple elements."),
    ("Target Properties", "Yield strength, hardness, density, dielectric constant, Tc, conductivity."),
    ("Numerical Values & Units", "Quantitative measurements with scientific units (MPa, GPa, g/cm³, K)."),
    ("Experimental Conditions", "Sintering temperatures, strain rates, dopant concentrations, atmosphere.")
]
for title_item, desc_item in items:
    p = tf1.add_paragraph()
    p.text = f"• {title_item}: "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(4)
    p_run = p.add_run()
    p_run.text = desc_item
    p_run.font.bold = False
    p_run.font.color.rgb = COLOR_MUTED_TEXT

# Right Column Top Card: Current Bottlenecks
c2 = create_card(s2, Inches(6.7), Inches(1.85), Inches(5.833), Inches(2.8), bg_color=COLOR_WHITE)
tb2 = s2.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(2.5))
tf2 = tb2.text_frame
tf2.word_wrap = True

p = tf2.paragraphs[0]
p.text = "Core Literature Bottlenecks"
p.font.name = FONT_HEADING
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

challenges = [
    "High Literature Volume: Millions of papers published across heterogeneous journals.",
    "Complex Topology: Multi-row headers, spanning cells (morerows, colspans).",
    "Manual Bottleneck: Human extraction is painfully slow, expensive, and error-prone.",
    "Implicit Relations: Compositions in Table 1 and properties in Table 2 remain unlinked.",
    "Data Silos: Information is hard to search, cross-reference, and compare across papers."
]
for ch in challenges:
    p = tf2.add_paragraph()
    p.text = f"⚠ {ch}"
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(3)

# Right Column Bottom Card: Core Transformation Concept
c3 = create_card(s2, Inches(6.7), Inches(4.8), Inches(5.833), Inches(1.9), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb3 = s2.shapes.add_textbox(Inches(6.9), Inches(4.9), Inches(5.4), Inches(1.7))
tf3 = tb3.text_frame
tf3.word_wrap = True

p = tf3.paragraphs[0]
p.text = "CORE TRANSFORMATION PARADIGM"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

p = tf3.add_paragraph()
p.text = "Scientific Papers  ➔  Tables  ➔  Structured Knowledge  ➔  Knowledge Graph"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
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
c_top = create_card(s3, Inches(0.8), Inches(1.85), Inches(11.733), Inches(1.4), bg_color=COLOR_PRIMARY_BLUE, border_color=None)
tb_top = s3.shapes.add_textbox(Inches(1.1), Inches(1.98), Inches(11.1), Inches(1.1))
tf_top = tb_top.text_frame
tf_top.word_wrap = True

p = tf_top.paragraphs[0]
p.text = "FORMAL PROBLEM STATEMENT"
p.font.name = FONT_HEADING
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = COLOR_CARD_ACCENT_BG

p = tf_top.add_paragraph()
p.text = "“Scientific materials knowledge is distributed across research papers and is frequently presented in heterogeneous tables containing compositions, properties, units and experimental information. Extracting, linking and exploring this information across multiple papers remains challenging.”"
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(3)

# 6 Key Obstacles Grid (3 columns x 2 rows)
obstacles = [
    ("1. Heterogeneous Table Formats", "Different publishers use varied XML/HTML schemas (Elsevier, JATS, HTML) with complex spanning cells."),
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
    top = Inches(3.38 + row * 1.55)
    
    card_ob = create_card(s3, left, top, Inches(3.78), Inches(1.45), bg_color=COLOR_WHITE)
    tb_ob = s3.shapes.add_textbox(left + Inches(0.12), top + Inches(0.08), Inches(3.54), Inches(1.3))
    tf_o = tb_ob.text_frame
    tf_o.word_wrap = True
    
    p = tf_o.paragraphs[0]
    p.text = ob_title
    p.font.name = FONT_HEADING
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE
    
    p = tf_o.add_paragraph()
    p.text = ob_desc
    p.font.name = FONT_BODY
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2)

# Central Research Question Callout Banner
c_rq = create_card(s3, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.58), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT, border_width=1.5)
tb_rq = s3.shapes.add_textbox(Inches(1.1), Inches(5.2), Inches(11.1), Inches(1.38))
tf_rq = tb_rq.text_frame
tf_rq.word_wrap = True

p = tf_rq.paragraphs[0]
p.text = "🎯 CORE RESEARCH QUESTION"
p.font.name = FONT_HEADING
p.font.size = Pt(10.5)
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
    top = Inches(1.85 + row * 2.35)
    
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
# SLIDE 5 — LITERATURE REVIEW COMPARISON TABLE (USER EXACT TABLE)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, COLOR_BG_SOFT)
add_header(s5, "Literature Analysis", "Literature Review Comparison", "Direct Comparative Matrix of State-of-the-Art Materials Extraction Methodologies")

# Create Table Shape (5 rows of research + 1 header row)
rows_cnt = 6
cols_cnt = 5
top_t = Inches(1.85)
left_t = Inches(0.8)
width_t = Inches(11.733)
height_t = Inches(4.35)

table_shape = s5.shapes.add_table(rows_cnt, cols_cnt, left_t, top_t, width_t, height_t)
table = table_shape.table

# Set Column Widths based on user table specification
table.columns[0].width = Inches(2.2) # Research
table.columns[1].width = Inches(2.4) # Technique
table.columns[2].width = Inches(1.8) # Input
table.columns[3].width = Inches(2.8) # Main Contribution
table.columns[4].width = Inches(2.533) # Limitation / Gap

headers_lit = ["Research", "Technique", "Input", "Main Contribution", "Limitation / Gap"]
for i, h in enumerate(headers_lit):
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

# User-requested table content exactly
exact_user_table = [
    ("MatSciBERT (2022)", "Domain-specific BERT", "Scientific text", "Materials NER & relation extraction", "Primarily text-focused"),
    ("Zhang et al. (2023)", "NLP + image/table extraction + ML", "Text + tables", "Large-scale material information mining", "Application-focused pipeline"),
    ("MaTableGPT (2024/25)", "GPT/LLM", "Materials tables", "Flexible table data extraction", "LLM cost, hallucination/control"),
    ("MatSKRAFT (2025)", "Constraint-driven GNN", "Scientific tables", "Composition & property extraction at scale", "Complex research-oriented pipeline"),
    ("Dreger et al. (2025)", "LLM + rules + KG", "Structured tables", "Converts tables into knowledge graphs", "Tested on 15 heterogeneous flat tables")
]

for row_idx, row_content in enumerate(exact_user_table):
    for col_idx, cell_value in enumerate(row_content):
        cell = table.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_WHITE if row_idx % 2 == 0 else COLOR_BG_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = cell_value
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_DARK
        if col_idx == 0:
            p.font.bold = True
            p.font.color.rgb = COLOR_NAVY_DARK

# Bottom Synthesis Card
c_take = create_card(s5, Inches(0.8), Inches(6.32), Inches(11.733), Inches(0.55), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
tb_t = s5.shapes.add_textbox(Inches(0.95), Inches(6.35), Inches(11.4), Inches(0.48))
tf_t = tb_t.text_frame
tf_t.word_wrap = True
p = tf_t.paragraphs[0]
p.text = "💡 Critical Gap Synthesis: Existing research addresses individual components in isolation. CrystaGraph unifies multi-paper extraction, structured SQLite storage, cross-table relationship linking, and interactive graph exploration into a production-grade platform."
p.font.name = FONT_BODY
p.font.size = Pt(9.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

add_footer(s5, 5)

# ==============================================================================
# SLIDE 6 — RESEARCH GAP & WHY NOT JUST USE AN AI CHATBOT? (NEW & USP)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, COLOR_BG_SOFT)
add_header(s6, "Core Dilemma & USP", "Research Gap: Why Not Just Use an AI Chatbot?", "Fundamental Failure Modes of General LLMs/Chatbots on Tabular Scientific Literature")

# Left Column: The Problem with Standard Chatbots (ChatGPT / Claude / Gemini)
card_llm = create_card(s6, Inches(0.8), Inches(1.85), Inches(5.6), Inches(4.85), bg_color=COLOR_WHITE, border_color=COLOR_RED_ALERT, border_width=1.5)
tb_llm = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.55))
tf_llm = tb_llm.text_frame
tf_llm.word_wrap = True

p = tf_llm.paragraphs[0]
p.text = "❌ Why Standard AI Chatbots Fail on Tables"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_RED_ALERT

chatbot_flaws = [
    ("Numerical & Stoichiometric Hallucinations", "Chatbots invent or drift numbers; chemical percentages frequently fail to sum to 100% or violate valency laws."),
    ("Loss of 2D Table Spatial Topology", "LLMs flatten tables into 1D text token streams, causing severe misalignment across multi-row headers and row/col spans."),
    ("Inability to Cross-Link Multi-Table Data", "Chatbots cannot reliably correlate Table 1 alloy samples with Table 2 property measurements across multi-page papers."),
    ("Token Limits & High Inference Cost", "Feeding dozens of full-text papers with embedded tables exceeds prompt context windows and costs dollars per query."),
    ("Ephemeral, Non-Queryable Output", "Outputs are plain text/markdown—not queryable with SQL, not indexed, and impossible to query in real-time downstream.")
]
for title_flaw, desc_flaw in chatbot_flaws:
    p = tf_llm.add_paragraph()
    p.text = f"• {title_flaw}: "
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(3)
    pr = p.add_run()
    pr.text = desc_flaw
    pr.font.bold = False
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Right Column: The CrystaGraph Solution (USP)
card_cg = create_card(s6, Inches(6.7), Inches(1.85), Inches(5.833), Inches(4.85), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT, border_width=1.5)
tb_cg = s6.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.4), Inches(4.55))
tf_cg = tb_cg.text_frame
tf_cg.word_wrap = True

p = tf_cg.paragraphs[0]
p.text = "✔ CrystaGraph's Grounded Solution (Our USP)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN_ACCENT

cg_solutions = [
    ("Deterministic Constraint Verification", "Enforces mathematical bounds (0-100%) and chemical formula rules without generative hallucination."),
    ("Hierarchical XML/PDF Structural Parsing", "Explicitly resolves `tgroup`, `colspec`, `morerows`, and `namest/nameend` spanning cell coordinates."),
    ("Associative Cross-Table Entity Linker", "Deterministically merges compositions from Table 1 with mechanical/thermal properties from Table 2."),
    ("Indexed Relational Knowledge Base", "Persists structured data into a 7-table SQLite schema (`matgraph.db`) for sub-millisecond querying."),
    ("Multi-Relational Knowledge Graph & ML", "Generates interactive NetworkX/Plotly ontology and trains downstream Random Forest property predictors.")
]
for title_sol, desc_sol in cg_solutions:
    p = tf_cg.add_paragraph()
    p.text = f"✔ {title_sol}: "
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(3)
    pr = p.add_run()
    pr.text = desc_sol
    pr.font.bold = False
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_TEXT_DARK

add_footer(s6, 6)

# ==============================================================================
# SLIDE 7 — WHAT IS NEW & UPDATED FROM PROJECT 3?
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, COLOR_BG_SOFT)
add_header(s7, "Innovation & Evolution", "What is New & Updated from Project 3?", "Major Architectural Advances and Unique Selling Proposition (USP) of CrystaGraph")

# Comparison Cards (Project 3 vs Project 4 CrystaGraph)
w_half = Inches(5.66)

# Left: Project 3
c_p3 = create_card(s7, Inches(0.8), Inches(1.85), w_half, Inches(4.85), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
tb_p3 = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), w_half - Inches(0.4), Inches(4.55))
tf_p3 = tb_p3.text_frame
tf_p3.word_wrap = True

p = tf_p3.paragraphs[0]
p.text = "Project 3 (Foundational Prototype)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_MUTED_TEXT

p3_items = [
    ("Single-Paper Exploratory Scope", "Executed exclusively on a single sample paper with isolated scripts."),
    ("CLI Script Execution Only", "Required manual terminal execution of individual python scripts without an integrated pipeline."),
    ("Basic Unlinked Extraction", "Extracted raw tokens without associating alloy compositions with target properties."),
    ("No Persistent Database", "Outputs dumped into random temporary pickle/text files without queryable schema."),
    ("No Visual Exploration Platform", "Lacked any user interface, graphical dashboard, or interactive exploration."),
    ("No Machine Learning Modeling", "No property prediction or empirical validation capabilities.")
]
for title_item, desc_item in p3_items:
    p = tf_p3.add_paragraph()
    p.text = f"• {title_item}: "
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(3)
    pr = p.add_run()
    pr.text = desc_item
    pr.font.bold = False
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Right: Project 4 CrystaGraph
c_p4 = create_card(s7, Inches(6.87), Inches(1.85), w_half, Inches(4.85), bg_color=COLOR_WHITE, border_color=COLOR_PRIMARY_BLUE, border_width=1.5)
tb_p4 = s7.shapes.add_textbox(Inches(7.07), Inches(2.0), w_half - Inches(0.4), Inches(4.55))
tf_p4 = tb_p4.text_frame
tf_p4.word_wrap = True

p = tf_p4.paragraphs[0]
p.text = "Project 4 / CrystaGraph (Major Advances)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

p4_items = [
    ("Multi-Paper Automated Ingestion", "Processes 10+ real scientific papers across XML and PDF with automated DOI retrieval."),
    ("Automated XML Cell Span Resolution", "Traverses `morerows` & `colspans` in `tgroup` tables with zero XML crashes."),
    ("Associative Knowledge Linker", "Unifies Table 1 compositions with Table 2 properties into complete relational triples."),
    ("Indexed Relational SQLite Base", "Stores 7 relational tables (`matgraph.db`) with optimized indices for sub-second search."),
    ("Interactive Knowledge Graph Engine", "Constructs multi-relational NetworkX/Plotly ontology (Paper➔Table➔Material➔Property)."),
    ("Machine Learning Property Predictor", "Random Forest regression forecasting Yield Strength, Hardness, Density (R²=0.88-0.997)."),
    ("Production Streamlit Platform", "8 dedicated pages with real-time search, visual analytics, and CSV/JSON export.")
]
for title_item, desc_item in p4_items:
    p = tf_p4.add_paragraph()
    p.text = f"🚀 {title_item}: "
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_PRIMARY_BLUE
    p.space_before = Pt(2.5)
    pr = p.add_run()
    pr.text = desc_item
    pr.font.bold = False
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_TEXT_DARK

add_footer(s7, 7)

# ==============================================================================
# SLIDE 8 — OBJECTIVES & SCOPE
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, COLOR_BG_SOFT)
add_header(s8, "Project Scope", "Project Objectives", "Four Core Architectural Pillars of the CrystaGraph Mining Platform")

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
            "Deploy AI Property Predictor for novel alloy composition forecasting.",
            "Enable structured data downloads in standardized CSV and JSON formats."
        ]
    }
]

for idx, p_info in enumerate(pillars):
    col = idx % 2
    row = idx // 2
    left = Inches(0.8 + col * 5.95)
    top = Inches(1.85 + row * 2.45)
    
    card_pil = create_card(s8, left, top, Inches(5.78), Inches(2.3), bg_color=COLOR_WHITE)
    
    ribbon = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.12), top + Inches(0.12), Inches(5.54), Inches(0.35))
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

    tb_c = s8.shapes.add_textbox(left + Inches(0.15), top + Inches(0.5), Inches(5.48), Inches(1.7))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    for o_idx, obj in enumerate(p_info["objectives"]):
        p = tf_c.paragraphs[0] if o_idx == 0 else tf_c.add_paragraph()
        p.text = f"✔ {obj}"
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_before = Pt(2)

add_footer(s8, 8)

# ==============================================================================
# SLIDE 9 — SYSTEM ARCHITECTURE (FEATURING UPLOADED ARCHITECTURE IMAGE)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, COLOR_BG_WHITE)
add_header(s9, "System Architecture", "CrystaGraph System Architecture", "End-to-End Five-Stage Pipeline from Research Papers to Interactive Knowledge Graph & UI")

# Left Column: Concise Stage Commentary Card
c_arch_desc = create_card(s9, Inches(0.8), Inches(1.85), Inches(4.3), Inches(4.85), bg_color=COLOR_BG_CARD, border_color=COLOR_CARD_BORDER)
tb_ad = s9.shapes.add_textbox(Inches(0.95), Inches(1.95), Inches(4.0), Inches(4.65))
tf_ad = tb_ad.text_frame
tf_ad.word_wrap = True

p = tf_ad.paragraphs[0]
p.text = "5-Stage Pipeline Overview"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

stages_desc = [
    ("1. Paper & Dataset Prep", "Ingests research papers via DOI, XML, or PDF. Subsets and splits for NLP/GNN training."),
    ("2. Table Extraction", "XML/PDF tree parsing, table region detection, row/col extraction, cell-span cleaning & normalization."),
    ("3. Information Extraction", "MatSKRAFT-based chemical composition mining, material property extraction, numerical & unit parsing."),
    ("4. Knowledge Integration", "Entity linking (Material-Composition-Property), structured SQLite storage & Knowledge Graph construction."),
    ("5. Exploration Platform", "Streamlit UI: Paper, Table, and Material Explorers, Knowledge Graph, Analytics & CSV/JSON Export.")
]
for st_t, st_d in stages_desc:
    p = tf_ad.add_paragraph()
    p.text = f"• {st_t}: "
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(3)
    pr = p.add_run()
    pr.text = st_d
    pr.font.bold = False
    pr.font.size = Pt(8.5)
    pr.font.color.rgb = COLOR_MUTED_TEXT

# Right Column: The Uploaded Architecture Diagram Image
if os.path.exists(ARCH_IMG_PATH):
    img_left = Inches(5.3)
    img_top = Inches(1.85)
    img_width = Inches(7.233)
    img_height = Inches(4.82) # aspect ratio matches ~1.5:1
    s9.shapes.add_picture(ARCH_IMG_PATH, img_left, img_top, width=img_width, height=img_height)
else:
    # Fallback placeholder if image not found
    c_img_box = create_card(s9, Inches(5.3), Inches(1.85), Inches(7.233), Inches(4.82), bg_color=COLOR_CARD_ACCENT_BG, border_color=COLOR_CYAN_ACCENT)
    tb_fb = s9.shapes.add_textbox(Inches(5.5), Inches(3.5), Inches(6.8), Inches(1.5))
    tf_fb = tb_fb.text_frame
    p = tf_fb.paragraphs[0]
    p.text = "CrystaGraph Architecture Diagram"
    p.font.size = Pt(18)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

add_footer(s9, 9, "CrystaGraph Architectural Framework")

# ==============================================================================
# SLIDE 10 — EXPERIMENTAL RESULTS & VALIDATION METRICS
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, COLOR_BG_SOFT)
add_header(s10, "Empirical Validation", "Experimental Results & Validation Metrics", "Genuine Execution Benchmarks Across 10 Authentic Research Papers & Machine Learning Models")

# Left Column: Quantitative Execution Metrics Card
c_m1 = create_card(s10, Inches(0.8), Inches(1.85), Inches(5.7), Inches(4.85), bg_color=COLOR_WHITE)
tb_m1 = s10.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(4.65))
tf_m1 = tb_m1.text_frame
tf_m1.word_wrap = True

p = tf_m1.paragraphs[0]
p.text = "Pipeline Extraction Performance (Genuine Execution)"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

# Metrics Table
metrics_data = [
    ("Scientific Papers Ingested", "10 Papers (100% Success Rate)"),
    ("Tables Detected & Extracted", "20 Tables (100% Success Rate)"),
    ("Unique Materials Discovered", "50 Distinct Material Systems"),
    ("Chemical Components & Oxides", "49 Elements & Ceramic Oxides"),
    ("Physical Properties Profiled", "32 Canonical Property Types"),
    ("Composition Entries Mined", "205 Stoichiometric Records"),
    ("Property Measurements Mined", "255 Quantitative Values"),
    ("Linked Knowledge Triples", "255 (Composition-Property Tuples)"),
    ("Numeric Validity Ratio", "98.43% Non-Null Numeric Values"),
    ("Unit Standardization Ratio", "98.04% Canonical SI Units"),
    ("Total Pipeline Execution Time", "0.048 s (~0.005 s / paper)")
]
for m_label, m_val in metrics_data:
    p = tf_m1.add_paragraph()
    p.text = f"• {m_label}: "
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_NAVY_DARK
    p.space_before = Pt(2.5)
    pr = p.add_run()
    pr.text = m_val
    pr.font.bold = False
    pr.font.size = Pt(9)
    pr.font.color.rgb = COLOR_TEAL_ACCENT

# Right Column: Machine Learning Prediction Benchmarks
c_m2 = create_card(s10, Inches(6.8), Inches(1.85), Inches(5.733), Inches(4.85), bg_color=COLOR_WHITE)
tb_m2 = s10.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.3), Inches(4.65))
tf_m2 = tb_m2.text_frame
tf_m2.word_wrap = True

p = tf_m2.paragraphs[0]
p.text = "Downstream ML Property Prediction Accuracy"
p.font.name = FONT_HEADING
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL_ACCENT

p = tf_m2.add_paragraph()
p.text = "Random Forest models trained on mined composition vectors to predict physical properties directly from chemical stoichiometry:"
p.font.name = FONT_BODY
p.font.size = Pt(9.5)
p.font.color.rgb = COLOR_TEXT_DARK
p.space_before = Pt(3)

ml_results = [
    ("Yield Strength (MPa)", "R² = 0.880", "RMSE: 237.7 MPa", "Top Features: Ti (39%), Mn (24%), Al (20%)"),
    ("Density (g/cm³)", "R² = 0.997", "RMSE: 5.23 g/cm³", "Top Features: Li (42%), O (41%), K (5%)"),
    ("Tensile Strength (MPa)", "R² = 0.920", "RMSE: 245.3 MPa", "Top Features: Mg (20%), Mn (19%), Cu (17%)"),
    ("Dielectric Constant", "R² = 0.880", "RMSE: 371.28", "Top Features: PbO (24%), ZrO2 (23%), Na2O (15%)")
]
for prop_name, r2_val, rmse_val, feats in ml_results:
    p = tf_m2.add_paragraph()
    p.text = f"🎯 {prop_name} — "
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_PRIMARY_BLUE
    p.space_before = Pt(3.5)
    
    pr = p.add_run()
    pr.text = f"{r2_val} | {rmse_val}"
    pr.font.bold = True
    pr.font.color.rgb = COLOR_GREEN
    
    p_sub = tf_m2.add_paragraph()
    p_sub.text = f"   {feats}"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(8.5)
    p_sub.font.color.rgb = COLOR_MUTED_TEXT

add_footer(s10, 10, "Evaluated on 10 peer-reviewed papers: MSEA, EnSM, Acta Mater, Phys C, Nano Energy")

# ==============================================================================
# SLIDE 11 — STREAMLIT PLATFORM & FEATURE SHOWCASE
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, COLOR_BG_SOFT)
add_header(s11, "Interactive Exploration", "Streamlit Platform & Feature Showcase", "Six Core Web Modules Empowering Real-Time Materials Knowledge Discovery")

# 6 Feature Cards (2 rows x 3 columns)
features = [
    {
        "title": "1. Paper Explorer",
        "tag": "Document Corpus",
        "desc": "Browse ingested XML/PDF publications with title, DOI, abstract, and automated inventory of all extracted research tables with instant CSV/JSON downloads."
    },
    {
        "title": "2. Table Explorer",
        "tag": "Verification & QA",
        "desc": "Side-by-side verification comparing Raw XML tables with Cleaned normalized DataFrames. Inspects table captions, footnotes, and experimental conditions."
    },
    {
        "title": "3. Material Explorer",
        "tag": "Stoichiometry & Properties",
        "desc": "Search any material (Ti-6Al-4V, BaTiO3, LiFePO4) to render interactive chemical composition pie-charts (wt.%, at.%) alongside linked measured property tables."
    },
    {
        "title": "4. Knowledge Graph",
        "tag": "Multi-Relational Network",
        "desc": "Interactive 2D/3D NetworkX and Plotly visualization connecting Paper (Blue) ➔ Table (Green) ➔ Material (Orange) ➔ Property (Purple) ➔ Value (Red)."
    },
    {
        "title": "5. AI Property Predictor",
        "tag": "ML Inference Engine",
        "desc": "Enter custom chemical formulations to generate instant property forecasts (Yield Strength, Hardness, Density) with 95% confidence intervals and feature importances."
    },
    {
        "title": "6. Analytics & Data Export",
        "tag": "Statistical Intelligence",
        "desc": "Property distribution histograms, boxplots, cross-property trade-off scatter plots, and one-click export of complete relational datasets in CSV and JSON formats."
    }
]

for idx, ft in enumerate(features):
    col = idx % 3
    row = idx // 3
    left = Inches(0.8 + col * 3.98)
    top = Inches(1.85 + row * 2.45)
    
    card_ft = create_card(s11, left, top, Inches(3.78), Inches(2.3), bg_color=COLOR_WHITE)
    
    # Tag Badge
    tag_b = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.15), top + Inches(0.12), Inches(3.48), Inches(0.28))
    tag_b.fill.solid()
    tag_b.fill.fore_color.rgb = COLOR_CARD_ACCENT_BG
    tag_b.line.color.rgb = COLOR_CYAN_ACCENT
    tag_b.line.width = Pt(0.75)
    tf_tb = tag_b.text_frame
    p_tb = tf_tb.paragraphs[0]
    p_tb.text = f"{ft['title']} — {ft['tag']}".upper()
    p_tb.font.name = FONT_HEADING
    p_tb.font.size = Pt(8.5)
    p_tb.font.bold = True
    p_tb.font.color.rgb = COLOR_CYAN_ACCENT
    p_tb.alignment = PP_ALIGN.CENTER

    tb = s11.shapes.add_textbox(left + Inches(0.15), top + Inches(0.48), Inches(3.48), Inches(1.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = ft["title"]
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY_DARK

    p = tf.add_paragraph()
    p.text = ft["desc"]
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(3)

add_footer(s11, 11)

# ==============================================================================
# SLIDE 12 — EXPECTED CONTRIBUTIONS, FUTURE SCOPE & REFERENCES
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, COLOR_BG_WHITE)
add_header(s12, "Impact & Vision", "Expected Contributions, Future Scope & References", "Bridging Tabular Literature with AI-Driven Materials Discovery")

# Left Column: Research Contributions
c_c1 = create_card(s12, Inches(0.8), Inches(1.85), Inches(5.7), Inches(3.3), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
tb_c1 = s12.shapes.add_textbox(Inches(1.0), Inches(1.98), Inches(5.3), Inches(3.05))
tf_c1 = tb_c1.text_frame
tf_c1.word_wrap = True

p = tf_c1.paragraphs[0]
p.text = "Core Academic Contributions"
p.font.name = FONT_HEADING
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

contribs = [
    "Multi-Paper Automated Ingestion: Zero-crash XML/PDF tree parsing across journals.",
    "Zero-Hallucination Extraction: Grounded deterministic parsing vs conversational LLMs.",
    "Associative Relation Linking: Maps Table 1 compositions with Table 2 properties.",
    "Multi-Relational Knowledge Graph: Connects Paper➔Table➔Material➔Property relations.",
    "Open Relational Repository: 7-table SQLite schema queryable via SQL and REST API."
]
for cb in contribs:
    p = tf_c1.add_paragraph()
    p.text = f"✔ {cb}"
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2.5)

# Right Column: Future Research Scope
c_c2 = create_card(s12, Inches(6.8), Inches(1.85), Inches(5.733), Inches(3.3), bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER)
tb_c2 = s12.shapes.add_textbox(Inches(7.0), Inches(1.98), Inches(5.3), Inches(3.05))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True

p = tf_c2.paragraphs[0]
p.text = "Future Scope & Roadmaps"
p.font.name = FONT_HEADING
p.font.size = Pt(13.5)
p.font.bold = True
p.font.color.rgb = COLOR_TEAL_ACCENT

futures = [
    "Corpus Scaling: Expand from 10 papers to 1,000+ open-access papers via Elsevier API.",
    "Vision Transformers: Integrate Table-Transformer & LayoutLMv3 for complex PDF scans.",
    "Hybrid LLM + GNN: Combine prompt embeddings with graph neural network reasoning.",
    "Inverse Materials Design: Train generative models on graph to suggest novel alloys.",
    "Automated Benchmarking: Implement automated stoichiometric cross-checking checks."
]
for ft in futures:
    p = tf_c2.add_paragraph()
    p.text = f"🚀 {ft}"
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT_DARK
    p.space_before = Pt(2.5)

# Bottom References & Concluding Vision
c_final = create_card(s12, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.55), bg_color=COLOR_PRIMARY_BLUE, border_color=None)
tb_final = s12.shapes.add_textbox(Inches(1.0), Inches(5.35), Inches(11.3), Inches(1.35))
tf_final = tb_final.text_frame
tf_final.word_wrap = True

p = tf_final.paragraphs[0]
p.text = "KEY ACADEMIC REFERENCES"
p.font.name = FONT_HEADING
p.font.size = Pt(9.5)
p.font.bold = True
p.font.color.rgb = COLOR_CARD_ACCENT_BG

p = tf_final.add_paragraph()
p.text = "[1] MatSciBERT (Gupta et al., 2022) | [2] Zhang et al., Digital Discovery (2023) | [3] MaTableGPT (Yi et al., 2025) | [4] MatSKRAFT (Hira et al., 2025) | [5] Dreger et al., Adv. Intell. Syst. (2025)"
p.font.name = FONT_BODY
p.font.size = Pt(8.5)
p.font.color.rgb = COLOR_CARD_ACCENT_BG
p.space_before = Pt(1.5)

p = tf_final.add_paragraph()
p.text = "“CrystaGraph extends research-oriented material information extraction toward an integrated environment for multi-paper knowledge extraction, relationship discovery and interactive exploration.”"
p.font.name = FONT_BODY
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(3)

add_footer(s12, 12, "BML Munjal University — Department of Computer Science & Engineering")

# Save Presentation
output_path = os.path.join(PROJECT_ROOT, "CrystaGraph_Project4_Presentation.pptx")
prs.save(output_path)
print(f"[SUCCESS] Updated 12-slide presentation generated successfully at: {output_path}")
