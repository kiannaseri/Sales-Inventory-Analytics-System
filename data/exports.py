import pandas as pd
from tkinter import filedialog, messagebox
import os
from datetime import datetime


class ExportManager:
    """مدیریت خروجی‌های پیشرفته PDF/Excel"""

    @staticmethod
    def export_to_excel(data, analysis_results, filename=None):
        """خروجی به Excel با فرمت پیشرفته (چند شیت)"""
        if data is None or data.empty:
            return False, "No data to export"

        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

        if not filename:
            return False, "Cancelled"

        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # شیت 1: داده اصلی
                data.to_excel(writer, sheet_name='Raw Data', index=False)

                # شیت 2: داده تمیز شده
                if 'cleaned_data' in analysis_results:
                    analysis_results['cleaned_data'].to_excel(writer, sheet_name='Cleaned Data', index=False)

                # شیت 3: آمار فروش
                if 'daily_sales' in analysis_results:
                    analysis_results['daily_sales'].to_excel(writer, sheet_name='Daily Sales')

                # شیت 4: محصولات پرفروش
                if 'top_products' in analysis_results:
                    top_df = pd.DataFrame(analysis_results['top_products'].items(), columns=['Product', 'Units Sold'])
                    top_df.to_excel(writer, sheet_name='Top Products', index=False)

                # شیت 5: محصولات کم‌فروش
                if 'low_products' in analysis_results:
                    low_df = pd.DataFrame(analysis_results['low_products'].items(), columns=['Product', 'Units Sold'])
                    low_df.to_excel(writer, sheet_name='Low Products', index=False)

                # شیت 6: موجودی رو به اتمام
                if 'low_stock' in analysis_results and not analysis_results['low_stock'].empty:
                    stock_df = pd.DataFrame(analysis_results['low_stock'].items(),
                                            columns=['Product', 'Remaining Stock'])
                    stock_df.to_excel(writer, sheet_name='Low Stock Alert', index=False)

                # شیت 7: دسته‌بندی مشتریان
                if 'rfm_segments' in analysis_results:
                    rfm_df = pd.DataFrame(analysis_results['rfm_segments'].items(), columns=['Segment', 'Count'])
                    rfm_df.to_excel(writer, sheet_name='Customer Segments', index=False)

                # شیت 8: خلاصه گزارش
                summary_data = {
                    'Metric': ['Total Records', 'Total Sales', 'Average Order Value',
                               'Total Customers', 'Total Products', 'Analysis Date'],
                    'Value': [
                        len(data),
                        f"{data['sales_amount'].sum():,.0f}" if 'sales_amount' in data.columns else 'N/A',
                        f"{data['sales_amount'].sum() / data['quantity_sold'].sum():,.0f}" if all(
                            col in data.columns for col in ['sales_amount', 'quantity_sold']) and data[
                                                                                                  'quantity_sold'].sum() > 0 else 'N/A',
                        data['customer_id'].nunique() if 'customer_id' in data.columns else 'N/A',
                        data['product'].nunique() if 'product' in data.columns else 'N/A',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            return True, filename
        except Exception as e:
            return False, str(e)

    @staticmethod
    def export_to_pdf(data, analysis_results, filename=None):
        """خروجی به PDF با فرمت حرفه‌ای"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import matplotlib.pyplot as plt
            import io

            if not filename:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )

            if not filename:
                return False, "Cancelled"

            # ایجاد PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # عنوان
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                alignment=1,
                spaceAfter=30
            )
            story.append(Paragraph("Sales Analytics Report", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))

            # خلاصه
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Spacer(1, 10))

            summary_data = [
                ['Metric', 'Value'],
                ['Total Records', str(len(data))],
                ['Total Sales', f"{data['sales_amount'].sum():,.0f}" if 'sales_amount' in data.columns else 'N/A'],
                ['Total Customers', str(data['customer_id'].nunique()) if 'customer_id' in data.columns else 'N/A'],
                ['Total Products', str(data['product'].nunique()) if 'product' in data.columns else 'N/A']
            ]

            summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # محصولات پرفروش
            if 'top_products' in analysis_results:
                story.append(Paragraph("Top 10 Products", styles['Heading2']))
                story.append(Spacer(1, 10))

                top_data = [['Product', 'Units Sold']]
                for product, qty in list(analysis_results['top_products'].items())[:10]:
                    top_data.append([product, str(int(qty))])

                top_table = Table(top_data, colWidths=[3 * inch, 1.5 * inch])
                top_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(top_table)
                story.append(Spacer(1, 20))

            doc.build(story)
            return True, filename

        except ImportError:
            return False, "reportlab not installed. Run: pip install reportlab"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def export_to_html(data, analysis_results, filename=None):
        """خروجی به HTML (داشبورد وب)"""
        if data is None or data.empty:
            return False, "No data to export"

        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html")],
                initialfile=f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )

        if not filename:
            return False, "Cancelled"

        try:
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="fa">
            <head>
                <meta charset="UTF-8">
                <title>Sales Analytics Dashboard</title>
                <style>
                    body {{ font-family: Tahoma, Arial, sans-serif; margin: 20px; background: #f0f0f0; direction: rtl; }}
                    .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
                    h1 {{ color: #2c3e50; text-align: center; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                    .stat-card h3 {{ margin: 0 0 10px 0; }}
                    .stat-card p {{ font-size: 24px; margin: 0; font-weight: bold; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                    th {{ background-color: #2c3e50; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    .section {{ margin: 30px 0; }}
                    .section h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Sales Analytics Dashboard</h1>
                    <p style="text-align: center;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                    <div class="stats">
                        <div class="stat-card">
                            <h3>📋 Total Records</h3>
                            <p>{len(data)}</p>
                        </div>
                        <div class="stat-card">
                            <h3>💰 Total Sales</h3>
                            <p>{data['sales_amount'].sum():,.0f} Toman</p>
                        </div>
                        <div class="stat-card">
                            <h3>👥 Total Customers</h3>
                            <p>{data['customer_id'].nunique() if 'customer_id' in data.columns else 'N/A'}</p>
                        </div>
                        <div class="stat-card">
                            <h3>📦 Total Products</h3>
                            <p>{data['product'].nunique() if 'product' in data.columns else 'N/A'}</p>
                        </div>
                    </div>
            """

            # محصولات پرفروش
            if 'top_products' in analysis_results:
                html_content += """
                    <div class="section">
                        <h2>🔥 Top 10 Products</h2>
                        <table>
                            <tr><th>Product</th><th>Units Sold</th></tr>
                """
                for product, qty in list(analysis_results['top_products'].items())[:10]:
                    html_content += f"<tr><td>{product}</td><td>{int(qty)}</td></tr>"
                html_content += "</table></div>"

            html_content += """
                </div>
            </body>
            </html>
            """

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True, filename
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_export_formats():
        """لیست فرمت‌های خروجی"""
        return {
            "📊 Excel (.xlsx)": ExportManager.export_to_excel,
            "📄 PDF (.pdf)": ExportManager.export_to_pdf,
            "🌐 HTML (.html)": ExportManager.export_to_html
        }