# Document Intelligence Pipeline

A high-performance, multi-stage document processing solution for extracting structured information and semantic insights from PDF documents. This project was developed for the "Connecting the Dots" hackathon and consists of two primary engines optimized for CPU-only execution.

## Features

### Round 1A: Heading Extraction Engine
- **Advanced Statistical Analysis**: Dynamic adaptive thresholding with z-score normalization for font size analysis
- **Hybrid Scoring Engine**: Combines statistical anomaly detection with linguistic intelligence
- **Multi-language Support**: Handles Latin, CJK (Chinese, Japanese, Korean), Arabic, Hebrew, Cyrillic, Thai, Greek, and Indic scripts
- **Intelligent Classification**: Multi-pass pipeline with contextual role tagging and hierarchical refinement
- **Linguistic Intelligence**: Lightweight spaCy integration for POS tagging and semantic analysis
- **High Performance**: Optimized for speed with PyMuPDF library and CPU-only architecture under 100MB footprint
---
## Architecture

### Round 1A: Heading Extraction
```
PDF Input → PyMuPDF Parser → Feature Engineering → Statistical Analysis → Contextual Tagging → Hybrid Scoring → Dynamic Thresholding → JSON Output
```

**Multi-Pass Pipeline:**
1. **Deep Feature Extraction**: Font properties, positioning, linguistic features, script detection
2. **Statistical Analysis**: Document typography census with z-score normalization
3. **Contextual Role Tagging**: Position-based classification (headers/footers/noise detection)
4. **Hybrid Scoring Engine**: Statistical anomaly detection + linguistic intelligence + visual cues
5. **Dynamic Adaptive Thresholding**: Automatic threshold calculation based on document statistics
6. **Hierarchical Refinement**: Numeric prefix detection and style-based level assignment

---
## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd your-repo
```

### 2. Install Dependencies (for Round 1A)
```bash
pip install -r requirements.txt
```

### 2. Setup Input Data

**For Round 1A:**
```bash
# Place PDF files in the data directory
cp your-pdfs/*.pdf ./input/
```

### 3. Run the Solutions

**Round 1A - Heading Extraction:**
```bash
bash run_solution_1a.sh
```
Output will be generated in `./output/` directory as structured JSON files.

---
## 📁 Project Structure

```
your-repo/
├── README.md                          # Current File
├── requirements.txt                   # Python dependencies
├── run_solution_1a.sh                 # Round 1A execution script
├── run_solution_1b.sh                 # Round 1B execution script
├── Dockerfile                         # Round 1A container configuratio
├── input/                             # Round 1A input PDFs
├── models/                            # Optimized ONNX models
├── output/
├── notebooks/
│   └── 01_model_optimization.ipynb    # To be implemented
└── src/
    ├── common/
    │   └── pdf_parser.py              # Shared PDF parsing utilities
    └── round_1a/
        ├── main.py                    # Round 1A main executable
        └── heading_detector.py        # Heading detection logic
```
---
## Technical Details

### Round 1A Technologies
- **PyMuPDF (Fitz)**: High-performance PDF parsing with granular text extraction
- **spaCy**: Lightweight NLP model (en_core_web_sm) for linguistic intelligence
- **Statistical Analysis**: Z-score normalization and dynamic thresholding algorithms
- **Unicode Analysis**: Comprehensive script detection across 8 major writing systems
- **Hybrid Classification**: Multi-feature scoring with contextual role tagging
- **Fragment Reconstruction**: Intelligent line merging for broken PDF text elements

### Performance Optimizations
- **INT8 Quantization**: 2-3x faster CPU inference
- **Multi-stage Pipeline**: Balanced speed and accuracy
- **Efficient Indexing**: FAISS for fast similarity search
---
## 🌐 Language Support

### Round 1A
- **8 Major Scripts**: Latin, CJK (Chinese, Japanese, Korean), Arabic, Hebrew, Cyrillic, Thai, Greek, Indic
- **Special Handling**: 
  - CJK bracket detection (【...】 for Japanese headings)
  - Right-to-left text support for Arabic/Hebrew
  - Script-specific keyword recognition
- **Adaptive Heuristics**: Context-aware classification based on detected script
---
## Output Formats

### Round 1A Output
```json
{
  "title": "Document Title Not Found",
  "outline": [
    {
      "text": "Introduction",
      "page": 1,
      "level": "H1"
    },
    {
      "text": "1.1 Background",
      "page": 2,
      "level": "H2"
    },
    {
      "text": "1.1.1 Problem Statement",
      "page": 2,
      "level": "H3"
    }
  ]
}
```

---
## 🐳 Docker Usage

Rounds are containerized for consistent execution across environments:

```bash
# Build and run Round 1A container
docker build -f Dockerfile -t doc-intelligence-1a .
docker run -v $(pwd)/data:/app/input -v $(pwd)/output_1a:/app/output doc-intelligence-1a

```
---
## Troubleshooting

### Common Issues
- **Missing spaCy Model**: Run `python -m spacy download en_core_web_sm` for Round 1A
- **Memory Issues**: Verify sufficient RAM for document processing (especially for linguistic analysis)
- **Docker Issues**: Ensure Docker daemon is running and has adequate resources
---
## Usage

This project was developed for the "Connecting the Dots" hackathon.

---

*Built with ❤️ for intelligent document processing!*
