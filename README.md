# Lexical-and-Syntax-Analysis-Program
A Python implementation of a lexical analyzer that performs tokenization as part of the compiler front-end.
The program processes an input string or file, recognizes patterns using regular expressions, and outputs tokens including identifiers, keywords, literals, operators, and punctuation symbols.
This project was created for the PLCD assignment and serves as a foundational introduction to compiler construction concepts.


# Features
- **Token Recognition:** Identifies different token types including:
  - **Keywords:** `if`, `else`, `while`, `for`, `int`, etc.  
  - **Identifiers:** Variable and function names  
  - **Literals:** Numbers, strings, and constants  
  - **Operators:** Arithmetic (`+`, `-`, `*`, `/`), relational (`>`, `<`, `==`), logical (`&&`, `||`)  
  - **Punctuation and Separators:** `;`, `,`, `{`, `}`, `()`
- **Input Options:** Accepts input from a **text file** or **direct string input**.  
- **Output:** Displays a **token list with token type**, making it easy to understand the classification.  
- **Error Handling:** Handles invalid or unrecognized tokens gracefully.  
- **Educational Purpose:** Serves as a practical introduction to **compiler front-end design**.


# Instructions to run the code 
- **Open the code file in VS Code** 
- **Install these following packages using VS terminal** 
    • streamlit  
    • pandas   
    • graphviz  
    Use this command-    pip install streamlit pandas graphviz

  - **Then run the code using the following command in VS terminal**
    • python -m streamlit run "Lexical and Syntax Analysis Program.py" 
    or 
    • streamlit run "Lexical and Syntax Analysis Program.py"

- **After the UI appears in the browser. You can execute it by entering an expression or by uploading a file.** 

    - **If you are entering an expression,**
      - Enter arithmetic, logical, and relational expression and click the “Analyze” button. 
      - The application has the capability to accept the unary expression. (Only unary operator like minus( – ) and Logical Not ( ! ) will work)
              For example-  a+b 
                            A*B-C/D 
                            x=(a+b)*3 || !(a>2 && b<=5) 
                            y=!a+b
      
      - Invalid expressions will display an error message with the exact error position.
    
    - **If you are uploading a file,** 
      - Only .txt format file will accepted.   
      - It is designed to handle one expression at a time, so the uploaded file must contain only a single expression in one line. 
      - Then, the expression will be loaded and visible in the UI. After that click the “Analyze” button.  
      - For testing, I have uploaded some .txt files in the zip file.
