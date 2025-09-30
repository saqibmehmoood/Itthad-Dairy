import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime
import csv
import base64
import os

# ---------- CONFIG ----------
TEMPLATE_PATH = r"C:\Users\samarahmad\Desktop\My Projects\Invoice-app\Template file .pdf"
OUTPUT_DIR = "."

# ---------- Overlay Generator ----------
def create_overlay_bytes(data, page_size):
    width, height = page_size
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    # ---------------- LOGO ----------------
    logo_path = r"C:\Users\samarahmad\Desktop\My Projects\Invoice-app\Logo.png"
    try:
        # top-left corner example (adjust X,Y as needed for your template)
        c.drawImage(logo_path, 40, height - 110, width=80, height=80,
                    preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print("Logo not found or error loading:", e)

    # ---------------- HEADER ----------------
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 40, "ITTHAD DAIRY FARM")

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 60, "Chak Mathroma, Darul Fazal, Rabwah")
    c.drawCentredString(width / 2, height - 75, "Contact: 0331-6198039")
    c.drawCentredString(width / 2, height - 90, "Love For All")

     # ---------------- CUSTOMER & INVOICE INFO ----------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 140, f"Bill To: {data['Name']}")

    c.setFont("Helvetica", 12)
    c.drawString(30, height - 160, f"Phone: {data['Phone']}")
    c.drawString(30, height - 180, f"Address: {data['Address']}")

    c.setFont("Helvetica", 12)
    c.drawRightString(width - 30, height - 140, f"Invoice No: {data['Invoice No']}")
    c.drawRightString(width - 30, height - 160, f"Date: {datetime.now().strftime('%d %b %Y')}")

    # ---------------- TABLE HEADER ----------------
    y = height - 200
    c.setFont("Helvetica-Bold", 12)
    c.line(30, y, width - 30, y)
    y -= 20
    c.drawString(40, y, "Description")
    c.drawString(240, y, "Quantity")
    c.drawString(340, y, "Unit Price")
    c.drawString(460, y, "Amount")
    y -= 10
    c.line(30, y, width - 30, y)

    # ---------------- TABLE ROW ----------------
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(40, y, "Milk (Buffalo)")
    c.drawString(240, y, f"{data['Total Quantity']} Liters")
    c.drawString(340, y, f"Rs. {data['Price per Liter']}")
    c.drawString(460, y, f"Rs. {data['Total Amount']}")

    # ---------------- TOTALS ----------------
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(440, y, "Total:")
    c.drawRightString(540, y, f"Rs. {data['Total Amount']}")

    y -= 20
    c.setFont("Helvetica", 12)
    c.drawRightString(440, y, "Due Amount:")
    c.drawRightString(540, y, f"Rs. {data['Due Amount']}")

    y -= 20
    c.drawRightString(440, y, "Payable:")
    c.drawRightString(540, y, f"Rs. {data['Payable']}")

    # ---------------- FOOTER ----------------
    y -= 60
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, "Payment Term : Account Holder : Inzimam Ul Haq : 03065278010 : JazzCash")

    y -= 70
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, "Thank you for your business!")

    c.save()
    packet.seek(0)
    return packet


# ---------- Merge Template + Overlay ----------
def generate_invoice(data, filename="invoice.pdf"):
    template_pdf = PdfReader(open(TEMPLATE_PATH, "rb"))
    page = template_pdf.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    overlay_bytes = create_overlay_bytes(data, (width, height))
    overlay_pdf = PdfReader(overlay_bytes)

    output = PdfWriter()
    page.merge_page(overlay_pdf.pages[0])
    output.add_page(page)

    with open(filename, "wb") as f:
        output.write(f)

    return filename


# ---------- CSV Logger ----------
def save_record(data):
    filename = "invoice_records.csv"
    headers = ["Invoice No", "Name", "Phone", "Address", "Total Quantity", "Price per Liter", "Total Amount", "Due Amount", "Payable", "Date"]

    try:
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if f.tell() == 0:
                writer.writeheader()
            data["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(data)
    except Exception as e:
        print("Error saving record:", e)


# ---------- PDF Viewer ----------
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# ---------- STREAMLIT UI ----------
import base64

def load_logo_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_path = r"C:\Users\samarahmad\Desktop\My Projects\Invoice-app\Logo.png"
logo_base64 = load_logo_as_base64(logo_path)

# ---------- HEADER ----------
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='font-size: 36px; margin-bottom: 0;'>ITTHAD DAIRY FARM</h1>
        <h3 style='font-size: 20px; margin-top: 5px; color: gray;'>Invoice Generator</h3>
        <img src="data:image/png;base64,{logo_base64}" 
             style='margin-top:15px; width:120px; height:120px; border-radius:50%; object-fit:cover;'>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- CUSTOMER INFO ----------
# ---------- CUSTOMER INFO ----------
st.markdown(
    """
    <div style='display: flex; justify-content: center; margin: 15px 0;'>
        <span style='background: #ffffff; color: black; font-weight: bold;
                     padding: 8px 20px; border-radius: 25px; 
                     box-shadow: 0px 2px 6px rgba(0,0,0,0.1);'>
            👤 Customer Information
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
invoice_no = st.text_input("Invoice No")
name = st.text_input("Customer Name")
phone = st.text_input("Phone Number")
address = st.text_area("Address")

# ---------- PAYMENT INFO ----------
st.markdown(
    """
    <div style='display: flex; justify-content: center; margin: 20px 0;'>
        <span style='background: #ffffff; color: black; font-weight: bold;
                     padding: 8px 20px; border-radius: 25px; 
                     box-shadow: 0px 2px 6px rgba(0,0,0,0.1);'>
            💰 Payment Information
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
quantity = st.number_input("Milk Quantity (Liters)", min_value=0, step=1)
price = st.number_input("Price per Liter", min_value=0, step=1)
due = st.number_input("Due Amount", min_value=0, step=1)

# ---------- LIVE PREVIEW ----------
if name and quantity > 0:
    total_amount = quantity * price
    payable = total_amount - due

    st.markdown(
        f"""
        <div style='background-color:#E8F6EF; padding:15px; border-radius:10px; 
                    margin-top:20px; text-align:center;'>
            <h4>Invoice Preview</h4>
            <p><b>Customer:</b> {name} | <b>Phone:</b> {phone}</p>
            <p><b>Quantity:</b> {quantity} L | <b>Rate:</b> Rs.{price}/L</p>
            <p><b>Total:</b> Rs.{total_amount} | <b>Due:</b> Rs.{due} | <b>Payable:</b> Rs.{payable}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- BUTTON ----------
if st.button("Generate Invoice"):
    total_amount = quantity * price
    payable = total_amount - due

    data = {
        "Invoice No": invoice_no,
        "Name": name,
        "Phone": phone,
        "Address": address,
        "Total Quantity": quantity,
        "Price per Liter": price,
        "Total Amount": total_amount,
        "Due Amount": due,
        "Payable": payable
    }

    month_year = datetime.now().strftime("%B%Y")
    safe_name = name.strip().replace(" ", "_") or "Customer"
    filename = f"{safe_name}_{month_year}.pdf"

    generate_invoice(data, filename)
    save_record(data)

    show_pdf(filename)

    with open(filename, "rb") as f:
        st.download_button("⬇️ Download Invoice", f, file_name=filename)
