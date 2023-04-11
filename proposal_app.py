import streamlit as st
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from PIL import Image
from io import BytesIO

# Connect to the SQLite database
conn = sqlite3.connect('proposals2.db')

# Define a function to create the proposals table if it does not exist
def create_table():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS proposals
                 (proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  client_name TEXT,
                  proposal_date TEXT,
                  proposal_status TEXT,
                  image BLOB DEFAULT NULL)''')
    conn.commit()

# Define a function to insert a new proposal into the database
def insert_proposal(client_name, proposal_date, proposal_status, image):
    # Insert the new proposal into the database
    c = conn.cursor()
    c.execute("INSERT INTO proposals (client_name, proposal_date, proposal_status, image) VALUES (?, ?, ?, ?)", (client_name, proposal_date, proposal_status, image))
    conn.commit()
    st.success("Proposal added to the database!")

# Define a function to generate a PDF proposal
def generate_proposal(proposal_id):
    # Get the proposal details from the database
    c = conn.cursor()
    c.execute("SELECT * FROM proposals WHERE proposal_id = ?", (proposal_id,))
    result = c.fetchone()

    # If the proposal does not exist, return an error message
    if not result:
        return "Error: Proposal not found"

    # Set up the PDF canvas
    pdf_file = "proposal_" + str(proposal_id) + ".pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, 10 * inch, "Proposal for " + result[1])
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, 9 * inch, "Proposal ID: " + str(result[0]))
    c.drawString(1 * inch, 8 * inch, "Proposal Date: " + result[2])
    c.drawString(1 * inch, 7 * inch, "Proposal Status: " + result[3])

    # Add the image to the PDF
    if result[4]:
        try:
            # Check the image data
            print("Image data before opening the image:", result[4])
            image = Image.open(BytesIO(result[4]))
            print("Image data after opening the image:", image)
            image_width, image_height = image.size
            if image_width > image_height:
                image_width = 4.5 * inch
                image_height = 2.53 * inch
            else:
                image_height = 4.5 * inch
                image_width = 2.53 * inch
            c.drawImage(image, 1 * inch, 6 * inch, width=image_width, height=image_height)
        except:
            pass

    c.showPage()
    c.save()

    st.success("Proposal generated successfully!")

# Define the Streamlit app
def app():
    st.set_page_config(page_title="Proposal Generator", page_icon=":money_with_wings:")
    st.title("Proposal Generator")
    create_table()
    c = conn.cursor()

    # Define the form inputs
    client_name = st.text_input("Client Name")
    proposal_date = st.date_input("Proposal Date")
    proposal_status = st.selectbox("Proposal Status", ["Draft", "Submitted", "Accepted", "Rejected"])
    image_file = st.file_uploader("Upload an image (1280 x 720 px)", type=["png", "jpg"])

     # Define the form submit button
    if st.button("Generate Proposal"):
        # Convert the image to bytes
        image_bytes = None
        if image_file is not None:
            image = Image.open(image_file)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

        # Insert the new proposal into the database
        insert_proposal(client_name, proposal_date, proposal_status, image_bytes)

        # Get the proposal ID from the database
        c.execute("SELECT MAX(proposal_id) FROM proposals")
        result = c.fetchone()
        proposal_id = result[0]

        # Generate the PDF proposal
        generate_proposal(proposal_id)

        # Define the download button
        with open("proposal_" + str(proposal_id) + ".pdf", "rb") as f:
            pdf_bytes = f.read()
            st.download_button(label="Download Proposal", data=pdf_bytes, file_name="proposal_" + str(proposal_id) + ".pdf", mime="application/pdf")

if __name__ == '__main__':
    app()
