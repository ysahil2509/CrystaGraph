import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

PRIMARY_BLUE = RGBColor(0x2F, 0x54, 0x96)
NAVY_BLUE = RGBColor(0x1F, 0x37, 0x63)
DARK_TEXT = RGBColor(0x22, 0x22, 0x22)
MUTED_TEXT = RGBColor(0x55, 0x55, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

def strip_emojis(text):
    # Regex to remove emojis and symbol blocks
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub("", text)
    # Also clean any duplicate spaces caused by removal
    cleaned = re.sub(r' +', ' ', cleaned).strip()
    return cleaned

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
    text = strip_emojis(text)
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
            run.font.color.rgb = RGBColor(0x1F, 0x37, 0x63)
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
        cells = [strip_emojis(c.strip()) for c in l.strip('|').split('|')]
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
    run = p.add_run(strip_emojis(code_text))
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
            r_cap = p_cap.add_run(strip_emojis(caption))
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(9.5)
            r_cap.italic = True
            r_cap.font.color.rgb = MUTED_TEXT

def build_clean_docx():
    print("Building clean, professional PROJECT_IV_REPORT_CRYSTAGRAPH.docx without emojis...")
    doc = docx.Document()
    
    # Page setup - A4, 1.0 inch margins
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # 1. CLEAN ACADEMIC COVER PAGE
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
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
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("on")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.italic = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("CrystaGraph: AI-Driven Materials Knowledge Mining and Cross-Paper Synthesis Platform")
    r.font.name = "Times New Roman"
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = NAVY_BLUE

    # University Logo
    add_image_if_exists(doc, "assets/bmu_logo.png", width=3.0)

    # Authors
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Submitted by:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

    authors = [
        ("Sahil Yadav", "230860"),
        ("Ayush Yadav", "230517"),
        ("Nitin Yadav", "230771"),
        ("Harshdeep Dhull", "230792")
    ]
    for name, roll in authors:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(f"{name} (Roll No. {roll})")
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("Under the mentorship of:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("Dr. Arijit Maitra")
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

    # Read markdown source
    with open("PROJECT_IV_REPORT_CRYSTAGRAPH.md", "r") as f:
        md_text = f.read()

    parts = md_text.split("---")
    body_text = "\n---\n".join(parts[1:])
    
    tokens = re.split(r'(```[a-zA-Z0-9_-]*\n.*?```)', body_text, flags=re.DOTALL)
    
    for token in tokens:
        if not token.strip():
            continue
            
        if token.startswith("```"):
            m = re.match(r'```([a-zA-Z0-9_-]*)\n(.*?)```', token, flags=re.DOTALL)
            if m:
                lang = m.group(1).strip()
                code_body = m.group(2).strip()
                if lang == "mermaid":
                    if "flowchart" in code_body:
                        diag_title = "System Execution & Data Flow Hierarchy"
                    elif "sequenceDiagram" in code_body:
                        diag_title = "Multi-Paper Batch Processing & Cross-Synthesis Sequence"
                    elif "erDiagram" in code_body:
                        diag_title = "Relational & Materials Knowledge Graph Entity Relationship Model"
                    else:
                        diag_title = "Architectural Process Flowchart"
                    
                    p_box = doc.add_paragraph()
                    p_box.paragraph_format.space_before = Pt(4)
                    p_box.paragraph_format.space_after = Pt(4)
                    r_b = p_box.add_run(f"[Workflow Architecture: {diag_title}]")
                    r_b.bold = True
                    r_b.font.color.rgb = PRIMARY_BLUE
                    r_b.font.size = Pt(10.5)
                else:
                    format_code_box(doc, code_body)
            continue
            
        sub_tokens = re.split(r'(\n\|.+?\n\|[-: |]+\n(?:\|.+?\n)+)', token)
        for sub in sub_tokens:
            if not sub.strip():
                continue
            if sub.strip().startswith('|') and ('\n|' in sub):
                format_markdown_table(doc, sub)
                continue
                
            lines = sub.splitlines()
            idx = 0
            while idx < len(lines):
                line = lines[idx].strip()
                idx += 1
                if not line or line == "---":
                    continue
                    
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    heading_text = strip_emojis(line.lstrip("#").strip())
                    
                    if level == 1 or "CHAPTER" in heading_text or "DECLARATION" in heading_text or "ABSTRACT" in heading_text or "TABLE OF CONTENTS" in heading_text or "REFERENCES" in heading_text or heading_text == "APPENDIX":
                        doc.add_page_break()
                        
                    p_h = doc.add_paragraph()
                    p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    
                    if level == 1:
                        p_h.paragraph_format.space_before = Pt(14)
                        p_h.paragraph_format.space_after = Pt(6)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(heading_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(16)
                        r_h.bold = True
                        r_h.font.color.rgb = PRIMARY_BLUE
                    elif level == 2:
                        p_h.paragraph_format.space_before = Pt(12)
                        p_h.paragraph_format.space_after = Pt(4)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(heading_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(14)
                        r_h.bold = True
                        r_h.font.color.rgb = PRIMARY_BLUE
                    elif level == 3:
                        p_h.paragraph_format.space_before = Pt(10)
                        p_h.paragraph_format.space_after = Pt(3)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(heading_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(12)
                        r_h.bold = True
                        r_h.font.color.rgb = NAVY_BLUE
                    else:
                        p_h.paragraph_format.space_before = Pt(8)
                        p_h.paragraph_format.space_after = Pt(2)
                        p_h.paragraph_format.keep_with_next = True
                        r_h = p_h.add_run(heading_text)
                        r_h.font.name = "Times New Roman"
                        r_h.font.size = Pt(11)
                        r_h.bold = True
                        r_h.font.italic = True
                        r_h.font.color.rgb = DARK_TEXT
                    
                    # Embed relevant figures with clean academic captions
                    if "4.1 Global Architectural Framework" in heading_text:
                        add_image_if_exists(doc, "assets/crystagraph_architecture.jpg", caption="Figure 4.1: CrystaGraph End-to-End Architectural Pipeline & Multi-Paper Ingestion Engine", width=5.8)
                    elif "4.4 Database Schema & Graph Representation" in heading_text:
                        add_image_if_exists(doc, "assets/screenshot_knowledge_graph.png", caption="Figure 4.2: Materials Knowledge Graph Network Representation", width=5.6)
                    elif "4.5 Clean ChatGPT-Style Front-End Workstation" in heading_text:
                        add_image_if_exists(doc, "assets/screenshot_dashboard.png", caption="Figure 4.3: CrystaGraph AI Copilot Web Interface", width=5.6)
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
    print(f"SUCCESS: Generated clean, professional {output_path} ({file_size_kb:.1f} KB)")

if __name__ == "__main__":
    build_clean_docx()
