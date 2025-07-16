# Introduction

This document provides a technical overview of the solution for Adobe's "Connecting the Dots" hackathon. The project consists of two primary components: a heading extraction engine (Round 1A) and a semantic relevance engine (Round 1B). The overall architecture is a hybrid, multi-stage pipeline designed to meet specific performance and accuracy requirements.

# System Architecture

The solution is composed of two distinct, interconnected engines:

## Heading Extraction Engine

The objective of this engine is to process a PDF document and generate a structured JSON outline containing its title and hierarchical headings (H1, H2, H3). The design prioritizes high-speed, offline processing on a CPU-only architecture.

### Core Technology: PDF Parsing

The foundation of the engine is the *PyMuPDF (Fitz)* library, selected for its high performance and granular data extraction capabilities. As Python bindings for a C-based library, it offers a significant speed advantage over pure Python alternatives.

It utilizes the `Page.get_text("dict")` method, which provides a structured representation of the page content. This method yields a hierarchy of blocks, lines, and spans, along with the following critical metadata for each text element:

* **Bounding Box (`bbox`)**: The precise coordinates of the text on the page.
* **Font Properties (`font`, `size`, `flags`)**: The font name, size, and a bitmask indicating properties such as bold or italic.
* **Writing Direction (`dir`)**: A tuple representing the text's angle, essential for correctly interpreting non-horizontal text layouts.

This detailed output serves as the primary input for the classification methodology.

