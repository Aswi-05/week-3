from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import sqlite3
import pandas as pd
import logging
import os

# Set up logging
logging.basicConfig(filename="operation_log.txt", level=logging.INFO)

# --- PDF FUNCTIONS ---

def merge_pdfs(pdf_list, output_path):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf.strip())
    merger.write(output_path)
    merger.close()
    print(f"Merged PDF saved to: {output_path}")
    log_operation(f"Merged PDFs into {output_path}")
    save_to_db(f"Merged PDFs into {output_path}")

def split_pdf(input_path, output_folder):
    reader = PdfReader(input_path)
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        output_file = os.path.join(output_folder, f"page_{i+1}.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)
        print(f"Saved: {output_file}")
        log_operation(f"Split page {i+1} to {output_file}")
        save_to_db(f"Split page {i+1} to {output_file}")

# --- CALCULATOR FUNCTIONS ---

def calculator():
    try:
        a = float(input("Enter first number: "))
        op = input("Enter operator (+, -, *, /): ")
        b = float(input("Enter second number: "))

        if op == '+':
            result = a + b
        elif op == '-':
            result = a - b
        elif op == '*':
            result = a * b
        elif op == '/':
            result = a / b if b != 0 else "Error: Division by zero"
        else:
            result = "Invalid operator"

        print(f"Result: {result}")
        log_operation(f"{a} {op} {b} = {result}")
        save_to_db(f"{a} {op} {b} = {result}")
    except ValueError:
        print("Invalid input.")

# --- LOGGING & DATABASE ---

def log_operation(operation):
    logging.info(operation)

def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS history (operation TEXT)")
    conn.commit()
    conn.close()

def save_to_db(operation):
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (operation) VALUES (?)", (operation,))
    conn.commit()
    conn.close()

def export_history():
    conn = sqlite3.connect("history.db")
    df = pd.read_sql_query("SELECT * FROM history", conn)
    df.to_csv("operation_history.csv", index=False)
    print("History exported to operation_history.csv")
    conn.close()

# --- MAIN MENU ---

def main_menu():
    init_db()
    while True:
        print("\n--- PDF & Calculator Tool ---")
        print("1. Merge PDFs")
        print("2. Split PDF")
        print("3. Calculator")
        print("4. Export History (CSV)")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            files = input("Enter PDF file paths separated by commas: ").split(',')
            output = input("Enter output file path: ")
            merge_pdfs(files, output)
        elif choice == '2':
            file = input("Enter path of PDF to split: ")
            folder = input("Enter folder to save split files: ")
            if not os.path.exists(folder):
                os.makedirs(folder)
            split_pdf(file, folder)
        elif choice == '3':
            calculator()
        elif choice == '4':
            export_history()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()

