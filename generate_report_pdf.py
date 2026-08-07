import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw running headers/footers
    with correct total page count (e.g. 'Page X of 10') on all pages except the cover.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Page 1 is the cover sheet: omit headers, footers and page numbers
        if self._pageNumber == 1:
            # Draw a subtle background graphic or brand bar on the left
            self.setFillColor(colors.HexColor("#0f172a")) # Dark background banner color
            self.rect(0, 0, 18, 792, fill=True, stroke=False)
            self.setFillColor(colors.HexColor("#00e676")) # Agro green accent accent
            self.rect(18, 0, 6, 792, fill=True, stroke=False)
            return

        # Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569")) # Slate-600
        self.drawString(54, 750, "AGROVET AI — TECHNICAL PROJECT REPORT")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 750, "SYSTEM SPECIFICATIONS & ARCHITECTURE")
        self.setStrokeColor(colors.HexColor("#cbd5e1")) # Slate-300
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)

        # Running Footer
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#94a3b8")) # Slate-400
        self.drawString(54, 42, "CONFIDENTIAL")
        self.setFont("Helvetica", 8)
        self.drawString(135, 42, "— FOR EVALUATION & DEVELOPMENT ONLY")
        self.drawRightString(558, 42, f"Page {self._pageNumber} of {page_count}")
        self.line(54, 52, 558, 52)


def create_report_pdf():
    pdf_filename = "AgroVet_AI_Technical_Report.pdf"
    
    # 0.75 inch margins (54pt)
    # Target printable area: 504 pt width x 684 pt height (on a 612 x 792 letter sheet)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )

    styles = getSampleStyleSheet()
    
    # Define color palette
    c_primary = colors.HexColor("#0f172a")    # Slate-900 (Deep dark navy/gray)
    c_accent_green = colors.HexColor("#16a34a") # Emerald-600 (Agri theme)
    c_accent_blue = colors.HexColor("#2563eb")  # Blue-600 (Vet theme)
    c_text_dark = colors.HexColor("#1e293b")    # Slate-800
    c_text_muted = colors.HexColor("#64748b")   # Slate-500

    # Custom Paragraph Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=c_primary,
        spaceAfter=15
    )

    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=c_accent_blue,
        spaceAfter=150
    )

    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=c_text_dark,
        spaceAfter=6
    )

    style_h1 = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_accent_green,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_text_dark,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )

    style_bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=c_text_dark,
        leftIndent=15,
        spaceAfter=4
    )

    style_table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_text_dark
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 100))
    story.append(Paragraph("AGROVET AI", style_cover_title))
    story.append(HRFlowable(width="100%", thickness=4, color=c_accent_green, spaceBefore=0, spaceAfter=8))
    story.append(Paragraph("Multi-Domain Computer Vision Platform for Agricultural Pathology & Veterinary Diagnostic Imaging", style_cover_subtitle))
    
    story.append(Spacer(1, 150))
    
    meta_table_data = [
        [Paragraph("<b>Document Title:</b>", style_table_text), Paragraph("Technical Specifications & Project Report", style_table_text)],
        [Paragraph("<b>Software Version:</b>", style_table_text), Paragraph("1.0.0 (Production Release)", style_table_text)],
        [Paragraph("<b>Release Date:</b>", style_table_text), Paragraph(datetime.now().strftime("%B %d, %Y"), style_table_text)],
        [Paragraph("<b>Authors:</b>", style_table_text), Paragraph("AI Architecture Group & Lead Developer", style_table_text)],
        [Paragraph("<b>System Core:</b>", style_table_text), Paragraph("React (Vite) / Python FastAPI / PyTorch CNN / SQLite / Docker", style_table_text)]
    ]
    meta_table = Table(meta_table_data, colWidths=[110, 394])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: EXECUTIVE SUMMARY & TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Executive Summary", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    story.append(Paragraph(
        "AgroVet AI is an integrated, full-stack artificial intelligence application engineered to support two distinct classification domains using deep learning: Agricultural Foliar Leaf Pathology (detecting 22 crop disease combinations) and Veterinary Orthopedic Radiography (detecting 14 animal trauma anomalies).",
        style_body
    ))
    story.append(Paragraph(
        "By hosting both domains within a single containerized system, AgroVet AI provides immediate field diagnostic results with built-in Explainable AI (XAI) using Gradient-Weighted Class Activation Mapping (Grad-CAM). The system requires no user authentication for its core operational functions, resolving adoption issues for rural agricultural users and veterinary clinicians in high-stress field conditions. Scans are logged locally in an SQLite database, compiled into an administrative telemetry dashboard, and can be rendered on-demand as professional, publication-quality diagnostic PDFs.",
        style_body
    ))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Table of Contents", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    
    toc_data = [
        [Paragraph("<b>Section Title</b>", style_table_text), Paragraph("<b>Target Page</b>", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("Executive Summary & Table of Contents", style_table_text), Paragraph("Page 2", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("1. Introduction, Background & Problem Statement", style_table_text), Paragraph("Page 3", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("2. System Architecture & Inter-Component Data Flow", style_table_text), Paragraph("Page 4", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("3. Deep Learning Engine & PyTorch Model Architectures", style_table_text), Paragraph("Page 5", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("4. Explainable AI: Grad-CAM Core Principles & Hook Logic", style_table_text), Paragraph("Page 6", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("5. Persistence Layer & Administrative Telemetry Dashboard", style_table_text), Paragraph("Page 7", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("6. Professional PDF Generation System", style_table_text), Paragraph("Page 8", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("7. User Interface Design System & Custom CSS Styling Rules", style_table_text), Paragraph("Page 9", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))],
        [Paragraph("8. Deployment Framework, Optimization & Future Enhancements", style_table_text), Paragraph("Page 10", ParagraphStyle('R', parent=style_table_text, alignment=TA_RIGHT))]
    ]
    toc_table = Table(toc_data, colWidths=[384, 120])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SECTION 1: INTRODUCTION & BACKGROUND
    # =========================================================================
    story.append(Paragraph("1. Introduction & Background", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_green, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("1.1 Operational Domain Context", style_h2))
    story.append(Paragraph(
        "In modern agrarian and veterinary medicine, rapid diagnostics translate directly into damage control. Agricultural extension workers and farmers often wait days or weeks for laboratory foliar tissue analysis, allowing fungal diseases like Early Blight or Late Blight to ruin entire fields. In contrast, remote veterinary shelters or rural clinics face immediate clinical situations where injured animals (dogs, cats, cows, horses) require initial trauma evaluations. Immediate radiographic screenings for bone fractures or joint abnormalities allow staff to splint limbs and prepare treatment plans before a specialist veterinarian arrives.",
        style_body
    ))
    
    story.append(Paragraph("1.2 The AgroVet AI Unified Diagnostic Framework", style_h2))
    story.append(Paragraph(
        "AgroVet AI acts as a single, accessible gateway for local diagnostic imaging, designed to solve several operational bottlenecks simultaneously:",
        style_body
    ))
    story.append(Paragraph(
        "<b>• No-Login Mandate:</b> Deployed as a friction-free utility, field workers do not need to register, remember credentials, or connect to OAuth services under unstable cellular data coverage. The core diagnostic page runs immediately in any browser.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Double-Domain Processing:</b> Combines plant disease pathology and veterinary bone analysis under one API routing engine, maximizing container resource utilization.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Explainable Visual Evidence:</b> Rather than returning a single classification class and a confidence score, the system generates attention maps showing where the model located leaf lesions or bone fractures, helping prevent 'black-box' trust failures.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Documentable Data:</b> Generates professional PDFs that can be printed, archived, or shared via email with diagnostic experts for validation.",
        style_bullet
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: SECTION 2: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. System Architecture & Data Flow", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("2.1 High-Level Component Layout", style_h2))
    story.append(Paragraph(
        "The system is organized into a React Single Page Application (SPA) frontend built on Vite, communicating via asynchronous JSON and binary payloads with a Python FastAPI server. The database is SQLite, stored inside the backend container to ensure zero external dependencies during standard local deployment.",
        style_body
    ))

    arch_data = [
        [Paragraph("<b>Component</b>", style_table_header), Paragraph("<b>Tech Stack Details</b>", style_table_header), Paragraph("<b>Operational Function</b>", style_table_header)],
        [Paragraph("Frontend Client", style_table_text), Paragraph("React 18, Vite, Custom CSS (NVIDIA Dark Theme), Lucide Icons", style_table_text), Paragraph("Handles client-side routing, drag-and-drop uploads, interactive sample selection, SVG metric rendering, and modal details collection.", style_table_text)],
        [Paragraph("API Gateway Server", style_table_text), Paragraph("Python FastAPI, Uvicorn Server, CORS Middleware", style_table_text), Paragraph("Manages routing, async execution pools, file ingestion, static content directories, and acts as the orchestrator for inference and PDF compilation.", style_table_text)],
        [Paragraph("Deep Learning Engine", style_table_text), Paragraph("PyTorch 2.0+, Torchvision, PIL, NumPy", style_table_text), Paragraph("Loads trained SimpleCNN weights, preprocesses incoming tensors, computes class logits, and processes backward gradient hooks.", style_table_text)],
        [Paragraph("Explainability (XAI)", style_table_text), Paragraph("OpenCV (cv2), Grad-CAM mathematical overlays", style_table_text), Paragraph("Extracts activation feature maps and gradients, blends a jet colormap with the original image, and exports JPEGs.", style_table_text)],
        [Paragraph("Persistence & Logging", style_table_text), Paragraph("SQLite3 database, native Python SQLite driver", style_table_text), Paragraph("Stores analysis records, files, prediction confidences, dates, and updates user details for historical report tracking.", style_table_text)],
        [Paragraph("PDF Compilation", style_table_text), Paragraph("ReportLab Flowables API (SimpleDocTemplate)", style_table_text), Paragraph("Compiles database records into double-channel imagery layouts, structured text flowables, and exports PDF files.", style_table_text)]
    ]
    
    arch_table = Table(arch_data, colWidths=[90, 150, 264])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    
    story.append(arch_table)
    
    story.append(Paragraph("2.2 Dynamic Request-Response Lifecycle", style_h2))
    story.append(Paragraph(
        "A typical client-server loop begins with a REST request to either `/api/diagnose/plant` or `/api/diagnose/animal`. The file is saved locally to generating a UUID name. The inference engine performs classification, passes the outputs to the Grad-CAM module to build the attention map, records the statistics in the SQLite database, and returns the metadata to the React app in a single, high-performance request-response cycle.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: SECTION 3: DEEP LEARNING ENGINE & TRAINING
    # =========================================================================
    story.append(Paragraph("3. Deep Learning Engine & Model Training", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_green, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("3.1 Neural Network Design: SimpleCNN", style_h2))
    story.append(Paragraph(
        "Both diagnostic domains utilize a custom 3-layer Convolutional Neural Network (CNN) class (`SimpleCNN`) that inherits from `torch.nn.Module`. This architecture balances classification performance with rapid, lightweight training execution, suitable for local setups without dedicated GPUs.",
        style_body
    ))
    story.append(Paragraph(
        "<b>• Conv2d Layers:</b> The network registers three sequential 2D convolutional layers. Conv1 converts the 3-channel input to 16 feature maps. Conv2 expands this to 32 channels, and Conv3 finishes with 64 channels. Each layer uses a 3x3 kernel with padding of 1 to preserve border spatial dimensions.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Max Pooling:</b> 2x2 Max Pooling layers downsample the activation grids by half after each convolution block, reducing a 224x224 input to 112x112, 56x56, and finally 28x28 pixels.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Fully Connected Layers:</b> The final 64x28x28 tensor is flattened into a 1D vector of 50,176 elements. A Linear layer maps this to a hidden layer of 128 elements, and the final classification layer maps to the category logits.",
        style_bullet
    ))

    story.append(Paragraph("3.2 Synthetic Data Training Pipeline", style_h2))
    story.append(Paragraph(
        "To allow instant local operation without requesting massive datasets, the backend includes `train_models.py` which auto-generates simulated datasets to train the PyTorch networks:",
        style_body
    ))
    story.append(Paragraph(
        "<b>1. Leaf Anomaly Simulation:</b> Synthesizes RGB image arrays representing green circular leaves. Diseased leaves are generated with random clusters of brown and yellow pixels to represent foliar lesions.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>2. Bone Trauma Simulation:</b> Synthesizes grayscale limb shapes against black backgrounds. Bone fractures are simulated as jagged lines of high contrast.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>3. Model Export:</b> The networks are trained using the Cross-Entropy loss function and Adam optimizer for 2 epochs, saving the final parameters to `plant_model.pth` and `xray_model.pth`.",
        style_bullet
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: SECTION 4: EXPLAINABLE AI (GRAD-CAM)
    # =========================================================================
    story.append(Paragraph("4. Explainable AI: Grad-CAM Implementation", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("4.1 Principles & Core Mathematics", style_h2))
    story.append(Paragraph(
        "Standard convolutional networks are often critiqued as 'black boxes' because their hidden decisions lack spatial visibility. AgroVet AI resolves this by overlaying Gradient-Weighted Class Activation Maps (Grad-CAM).",
        style_body
    ))
    story.append(Paragraph(
        "Grad-CAM uses the gradients flowing back from the predicted class logit ($y^c$) to the last convolutional layer's activation map ($A^k$) to compute an attention score for each filter. This highlights the spatial structures that drive the model's prediction.",
        style_body
    ))
    story.append(Paragraph(
        "First, we calculate the channel weight alpha ($\alpha_k^c$) by averaging the gradients over the height $v$ and width $u$ of the feature maps:",
        style_body
    ))
    story.append(Paragraph(
        "<i>&alpha;<sub>k</sub><sup>c</sup> = (1 / Z) &Sigma;<sub>i</sub> &Sigma;<sub>j</sub> (&part; y<sup>c</sup> / &part; A<sub>i,j</sub><sup>k</sup>)</i>",
        ParagraphStyle('Math', parent=style_body, alignment=TA_CENTER, fontName='Helvetica-Oblique', textColor=c_accent_blue)
    ))
    story.append(Paragraph(
        "Next, we compute a weighted linear combination of all forward activations $A^k$ and apply the Rectified Linear Unit (ReLU) to isolate features that positively contribute to the target class:",
        style_body
    ))
    story.append(Paragraph(
        "<i>L<sup>c</sup><sub>Grad-CAM</sub> = ReLU( &Sigma;<sub>k</sub> &alpha;<sub>k</sub><sup>c</sup> A<sup>k</sup> )</i>",
        ParagraphStyle('Math2', parent=style_body, alignment=TA_CENTER, fontName='Helvetica-Oblique', textColor=c_accent_blue)
    ))

    story.append(Paragraph("4.2 Interception Hooks and OpenCV Image Overlay", style_h2))
    story.append(Paragraph(
        "During model forward propagation, the network registers a gradient hook on the final conv layer using `x.register_hook(save_gradient)`. Once the backward gradient pass runs, these gradients are captured. The raw 2D activation matrix is normalized, resized using bilinear interpolation to match the dimensions of the original image, converted to a pseudo-color JET colormap, and blended with the original BGR image:",
        style_body
    ))
    story.append(Paragraph(
        "<b>Overlay Blend Formula:</b> <i>Image<sub>Overlay</sub> = 0.6 &middot; Image<sub>Original</sub> + 0.4 &middot; Heatmap<sub>Colored</sub></i>",
        ParagraphStyle('Formula', parent=style_body, alignment=TA_CENTER, fontName='Helvetica-Oblique')
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: SECTION 5: DATABASE & ADMIN ANALYTICS
    # =========================================================================
    story.append(Paragraph("5. Database & Admin Analytics Dashboard", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_green, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("5.1 Database Schema & Data Access Layer", style_h2))
    story.append(Paragraph(
        "To minimize deployment dependencies, data persistence is handled by a single SQLite database file (`backend/agrovet.db`). The database schema is designed for rapid diagnostic logging and telemetry parsing, tracking the raw file paths and generated Grad-CAM heatmap overlays.",
        style_body
    ))
    
    db_schema_data = [
        [Paragraph("<b>Field Name</b>", style_table_header), Paragraph("<b>Data Type</b>", style_table_header), Paragraph("<b>Constraints</b>", style_table_header), Paragraph("<b>Description</b>", style_table_header)],
        [Paragraph("id", style_table_text), Paragraph("INTEGER", style_table_text), Paragraph("PRIMARY KEY AUTOINCREMENT", style_table_text), Paragraph("Unique sequence identifier for the analysis entry.", style_table_text)],
        [Paragraph("user_name", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NULL", style_table_text), Paragraph("Demographic name collected before PDF download.", style_table_text)],
        [Paragraph("user_mobile", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NULL", style_table_text), Paragraph("Optional contact phone number.", style_table_text)],
        [Paragraph("user_email", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NULL", style_table_text), Paragraph("Optional electronic mail contact.", style_table_text)],
        [Paragraph("type", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Classification domain: 'plant' or 'animal'.", style_table_text)],
        [Paragraph("target_type", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Subject species/crop type (e.g., Dog, Tomato).", style_table_text)],
        [Paragraph("prediction", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Classified pathology name or medical finding.", style_table_text)],
        [Paragraph("confidence", style_table_text), Paragraph("REAL", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Softmax probability value (0.0 to 1.0).", style_table_text)],
        [Paragraph("image_path", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Local server path to original image.", style_table_text)],
        [Paragraph("heatmap_path", style_table_text), Paragraph("TEXT", style_table_text), Paragraph("NOT NULL", style_table_text), Paragraph("Local server path to Grad-CAM output.", style_table_text)],
        [Paragraph("created_at", style_table_text), Paragraph("TIMESTAMP", style_table_text), Paragraph("DEFAULT CURRENT_TIMESTAMP", style_table_text), Paragraph("Auto-generated submission time.", style_table_text)]
    ]
    
    db_table = Table(db_schema_data, colWidths=[70, 75, 110, 249])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(db_table)
    
    story.append(Paragraph("5.2 Telemetry Dashboard Interface", style_h2))
    story.append(Paragraph(
        "The server aggregates database records via `get_dashboard_stats()` to build the admin dashboard. To ensure a zero-dependency setup, the React client renders these trends using custom SVG vector graphics. The system draws line grids, dates, and glowing area polygons representing the monthly diagnostic load directly in the browser.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: SECTION 6: PDF REPORT GENERATION SYSTEM
    # =========================================================================
    story.append(Paragraph("6. PDF Report Generation System", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("6.1 Programmatic Document Compilation", style_h2))
    story.append(Paragraph(
        "AgroVet AI includes a high-fidelity PDF generation engine in `report_generator.py` powered by the ReportLab flowables pipeline. When a user requests a report, the server compiles the metadata, database fields, and local images into a structured PDF document.",
        style_body
    ))
    
    story.append(Paragraph("6.2 Layout Design & Flowables Flow", style_h2))
    story.append(Paragraph(
        "<b>• Branding Banner:</b> A structured table draws a charcoal background banner containing the 'AGROVET AI' title and domain details. A solid border matches the domain: Neon Green for agricultural reports, and Neon Blue for animal reports.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Demographic Metadata Grid:</b> A structured table formats the user name, email, contact phone, analysis date, and target subject parameters in a clean 2-column grid.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Double-Channel Visuals:</b> Renders the original uploaded image next to the Grad-CAM heatmap overlay. Images are constrained to $240 \text{ pt} \times 200 \text{ pt}$ boundaries to fit the margins without page overflow.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Structured Diagnoses:</b> Integrates symptom breakdowns, environmental causes, and action/treatment plans matching the predicted category.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Legal Disclaimer:</b> Every generated PDF includes a prominent, italicized footer warning that the AI-generated report is intended for preliminary screening and should be confirmed by a specialist veterinarian or plant pathologist.",
        style_bullet
    ))
    
    story.append(Paragraph("6.3 Streamed Delivery Pipeline", style_h2))
    story.append(Paragraph(
        "The PDF generation process runs synchronously within FastAPI. Once the document build is complete, the file path is wrapped in a FastAPI `FileResponse` object. This streams the raw PDF binary back to the client browser, prompting a native download dialog named after the user (e.g., `Dilip_Y_AgroVet_Report.pdf`).",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: SECTION 7: USER INTERFACE DESIGN SYSTEM
    # =========================================================================
    story.append(Paragraph("7. User Interface Design & Styling", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_green, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("7.1 Design Philosophy: NVIDIA-Style Glow", style_h2))
    story.append(Paragraph(
        "The AgroVet AI portal is designed with a premium, dark-mode-first aesthetic inspired by modern compute platforms like NVIDIA. Styling is defined in `src/index.css` using CSS custom variables to manage color palettes and interactive glowing borders.",
        style_body
    ))

    css_vars_data = [
        [Paragraph("<b>CSS Selector / Token</b>", style_table_header), Paragraph("<b>Value / Colors</b>", style_table_header), Paragraph("<b>Visual Application</b>", style_table_header)],
        [Paragraph("--bg-dark", style_table_text), Paragraph("#0a0f1d (Deep slate black)", style_table_text), Paragraph("Primary background color for the application viewport.", style_table_text)],
        [Paragraph("--card-bg", style_table_text), Paragraph("rgba(17, 24, 39, 0.7) (Translucent gray)", style_table_text), Paragraph("Background color for glassmorphic cards and containers.", style_table_text)],
        [Paragraph("--glow-green", style_table_text), Paragraph("#00e676 (Neon green)", style_table_text), Paragraph("Primary theme accent for plant diagnosis pages and success states.", style_table_text)],
        [Paragraph("--glow-blue", style_table_text), Paragraph("#00b0ff (Neon blue)", style_table_text), Paragraph("Primary theme accent for animal X-ray pages and metric highlights.", style_table_text)],
        [Paragraph("--text-light", style_table_text), Paragraph("#f3f4f6 (Off-white)", style_table_text), Paragraph("Primary readable body text color.", style_table_text)],
        [Paragraph("backdrop-filter", style_table_text), Paragraph("blur(12px)", style_table_text), Paragraph("Renders a glassmorphic blurred background behind transparent cards.", style_table_text)]
    ]
    
    css_table = Table(css_vars_data, colWidths=[120, 160, 224])
    css_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(css_table)
    
    story.append(Paragraph("7.2 Gated Report Acquisition Flow", style_h2))
    story.append(Paragraph(
        "To encourage data logging without creating friction, the platform does not require registration to perform scans. However, to download a PDF report, the interface prompts the user with a glassmorphic modal requesting their Name (Mandatory), Mobile Number (Optional), and Email (Optional). Once submitted, the backend logs these details and streams the generated report.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: SECTION 8: DEPLOYMENT & ROADMAP
    # =========================================================================
    story.append(Paragraph("8. Deployment Framework & Roadmap", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent_blue, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("8.1 Containerized Docker Deployment", style_h2))
    story.append(Paragraph(
        "To ensure AgroVet AI runs reliably across diverse desktop, tablet, and mobile browsers, the application is packaged in a multi-stage Docker container. Stage 1 compiles the React frontend assets, and Stage 2 sets up the Python backend server. The compiled React files are copied into the backend's static directories, allowing FastAPI to serve both the API and the user interface from a single port (8000).",
        style_body
    ))

    story.append(Paragraph("8.2 Optimization & Performance", style_h2))
    story.append(Paragraph(
        "<b>• Model Evaluation Mode:</b> The PyTorch models are initialized and locked in evaluation mode (`model.eval()`) on startup, disabling gradient caching for forward passes. This keeps memory usage low and response times fast during concurrent user requests.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>• Static Asset Caching:</b> Image files and generated Grad-CAM heatmaps are saved under the mounted static `/data` directory. These assets are cached by the browser to reduce redundant loads during UI navigation.",
        style_bullet
    ))

    story.append(Paragraph("8.3 Future Roadmap & Research Directions", style_h2))
    story.append(Paragraph(
        "<b>1. Advanced Backbone Models:</b> Upgrade the custom SimpleCNN classification backend to pre-trained transfer learning architectures like ResNet-50 or MobileNet-V3. This will improve prediction accuracy on complex, real-world leaf lesions and veterinary X-rays.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>2. Web Assembly (Wasm) Portability:</b> Export trained PyTorch weights to the ONNX format, allowing the models to run directly in the client browser. This enables offline field diagnostics under poor cellular coverage.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>3. Multi-Spectral Image Analysis:</b> Extend the agricultural model to parse multi-spectral satellite or drone imagery, enabling early crop disease detection before leaf damage becomes visible to RGB cameras.",
        style_bullet
    ))

    # Build document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report successfully compiled: {pdf_filename}")

if __name__ == "__main__":
    create_report_pdf()
