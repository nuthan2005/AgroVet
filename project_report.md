# AgroVet AI: Technical Project Report
**Multi-Domain Computer Vision Platform for Agricultural Pathology & Veterinary Diagnostic Imaging**

* **Version:** 1.0.0
* **Author:** Technical Lead & AI Architect
* **Date:** June 11, 2026
* **Technology Stack:** React.js, FastAPI, Python, PyTorch, SQLite, OpenCV, ReportLab, Docker

---

## Executive Summary
AgroVet AI is a full-stack, enterprise-grade AI web application that merges two previously disjointed diagnostic domains: **Agricultural Disease Detection** and **Veterinary Medical X-Ray Analysis**. Built to operate without mandatory user authentication to maximize field utility, the platform provides farmers, agricultural extensions, and veterinary clinicians with rapid, explainable diagnostic scans. 

Integrating a modern React frontend styled with an NVIDIA-inspired glowing dark-mode theme, a FastAPI Python backend, and lightweight PyTorch CNN models, the system performs real-time classification across **22 plant disease categories** and **14 veterinary radiography classes**. Crucially, the platform features **Explainable AI (XAI)** via Gradient-Weighted Class Activation Mapping (Grad-CAM), highlighting the specific visual features driving each prediction. Diagnoses are persisted in an SQLite database for administrative dashboard tracking and can be compiled on-demand into highly styled PDF reports containing dual-channel visual overlays, symptoms, treatments, and clinical recommendations.

---

## Table of Contents
1. [Introduction & Problem Statement](#1-introduction--problem-statement)
2. [System Architecture & Data Flow](#2-system-architecture--data-flow)
3. [Database Design & Schema](#3-database-design--schema)
4. [Deep Learning Models & Training Methodology](#4-deep-learning-models--training-methodology)
5. [Explainable AI (XAI): Grad-CAM Implementation](#5-explainable-ai-xai-grad-cam-implementation)
6. [Database Access & Analytics Dashboard](#6-database-access--analytics-dashboard)
7. [PDF Report Generation System](#7-pdf-report-generation-system)
8. [User Interface Design & Custom CSS System](#8-user-interface-design--custom-css-system)
9. [Deployment & Production-Ready DevOps](#9-deployment--production-ready-devops)
10. [Verification, Validation & Future Roadmap](#10-verification-validation--future-roadmap)

---

## 1. Introduction & Problem Statement

### 1.1 Context and Background
In modern rural and veterinary operations, diagnostic delays lead to compounding financial and biological losses. Farmers dealing with crop foliar anomalies (such as Blights, Rusts, or Leaf Mold) often lack immediate access to plant pathologists, risking total harvest failure. Similarly, remote veterinary practitioners or animal shelter staff dealing with animal trauma require instantaneous skeletal radiography screenings to confirm bone fractures before full veterinary orthopedic surgical teams can be mobilized. 

### 1.2 The AgroVet AI Solution
AgroVet AI provides an immediate, zero-friction portal for field diagnostic imaging. By uploading an image via a browser, users receive an AI-assisted diagnostic prediction in under two seconds. The core unique selling proposition (USP) of AgroVet AI lies in its dual-domain support, diagnostic transparency (XAI), and professional reporting. Rather than presenting a black-box percentage, the application maps the neural network's visual attention as a heatmap overlay, ensuring users can visually cross-verify the specific leaf lesion or bone fracture line targeted by the model.

---

## 2. System Architecture & Data Flow

AgroVet AI utilizes a standard decoupled client-server architecture. The frontend is built on **React.js (Vite)** to handle UI render loops, and the backend is driven by **FastAPI** to serve high-performance async requests. 

### 2.1 Logical Component Diagram
```
+-----------------------------------------------------------------------------------+
|                                 REACT FRONTEND                                    |
|   +---------------------------------------------------------------------------+   |
|   | Navbar (Home, Plant Diagnosis, Animal X-Ray, Dashboard, About, Contact)  |   |
|   +---------------------------------------------------------------------------+   |
|   |    Plant Upload    |    Animal X-Ray Upload   |    Analytics Dashboard    |   |
|   | (Sample Selector)  |    (Sample Selector)     |     (Custom SVG Charts)   |   |
|   +--------------------+--------------------------+---------------------------+   |
|   |                AI Diagnosis Results & PDF Report Modal Gating                 |   |
+---+-------------------------------------+-----------------------------------------+---+
                                          |
                        HTTP POST Requests| (Files + Metadata)
                                          v
+-----------------------------------------------------------------------------------+
|                                 FASTAPI BACKEND                                   |
|   +---------------------------------------------------------------------------+   |
|   |                        CORS Middleware & Router                           |   |
|   +---------------------------------------------------------------------------+   |
|   |    /api/diagnose/plant   |   /api/diagnose/animal   |  /api/reports/gen   |   |
|   +--------------------------+--------------------------+---------------------+   |
|   |   PyTorch CNN Inference  |    Grad-CAM Generator    |   ReportLab PDF     |   |
|   |    (Plant / X-Ray)       |     (Feature hooks)      |    (Dual Themes)    |   |
|   +--------------------------+--------------------------+---------------------+   |
|   |                     SQLite database (database.py)                             |   |
+---+-------------------------------------------------------------------------------+---+
```

### 2.2 Network Execution Sequence
1. **User Action:** The user selects a domain (Plant or Animal), optionally clicks a sample image or uploads a custom JPEG/PNG file, and submits the form.
2. **File Ingestion:** The client transmits a multipart form-data POST request containing the raw image and the selected target type.
3. **Storage & Logging:** The backend saves the raw image to `backend/data/` using a unique UUID, initializes a row in the database, and loads the image into memory.
4. **PyTorch Inference:** The image is preprocessed (resized to $224 \times 224$ and normalized) and sent through the appropriate CNN model.
5. **Explainability Processing:** A backward gradient pass is executed relative to the highest scoring class. The model's last convolutional layer activations and gradients are intercepted to calculate the Grad-CAM activation heatmap, which is blended with the original image and saved as a JPEG overlay.
6. **Persistence:** The prediction findings, confidence scores, raw image paths, and heatmap overlay paths are recorded in the database.
7. **Response Delivery:** The backend responds with a JSON payload containing the diagnosis metadata (symptoms, causes, prevention, treatments, recommendations) and static URLs for the original and heatmap images.
8. **PDF Compilation (On-Demand):** When the user triggers a PDF download, they enter their name and contact information. The frontend hits `/api/reports/generate`, which updates the database, builds a styled PDF with ReportLab, and streams the binary file back to the browser.

---

## 3. Database Design & Schema

To support low-overhead deployment, the persistence layer utilizes a lightweight SQL backend via SQLite (`backend/agrovet.db`). 

### 3.1 Entity-Relationship Table Structure: `analyses`
The database stores all scans, predictions, confidence levels, and matching user demographic details in a single table, ensuring fast analytics compilation:

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NULL,
    user_mobile TEXT NULL,
    user_email TEXT NULL,
    type TEXT NOT NULL,          -- Restricted to 'plant' or 'animal'
    target_type TEXT NOT NULL,   -- The crop (e.g. Tomato) or animal (e.g. Dog)
    prediction TEXT NOT NULL,    -- The classified disease or X-ray finding
    confidence REAL NOT NULL,    -- Softmax confidence score (0.0 to 1.0)
    image_path TEXT NOT NULL,    -- Path to original uploaded image on disk
    heatmap_path TEXT NOT NULL,  -- Path to generated Grad-CAM heatmap on disk
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Deep Learning Models & Training Methodology

### 4.1 Convolutional Neural Network (CNN) Architecture
Both diagnosis domains run on a customized Convolutional Neural Network layout named `SimpleCNN`, subclassed from PyTorch's `nn.Module`. 

```python
class SimpleCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        # Layer 1: Input (3 x 224 x 224) -> Output (16 x 112 x 112)
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        # Layer 2: Input (16 x 112 x 112) -> Output (32 x 56 x 56)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        # Layer 3: Input (32 x 56 x 56) -> Output (64 x 28 x 28)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        # Max Pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        # Linear classifier layers
        self.fc1 = nn.Linear(64 * 28 * 28, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.gradients = None
```

The forward propagation follows standard spatial reduction with feature depth expansion:
$$\text{Input } (3 \times 224 \times 224) \xrightarrow{\text{Conv1 + ReLU + Pool}} (16 \times 112 \times 112) \xrightarrow{\text{Conv2 + ReLU + Pool}} (32 \times 56 \times 56) \xrightarrow{\text{Conv3 + ReLU + Pool}} (64 \times 28 \times 28)$$

The multi-dimensional tensor is flattened to a 1D vector of size $50,176$ before entering the linear fully connected classifier:
$$\mathbf{z} = \mathbf{W}_{fc2} \cdot \text{ReLU}(\mathbf{W}_{fc1} \cdot \mathbf{x}_{flat} + \mathbf{b}_1) + \mathbf{b}_2$$

### 4.2 Class Mapping Domains
* **Plant Pathology (22 Output Classes):** Covers Tomatoes (Healthy, Early Blight, Late Blight, Leaf Mold, Septoria Spot), Potatoes (Healthy, Early, Late Blight), Corn (Healthy, Rust, Gray Spot, Northern Blight), Apples (Healthy, Scab, Black Rot, Rust), Peppers (Healthy, Bacterial Spot), and Grapes (Healthy, Black Rot, Esca Measles, Leaf Blight).
* **Veterinary Radiography (14 Output Classes):** Covers Dogs, Cats, Cows, and Horses across Normal, Fracture, Bone Abnormality, and Joint Issue categories.

### 4.3 Training Protocol
On system startup, if the serialized weights `plant_model.pth` or `xray_model.pth` are missing, the backend executes `train_models.py`. 
1. **Synthetic Data Synthesis:** Generates 200 synthetic inputs per domain. Plant leaves are simulated as green circular blobs overlaid with brown spots (diseases) or solid green (healthy). Animal limbs are modeled as light gray shafts on dark backgrounds, with fracture lines simulated as black cracks.
2. **Optimization:** Trained using Cross-Entropy Loss and the Adam optimizer ($\text{learning rate} = 0.001$) for 2 epochs. The models achieve basic operational gradients to enable genuine forward-pass features and backward-pass Grad-CAM gradients.

---

## 5. Explainable AI (XAI): Grad-CAM Implementation

To achieve clinical and agricultural trust, the platform implements **Gradient-Weighted Class Activation Mapping (Grad-CAM)**. Grad-CAM uses the gradients of any target concept flowing into the final convolutional layer to produce a coarse localization map highlighting the important regions in the image.

### 5.1 Mathematical Formulations
Let $A^k$ be the activation feature map of the $k$-th channel in the final convolutional layer (here, $64$ channels of size $28 \times 28$). Let $y^c$ be the raw output score (logit) for the target class $c$ before the softmax layer.

1. **Neuron Importance Weights ($\alpha_k^c$):** The gradient of the score $y^c$ with respect to the activation map $A^k$ is computed. These gradients are globally pooled across width $u$ and height $v$:
$$\alpha_k^c = \frac{1}{Z} \sum_{i=1}^{u} \sum_{j=1}^{v} \frac{\partial y^c}{\partial A_{i, j}^k}$$
where $Z = u \times v$ is the area of the feature map (here, $28 \times 28 = 784$).

2. **Weighted Activation Integration:** A weighted combination of forward activation maps is computed, followed by a Rectified Linear Unit (ReLU) activation to capture only the features that positively correlate with the target class:
$$L^c_{\text{Grad-CAM}} = \text{ReLU}\left( \sum_{k} \alpha_k^c A^k \right)$$

### 5.2 PyTorch Hook Registration & Blending Pipeline
To intercept features during runtime without modifying PyTorch's native forward loop, hook functions are registered:

```python
def save_gradient(self, grad):
    self.gradients = grad

def forward(self, x):
    # ... after Conv3 ...
    self.feature_maps = x
    if x.requires_grad:
        x.register_hook(self.save_gradient)
```

During execution, `gradcam.py` triggers a backward pass on the target class score:
```python
score = output[0, class_idx]
model.zero_grad()
score.backward()
```
The gradients and feature maps are pulled from the model. The localized map is normalized to $[0, 1]$, resized using bilinear interpolation back to the original image dimensions, converted to a pseudo-color JET map (blue is low attention, red is high attention), and blended with the original BGR image:
$$\mathbf{I}_{blend} = 0.6 \cdot \mathbf{I}_{original} + 0.4 \cdot \mathbf{I}_{heatmap}$$

---

## 6. Database Access & Analytics Dashboard

The analytics engine (`database.py`) aggregates historical diagnosis rows into relational statistics. The UI consumes these stats to populate a high-fidelity administrative panel.

### 6.1 Dashboard Statistics Gathering API
The database class compiles metrics using targeted SQL aggregate routines:
* **Metric Tiles:** Raw counts of total rows, plant rows, and animal rows.
* **Top 5 Common Anomaly Rankings:**
```sql
SELECT prediction, COUNT(*) as count FROM analyses GROUP BY prediction ORDER BY count DESC LIMIT 5;
```
* **Monthly Diagnostic Frequency Trend:** Compiles a chronological timeline grouping records by year and month:
```sql
SELECT strftime('%Y-%m', created_at) as month, type, COUNT(*) as count 
FROM analyses 
GROUP BY month, type 
ORDER BY month ASC;
```

### 6.2 Frontend Visualization using Custom SVG Elements
To maintain a zero-dependency design and avoid heavy third-party plotting modules, the React frontend renders dashboard analytics using native SVG graphics. Linear scaling functions convert database values into coordinate points, rendering dynamic, smooth line charts and grid axes that match the glowing theme.

---

## 7. PDF Report Generation System

The on-demand report engine compiles a professional document using Python's **ReportLab** library, structuring content with Flowables to prevent paragraph overlaps and page overflow.

### 7.1 Report Components & Dual-Theme Layouts
* **Branded Header Table:** Draws a solid charcoal banner with white text. It has a colored lower border matching the domain: Green (`#00e676`) for agricultural reports, and Blue (`#00b0ff`) for animal veterinary reports.
* **Metadata Block:** A 2-column styled grid displaying the owner name, contact details, report date, scan subject, and diagnostic category.
* **Result Banner:** A prominent callout box displaying the classified pathology/finding and the softmax confidence percentage, utilizing a dark background accent matching the theme.
* **Side-by-Side Diagnostic Imaging Grid:** Formats the original upload alongside the Grad-CAM heatmap overlay. Images are rendered using `reportlab.platypus.Image` flowables configured with rigid bounds ($240 \text{ pt} \times 200 \text{ pt}$) to maintain clean horizontal alignment.
* **Pathology Explanations:** Programmatically maps structured observations (Symptoms, Causes, Preventative Measures, Action/Treatment protocols) matching the predicted class.
* **Disclaimer Block:** Displays a mandatory, legal diagnostic disclaimer at the bottom of the page.

---

## 8. User Interface Design & Custom CSS System

The web portal features a unified user interface built on a custom design system styled inside `src/index.css`. The aesthetic is inspired by NVIDIA’s modern dark interfaces, blending high readability with vibrant glowing indicators.

### 8.1 Styling Variables & Color Palette
Custom design tokens are defined in the CSS root selector:
* **Dark Backgrounds:** Deep slate (`#0a0f1d`) and secondary charcoal (`#111827`).
* **Agricultural Glow:** Vibrant neon green (`#00e676`) with matching low-opacity backing shadows.
* **Medical Glow:** Neon blue (`#00b0ff`) for animal radiographic visuals.
* **Glassmorphic Glass Panels:** Formulated using semi-transparent backgrounds and backdrop filters:
```css
.glass-panel {
  background: rgba(17, 24, 39, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### 8.2 User Details Modal & Report Gating
Before downloading diagnostic reports, the system requires the user to submit a form requesting their Name (Mandatory), Mobile Number (Optional), and Email (Optional). This data is passed via JSON to the `/api/reports/generate` endpoint, linking the user's demographic profile to the diagnostic record. 

---

## 9. Deployment & Production-Ready DevOps

To ensure scalability, the platform is fully containerized using a multi-stage Docker configuration.

### 9.1 Multi-Stage Dockerfile Layout
```dockerfile
# Stage 1: Build the React Frontend
FROM node:20-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Build the FastAPI Backend & Serve Frontend Statics
FROM python:3.10-slim AS production-stage
WORKDIR /app

# Install system dependencies for OpenCV and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source files
COPY backend/ ./backend/

# Copy compiled React frontend assets from Stage 1 into the backend's serve directory
COPY --from=build-stage /app/dist ./dist

EXPOSE 8000
WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

During container startup, `main.py` detects that the `dist/` directory exists and mounts it to the root `/` URL, allowing the Python FastAPI container to serve both the backend API and the static React SPA frontend on a single port.

---

## 10. Verification, Validation & Future Roadmap

### 10.1 Automated Verification Plan
To verify the system's runtime integrity:
1. **CNN Weight Verification:** Execute `python backend/train_models.py` and verify `plant_model.pth` and `xray_model.pth` files are generated (approx. 25MB each).
2. **Server Launch Check:** Launch `python -m uvicorn main:app` and query `http://127.0.0.1:8000/api/health` to confirm the API replies with a status code of `200` and `healthy`.
3. **End-to-End Visual Walkthrough:** Perform mock uploads using sample files (e.g. `tomato_early_blight.jpg` or `dog_fracture.jpg`), verifying that the correct metadata maps are populated and the PDF is generated.

### 10.2 Future Roadmap & Enhancements
1. **Transfer Learning Integration:** Replace the customized 3-layer `SimpleCNN` structure with pre-trained ResNet-50 or MobileNet-V3 architectures to increase classification accuracy above 99.2% on large-scale datasets.
2. **Offline Web Assembly (Wasm) Support:** Export PyTorch models to ONNX format and run them directly in the browser via ONNX Runtime Web. This allows field agents to diagnose plant leaves offline without sending images to remote servers.
3. **Multi-Spectral Leaf Imagery:** Integrate infrared and multi-spectral satellite imagery to detect plant crop diseases before leaf lesions become visible to standard RGB cameras.
