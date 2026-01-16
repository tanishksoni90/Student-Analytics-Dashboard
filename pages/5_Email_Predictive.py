import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(page_title="Email / Predictive", page_icon="📧", layout="wide")

data_mode = st.session_state.get("data_mode", None)

if data_mode is None:
    st.warning("⚠️ Please upload a data file on the Home page to begin.")
    st.stop()

# ============================================
# PDF REPORT GENERATION
# ============================================
def generate_student_pdf_report(student_data, df, score_columns, logo_path="logo.png"):
    """Generate a professional PDF report for a student."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import os
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=24, 
        textColor=colors.HexColor('#1a5276'), alignment=TA_CENTER, spaceAfter=20
    )
    header_style = ParagraphStyle(
        'CustomHeader', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor('#2874a6'), spaceBefore=15, spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'], fontSize=11, spaceAfter=6
    )
    
    # Header with Logo
    try:
        if logo_path and os.path.exists(logo_path):
            logo = Image(logo_path, width=1.2*inch, height=0.6*inch)
            logo.hAlign = 'RIGHT'
            
            # Create header table with title on left and logo on right
            header_title = Paragraph("Student Assessment Report", title_style)
            header_table = Table(
                [[header_title, logo]],
                colWidths=[5.5*inch, 1.5*inch]
            )
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            story.append(header_table)
        else:
            story.append(Paragraph("Student Assessment Report", title_style))
    except Exception:
        story.append(Paragraph("Student Assessment Report", title_style))
    
    story.append(Spacer(1, 10))
    
    # Student Info Box
    student_name = student_data.get('Student_Name', 'N/A')
    total_max = student_data.get('Total_Max', 480)
    total_pct = student_data['Total_Percentage']
    rank = int(student_data['Rank'])
    
    # Performance status
    if total_pct >= 80:
        status = "EXCELLENT"
        status_color = colors.HexColor('#27ae60')
    elif total_pct >= 65:
        status = "GOOD"
        status_color = colors.HexColor('#3498db')
    elif total_pct >= 50:
        status = "AVERAGE"
        status_color = colors.HexColor('#f39c12')
    else:
        status = "NEEDS IMPROVEMENT"
        status_color = colors.HexColor('#e74c3c')
    
    # Student details table
    story.append(Paragraph("Student Information", header_style))
    
    info_data = [
        ['Name:', student_name, 'Registration:', student_data.get('College_Reg', 'N/A')],
        ['Email:', student_data.get('Email', 'N/A'), 'Batch:', str(student_data.get('Batch', 'N/A'))],
        ['Branch:', student_data.get('Branch', 'N/A'), 'Report Date:', datetime.now().strftime('%d %b %Y')]
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#2c3e50')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # Performance Summary Box
    story.append(Paragraph("Performance Summary", header_style))
    
    perf_data = [
        ['Overall Score', 'Percentage', 'Rank', 'Status'],
        [f"{int(student_data['Score'])}/{total_max}", f"{total_pct:.1f}%", 
         f"{rank} of {len(df)}", status]
    ]
    
    perf_table = Table(perf_data, colWidths=[1.5*inch, 1.5*inch, 1.4*inch, 2.4*inch])
    perf_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (3, 1), (3, 1), status_color),
        ('TEXTCOLOR', (3, 1), (3, 1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 20))
    
    # Section-wise Performance
    story.append(Paragraph("Section-wise Performance", header_style))
    
    # Generate comparison chart
    sections = []
    student_pcts = []
    class_avgs = []
    
    for col_name, max_val in score_columns.items():
        section_name = col_name.split('(')[0].strip()
        sections.append(section_name)
        student_pcts.append((student_data[col_name] / max_val) * 100)
        class_avgs.append((df[col_name].mean() / max_val) * 100)
    
    # Create the bar chart using matplotlib (more reliable for PDF export)
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig_chart, ax = plt.subplots(figsize=(7, 4))
        
        x = np.arange(len(sections))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, student_pcts, width, label=student_name, color='#3498db')
        bars2 = ax.bar(x + width/2, class_avgs, width, label='Class Average', color='#95a5a6')
        
        # Add value labels on bars
        for bar, pct in zip(bars1, student_pcts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                   f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, color='#2c3e50')
        for bar, pct in zip(bars2, class_avgs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, color='#7f8c8d')
        
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Your Performance vs Class Average', fontsize=14, color='#2c3e50', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(sections)
        ax.set_ylim(0, 110)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save to bytes
        chart_buffer = io.BytesIO()
        fig_chart.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight', 
                         facecolor='white', edgecolor='none')
        chart_buffer.seek(0)
        plt.close(fig_chart)
        
        chart_img = Image(chart_buffer, width=5.5*inch, height=3.2*inch)
        story.append(chart_img)
    except Exception as e:
        # If chart generation fails, add a note
        story.append(Paragraph(f"<i>(Chart could not be generated: {str(e)[:50]})</i>", normal_style))
    
    story.append(Spacer(1, 15))
    
    # Section details table
    section_headers = ['Section', 'Score', 'Your %', 'Class Avg', 'Difference']
    section_rows = [section_headers]
    
    for col_name, max_val in score_columns.items():
        section_name = col_name.split('(')[0].strip()
        score = student_data[col_name]
        pct = (score / max_val) * 100
        class_avg = (df[col_name].mean() / max_val) * 100
        diff = pct - class_avg
        diff_str = f"+{diff:.1f}%" if diff >= 0 else f"{diff:.1f}%"
        
        section_rows.append([
            section_name,
            f"{int(score)}/{max_val}",
            f"{pct:.1f}%",
            f"{class_avg:.1f}%",
            diff_str
        ])
    
    section_table = Table(section_rows, colWidths=[1.5*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    
    table_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]

    # Color code the Difference column
    for i, row in enumerate(section_rows[1:], start=1):
        diff_val = float(row[4].replace('%', '').replace('+', ''))
        if diff_val >= 5:
            table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#d4edda')))
            table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#155724')))
        elif diff_val <= -5:
            table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#f8d7da')))
            table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#721c24')))
    
    section_table.setStyle(TableStyle(table_style))
    story.append(section_table)
    story.append(Spacer(1, 20))
    
    # Strengths and Areas for Improvement
    story.append(Paragraph("Analysis & Recommendations", header_style))
    
    strengths = []
    improvements = []
    
    for col_name, max_val in score_columns.items():
        section_name = col_name.split('(')[0].strip()
        student_pct = (student_data[col_name] / max_val) * 100
        class_avg = (df[col_name].mean() / max_val) * 100
        
        if student_pct > class_avg:
            strengths.append(f"• {section_name}: {student_pct:.1f}% (above class average of {class_avg:.1f}%)")
        else:
            gap = class_avg - student_pct
            improvements.append(f"• {section_name}: {gap:.1f}% below class average - focus on practice")
    
    if strengths:
        story.append(Paragraph("<b>Strengths:</b>", normal_style))
        for s in strengths:
            story.append(Paragraph(f'<font color="#27ae60">{s}</font>', normal_style))
    
    if improvements:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Areas for Improvement:</b>", normal_style))
        for imp in improvements:
            story.append(Paragraph(f'<font color="#e74c3c">{imp}</font>', normal_style))
    
    if not improvements:
        story.append(Paragraph('<font color="#27ae60">Excellent! Above class average in all sections.</font>', normal_style))
    
    story.append(Spacer(1, 20))
    
    # Percentile Information
    percentile = (df['Score'] < student_data['Score']).sum() / len(df) * 100
    
    story.append(Paragraph("Statistical Position", header_style))
    
    stats_data = [
        ['Percentile Rank', 'Top %', 'Students Scored Lower', 'Students Scored Higher'],
        [f"{percentile:.1f}th", f"Top {100-percentile:.1f}%", 
         str(int((df['Score'] < student_data['Score']).sum())),
         str(int((df['Score'] > student_data['Score']).sum()))]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.7*inch, 1.7*inch, 1.7*inch, 1.7*inch])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(stats_table)

    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'], fontSize=9, 
        textColor=colors.HexColor('#7f8c8d'), alignment=TA_CENTER
    )
    story.append(Paragraph("─" * 80, footer_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%d %B %Y at %H:%M')}", footer_style))
    story.append(Paragraph("This is an automated report. For queries, contact the assessment team.", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================
# ASSESSMENT - EMAIL REPORTS
# ============================================
if data_mode == "assessment":
    st.title("📧 Email Student Reports")
    
    if "assessment_df" not in st.session_state:
        st.warning("Please upload assessment data on the Home page.")
        st.stop()
    
    df = st.session_state["assessment_df"]
    score_columns = st.session_state.get("score_columns", {})
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    
    # Email Configuration
    st.subheader("⚙️ Email Configuration")
    
    with st.expander("📧 SMTP Settings", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sender_email = st.text_input("Sender Email", placeholder="your-email@gmail.com")
            sender_password = st.text_input("App Password", type="password",
                                            help="Gmail App Password (not regular password)")
            
            st.info("""
            **Gmail App Password:**
            1. Google Account → Security
            2. Enable 2-Step Verification
            3. App Passwords → Generate for 'Mail'
            """)
        
        with col2:
            email_subject = st.text_input("Subject", value="Your Assessment Performance Report")
            sender_name = st.text_input("Sender Name", value="Assessment Team")
            attach_pdf = st.checkbox("📎 Attach PDF Report", value=True, 
                                    help="Attach a detailed PDF report to each email")
    
    st.write("---")

    # Email Template
    default_template = """Dear {student_name},

Please find attached your detailed Assessment Performance Report.

Quick Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Overall Score: {score}/{total_max} ({percentage}%)
🏆 Rank: {rank} out of {total_students} students
📈 Percentile: {percentile}th
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Section-wise Performance:
{section_details}

{performance_message}

The attached PDF report contains detailed analysis including:
• Section-wise breakdown with class comparison
• Strengths and areas for improvement
• Statistical position among peers

Best regards,
{sender_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated email with your personalized report attached.
"""
    
    with st.expander("📝 Email Template"):
        email_template = st.text_area("Template", value=default_template, height=400)
    
    st.write("---")
    
    # Helper Functions
    def generate_email_body(student_data, df, template, sender_name, score_columns):
        total_max = student_data.get('Total_Max', 480)
        percentile = (df['Score'] < student_data['Score']).sum() / len(df) * 100
        
        section_lines = []
        for col_name, max_val in score_columns.items():
            name = col_name.split('(')[0].strip()
            score = student_data[col_name]
            pct = (score / max_val) * 100
            class_avg = (df[col_name].mean() / max_val) * 100
            diff = pct - class_avg
            indicator = "↑" if diff >= 0 else "↓"
            section_lines.append(f"• {name}: {int(score)}/{max_val} ({pct:.1f}%) {indicator} {abs(diff):.1f}% vs class avg")
        
        # Performance message
        total_pct = student_data['Total_Percentage']
        if total_pct >= 80:
            perf_msg = "🎉 Excellent Performance! You're among the top performers. Keep up the great work!"
        elif total_pct >= 65:
            perf_msg = "👍 Good Performance! You're doing well. A little more effort can take you to the top!"
        elif total_pct >= 50:
            perf_msg = "📈 Average Performance. Focus on your weaker sections to improve your overall score."
        else:
            perf_msg = "📚 There's room for improvement. We recommend additional practice and support."
        
        return template.format(
            student_name=student_data.get('Student_Name', 'Student'),
            score=int(student_data['Score']),
            total_max=int(total_max),
            percentage=f"{student_data['Total_Percentage']:.1f}",
            rank=int(student_data['Rank']),
            total_students=len(df),
            percentile=f"{percentile:.0f}",
            section_details="\n".join(section_lines),
            performance_message=perf_msg,
            sender_name=sender_name
        )
    
    def send_email_with_attachment(to_email, subject, body, pdf_data, pdf_filename, 
                                   sender_email, sender_password, sender_name):
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF if provided
            if pdf_data:
                pdf_attachment = MIMEApplication(pdf_data, _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                msg.attach(pdf_attachment)
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return True, None
        except Exception as e:
            return False, str(e)

    # Send Options
    st.subheader("📤 Send Options")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Preview Report", "🧪 Test Email", "📧 Individual", "📬 Bulk Send"])
    
    # TAB 1: PREVIEW PDF REPORT
    with tab1:
        st.subheader("📄 Preview PDF Report")
        st.write("Preview how the PDF report will look before sending.")
        
        if 'Student_Name' in df.columns:
            preview_student = st.selectbox(
                "Select Student to Preview:",
                options=df['Student_Name'].tolist(),
                key="preview_student"
            )
            preview_data = df[df['Student_Name'] == preview_student].iloc[0]
        else:
            preview_data = df.iloc[0]
            preview_student = "Student 1"
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Generate Preview", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_bytes = generate_student_pdf_report(preview_data, df, score_columns)
                        st.session_state['preview_pdf'] = pdf_bytes
                        st.session_state['preview_name'] = preview_student
                        st.success("✅ PDF generated!")
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")
        
        with col2:
            if 'preview_pdf' in st.session_state:
                st.download_button(
                    "📥 Download Preview PDF",
                    data=st.session_state['preview_pdf'],
                    file_name=f"Report_{st.session_state.get('preview_name', 'Student')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        # Show student summary
        if preview_data is not None:
            st.write("---")
            st.write("**Student Summary:**")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Score", f"{preview_data['Score']}/{preview_data.get('Total_Max', 480)}")
            col2.metric("Percentage", f"{preview_data['Total_Percentage']:.1f}%")
            col3.metric("Rank", f"{int(preview_data['Rank'])}/{len(df)}")
            
            percentile = (df['Score'] < preview_data['Score']).sum() / len(df) * 100
            col4.metric("Percentile", f"{percentile:.0f}th")
    
    # TAB 2: TEST EMAIL
    with tab2:
        st.subheader("🧪 Send Test Email")
        st.write("Test your email configuration with PDF attachment before sending to students.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_email_address = st.text_input(
                "Test Email Address",
                placeholder="test@example.com",
                help="Enter any email address to send a test email"
            )
            
            if 'Student_Name' in df.columns:
                sample_student = st.selectbox(
                    "Sample Student (for test):",
                    options=df['Student_Name'].tolist(),
                    help="Select a student to use as sample data",
                    key="test_sample"
                )
                sample_data = df[df['Student_Name'] == sample_student].iloc[0]
            else:
                sample_data = df.iloc[0]
        
        with col2:
            st.write("**Email Preview:**")
            if sample_data is not None:
                preview_body = generate_email_body(sample_data, df, email_template, sender_name, score_columns)
                st.text_area("Email Body", value=preview_body, height=200, disabled=True)
        
        if st.button("🧪 Send Test Email with PDF", type="primary", use_container_width=True):
            if not sender_email or not sender_password:
                st.error("❌ Please configure SMTP settings first!")
            elif not test_email_address:
                st.error("❌ Please enter a test email address!")
            else:
                with st.spinner("Generating PDF and sending test email..."):
                    try:
                        # Generate PDF
                        pdf_data = None
                        pdf_filename = None
                        if attach_pdf:
                            pdf_data = generate_student_pdf_report(sample_data, df, score_columns)
                            pdf_filename = f"Assessment_Report_{sample_data.get('Student_Name', 'Student').replace(' ', '_')}.pdf"
                        
                        # Generate email body
                        body = generate_email_body(sample_data, df, email_template, sender_name, score_columns)
                        
                        # Send email
                        success, error = send_email_with_attachment(
                            test_email_address,
                            f"[TEST] {email_subject}",
                            body,
                            pdf_data,
                            pdf_filename,
                            sender_email,
                            sender_password,
                            sender_name
                        )
                        
                        if success:
                            st.success(f"✅ Test email sent successfully to {test_email_address}!")
                            if attach_pdf:
                                st.info("📎 PDF report attached to the email.")
                            st.balloons()
                        else:
                            st.error(f"❌ Failed to send: {error}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    # TAB 3: INDIVIDUAL EMAIL
    with tab3:
        st.subheader("📧 Send to Individual Student")
        
        if 'Student_Name' in df.columns and 'Email' in df.columns:
            student_options = [f"{row['Student_Name']} ({row['Email']})" for _, row in df.iterrows()]
            selected = st.selectbox("Select Student:", options=student_options, key="individual_select")
            
            if selected:
                email_addr = selected.split('(')[-1].replace(')', '')
                student_data = df[df['Email'] == email_addr].iloc[0]
                
                # Show preview
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Student Details:**")
                    st.write(f"• Name: {student_data['Student_Name']}")
                    st.write(f"• Score: {student_data['Score']}/{student_data.get('Total_Max', 480)}")
                    st.write(f"• Rank: {int(student_data['Rank'])}/{len(df)}")
                
                with col2:
                    send_to_self = st.checkbox("Send to myself first (test)", value=True, key="ind_test")
                
                if st.button("📧 Send Email with Report", use_container_width=True, key="send_individual"):
                    if not sender_email or not sender_password:
                        st.error("Configure email settings!")
                    else:
                        with st.spinner("Generating PDF and sending..."):
                            try:
                                # Generate PDF
                                pdf_data = None
                                pdf_filename = None
                                if attach_pdf:
                                    pdf_data = generate_student_pdf_report(student_data, df, score_columns)
                                    pdf_filename = f"Assessment_Report_{student_data['Student_Name'].replace(' ', '_')}.pdf"
                                
                                body = generate_email_body(student_data, df, email_template, sender_name, score_columns)
                                target = sender_email if send_to_self else email_addr
                                subj = f"[TEST] {email_subject}" if send_to_self else email_subject
                                
                                success, error = send_email_with_attachment(
                                    target, subj, body, pdf_data, pdf_filename,
                                    sender_email, sender_password, sender_name
                                )
                                
                                if success:
                                    st.success(f"✅ Email sent to {target}!")
                                else:
                                    st.error(f"❌ Failed: {error}")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
        else:
            st.warning("Student_Name and Email columns required.")
    
    # TAB 4: BULK SEND
    with tab4:
        st.subheader("📬 Bulk Send to All Students")
        
        st.warning("⚠️ This will generate PDF reports and send emails to ALL students!")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Students", len(df))
        col2.metric("Valid Emails", df['Email'].notna().sum() if 'Email' in df.columns else 0)
        
        est_time = len(df) * 3  # ~3 seconds per student with PDF generation
        col3.metric("Est. Time", f"{est_time//60}m {est_time%60}s")
        col4.metric("PDF Reports", "Yes" if attach_pdf else "No")
        
        send_to_self_bulk = st.checkbox("Send all to myself (test mode)", value=True, key="bulk_test_mode")
        confirm = st.checkbox("I confirm bulk send with PDF attachments", key="bulk_confirm_pdf")
        
        if st.button("📬 Send Reports to All Students", disabled=not confirm, use_container_width=True):
            if not sender_email or not sender_password:
                st.error("Configure email settings!")
            elif 'Email' not in df.columns:
                st.error("Email column not found!")
            else:
                progress = st.progress(0)
                status = st.empty()
                results = st.empty()
                
                success_count = 0
                fail_count = 0
                failed_students = []
                
                total = len(df)
                
                for i, (_, student_data) in enumerate(df.iterrows()):
                    if pd.notna(student_data.get('Email')):
                        student_name = student_data.get('Student_Name', f'Student {i+1}')
                        status.text(f"📧 Processing {student_name} ({i+1}/{total})...")
                        
                        try:
                            # Generate PDF
                            pdf_data = None
                            pdf_filename = None
                            if attach_pdf:
                                pdf_data = generate_student_pdf_report(student_data, df, score_columns)
                                pdf_filename = f"Assessment_Report_{student_name.replace(' ', '_')}.pdf"
                            
                            body = generate_email_body(student_data, df, email_template, sender_name, score_columns)
                            target = sender_email if send_to_self_bulk else student_data['Email']
                            subj = f"[TEST] {email_subject}" if send_to_self_bulk else email_subject
                            
                            success, error = send_email_with_attachment(
                                target, subj, body, pdf_data, pdf_filename,
                                sender_email, sender_password, sender_name
                            )
                            
                            if success:
                                success_count += 1
                            else:
                                fail_count += 1
                                failed_students.append(f"{student_name}: {error}")
                        except Exception as e:
                            fail_count += 1
                            failed_students.append(f"{student_name}: {str(e)}")
                    
                    progress.progress((i + 1) / total)
                    results.text(f"✅ Sent: {success_count} | ❌ Failed: {fail_count}")
                
                status.empty()
                progress.empty()
                results.empty()
                
                st.success(f"✅ Bulk send complete! Sent: {success_count}/{total}")
                
                if failed_students:
                    with st.expander("❌ Failed Emails"):
                        for f in failed_students:
                            st.write(f"• {f}")


# ============================================
# COURSE - PREDICTIVE FEATURES
# ============================================
elif data_mode == "course":
    st.title("🔮 Predictive Features & Reports")
    
    if "df" not in st.session_state:
        st.warning("Please upload course data on the Home page.")
        st.stop()
    
    df = st.session_state["df"]
    course_columns = st.session_state.get("course_columns", [])
    
    @st.cache_data
    def get_at_risk_students(_df, min_courses, max_completion):
        criteria = (_df['Courses Started'] >= min_courses) & (_df['Overall Completion %'] <= max_completion)
        return _df[criteria]
    
    @st.cache_data
    def get_recommendations(_df, _course_columns, student_reg, top_n=10):
        student_data = _df[_df['Registration Number'] == student_reg].iloc[0]
        student_branch = student_data['Branch Name']
        
        student_courses = student_data[_course_columns]
        started_courses = set(student_courses[student_courses >= 10].index)  # >=10% as started
        
        branch_df = _df[_df['Branch Name'] == student_branch]
        branch_enrollment = (branch_df[_course_columns] >= 10).sum().sort_values(ascending=False)  # >=10% as enrolled
        top_branch_courses = set(branch_enrollment.head(top_n).index)
        
        recommendations = list(top_branch_courses - started_courses)
        
        result = branch_enrollment[recommendations].reset_index()
        result.columns = ['Course', 'Branch Enrollment']
        return result.sort_values('Branch Enrollment', ascending=False)
    
    tab1, tab2 = st.tabs(["**At-Risk Students**", "**Course Recommendations**"])
    
    with tab1:
        st.header("🚨 At-Risk Student Identifier")
        st.write("Find students who may need extra support.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_courses = st.slider("Min 'Courses Started':", 1, 20, 5)
        
        with col2:
            max_completion = st.slider("Max 'Overall Completion %':", 10, 100, 30)
        
        if 'Courses Started' in df.columns and 'Overall Completion %' in df.columns:
            at_risk_df = get_at_risk_students(df, min_courses, max_completion)
            
            st.subheader(f"Found {len(at_risk_df)} students")
            
            if not at_risk_df.empty:
                # Build display columns dynamically based on what exists
                display_cols = []
                if 'First Name' in at_risk_df.columns:
                    display_cols.extend(['First Name', 'Last Name'])
                elif 'Full Name' in at_risk_df.columns:
                    display_cols.append('Full Name')
                
                for col in ['Registration Number', 'Branch Name', 'Courses Started', 'Courses Completed', 'Overall Completion %']:
                    if col in at_risk_df.columns:
                        display_cols.append(col)
                
                display_cols = [c for c in display_cols if c in at_risk_df.columns]
                
                sorted_df = at_risk_df[display_cols].sort_values('Overall Completion %', ascending=True)
                st.dataframe(sorted_df, use_container_width=True)
                
                csv_data = sorted_df.to_csv(index=False)
                st.download_button("📥 Download Report", data=csv_data,
                                  file_name=f"at_risk_report.csv", mime="text/csv")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("At-Risk Count", len(at_risk_df))
                col2.metric("% of Total", f"{len(at_risk_df)/len(df)*100:.1f}%")
                col3.metric("Avg Completion", f"{at_risk_df['Overall Completion %'].mean():.1f}%")
            else:
                st.success("🎉 No students match these criteria!")
    
    with tab2:
        st.header("💡 Course Recommendation Engine")
        
        if 'Registration Number' not in df.columns or 'Branch Name' not in df.columns:
            st.error("Required columns not found.")
            st.stop()
        
        student_list = df['Registration Number'].unique()
        selected_reg = st.selectbox("Select Student:", options=student_list)
        
        if selected_reg:
            student_data = df[df['Registration Number'] == selected_reg].iloc[0]
            
            # Get student name - handle different column formats
            if 'First Name' in df.columns and 'Last Name' in df.columns:
                student_name = f"{student_data.get('First Name', '')} {student_data.get('Last Name', '')}"
            elif 'Full Name' in df.columns:
                student_name = student_data.get('Full Name', 'N/A')
            else:
                student_name = 'N/A'
                for col in df.columns:
                    if 'name' in col.lower() and col.lower() not in ['branch name']:
                        student_name = student_data.get(col, 'N/A')
                        break
            
            col1, col2, col3 = st.columns(3)
            col1.info(f"**Name:** {student_name}")
            col2.info(f"**Branch:** {student_data.get('Branch Name', 'N/A')}")
            col3.info(f"**Started:** {student_data.get('Courses Started', 0)} courses")
            
            recommendations = get_recommendations(df, course_columns, selected_reg)
            
            if recommendations.empty:
                st.success("🎉 Already enrolled in most popular courses!")
            else:
                st.subheader("📚 Recommended Courses")
                st.dataframe(recommendations, use_container_width=True)
                
                if len(recommendations) > 0:
                    fig = px.bar(recommendations.head(10), x='Course', y='Branch Enrollment',
                                title="Top 10 Recommendations")
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
