import re
import streamlit as st
import pandas as pd
import graphviz



### Tokenize
def extract_tokens(expr):
    patterns = [
        ('ASSIGN', r'='),
        ('AND', r'&&'),
        ('OR', r'\|\|'),
        ('NOT', r'!'),
        ('EQUAL', r'=='),
        ('NOT_EQUAL', r'!='),
        ('LESSTHAN_EQUAL', r'<='), 
        ('GREATERTHAN_EQUAL', r'>='),
        ('LESSTHAN', r'<'), 
        ('GREATERTHAN', r'>'),
        ('PLUS', r'\+'), 
        ('MINUS', r'-'),
        ('MULT', r'\*'), 
        ('DIV', r'/'),
        ('LEFTPAREN', r'\('), 
        ('RIGHTPAREN', r'\)'),
        ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUM', r'\d+'),
        ('SPACE', r'[ \t]+')
    ]

    general_map = {
        'ID': 'Identifier',
        'NUM': 'Literal',
        'PLUS': 'Operator', 'MINUS': 'Operator', 'MULT': 'Operator', 'DIV': 'Operator',
        'ASSIGN': 'Operator', 'EQUAL': 'Operator', 'NOT_EQUAL': 'Operator',
        'LESSTHAN_EQUAL': 'Operator', 'GREATERTHAN_EQUAL': 'Operator', 'LESSTHAN': 'Operator', 'GREATERTHAN': 'Operator',
        'AND': 'Operator', 'OR': 'Operator', 'NOT': 'Operator',
        'LEFTPAREN': 'Delimiter', 'RIGHTPAREN': 'Delimiter'
    }

    token1 = []   # tokens for parser: (TYPE, LEXEME, START_POS)
    token2 = []   # for display: (Type, Lexeme)
    symbols = []  # for symbol table display: dict with position

    pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns)
    for m in re.finditer(pattern, expr):
        t_type = m.lastgroup
        t_val = m.group()
        start = m.start()
        if t_type == 'SPACE':
            continue
        if t_type in general_map:
            token1.append((t_type, t_val, start))
            token2.append((general_map[t_type], t_val))
            symbols.append({'Token': t_type, 'Lexeme': t_val, 'Position': start})
        else:
            # Tokenize error in the position
            raise ValueError(f"Unexpected symbol '{t_val}' at position {start}")
    return token1, token2, symbols




### Parser

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.nodes = []
        self.edges = []

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def match(self, typ):
        if self.current()[0] == typ:
            val = self.current()[1]
            self.pos += 1
            return val
        return None

    def expect(self, typ):
        val = self.match(typ)
        if not val:
            cur = self.current()
            pos = cur[2] if len(cur) > 2 else 'end'
            raise ValueError(f"Expected {typ}, found '{cur[1]}' at position {pos}")
        return val

    # S -> id = E | E
    def parse_S(self, parent=None):
        node_id = f"S_{len(self.nodes)}"
        self.nodes.append((node_id, "S", "non-terminal"))
        if parent:
            self.edges.append((parent, node_id))

        if self.current()[0] == 'ID' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == 'ASSIGN':
            id_val = self.match('ID')
            assign_val = self.match('ASSIGN')
            id_node = f"ID_{len(self.nodes)}"
            self.nodes.append((id_node, id_val, "terminal"))
            self.edges.append((node_id, id_node))
            assign_node = f"ASSIGN_{len(self.nodes)}"
            self.nodes.append((assign_node, assign_val, "terminal"))
            self.edges.append((node_id, assign_node))
            self.parse_E(node_id)
        else:
            self.parse_E(node_id)
        return node_id

    # E -> L E'
    def parse_E(self, parent):
        node_id = f"E_{len(self.nodes)}"
        self.nodes.append((node_id, "E", "non-terminal"))
        self.edges.append((parent, node_id))
        self.parse_L(node_id)
        self.parse_E_prime(node_id)
        return node_id

    # E' -> || L E' | ε
    def parse_E_prime(self, parent):
        node_id = f"E'_node_{len(self.nodes)}"
        self.nodes.append((node_id, "E'", "non-terminal"))
        self.edges.append((parent, node_id))
        if self.current()[0] == 'OR':
            or_val = self.match('OR')
            or_node = f"OR_{len(self.nodes)}"
            self.nodes.append((or_node, "||", "terminal"))
            self.edges.append((node_id, or_node))

            # after OR require a valid operand start
            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid expression after '||' near '{cur[1]}' at position {pos}")
            self.parse_L(node_id)
            self.parse_E_prime(node_id)
        else:
            eps_id = f"EPS_{len(self.nodes)}"
            self.nodes.append((eps_id, "ε", "epsilon"))
            self.edges.append((node_id, eps_id))

    # L -> R L'
    def parse_L(self, parent):
        node_id = f"L_{len(self.nodes)}"
        self.nodes.append((node_id, "L", "non-terminal"))
        self.edges.append((parent, node_id))
        self.parse_R(node_id)
        self.parse_L_prime(node_id)
        return node_id

    # L' -> && R L' | ε
    def parse_L_prime(self, parent):
        node_id = f"L'_node_{len(self.nodes)}"
        self.nodes.append((node_id, "L'", "non-terminal"))
        self.edges.append((parent, node_id))
        if self.current()[0] == 'AND':
            and_val = self.match('AND')
            and_node = f"AND_{len(self.nodes)}"
            self.nodes.append((and_node, "&&", "terminal"))
            self.edges.append((node_id, and_node))

            # after AND require valid operand start
            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid expression after '&&' near '{cur[1]}' at position {pos}")
            self.parse_R(node_id)
            self.parse_L_prime(node_id)
        else:
            eps_id = f"EPS_{len(self.nodes)}"
            self.nodes.append((eps_id, "ε", "epsilon"))
            self.edges.append((node_id, eps_id))

    # R -> A R'
    def parse_R(self, parent):
        node_id = f"R_{len(self.nodes)}"
        self.nodes.append((node_id, "R", "non-terminal"))
        self.edges.append((parent, node_id))
        self.parse_A(node_id)
        self.parse_R_prime(node_id)
        return node_id

    # R' -> (== | != | < | <= | > | >=) A R' | ε
    def parse_R_prime(self, parent):
        node_id = f"R'_node_{len(self.nodes)}"
        self.nodes.append((node_id, "R'", "non-terminal"))
        self.edges.append((parent, node_id))
        ops = ['EQUAL', 'NOT_EQUAL', 'LESSTHAN', 'GREATERTHAN', 'LESSTHAN_EQUAL', 'GREATERTHAN_EQUAL']
        if self.current()[0] in ops:
            op_type = self.current()[0]
            op_val = self.match(op_type)
            op_node = f"{op_type}_{len(self.nodes)}"
            self.nodes.append((op_node, op_val, "terminal"))
            self.edges.append((node_id, op_node))

            # after relational operator require operand start
            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid expression after relational operator near '{cur[1]}' at position {pos}")
            self.parse_A(node_id)
            self.parse_R_prime(node_id)
        else:
            eps_id = f"EPS_{len(self.nodes)}"
            self.nodes.append((eps_id, "ε", "epsilon"))
            self.edges.append((node_id, eps_id))

    # A -> T A'
    def parse_A(self, parent):
        node_id = f"A_{len(self.nodes)}"
        self.nodes.append((node_id, "A", "non-terminal"))
        self.edges.append((parent, node_id))
        self.parse_T(node_id)
        self.parse_A_prime(node_id)
        return node_id

    # A' -> + T A' | - T A' | ε
    def parse_A_prime(self, parent):
        node_id = f"A'_node_{len(self.nodes)}"
        self.nodes.append((node_id, "A'", "non-terminal"))
        self.edges.append((parent, node_id))
        if self.current()[0] in ['PLUS', 'MINUS']:
            op_type = self.current()[0]
            op_val = self.match(op_type)

            # require a valid operand start after binary +/- 
            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid expression: unexpected token '{cur[1]}' after '{op_val}' at position {pos}")
            op_node = f"OP_{len(self.nodes)}"
            self.nodes.append((op_node, op_val, "terminal"))
            self.edges.append((node_id, op_node))
            self.parse_T(node_id)
            self.parse_A_prime(node_id)
        else:
            eps_id = f"EPS_{len(self.nodes)}"
            self.nodes.append((eps_id, "ε", "epsilon"))
            self.edges.append((node_id, eps_id))

    # T -> F T'
    def parse_T(self, parent):
        node_id = f"T_{len(self.nodes)}"
        self.nodes.append((node_id, "T", "non-terminal"))
        self.edges.append((parent, node_id))
        self.parse_F(node_id)
        self.parse_T_prime(node_id)
        return node_id

    # T' -> * F T' | / F T' | ε
    def parse_T_prime(self, parent):
        node_id = f"T'_node_{len(self.nodes)}"
        self.nodes.append((node_id, "T'", "non-terminal"))
        self.edges.append((parent, node_id))
        if self.current()[0] in ['MULT', 'DIV']:
            op_type = self.current()[0]
            op_val = self.match(op_type)

            # require a valid operand start after * or /
            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid expression: unexpected token '{cur[1]}' after '{op_val}' at position {pos}")
            op_node = f"OP_{len(self.nodes)}"
            self.nodes.append((op_node, op_val, "terminal"))
            self.edges.append((node_id, op_node))
            self.parse_F(node_id)
            self.parse_T_prime(node_id)
        else:
            eps_id = f"EPS_{len(self.nodes)}"
            self.nodes.append((eps_id, "ε", "epsilon"))
            self.edges.append((node_id, eps_id))

    # F -> (E) | -F | !F | id | num
    def parse_F(self, parent):
        node_id = f"F_{len(self.nodes)}"
        self.nodes.append((node_id, "F", "non-terminal"))
        self.edges.append((parent, node_id))

        if self.current()[0] == 'LEFTPAREN':
            self.match('LEFTPAREN')
            self.parse_E(node_id)
            self.expect('RIGHTPAREN')
        elif self.current()[0] in ['MINUS', 'NOT']:
            tok = self.current()[0]

            if tok == 'MINUS':
                prev_tok = self.tokens[self.pos - 1][0] if self.pos > 0 else None
                if not (self.pos == 0 or prev_tok == 'LEFTPAREN' or prev_tok == 'ASSIGN'):
                    cur = self.current()
                    pos = cur[2] if len(cur) > 2 else 'end'
                    raise ValueError(f"Invalid unary '-' near '{cur[1]}' at position {pos}")
                
            op_val = self.match(tok)
            op_node = f"UNARY_{len(self.nodes)}"
            self.nodes.append((op_node, op_val, "terminal"))
            self.edges.append((node_id, op_node))

            if self.current()[0] not in ['ID', 'NUM', 'LEFTPAREN', 'MINUS', 'NOT']:
                cur = self.current()
                pos = cur[2] if len(cur) > 2 else 'end'
                raise ValueError(f"Invalid unary expression near '{op_val}' at position {pos}")
            self.parse_F(node_id)
        elif self.current()[0] in ['ID', 'NUM']:
            val = self.match(self.current()[0])
            leaf = f"VAL_{len(self.nodes)}"
            self.nodes.append((leaf, val, "terminal"))
            self.edges.append((node_id, leaf))
        else:
            cur = self.current()
            pos = cur[2] if len(cur) > 2 else 'end'
            raise ValueError(f"Unexpected symbol: '{cur[1]}' at position {pos}")



### Parse Tree Graph
def make_tree(parser):
    dot = graphviz.Digraph(format='png')
    for n_id, label, n_type in parser.nodes:
        if n_type == "non-terminal":
            dot.node(n_id, label, shape="box", style="filled", color="#cce5ff")
        elif n_type == "terminal":
            dot.node(n_id, label, shape="ellipse", style="filled", color="#ffe599")
        elif n_type == "epsilon":
            dot.node(n_id, label, shape="ellipse", style="filled", color="#d9d9d9")
    for parent, child in parser.edges:
        dot.edge(parent, child)
    return dot


### Streamlit UI

st.set_page_config(page_title="Lexical Analyzer & Parser", layout="centered")

st.markdown("""<style>
            
body { background: linear-gradient(135deg, #f0e6ff 0%, #ffffff 100%); font-family: 'Segoe UI', sans-serif; }
.header { text-align: center; background: linear-gradient(90deg, #4B0082, #8A2BE2); padding: 0.3rem 1rem; border-radius: 18px; color: white; margin-bottom: 2rem; box-shadow: 0px 4px 20px rgba(0,0,0,0.2); }
.header h1 { font-size: 2.5rem; font-weight: 700; margin: 0;}
.header p { font-size: 1.1rem; color: #f1f1f1; margin-top: 0.5rem;}
.card { background: rgba(255, 255, 255, 0.8); border-radius: 16px; padding: 1.8rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 1.8rem; backdrop-filter: blur(10px); transition: transform 0.2s ease, box-shadow 0.2s ease;}
.card:hover { transform: translateY(-4px); box-shadow: 0 6px 18px rgba(0,0,0,0.15); }
.section-title { font-size: 1.4rem; font-weight: 600; color: #4B0082; border-left: 4px solid #8A2BE2; padding-left: 10px; margin-bottom: 1rem;}
.result-valid { background: linear-gradient(90deg, #d1fadd, #b8eac6); color: #005b2c; border-left: 6px solid #00a04b; padding: 12px; border-radius: 10px; font-weight: 600; }
.result-invalid { background: linear-gradient(90deg, #ffd7d7, #ffbfbf); color: #a80000; border-left: 6px solid #ff0000; padding: 12px; border-radius: 10px; font-weight: 600; }
.stTextInput > div > div > input { border-radius: 10px; border: 1px solid #8A2BE2; }
.stButton>button { background: linear-gradient(90deg, #4B0082, #8A2BE2); color: white; border: none; border-radius: 10px; padding: 0.6rem 1.4rem; font-weight: 600; transition: 0.3s ease; }
.stButton>button:hover { background: linear-gradient(90deg, #3b0069, #732bbd); transform: scale(1.03); }
            
.block-container { padding-top: 5.5rem; padding-bottom: 0.5rem; margin-top: -2rem;}

</style>""", unsafe_allow_html=True)

st.markdown("""<div class="header">
<h1>Lexical Analyzer & Parser</h1>
<p>Enter an arithmetic or logical expression to see tokens, symbol table, and parse tree.</p>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Enter Expression or Upload a File</div>', unsafe_allow_html=True)





### Expression Input Section

# Enter Exppression Option
expr_input = st.text_input(
    "Enter Expression:",
    placeholder="Example: x=(a+b)*3 || !(a>2 && b<=5)"
)

# File Upload (Only one expression can be taken from the file)
uploaded_file = st.file_uploader(
    "Or upload a file containing an expression (.txt):", 
    type=["txt"]
)
if uploaded_file is not None:
    expr_input = uploaded_file.read().decode("utf-8").strip()
    st.success("Good! Expression successfully loaded from file!")
    
    # CSS for uploaded expression
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #e6e0ff, #f8f4ff); 
            border-radius: 16px; 
            padding: 1rem; 
            font-family: 'Segoe UI', sans-serif; 
            font-size: 20px; 
            color: #1a1a1a; 
            margin-bottom: 1.8rem;
            white-space: pre-wrap;
            overflow-wrap: break-word;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            ">
        {expr_input}
        </div>
        """,
        unsafe_allow_html=True
    )

### Analyze Button
if st.button("Analyze"):
    if not expr_input.strip():
        st.warning("Please enter an expression or upload a file")
    else:
        try:
            token3, token4, symbols = extract_tokens(expr_input)
            parser = Parser(token3)
            root = parser.parse_S()

            if parser.current()[0] != 'EOF':
                cur = parser.current()
                pos = cur[2] if len(cur) > 2 else None
                reason = f"Extra token '{cur[1]}' (type {cur[0]}) starting at position {pos}." if pos is not None else f"Extra token '{cur[1]}' (type {cur[0]})."
                st.markdown('<div class="result-invalid , card">Ooops!! Expression is INVALID </div>', unsafe_allow_html=True)
                st.error(reason)

                if pos is not None:
                    pointer = ' ' * pos + '^'
                    st.code(expr_input + '\n' + pointer)
            else:
                # Display valid expression
                st.markdown('<div class="result-valid , card">Expression is VALID</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">Lexical Analysis</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Tokens Table**")
                st.dataframe(pd.DataFrame(token4, columns=["Token Type", "Lexeme"]), use_container_width=True)
            with col2:
                st.write("**Symbol Table**")
                symbol_table_df = pd.DataFrame(symbols).drop(columns=['Position'], errors='ignore')
                st.dataframe(symbol_table_df, use_container_width=True)

            st.markdown('<div class="section-title"> Parse Tree </div>', unsafe_allow_html=True)
            if parser.nodes:
                st.graphviz_chart(make_tree(parser))

        except ValueError as e:
            # Display invalid expression
            st.markdown('<div class="result-invalid , card">Ooops!! Expression is INVALID </div>', unsafe_allow_html=True)

            reason = str(e)
            pos = None
            if 'parser' in locals():
                cur = parser.current()
                if len(cur) > 2:
                    pos = cur[2]
            # Showing the error in the position
            st.error(reason)
            if pos is not None:
                pointer = ' ' * pos + '^'
                st.code(expr_input + '\n' + pointer)




### View Grammar Rule used in this code (For understanding only)

# CSS for Grammar Rule Output
grammar_html = """
<style>
.grammar { font-family: 'Courier New', monospace; line-height: 1.6; }
.nt { color: #1E90FF; font-weight: bold; }       
.tok { color: #FF4500; }                      
.idnum { color: #008000; }                  
.epsilon { color: #808080; }                    
.start { color: #4B0082; font-weight: bold; }   
</style>

<div class="grammar">
<span class="start">S</span> → <span class="idnum"> id </span> = <span class="nt"> E </span> | <span class="nt"> E </span><br>
<span class="nt">E</span> → <span class="nt">L</span> <span class="nt">E′</span><br>
<span class="nt">E′</span> → <span class="tok">||</span> <span class="nt">L</span> <span class="nt">E′</span> | <span class="epsilon">ε</span><br>
<span class="nt">L</span> → <span class="nt">R</span> <span class="nt">L′</span><br>
<span class="nt">L′</span> → <span class="tok">&&</span> <span class="nt">R</span> <span class="nt">L′</span> | <span class="epsilon">ε</span><br>
<span class="nt">R</span> → <span class="nt">A</span> <span class="nt">R′</span><br>
<span class="nt">R′</span> → (<span class="tok">== </span> | <span class="tok"> != </span> | <span class="tok"> < </span> | <span class="tok"> <= </span> | <span class="tok"> > </span> | <span class="tok"> >= </span>) <span class="nt">A</span> <span class="nt">R′</span> | <span class="epsilon">ε</span><br>
<span class="nt">A</span> → <span class="nt">T</span> <span class="nt">A′</span><br>
<span class="nt">A′</span> → <span class="tok"> + </span> | <span class="tok"> - </span> <span class="nt">T</span> <span class="nt">A′</span> | <span class="epsilon">ε</span><br>
<span class="nt">T</span> → <span class="nt">F</span> <span class="nt">T′</span><br>
<span class="nt">T′</span> → <span class="tok">* </span> | <span class="tok">/ </span> <span class="nt">F</span> <span class="nt">T′</span> | <span class="epsilon">ε</span><br>
<span class="nt">F</span> → (<span class="nt">E</span>) | <span class="tok">-<span class="nt">F</span></span> | <span class="tok">!<span class="nt">F</span></span> | <span class="idnum">id | num</span>
</div>

"""

st.expander("View Grammar Rules").markdown(grammar_html, unsafe_allow_html=True)


