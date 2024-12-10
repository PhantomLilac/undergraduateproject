import streamlit as st
import pandas as pd
import plotly.express as px
import arrow
from fpdf import FPDF
from datetime import datetime
import plotly.graph_objects as go

# Title of the app
st.title("Chronochat Visualizer")
st.write("""
    - This is a timeline analysis visualization tool
    - Timeline Analysis is useful to know what happened, when it happened, and who was involved.
    """)


# Note
with st.expander("Note"):
    st.write("""
    - Timestamp has changed from epoch to human-readable date time
    - key_remote_jid: WhatsApp ID of the communication partner (Contact number)
    - key_from_me: Message sent and recieved: ‘0’=incoming, ‘1’=outgoing
    - status: Message status: '0'=received, '4'=waiting on the server, '5'=received at the destination, 
    '6'=control message, '13'=message opened by the recipient (read)
    - media_wa_type: Message type: ’0’=text, ’1’=image, ’2’=audio, ’3’=video, 
    ’4’=contact card, ’5’=geo position)
    - need_push: ‘2’ if broadcast message, ‘0’ otherwise
    """)

# Add footer
def add_footer():
    st.markdown("""
        <style>
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: #f5f5f5;
                padding: 10px 0;
                text-align: center;
                font-size: small;
                color: #333;
            }
        </style>
        <div class="footer">
            © 2024 UTHM- All Rights Reserved .
        </div>
    """, unsafe_allow_html=True)

# File uploader to upload WhatsApp chat data CSV file
uploaded_file = st.file_uploader("Choose a file", type="csv")

if uploaded_file is not None:
    try:
        # Load the data into a dataframe
        whatsapp_data = pd.read_csv(uploaded_file)

        # Check if the dataframe is empty
        if whatsapp_data.empty:
            st.warning("The uploaded file is empty. Please upload a valid CSV file.")
        else:
            # Display the dataframe
            st.write(whatsapp_data)

            # Get the columns of the dataframe
            columns = whatsapp_data.columns.tolist()

            # Select attribute and timestamp for visualization
            viz_type = st.selectbox("Select Visualization Type:", ["Line Chart", "Scatter Plot", "Bar Chart"])

            # Auto-select the timestamp attribute
            timestamp_columns = [col for col in whatsapp_data.columns if
                                 'timestamp' in col.lower() or 'date' in col.lower()]
            if timestamp_columns:
                selected_timestamp = st.selectbox("Select Timestamp Attribute:", whatsapp_data.columns,
                                                  index=whatsapp_data.columns.tolist().index(timestamp_columns[0]))
            else:
                selected_timestamp = st.selectbox("Select Timestamp Attribute:", whatsapp_data.columns)

            if viz_type == "Scatter Plot":
                selected_attributes = st.multiselect("Select Attributes for Visualization:", columns)
            else:
                selected_attributes = [st.selectbox("Select Attribute for Visualization:", columns)]

            # Ensure there is data in the selected columns
            if selected_timestamp not in whatsapp_data.columns or not all(attr in whatsapp_data.columns for attr in
                                                                          selected_attributes):
                st.error("The selected columns do not exist in the uploaded data.")
            elif whatsapp_data[selected_timestamp].empty or any(whatsapp_data[attr].empty for attr in selected_attributes):
                st.error("The selected columns do not contain any data.")
            else:
                # Convert the selected timestamp column to datetime using arrow if it is in epoch format
                if (isinstance(whatsapp_data[selected_timestamp].iloc[0], (int, float)) and
                        len(str(int(whatsapp_data[selected_timestamp].iloc[0]))) == 10):
                    whatsapp_data[selected_timestamp] = whatsapp_data[selected_timestamp].apply(lambda x: arrow.get(x).datetime)
                else:
                    whatsapp_data[selected_timestamp] = whatsapp_data[selected_timestamp].apply(lambda x: arrow.get(x).datetime
                    if isinstance(x, (int, float)) else pd.to_datetime(x))

                # Ensure the selected attribute columns are numeric
                for attr in selected_attributes:
                    whatsapp_data[attr] = pd.to_numeric(whatsapp_data[attr], errors='coerce')

                # Drop rows with NaN values in the selected columns
                whatsapp_data.dropna(subset=[selected_timestamp] + selected_attributes, inplace=True)

                # Check if there is data left after dropping NaNs
                if whatsapp_data.empty:
                    st.error("The selected columns do not contain valid numeric data for plotting.")
                else:
                    # Create a figure
                    if viz_type == "Line Chart":
                        fig = go.Figure()
                        for i, attr in enumerate(selected_attributes):
                            fig.add_trace(go.Scatter(x=whatsapp_data[selected_timestamp], y=whatsapp_data[attr],
                                                     mode='lines+markers',
                                                     marker=dict(symbol='circle', size=5,color='blue'),
                                                     name=attr, showlegend=True, legendrank=i+1))
                        fig.update_layout(legend_title_text="Attribute", legend=dict(orientation="v", yanchor="middle", xanchor="center", x=1.15, y=0.95,
                                                      bordercolor='pink', borderwidth=1.5),
                                          title=f"Line Chart of {', '.join(selected_attributes)} over {selected_timestamp}",
                                          xaxis_title=selected_timestamp,
                                          yaxis_title=', '.join(selected_attributes))
                    elif viz_type == "Scatter Plot":
                        fig = go.Figure()
                        for i, attr in enumerate(selected_attributes):
                            fig.add_trace(go.Scatter(x=whatsapp_data[selected_timestamp], y=whatsapp_data[attr], mode='markers',
                                                     name=attr, text=whatsapp_data[attr]))
                        fig.update_layout(legend_title_text="Attribute", legend=dict(orientation="v", yanchor="middle", xanchor="center", x=1.15, y=0.95,
                                                      bordercolor='pink', borderwidth=1.5))
                    elif viz_type == "Bar Chart":
                            fig = px.bar(whatsapp_data.groupby([selected_timestamp,
                                                                selected_attributes[0]]).size().reset_index(name='count'),
                                         x=selected_timestamp, y='count', color=selected_attributes[0],
                                         color_discrete_map={attr: f"Attribute: {attr}" for attr
                                                             in whatsapp_data[selected_attributes[0]].unique()})
                            fig.update_layout(legend_title_text="Attribute", legend=dict(orientation="h"))

                    # Set the title and labels
                    attribute_titles = [attr if attr not in ['key_remote_jid', 'key_from_me', 'status', 'media_wa_type', 'timestamp']
                                        else {'key_remote_jid': 'Contact Numbers',
                                              'key_from_me': 'Message is received or sent',
                                              'status': 'Message status',
                                              'media_wa_type': 'Message type',
                                              'timestamp': 'Date and Time'}[attr] for attr in selected_attributes]
                    fig.update_layout(title=f"{viz_type.capitalize()} of {', '.join(attribute_titles)} over {selected_timestamp}",
                                      xaxis_title=selected_timestamp if selected_timestamp!= 'timestamp' else 'Date and Time',
                                      yaxis_title=', '.join(attribute_titles))

                    # Display the plot
                    st.plotly_chart(fig)

                   # Display result table
                    result_table = whatsapp_data[[selected_timestamp] +
                                                 selected_attributes].assign(count=1).groupby([selected_timestamp] +
                                                                                              selected_attributes).count().reset_index()
                    st.write("Result Table:")
                    st.write(result_table)

                    # Save and export the chart
                    def save_chart():
                        fig.write_image("chart.png")
                        st.download_button(label="Download Chart", data=open("chart.png", "rb"), file_name='chart.png', mime='image/png')

                    save_chart()

                    # Get title and description from user
                    title = st.text_input("Enter report title:")
                    description = st.text_area("Enter report description:")

                    # Generate report in PDF format
                    def generate_report():
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=15)
                        pdf.cell(200, 10, txt=title, ln=True, align='C')
                        pdf.ln(10)
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, txt=description, align='L')
                        pdf.ln(10)
                        pdf.image("chart.png", x=10, y=100, w=190)
                        pdf.output("report.pdf")

                    generate_report()
                    st.download_button(label="Download Report", data=open("report.pdf", "rb"),
                                       file_name='report.pdf', mime='application/pdf')

    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
else:
    st.warning("Please upload a CSV file to proceed.")

# Call the footer function at the end of the app layout
add_footer()
