# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 12:47:19 2023

@author: amrit
"""
import streamlit as st
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Connect to the SQLite database and create the table if it doesn't exist
conn = sqlite3.connect('proposal.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS proposals
             (proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
              client_name TEXT,
              proposal_date TEXT,
              proposal_status TEXT)''')
conn.commit()

# Define a function to insert a new proposal into the database
def insert_proposal(client_name, proposal_date, proposal_status):
    # Insert the new proposal into the database
    c = conn.cursor()
    c.execute("INSERT INTO proposals (client_name, proposal_date, proposal_status) VALUES (?, ?, ?)", (client_name, proposal_date, proposal_status))
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
    c.showPage()
    c.save()

    st.success("Proposal generated successfully!")

# Define the Streamlit app
def app():
    st.title("Proposal Generator")
    # Define the form inputs
    client_name = st.text_input("Client Name")
    proposal_date = st.date_input("Proposal Date")
    proposal_status = st.selectbox("Proposal Status", ["Draft", "Submitted", "Accepted", "Rejected"])

    # Define the form submit button
    if st.button("Generate Proposal"):
        if not client_name or not proposal_date or not proposal_status:
            st.error("Please fill in all the required fields!")
        else:
            insert_proposal(client_name, proposal_date.strftime('%Y-%m-%d'), proposal_status)
            proposal_id = c.lastrowid
            generate_proposal(proposal_id)



if __name__ == '__main__':
    app()
