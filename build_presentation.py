from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_CONNECTOR
from pathlib import Path

OUT = Path('Shortest_Route_Finder_DSA_Project.pptx')

# Project palette, taken from main.cpp's UI colors.
BG = RGBColor(14, 22, 38)
PANEL = RGBColor(21, 33, 54)
PANEL_LIGHT = RGBColor(27, 42, 67)
GRID = RGBColor(41, 58, 83)
WALL = RGBColor(8, 15, 28)
TEXT = RGBColor(232, 238, 247)
MUTED = RGBColor(143, 159, 181)
TEAL = RGBColor(76, 205, 190)
CORAL = RGBColor(255, 126, 143)
VISITED = RGBColor(48, 103, 151)
PATH = RGBColor(246, 198, 95)
INK = RGBColor(10, 17, 29)
WHITE = RGBColor(255, 255, 255)

FONT = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def set_bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, x, y, w, h, fill, line=None, radius=False, transparency=0):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.fill.transparency = transparency
    sh.line.color.rgb = line if line else fill
    sh.line.width = Pt(0.8)
    if radius:
        try:
            sh.adjustments[0] = 0.08
        except Exception:
            pass
    return sh


def line(slide, x1, y1, x2, y2, color=GRID, width=1.2, dash=None, begin=None, end=None):
    sh = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    sh.line.color.rgb = color
    sh.line.width = Pt(width)
    if dash:
        sh.line.dash_style = dash
    if begin:
        sh.line.begin_arrowhead = begin
    if end:
        sh.line.end_arrowhead = end
    return sh


def text(slide, value, x, y, w, h, size=18, color=TEXT, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0, italic=False,
         all_caps=False, line_spacing=1.05):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    run = p.add_run()
    run.text = value
    f = run.font
    f.name = font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    f.all_caps = all_caps
    return box


def rich_text(slide, runs, x, y, w, h, size=16, font=FONT, align=PP_ALIGN.LEFT,
              valign=MSO_ANCHOR.TOP, margin=0, line_spacing=1.05):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for item in runs:
        run = p.add_run()
        run.text = item.get('text', '')
        run.font.name = item.get('font', font)
        run.font.size = Pt(item.get('size', size))
        run.font.bold = item.get('bold', False)
        run.font.italic = item.get('italic', False)
        run.font.color.rgb = item.get('color', TEXT)
    return box


def pill(slide, label, x, y, w, fill, color=BG, size=10):
    rect(slide, x, y, w, 0.28, fill, fill, radius=True)
    text(slide, label, x, y+0.01, w, 0.25, size=size, color=color, bold=True,
         align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE, all_caps=True)


def footer(slide, num, source='Source: main.cpp + README.md'):
    line(slide, 0.55, 7.13, 12.78, 7.13, GRID, 0.7)
    text(slide, source, 0.58, 7.19, 5.5, 0.18, size=8.5, color=MUTED)
    text(slide, f'{num} / 8', 12.05, 7.17, 0.7, 0.2, size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def slide_heading(slide, kicker, title_value, subtitle=None, num=None):
    pill(slide, kicker, 0.62, 0.42, max(1.05, len(kicker)*0.075 + 0.36), TEAL, BG, size=9)
    text(slide, title_value, 0.62, 0.82, 12.1, 0.54, size=28, color=TEXT, bold=True)
    if subtitle:
        text(slide, subtitle, 0.64, 1.39, 11.9, 0.35, size=12.5, color=MUTED)
    if num:
        footer(slide, num)


def grid_visual(slide, x, y, rows=10, cols=10, cell=0.21, gap=0.025, variant='concept', label=True):
    # A visual model of the board; label clarifies when it is a zoomed conceptual view.
    walls = {(1,4),(1,5),(1,6),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(7,5),(7,6),(7,7),(3,7),(4,7),(5,7)}
    visited = {(5,2),(5,3),(6,2),(6,3),(6,4),(7,2),(7,3),(7,4),(8,3),(8,4),(8,5)}
    path = {(5,2),(6,2),(7,2),(8,2),(8,3),(8,4),(8,5),(8,6)}
    start = (5,1)
    finish = (8,6)
    for r in range(rows):
        for c in range(cols):
            fill = RGBColor(25, 39, 61)
            if variant == 'edit':
                if (r,c) in walls: fill = WALL
            elif variant == 'explore':
                if (r,c) in walls: fill = WALL
                elif (r,c) in visited: fill = VISITED
            elif variant == 'result':
                if (r,c) in walls: fill = WALL
                elif (r,c) in path: fill = PATH
                elif (r,c) in visited: fill = VISITED
            elif variant == 'concept':
                if (r,c) in walls: fill = WALL
            if (r,c) == start: fill = TEAL
            if (r,c) == finish: fill = CORAL
            rect(slide, x + c*(cell+gap), y + r*(cell+gap), cell, cell, fill, GRID, radius=False)
            if (r,c) in (start, finish) and cell >= 0.26:
                text(slide, 'S' if (r,c)==start else 'E', x+c*(cell+gap), y+r*(cell+gap)+0.005, cell, cell-0.01,
                     size=10, color=BG, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    if label:
        text(slide, '20 × 20 board', x, y + rows*(cell+gap)+0.08, 2.2, 0.2, size=9, color=MUTED)


def legend_item(slide, label, color, x, y, w=1.3):
    rect(slide, x, y+0.04, 0.14, 0.14, color, color)
    text(slide, label, x+0.22, y, w, 0.22, size=9.5, color=MUTED)


def code_panel(slide, title_value, lines, x, y, w, h, accent=TEAL):
    rect(slide, x, y, w, h, RGBColor(9, 16, 29), GRID, radius=True)
    rect(slide, x, y, w, 0.44, PANEL_LIGHT, PANEL_LIGHT, radius=True)
    rect(slide, x, y+0.38, w, 0.06, PANEL_LIGHT, PANEL_LIGHT)
    # small terminal dots
    for i, col in enumerate([CORAL, PATH, TEAL]):
        rect(slide, x+0.18+i*0.17, y+0.15, 0.08, 0.08, col, col, radius=True)
    text(slide, title_value, x+0.78, y+0.105, w-0.9, 0.2, size=10, color=MUTED, bold=True)
    # code lines
    code_box = slide.shapes.add_textbox(Inches(x+0.22), Inches(y+0.59), Inches(w-0.44), Inches(h-0.74))
    tf = code_box.text_frame
    tf.clear(); tf.word_wrap = False
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for idx, val in enumerate(lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.line_spacing = 1.0
        p.space_after = Pt(0)
        run = p.add_run(); run.text = val
        run.font.name = MONO; run.font.size = Pt(13.0); run.font.color.rgb = TEXT
    return code_box


def small_card(slide, x, y, w, h, number, title_value, body, accent=TEAL):
    rect(slide, x, y, w, h, PANEL, GRID, radius=True)
    pill(slide, number, x+0.18, y+0.18, 0.37, accent, BG, size=9)
    text(slide, title_value, x+0.68, y+0.18, w-0.86, 0.26, size=13.5, color=TEXT, bold=True)
    text(slide, body, x+0.2, y+0.58, w-0.4, h-0.72, size=10.5, color=MUTED, line_spacing=1.05)


def keycap(slide, label, x, y, w=0.58):
    rect(slide, x, y, w, 0.38, PANEL_LIGHT, GRID, radius=True)
    text(slide, label, x, y+0.04, w, 0.28, size=11, color=TEXT, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def mini_stage(slide, x, y, title_value, variant, caption, stage_num):
    rect(slide, x, y, 3.45, 3.85, PANEL, GRID, radius=True)
    pill(slide, f'0{stage_num}', x+0.18, y+0.18, 0.38, TEAL if stage_num==1 else (VISITED if stage_num==2 else PATH), BG, size=9)
    text(slide, title_value, x+0.68, y+0.18, 2.4, 0.25, size=14, color=TEXT, bold=True)
    grid_visual(slide, x+0.55, y+0.73, rows=10, cols=10, cell=0.22, gap=0.025, variant=variant, label=False)
    text(slide, caption, x+0.22, y+3.2, 3.0, 0.4, size=10.5, color=MUTED, align=PP_ALIGN.CENTER)

# Slide 1: Title
slide = prs.slides.add_slide(blank); set_bg(slide)
# subtle vertical accent
rect(slide, 0, 0, 0.16, 7.5, TEAL, TEAL)
pill(slide, 'DSA SUBJECT PROJECT', 0.7, 0.62, 2.02, TEAL, BG, size=10)
text(slide, 'Shortest Route\nFinder', 0.7, 1.28, 6.2, 1.55, size=34, color=TEXT, bold=True, line_spacing=0.92)
text(slide, "Visualizing Dijkstra’s algorithm on a 20 × 20 grid", 0.73, 3.03, 5.9, 0.42, size=14, color=MUTED)
text(slide, 'C++  ·  SFML 2.5.1  ·  Four-way movement', 0.73, 3.62, 5.8, 0.28, size=10.5, color=TEAL, bold=True)
# visual panel
rect(slide, 7.28, 0.65, 5.38, 4.62, PANEL, GRID, radius=True)
text(slide, 'THE IDEA', 7.66, 0.98, 1.2, 0.2, size=10, color=MUTED, bold=True)
text(slide, 'Cells become\na weighted graph.', 7.66, 1.35, 3.8, 0.78, size=22, color=TEXT, bold=True, line_spacing=0.95)
grid_visual(slide, 7.7, 2.55, rows=10, cols=10, cell=0.26, gap=0.026, variant='result', label=False)
legend_item(slide, 'Start', TEAL, 10.65, 2.78, 1.0)
legend_item(slide, 'Visited', VISITED, 10.65, 3.18, 1.0)
legend_item(slide, 'Path', PATH, 10.65, 3.58, 1.0)
legend_item(slide, 'Wall', WALL, 10.65, 3.98, 1.0)
text(slide, 'Watch the search expand, then reveal the route.', 10.65, 4.45, 1.7, 0.55, size=10.5, color=MUTED, line_spacing=1.0)
# member panel
rect(slide, 0.7, 4.52, 11.96, 1.94, PANEL, GRID, radius=True)
text(slide, 'TEAM', 1.0, 4.8, 0.8, 0.2, size=10, color=MUTED, bold=True)
team = [
    ('Sumedha Soni', 'RA2511030030013'),
    ('Tejas Chandola', 'RA2511030030029'),
    ('Vasu Parashar', 'RA2511030030054'),
    ('Paarth Daagar', 'RA2511030030061'),
]
for i, (name, ident) in enumerate(team):
    col = i % 2; row = i // 2
    x = 1.0 + col*5.65; y = 5.18 + row*0.55
    rect(slide, x, y+0.08, 0.11, 0.11, TEAL if i%2==0 else CORAL, TEAL if i%2==0 else CORAL, radius=True)
    text(slide, name, x+0.25, y, 2.2, 0.25, size=12.5, color=TEXT, bold=True)
    text(slide, ident, x+2.55, y+0.01, 2.5, 0.22, size=10.5, color=MUTED)
footer(slide, 1, 'Project presentation · C++ + SFML')

# Slide 2: graph model
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '01 · MODEL', 'How a grid becomes a graph', 'The board is a graph we can search one cell at a time.', 2)
# board area
rect(slide, 0.62, 1.93, 5.0, 4.72, PANEL, GRID, radius=True)
text(slide, 'Concept view of the board', 0.94, 2.2, 2.5, 0.25, size=13, color=TEXT, bold=True)
text(slide, 'A full board has 20 × 20 cells.', 0.94, 2.5, 3.5, 0.22, size=10, color=MUTED)
grid_visual(slide, 1.02, 2.95, rows=10, cols=10, cell=0.26, gap=0.028, variant='concept', label=False)
# neighbors arrows + callout
cx, cy = 3.28, 4.25
rect(slide, cx, cy, 0.32, 0.32, TEAL, TEAL)
for (x1,y1,x2,y2) in [(3.44,4.25,3.44,3.92),(3.44,4.57,3.44,4.90),(3.28,4.41,2.95,4.41),(3.60,4.41,3.93,4.41)]:
    line(slide, x1, y1, x2, y2, TEAL, 1.6, end=1)
legend_item(slide, 'Open cell', RGBColor(25,39,61), 0.98, 6.05, 1.2)
legend_item(slide, 'Wall', WALL, 2.55, 6.05, 1.0)
legend_item(slide, 'Start', TEAL, 3.76, 6.05, 0.9)
legend_item(slide, 'Destination', CORAL, 4.5, 6.05, 1.0)
# explanation cards
small_card(slide, 5.92, 1.93, 3.2, 1.35, '1', 'Cells are vertices', 'Each walkable square is one graph node.', TEAL)
small_card(slide, 9.32, 1.93, 3.38, 1.35, '2', 'Neighbors are edges', 'Only side-adjacent cells connect: four-way movement.', CORAL)
small_card(slide, 5.92, 3.48, 3.2, 1.35, '3', 'Walls remove edges', 'A wall cannot be entered, so that move is skipped.', PATH)
small_card(slide, 9.32, 3.48, 3.38, 1.35, '4', 'Every move costs 1', 'All open-cell edges have equal weight.', TEAL)
rect(slide, 5.92, 5.13, 6.78, 1.52, PANEL_LIGHT, PANEL_LIGHT, radius=True)
text(slide, 'GRID IN CODE', 6.22, 5.34, 1.15, 0.18, size=9.5, color=TEAL, bold=True)
text(slide, 'std::array<std::array<bool, COLS>, ROWS> walls{};', 7.55, 5.31, 4.65, 0.22, size=10.5, color=TEXT, font=MONO)
text(slide, 'ROUTE =', 6.22, 5.70, 1.0, 0.22, size=11, color=TEAL, bold=True)
text(slide, 'a sequence of connected, walkable cells', 7.22, 5.61, 4.9, 0.35, size=18, color=TEXT, bold=True)
text(slide, 'Dijkstra’s job is to choose the lowest-cost next cell.', 6.22, 6.20, 5.9, 0.25, size=11, color=MUTED)

# Slide 3: algorithm
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '02 · ALGORITHM', 'Dijkstra, in four simple steps', 'Because every move costs 1, the first finished route is shortest.', 3)
# top equation / queue
rect(slide, 0.62, 1.93, 12.08, 0.78, PANEL, GRID, radius=True)
text(slide, 'distance[start] = 0', 0.95, 2.17, 2.5, 0.24, size=15, color=TEAL, bold=True, font=MONO)
text(slide, 'all other distances = ∞', 3.95, 2.17, 2.8, 0.24, size=15, color=MUTED, bold=True, font=MONO)
text(slide, 'min-priority queue → smallest distance first', 7.6, 2.17, 4.55, 0.24, size=13, color=PATH, bold=True)
# cards
small_card(slide, 0.62, 3.05, 2.82, 2.1, '1', 'Initialize', 'Set the start to 0.\nEverything else begins at ∞.', TEAL)
small_card(slide, 3.58, 3.05, 2.82, 2.1, '2', 'Pop smallest', 'Take the cell with the lowest known distance.', CORAL)
small_card(slide, 6.54, 3.05, 2.82, 2.1, '3', 'Relax neighbors', 'For each valid neighbor, try:\ncurrent + 1.', PATH)
small_card(slide, 9.50, 3.05, 3.20, 2.1, '4', 'Remember & finish', 'Update distance + previous.\nStop when destination is reached.', TEAL)
# arrows between cards
for x in [3.32, 6.28, 9.24]:
    line(slide, x, 4.08, x+0.22, 4.08, TEAL, 1.5, end=1)
# mini trace
rect(slide, 0.62, 5.55, 12.08, 1.06, PANEL_LIGHT, PANEL_LIGHT, radius=True)
text(slide, 'MENTAL MODEL', 0.95, 5.8, 1.3, 0.18, size=9.5, color=MUTED, bold=True)
# node chain
nodes = [('S', TEAL), ('1', VISITED), ('2', VISITED), ('3', PATH), ('E', CORAL)]
startx = 3.0
for i, (lab, col) in enumerate(nodes):
    x = startx + i*1.08
    if i < len(nodes)-1:
        line(slide, x+0.28, 6.02, x+0.84, 6.02, GRID, 2.0, end=1)
    rect(slide, x, 5.77, 0.5, 0.5, col, col, radius=True)
    text(slide, lab, x, 5.87, 0.5, 0.25, size=12, color=BG, bold=True, align=PP_ALIGN.CENTER)
text(slide, 'Distances grow outward from S; the saved previous cell lets us rebuild the route backward.', 8.45, 5.84, 3.75, 0.43, size=10.5, color=MUTED)

# Slide 4: code
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '03 · CODE', 'The two lines of thinking inside the search', 'These snippets are taken from the project’s `main.cpp`.', 4)
# code panels
neighbor_lines = [
    'const int directions[4][2] = {',
    '    {-1, 0}, {1, 0}, {0, -1}, {0, 1}',
    '};',
    'for (const auto& direction : directions) {',
    '    Point next{current.row + direction[0],',
    '               current.col + direction[1]};',
    '    if (next.row < 0 || next.row >= ROWS ||',
    '        next.col < 0 || next.col >= COLS ||',
    '        walls[next.row][next.col]) continue;',
    '}',
]
update_lines = [
    'int newDistance = currentDistance + 1;',
    'if (newDistance < distance[next.row][next.col]) {',
    '    distance[next.row][next.col] = newDistance;',
    '    previous[next.row][next.col] = current;',
    '    queue.push({newDistance,',
    '                next.row * COLS + next.col});',
    '}',
]
code_panel(slide, 'main.cpp · neighbor check', neighbor_lines, 0.62, 1.95, 6.02, 3.95)
code_panel(slide, 'main.cpp · distance update', update_lines, 6.86, 1.95, 5.84, 3.95)
# explanations under code
rect(slide, 0.62, 6.12, 6.02, 0.66, PANEL, GRID, radius=True)
text(slide, 'WHY IT MATTERS', 0.86, 6.31, 1.3, 0.18, size=9.5, color=TEAL, bold=True)
text(slide, 'Bounds + walls keep the graph valid.', 2.3, 6.27, 3.95, 0.23, size=11.5, color=TEXT)
rect(slide, 6.86, 6.12, 5.84, 0.66, PANEL, GRID, radius=True)
text(slide, 'WHY IT MATTERS', 7.1, 6.31, 1.3, 0.18, size=9.5, color=PATH, bold=True)
text(slide, 'A better distance replaces the old one.', 8.54, 6.27, 3.75, 0.23, size=11.5, color=TEXT)

# Slide 5: visual result
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '04 · VISUALIZATION', 'From search state to on-screen route', 'The UI turns algorithm state into a story you can watch.', 5)
mini_stage(slide, 0.62, 1.95, 'Editing', 'edit', 'Place S, E, and walls.', 1)
mini_stage(slide, 4.38, 1.95, 'Exploring', 'explore', 'Visited cells appear first.', 2)
mini_stage(slide, 8.14, 1.95, 'Route ready', 'result', 'The shortest path turns gold.', 3)
line(slide, 4.08, 3.88, 4.3, 3.88, TEAL, 1.5, end=1)
line(slide, 7.84, 3.88, 8.06, 3.88, TEAL, 1.5, end=1)
# bottom explanation bar
rect(slide, 0.62, 6.08, 12.08, 0.64, PANEL_LIGHT, PANEL_LIGHT, radius=True)
text(slide, 'In code:', 0.92, 6.27, 0.75, 0.2, size=10, color=MUTED, bold=True)
text(slide, '`visited` reveals the frontier  →  `pathCells` reveals the rebuilt route', 1.75, 6.22, 6.9, 0.26, size=12, color=TEXT, bold=True, font=MONO)
text(slide, 'No route? The status panel reports it.', 9.3, 6.27, 2.8, 0.2, size=10.5, color=CORAL, bold=True, align=PP_ALIGN.RIGHT)

# Slide 6: controls and takeaways
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '05 · DEMO', 'How to run the demo — and what to remember', 'A simple flow for presenting the project aloud.', 6)
# left controls
rect(slide, 0.62, 1.95, 5.25, 4.55, PANEL, GRID, radius=True)
text(slide, 'DEMO FLOW', 0.94, 2.25, 1.3, 0.2, size=10, color=MUTED, bold=True)
steps = [
    ('01', 'Draw walls', 'Left-click + drag'),
    ('02', 'Choose start', 'Press S, then click'),
    ('03', 'Choose destination', 'Press E, then click'),
    ('04', 'Run Dijkstra', 'Press Space'),
    ('05', 'Reset', 'Press R'),
]
for i, (n, title_value, detail) in enumerate(steps):
    y = 2.72 + i*0.66
    pill(slide, n, 0.94, y, 0.42, TEAL if i<4 else CORAL, BG, size=8.5)
    text(slide, title_value, 1.58, y+0.01, 1.75, 0.22, size=12.5, color=TEXT, bold=True)
    text(slide, detail, 3.2, y+0.02, 2.1, 0.2, size=10.5, color=MUTED)
# right takeaways
rect(slide, 6.12, 1.95, 6.58, 4.55, PANEL, GRID, radius=True)
text(slide, 'KEY TAKEAWAYS', 6.45, 2.25, 1.6, 0.2, size=10, color=MUTED, bold=True)
small_card(slide, 6.45, 2.72, 5.92, 0.82, '1', 'Model first', 'A 20×20 grid becomes vertices + four-way edges.', TEAL)
small_card(slide, 6.45, 3.72, 5.92, 0.82, '2', 'Search smart', 'The priority queue always expands the lowest distance.', PATH)
small_card(slide, 6.45, 4.72, 5.92, 0.82, '3', 'Show the result', 'Visited cells explain the search; the gold path explains the answer.', CORAL)
rect(slide, 6.45, 5.83, 5.92, 0.36, PANEL_LIGHT, PANEL_LIGHT, radius=True)
text(slide, 'Start → map → Space → watch the route appear', 6.65, 5.9, 5.5, 0.2, size=11.5, color=TEXT, bold=True, align=PP_ALIGN.CENTER)

# Slide 7: DSA concepts only
slide = prs.slides.add_slide(blank); set_bg(slide)
slide_heading(slide, '06 · DSA CONCEPTS', 'The DSA ideas used in this project', 'Each concept has a direct role in finding and showing the route.', 7)
small_card(slide, 0.62, 1.95, 3.88, 1.55, '1', 'Graph representation', 'Grid cells are vertices; side-by-side cells are edges.', TEAL)
small_card(slide, 4.72, 1.95, 3.88, 1.55, '2', '2D array', 'The 20 × 20 board stores walls, distances, and states.', CORAL)
small_card(slide, 8.82, 1.95, 3.88, 1.55, '3', 'Weighted graph', 'Every open move has weight 1, so routes have a cost.', PATH)
small_card(slide, 0.62, 3.78, 3.88, 1.55, '4', 'Priority queue', 'The smallest distance is selected first.', TEAL)
small_card(slide, 4.72, 3.78, 3.88, 1.55, '5', 'Greedy choice', 'Dijkstra expands the currently cheapest known cell.', CORAL)
small_card(slide, 8.82, 3.78, 3.88, 1.55, '6', 'Relaxation', 'A shorter distance updates the neighbor and its predecessor.', PATH)
rect(slide, 0.62, 5.7, 12.08, 0.78, PANEL_LIGHT, PANEL_LIGHT, radius=True)
text(slide, 'PATH RECONSTRUCTION', 0.94, 5.95, 1.9, 0.2, size=9.5, color=TEAL, bold=True)
text(slide, 'The previous-cell array traces the final route back from destination to start.', 3.05, 5.90, 8.9, 0.27, size=13, color=TEXT, bold=True)

# Slide 8: Thank you
slide = prs.slides.add_slide(blank); set_bg(slide)
rect(slide, 0, 0, 0.16, 7.5, TEAL, TEAL)
text(slide, 'THANK YOU', 0.75, 1.88, 11.85, 0.72, size=40, color=TEXT, bold=True, align=PP_ALIGN.CENTER)
text(slide, 'Shortest Route Finder', 0.75, 2.82, 11.85, 0.35, size=18, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
text(slide, 'DSA Subject Project  ·  C++ + SFML', 0.75, 3.33, 11.85, 0.28, size=12, color=MUTED, align=PP_ALIGN.CENTER)
line(slide, 4.2, 4.15, 9.13, 4.15, GRID, 1.0)
text(slide, 'Sumedha Soni  ·  Tejas Chandola  ·  Vasu Parashar  ·  Paarth Daagar',
     0.75, 5.35, 11.85, 0.25, size=10.5, color=MUTED, align=PP_ALIGN.CENTER)
footer(slide, 8, 'Project presentation')

prs.save(OUT)
print(f'Wrote {OUT} with {len(prs.slides)} slides')
