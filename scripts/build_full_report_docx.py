import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

PRIMARY_BLUE = RGBColor(0x2F, 0x54, 0x96)
NAVY_BLUE = RGBColor(0x1F, 0x37, 0x63)
DARK_TEXT = RGBColor(0x22, 0x22, 0x22)
MUTED_TEXT = RGBColor(0x55, 0x55, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

EMOJI_MAP = {
    "CANDIDATE’S DECLARATION": "📜 CANDIDATE’S DECLARATION",
    "SUPERVISOR’S DECLARATION": "🖋️ SUPERVISOR’S DECLARATION",
    "ACKNOWLEDGMENT": "🙏 ACKNOWLEDGMENT",
    "TABLE OF CONTENTS": "📑 TABLE OF CONTENTS",
    "ABSTRACT": "💡 ABSTRACT",
    "CHAPTER 1: INTRODUCTION": "🚀 CHAPTER 1: INTRODUCTION",
    "1.1 Context and Motivation": "1.1 Context and Motivation 🌍",
    "1.2 Limitations of Conventional Large Language Models (LLMs)": "1.2 Limitations of Conventional Large Language Models (LLMs) ⚠️",
    "1.3 Project Objectives and Scope": "1.3 Project Objectives and Scope 🎯",
    "1.4 Report Organization": "1.4 Report Organization 📂",
    "CHAPTER 2: LITERATURE REVIEW": "📚 CHAPTER 2: LITERATURE REVIEW",
    "2.1 Information Extraction in Materials Informatics": "2.1 Information Extraction in Materials Informatics 🔍",
    "2.2 Survey of Existing Scientific Table Parsers": "2.2 Survey of Existing Scientific Table Parsers 📑",
    "2.3 Unit Standardization and Chemical Ontology Linking": "2.3 Unit Standardization and Chemical Ontology Linking 🧪",
    "2.4 Comparative Synthesis of State-of-the-Art Approaches": "2.4 Comparative Synthesis of State-of-the-Art Approaches 📊",
    "CHAPTER 3: PROBLEM STATEMENT": "❗ CHAPTER 3: PROBLEM STATEMENT",
    "3.1 Formal Problem Definition": "3.1 Formal Problem Definition 📐",
    "3.2 Technical Bottlenecks": "3.2 Technical Bottlenecks 🧩",
    "CHAPTER 4: METHODOLOGY & SYSTEM ARCHITECTURE": "⚙️ CHAPTER 4: METHODOLOGY & SYSTEM ARCHITECTURE",
    "4.1 Global Architectural Framework": "4.1 Global Architectural Framework 🏛️",
    "4.2 Multi-Stage Execution Pipeline": "4.2 Multi-Stage Execution Pipeline 🔄",
    "4.2.1 Stage 1: Ingestion & Document Preprocessing": "4.2.1 Stage 1: Ingestion & Document Preprocessing 📥",
    "4.2.2 Stage 2: 2D Table Geometry & Span Re-Indexing Engine": "4.2.2 Stage 2: 2D Table Geometry & Span Re-Indexing Engine 📐",
    "4.2.3 Stage 3: Stoichiometric Boundary Validation & Formula Mining": "4.2.3 Stage 3: Stoichiometric Boundary Validation & Formula Mining ⚗️",
    "4.2.4 Stage 4: 32-Property Canonical SI Normalization Matrix": "4.2.4 Stage 4: 32-Property Canonical SI Normalization Matrix ⚖️",
    "4.2.5 Stage 5: Multi-Paper Cross-Synthesis & Automated Discrepancy Resolution": "4.2.5 Stage 5: Multi-Paper Cross-Synthesis & Automated Discrepancy Resolution 🔀",
    "4.3 Machine Learning Property Prediction Engine": "4.3 Machine Learning Property Prediction Engine 🤖",
    "4.3.1 Algorithm Selection & Rationale": "4.3.1 Algorithm Selection & Rationale 📈",
    "4.3.2 Mathematical Formulation": "4.3.2 Mathematical Formulation 🧮",
    "4.4 Database Schema & Graph Representation": "4.4 Database Schema & Graph Representation 🗄️",
    "4.5 Clean ChatGPT-Style Front-End Workstation": "4.5 Clean ChatGPT-Style Front-End Workstation 💻",
    "4.6 Dual-Tier Security & Resilient Authentication": "4.6 Dual-Tier Security & Resilient Authentication 🛡️",
    "CHAPTER 5: EXPERIMENTAL ANALYSIS, DEPLOYMENT & DISCUSSION OF RESULTS": "📊 CHAPTER 5: EXPERIMENTAL ANALYSIS, DEPLOYMENT & DISCUSSION OF RESULTS",
    "5.1 Experimental Setup & Benchmark Corpus": "5.1 Experimental Setup & Benchmark Corpus 🧪",
    "5.2 Document Parsing & Geometric Extraction Evaluation": "5.2 Document Parsing & Geometric Extraction Evaluation 🎯",
    "5.3 Unit Normalization & Stoichiometric Validity Results": "5.3 Unit Normalization & Stoichiometric Validity Results ✅",
    "5.4 Machine Learning Regression Benchmarks ($R^2$, RMSE, MAE)": "5.4 Machine Learning Regression Benchmarks ($R^2$, RMSE, MAE) 📈",
    "5.5 Multi-Paper Batch Synthesis Case Study (Ti-6Al-4V Discrepancy Resolution)": "5.5 Multi-Paper Batch Synthesis Case Study (Ti-6Al-4V Discrepancy Resolution) 🔬",
    "5.6 Production Cloud Deployment (Vercel & Railway/Koyeb)": "5.6 Production Cloud Deployment (Vercel & Railway/Koyeb) ☁️",
    "5.7 System Interface & Operational Screen Walkthrough": "5.7 System Interface & Operational Screen Walkthrough 🖥️",
    "CHAPTER 6: CONCLUSIONS AND FUTURE SCOPE": "🏁 CHAPTER 6: CONCLUSIONS AND FUTURE SCOPE",
    "6.1 Summary of Contributions": "6.1 Summary of Contributions 🏆",
    "6.2 System Limitations": "6.2 System Limitations ⚠️",
    "6.3 Future Research Directions": "6.3 Future Research Directions 🔭",
    "REFERENCES": "📖 REFERENCES",
    "APPENDIX": "📎 APPENDIX",
    "Appendix A: REST API Endpoint Catalog": "Appendix A: REST API Endpoint Catalog 🔌",
    "Appendix B: Automated Test Suite Output": "Appendix B: Automated Test Suite Output 🧪",
    "Appendix C: Production Deployment Infrastructure Specifications": "Appendix C: Production Deployment Infrastructure Specifications 🏗️"
}

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_formatted_runs(p, text, base_size=12, base_font="Times New Roman", is_header=False, text_color=DARK_TEXT, line_spacing=1.15):
    p.paragraph_format.line_spacing = line_spacing
    tokens = re.split(r'(\*\*.*?\*\*|`.*?`|\*.*?\*)', text)
    for tok in tokens:
        if not tok:
            continue
        run = p.add_run()
        run.font.name = base_font
        run.font.size = Pt(base_size)
        run.font.color.rgb = text_color
        
        if tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            run.text = tok[2:-2]
            run.bold = True
        elif tok.startswith('`') and tok.endswith('`') and len(tok) >= 2:
            run.text = tok[1:-1]
            run.font.name = "Consolas"
            run.font.size = Pt(base_size - 1)
            run.font.color.rgb = RGBColor(0x8B, 0x00, 0x00)
        elif tok.startswith('*') and tok.endswith('*') and len(tok) >= 2:
            run.text = tok[1:-1]
            run.italic = True
        else:
            run.text = tok

def format_markdown_table(doc, md_table_text):
    lines = [l.strip() for l in md_table_text.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return
    
    rows_data = []
    for l in lines:
        if re.match(r'^\|[-: |]+\|$', l):
            continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        rows_data.append(cells)
        
    if not rows_data:
        return
        
    cols_count = max(len(r) for r in rows_data)
    table = doc.add_table(rows=len(rows_data), cols=cols_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table)
    
    for row_idx, row_data in enumerate(rows_data):
        is_header = (row_idx == 0)
        for col_idx in range(cols_count):
            cell = table.cell(row_idx, col_idx)
            val = row_data[col_idx] if col_idx < len(row_data) else ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.05
            
            if is_header:
                set_cell_background(cell, "2F5496")
                set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
                run = p.add_run(val)
                run.bold = True
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)
                run.font.color.rgb = WHITE
            else:
                bg = "FFFFFF" if row_idx % 2 == 1 else "F9FAFB"
                set_cell_background(cell, bg)
                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                add_formatted_runs(p, val, base_size=9.5, is_header=False)
                
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def format_code_box(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.27)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:color="D0D7DE"/>
            <w:left w:val="single" w:sz="18" w:color="2F5496"/>
            <w:bottom w:val="single" w:sz="6" w:color="D0D7DE"/>
            <w:right w:val="single" w:sz="6" w:color="D0D7DE"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x24, 0x29, 0x2F)
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def add_image_if_exists(doc, img_path, caption="", width=5.5):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(width))
        if caption:
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(9.5)
            r_cap.italic = True
            r_cap.font.color.rgb = MUTED_TEXT

def build_docx():
    print("Building PROJECT_IV_REPORT_CRYSTAGRAPH.docx...")
    doc = docx.Document()
    
    # Page setup - A4, 1.0 inch margins
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # 1. COVER PAGE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("A")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("PROJECT-IV REPORT")
    r.font.name = "Times New Roman"
    r.font.size = Pt(20)
    r.bold = True
    r.font.color.rgb = PRIMARY_BLUE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("on")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("🔬 CrystaGraph: AI-Driven Materials Knowledge Mining and Cross-Paper Synthesis Platform")
    r.font.name = "Times New Roman"
    r.font.size = Pt(19)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE

    # University Logo
    add_image_if_exists(doc, "assets/bmu_logo.png", width=3.2)

    # Authors Table / Information
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Submitted by:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

    authors = [
        ("Sahil Yadav", "230860", "👨‍💻"),
        ("Ayush Yadav", "230517", "👨‍💻"),
        ("Nitin Yadav", "230771", "👨‍💻"),
        ("Harshdeep Dhull", "230792", "👨‍💻")
    ]
    for name, roll, icon in authors:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(f"{icon} {name} (Roll No. {roll})")
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Under the mentorship of:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("👨‍🏫 Dr. Arijit Maitra")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.font.color.rgb = PRIMARY_BLUE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Department of Computer Science and Engineering\nSchool of Engineering and Technology\nBML MUNJAL UNIVERSITY, GURUGRAM (INDIA)\nNovember 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

    doc.add_page_break()

    # Now parse the markdown content for chapters, declarations, tables, and figures
    with open("PROJECT_IV_REPORT_CRYSTAGRAPH.md", "r") as f:
        md_text = f.read()

    # Split into sections after frontmatter title block
    parts = md_text.split("---")
    
    # We will process all content from parts[1:] (Declaration onwards)
    body_text = "\n---\n".join(parts[1:])
    
    # Regex parser for markdown blocks:
    # 1. Code blocks: ```...```
    # 2. Markdown tables: |...|
    # 3. Headings: #, ##, ###, ####
    # 4. Paragraphs and bullet points
    
    # Let's tokenize by code blocks first
    tokens = re.split(r'(```[a-zA-Z0-9_-]*\n.*?```)', body_text, flags=re.DOTALL)
    
    for token in tokens:
        if not token.strip():
            continue
            
        if token.startswith("```"):
            m = re.match(r'```([a-zA-Z0-9_-]*)\n(.*?)```', token, flags=re.DOTALL)
            if m:
                lang = m.group(1).strip()
                code_body = m.group(2).strip()
                # Skip raw mermaid blocks from printing as raw text, but represent them elegantly
                if lang == "mermaid":
                    # Check what kind of mermaid diagram
                    if "flowchart" in code_body:
                        diag_title = "System Flow & Execution Hierarchy Diagram"
                    elif "sequenceDiagram" in code_body:
                        diag_title = "Multi-Paper Batch Processing & Cross-Synthesis Sequence Diagram"
                    elif "erDiagram" in code_body:
                        diag_title = "Relational & Materials Knowledge Graph Entity Relationship Model"
                    else:
                        diag_title = "Architectural Process Flowchart"
                    
                    p_box = doc.add_paragraph()
                    p_box.paragraph_format.space_before = Pt(4)
                    p_box.paragraph_format.space_after = Pt(4)
                    r_b = p_box.add_run(f"📊 [Workflow Architecture Diagram: {diag_title}]")
                    r_b.bold = True
                    r_b.font.color.rgb = PRIMARY_BLUE
                    r_b.font.size = Pt(11)
                else:
                    format_code_box(doc, code_body)
            continue
            
        # If not a code block, split by tables
        sub_tokens = re.split(r'(\n\|.+?\n\|[-: |]+\n(?:\|.+?\n)+)', token)
        for sub in sub_tokens:
            if not sub.strip():
                continue
            if sub.strip().startswith('|') and ('\n|' in sub):
                format_markdown_table(doc, sub)
                continue
                
            # Now process normal paragraphs, headings, bullet lists
            lines = sub.splitlines()
            idx = 0
            while idx < len(lines):
                line = lines[idx].strip()
                idx += 1
                if not line or line == "---":
                    if line == "---":
                        pass
                    continue
                    
                # Check for headings
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    heading_text = line.lstrip("#").strip()
                    
                    # Apply emoji map if present
                    display_text = EMOJI_MAP.get(heading_text, heading_text)
                    
                    # If this is a major chapter (H1) or major declaration, add page break
                    if level == 1 or "CHAPTER" in heading_text or "DECLARATION" in heading_text or "ABSTRACT" in heading_text or "TABLE OF CONTENTS" in heading_text or "REFERENCES" in heading_text or heading_text == "APPENDIX":
                        doc.add_page_break()
                        
                    p_h = doc.add_paragraph()
                    p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
                    if level == 1:
                        p_h.paragraph_format.space_before = Pt(14)
                        p_h.paragraph_format.space_after = Pt(6)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(display_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(16)
                        r_h.bold = True
                        r_h.font.color.rgb = PRIMARY_BLUE
                    elif level == 2:
                        p_h.paragraph_format.space_before = Pt(12)
                        p_h.paragraph_format.space_after = Pt(4)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(display_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(14)
                        r_h.bold = True
                        r_h.font.color.rgb = PRIMARY_BLUE
                    elif level == 3:
                        p_h.paragraph_format.space_before = Pt(10)
                        p_h.paragraph_format.space_after = Pt(3)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(display_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(12.5)
                        r_h.bold = True
                        r_h.font.color.rgb = NAVY_BLUE
                    else:
                        p_h.paragraph_format.space_before = Pt(8)
                        p_h.paragraph_format.space_after = Pt(2)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(display_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(11.5)
                        r_h.bold = True
                        r_h.font.italic = True
                        r_h.font.color.rgb = DARK_TEXT
                    
                    # Embed relevant figures automatically after key section headings!
                    if "4.1 Global Architectural Framework" in heading_text:
                        add_image_if_exists(doc, "assets/crystagraph_architecture.jpg", caption="Figure 4.1: CrystaGraph End-to-End Architectural Pipeline & Multi-Paper Ingestion Engine", width=5.8)
                    elif "4.4 Database Schema & Graph Representation" in heading_text:
                        add_image_if_exists(doc, "assets/screenshot_knowledge_graph.png", caption="Figure 4.2: Neo4j / NetworkX Materials Knowledge Graph Visualization", width=5.6)
                    elif "4.5 Clean ChatGPT-Style Front-End Workstation" in heading_text:
                        add_image_if_exists(doc, "assets/screenshot_dashboard.png", caption="Figure 4.3: CrystaGraph Next.js 14 AI Copilot Workstation Interface", width=5.6)
                    elif "5.7 System Interface & Operational Screen Walkthrough" in heading_text:
                        add_image_if_exists(doc, "assets/screenshot_table_explorer.png", caption="Figure 5.1: Multi-Paper Table Extraction & Property Canonicalization View", width=5.6)
                        add_image_if_exists(doc, "assets/screenshot_material_explorer.png", caption="Figure 5.2: Materials Explorer & Stoichiometric Database View", width=5.6)
                        add_image_if_exists(doc, "assets/screenshot_property_predictor.png", caption="Figure 5.3: Random Forest & Gradient Boosted Property Predictor View", width=5.6)
                    continue

                # Bullet points
                if line.startswith("- ") or line.startswith("* "):
                    p_b = doc.add_paragraph()
                    p_b.paragraph_format.space_before = Pt(1)
                    p_b.paragraph_format.space_after = Pt(2)
                    p_b.paragraph_format.left_indent = Inches(0.25)
                    add_formatted_runs(p_b, "•  " + line[2:].strip(), base_size=11.5)
                    continue
                    
                # Numbered list
                m_num = re.match(r'^(\d+)\.\s+(.*)$', line)
                if m_num:
                    p_n = doc.add_paragraph()
                    p_n.paragraph_format.space_before = Pt(1)
                    p_n.paragraph_format.space_after = Pt(2)
                    p_n.paragraph_format.left_indent = Inches(0.25)
                    add_formatted_runs(p_n, f"{m_num.group(1)}.  {m_num.group(2).strip()}", base_size=11.5)
                    continue

                # Regular body paragraph
                p_text = doc.add_paragraph()
                p_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_text.paragraph_format.space_before = Pt(2)
                p_text.paragraph_format.space_after = Pt(5)
                add_formatted_runs(p_text, line, base_size=12, line_spacing=1.15)

    output_path = "PROJECT_IV_REPORT_CRYSTAGRAPH.docx"
    doc.save(output_path)
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"SUCCESS: Generated {output_path} ({file_size_kb:.1f} KB)")

if __name__ == "__main__":
    build_docx()
