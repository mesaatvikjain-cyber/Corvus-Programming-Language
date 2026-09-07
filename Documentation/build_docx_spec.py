import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1B365D"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    lines = code_text.strip().split('\n')
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_callout(doc, title, text, bg_hex="EBF3FC", border_hex="2E5B88"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}\n")
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10.5)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    run_b = p.add_run(text)
    run_b.font.name = 'Calibri'
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def create_specification():
    doc = Document()
    
    # Page Setup
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    # Cover / Header Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Corvus Programming Language")
    r_title.font.name = 'Calibri Light'
    r_title.font.size = Pt(28)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run("Official Language Specification & Runtime Reference Manual\nVersion 0.1.1")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = RGBColor(0x55, 0x6B, 0x82)
    
    # Meta Box
    add_callout(doc, "Document Metadata", 
                "Author: Saatvik Jain (11-Year-Old Creator of Corvus)\n"
                "Version: 0.1.1 (Includes Interactive input(), Lambdas, OOP & Diagnostics)\n"
                "License: MIT Open Source License\n"
                "Repository: https://github.com/mesaatvikjain-cyber/Corvus-Programming-Language-",
                bg_hex="F0F4F8", border_hex="1B365D")
    
    doc.add_heading("1. Executive Summary & Design Philosophy", level=1)
    p = doc.add_paragraph(
        "Corvus is a modern, clean, general-purpose programming language designed to combine high programmer expressiveness "
        "with explicit structure and actionable developer diagnostics. Corvus eliminates ambiguity in block scoping by "
        "replacing indentation and curly brace conventions with bracket delimiters [ ... ], while providing explicit variable type "
        "declarations, first-class lambdas, object-oriented capabilities, and friendly diagnostic error pointers."
    )
    
    add_callout(doc, "The Story Behind Corvus",
                '"I got inspired to build my own programming language after watching a video about a programmer who created G# and C#. '
                'Since I already knew Python, I decided to take on the challenge and build my very own programming language from scratch!"\n'
                '— Saatvik Jain, Creator of Corvus')
    
    doc.add_heading("2. Lexical Structure & Tokens", level=1)
    doc.add_paragraph(
        "Corvus source text (.crv) is processed as UTF-8 encoded characters. The lexical analyzer (lexer) tokenizes input stream "
        "using regular expressions into 6 main token categories:"
    )
    
    # Table of Tokens
    tbl = doc.add_table(rows=1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = tbl.rows[0].cells
    hdr_cells[0].text = "Token Category"
    hdr_cells[1].text = "Keywords / Symbols"
    hdr_cells[2].text = "Description & Usage"
    
    for c in hdr_cells:
        set_cell_background(c, "1B365D")
        for p in c.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                
    token_data = [
        ("Keywords", "set, const, mk, givout, if, elsif, else, for, in, while, brk, con, try, error, final, true, fal, null, and, or, not, xor, async, awt, cls, global, pass, get, input", "Reserved keywords governing control flow, scoping, and declarations."),
        ("Data Types", "int, flo, str, bool, lis, tup, dic, func, lmb", "Type descriptors used in variable declarations (set <type>; name = val)."),
        ("Literals", "Numbers (42, 3.14), Strings (\"hello\"), Booleans (true, fal), null", "Primitive values represented directly in code."),
        ("Comments", "?{ block comment }", "Block comments delimited by ?{ and }."),
        ("Delimiters", "[ ] ( ) { } ; , . => ?", "Scope delimiters [ ], Lists { }, Tuples ([ ]), Function args ( ), Fat arrow =>.")
    ]
    
    for row_idx, (cat, sym, desc) in enumerate(token_data):
        row_cells = tbl.add_row().cells
        row_cells[0].text = cat
        row_cells[1].text = sym
        row_cells[2].text = desc
        bg = "FAFAFA" if row_idx % 2 == 0 else "FFFFFF"
        for c in row_cells:
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=100, right=100)
            
    doc.add_paragraph()
    
    doc.add_heading("3. Declarations, Typing & Statements", level=1)
    
    doc.add_heading("3.1 Variable & Constant Declarations", level=2)
    doc.add_paragraph("Variables in Corvus are explicitly typed using the 'set <type>; identifier = value' syntax:")
    add_code_block(doc, 
        'set int; count = 10\n'
        'set str; greeting = "Hello Corvus"\n'
        'set const; MAX_LIMIT = 100  ?{ Immutable constant }'
    )
    
    doc.add_heading("3.2 Function Declarations & Return Statements", level=2)
    doc.add_paragraph("Functions are declared using 'mk func name(params) [ ... ]' and return values using 'givout':")
    add_code_block(doc,
        'mk func factorial(n) [\n'
        '    if (n <= 1) [\n'
        '        givout 1\n'
        '    ]\n'
        '    givout n * factorial(n - 1)\n'
        ']'
    )
    
    doc.add_heading("3.3 Interactive Terminal Input (v0.1.1)", level=2)
    doc.add_paragraph("Interactive user input is prompted using the 'input(prompt)' keyword:")
    add_code_block(doc,
        'set str; user_name = input("Enter your name: ")\n'
        'log("Welcome,", user_name)\n'
        '\n'
        'set str; age_str = input("Enter your age: ")\n'
        'set int; age = int(age_str)\n'
        'log("Next year you will be:", age + 1)'
    )
    
    doc.add_heading("4. Control Flow & Error Recovery", level=1)
    
    doc.add_heading("4.1 Conditional Branching", level=2)
    add_code_block(doc,
        'if (score >= 90) [\n'
        '    log("Grade: A")\n'
        '] elsif (score >= 75) [\n'
        '    log("Grade: B")\n'
        '] else [\n'
        '    log("Grade: C")\n'
        ']'
    )
    
    doc.add_heading("4.2 Iteration Loops (while & for)", level=2)
    add_code_block(doc,
        'set int; i = 1\n'
        'while (i <= 3) [\n'
        '    log("Iteration:", i)\n'
        '    i = i + 1\n'
        ']\n'
        '\n'
        'set lis; items = {10, 20, 30}\n'
        'for (item in items) [\n'
        '    log("Item:", item)\n'
        ']'
    )
    
    doc.add_heading("4.3 Exception Handling (try / error / final)", level=2)
    add_code_block(doc,
        'try [\n'
        '    set int; result = 10 / 0\n'
        '] error(err) [\n'
        '    log("Caught runtime error ->", err["message"])\n'
        '] final [\n'
        '    log("Cleanup execution completed.")\n'
        ']'
    )
    
    doc.add_heading("5. Functional Lambdas & Object-Oriented Classes", level=1)
    
    doc.add_heading("5.1 First-Class Lambdas", level=2)
    add_code_block(doc,
        'set lmb; double_fn = lmb[x] => x * 2\n'
        'set lis; numbers = {1, 2, 3, 4, 5}\n'
        'set lis; doubled = numbers.map(double_fn)\n'
        'log("Doubled list:", doubled)'
    )
    
    doc.add_heading("5.2 Classes & Object Instantiation", level=2)
    add_code_block(doc,
        'cls Person() [\n'
        '    set str; name\n'
        '    set int; age\n'
        '\n'
        '    mk func init(name_val, age_val) [\n'
        '        self.name = name_val\n'
        '        self.age = age_val\n'
        '    ]\n'
        '\n'
        '    mk func describe() [\n'
        '        log("Person -> Name:", self.name, "| Age:", self.age)\n'
        '    ]\n'
        ']\n'
        '\n'
        'set Person; user = Person("Saatvik Jain", 11)\n'
        'user.describe()'
    )
    
    doc.add_heading("6. Built-in Standard Library & Modules", level=1)
    
    doc.add_heading("6.1 Math Module (`get math`)", level=2)
    add_code_block(doc,
        'get math\n'
        'log("Math PI constant:", math.pi)\n'
        'log("Square root of 64:", math.sqrt(64))\n'
        'log("2 to the power 8:", math.pow(2, 8))'
    )
    
    doc.add_heading("6.2 System Module (`get system`)", level=2)
    add_code_block(doc,
        'get system\n'
        'log("Operating system:", system.os)\n'
        'log("CLI Arguments:", system.args)'
    )
    
    doc.add_heading("7. Compiler Architecture & Internal Pipeline", level=1)
    doc.add_paragraph(
        "The Corvus execution engine consists of 5 modular Python components:"
    )
    
    comp_data = [
        ("Driver (Corvus.py)", "Loads source file, initiates pipeline, handles top-level fatal error catches."),
        ("Lexer (lexercorvus.py)", "Tokenizes input stream into Token objects while maintaining line and column offsets."),
        ("AST Nodes (astnodes.py)", "Dataclass representation of language primitives, control nodes, and expressions."),
        ("Parser (parsercorvus.py)", "Recursive-descent parser with operator precedence climbing."),
        ("Evaluator (evaluatorcorvus.py)", "Tree-walk interpreter managing lexically-scoped Environment stack and visitor dispatch."),
        ("Diagnostics (errors.py)", "Diagnostic exception system printing exact line/column caret pointers (^).")
    ]
    
    tbl_c = doc.add_table(rows=1, cols=2)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_c.rows[0].cells[0].text = "Component"
    tbl_c.rows[0].cells[1].text = "Responsibility & Pipeline Stage"
    set_cell_background(tbl_c.rows[0].cells[0], "1B365D")
    set_cell_background(tbl_c.rows[0].cells[1], "1B365D")
    for cell in tbl_c.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                
    for row_idx, (comp, desc) in enumerate(comp_data):
        row = tbl_c.add_row().cells
        row[0].text = comp
        row[1].text = desc
        bg = "FAFAFA" if row_idx % 2 == 0 else "FFFFFF"
        for cell in row:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            
    doc.add_paragraph()
    
    doc.add_heading("8. VS Code Tooling Integration", level=1)
    doc.add_paragraph(
        "Corvus features a complete, standalone VS Code language support extension packaged as corvus-language-support-0.1.0.vsix. "
        "It includes custom TextMate grammar definitions (corvus.tmLanguage.json), language configuration rules, code snippets, "
        "and automatic file association for .crv files."
    )
    
    out_path_1 = r"C:\Users\Saatvik Jain\.gemini\antigravity\scratch\Corvus\Corvus v0.1.0.docx"
    out_path_2 = r"C:\Users\Saatvik Jain\.gemini\antigravity\scratch\Corvus\Corvus v0.1.1 Specification.docx"
    
    doc.save(out_path_1)
    doc.save(out_path_2)
    print(f"Successfully generated specifications at {out_path_1} and {out_path_2}")

if __name__ == "__main__":
    create_specification()
