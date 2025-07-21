import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Any
import spacy


class HeadingDetector:
    """
    Heading detection engine using statistical and linguistic features.
    """

    def __init__(self, doc_pages: List[Dict[str, Any]]):
        self.doc_pages = doc_pages
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except OSError:
            raise RuntimeError("Failed to load SpaCy model.")
        
        self.lines = self._preprocess_and_featurize()
        self.stats = self._calculate_document_statistics()
        self._tag_contextual_roles()
        self.classified_headings = []

    # === Pass 1: Preprocessing / Featurization === #

    def _get_script(self, text: str) -> str:
        if not text:
            return "Other"

        scripts = {
            "Latin": [(0x0020, 0x024F)], "Cyrillic": [(0x0400, 0x052F)],
            "Arabic": [(0x0600, 0x06FF)], "Hebrew": [(0x0590, 0x05FF)],
            "Devanagari": [(0x0900, 0x097F)], "Bengali": [(0x0980, 0x09FF)],
            "Gurmukhi": [(0x0A00, 0x0A7F)], "Gujarati": [(0x0A80, 0x0AFF)],
            "Oriya": [(0x0B00, 0x0B7F)], "Tamil": [(0x0B80, 0x0BFF)],
            "Telugu": [(0x0C00, 0x0C7F)], "Kannada": [(0x0C80, 0x0CFF)],
            "Malayalam": [(0x0D00, 0x0D7F)], "Sinhala": [(0x0D80, 0x0DFF)],
            "Thai": [(0x0E00, 0x0E7F)], "Lao": [(0x0E80, 0x0EFF)],
            "Tibetan": [(0x0F00, 0x0FFF)], "Myanmar": [(0x1000, 0x109F)],
            "Georgian": [(0x10A0, 0x10FF)], "Hangul": [(0xAC00, 0xD7AF)],
            "Greek": [(0x0370, 0x03FF)], "Armenian": [(0x0530, 0x058F)],
            "CJK": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x3040, 0x30FF)]
        }

        counts = defaultdict(int)
        for char in text:
            code = ord(char)
            for script, ranges in scripts.items():
                if any(start <= code <= end for start, end in ranges):
                    counts[script] += 1
                    break
        return max(counts, key=counts.get) if counts else "Other"

    def _preprocess_and_featurize(self) -> List[Dict[str, Any]]:
        raw_lines = []

        for i, page in enumerate(self.doc_pages):
            page_width = page.get("width", 612)
            page_height = page.get("height", 792)
            page_dims = {"width": page_width, "height": page_height}

            for block in page.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    text = "".join(span["text"] for span in spans).strip()
                    if not text:
                        continue
                    raw_lines.append(
                        self._extract_initial_features(line, text, i + 1, page_dims)
                    )

        merged_lines = self._merge_fragmented_lines(raw_lines)

        for i, line in enumerate(merged_lines):
            prev_line = (
                merged_lines[i - 1] if i > 0 and merged_lines[i - 1]["page_num"] == line["page_num"] else None
            )
            line["space_before"] = (
                line["bbox"][1] - prev_line["bbox"][3] if prev_line else 20.0
            )

            doc_nlp = self.nlp(line["text"])
            total = len(doc_nlp)
            line["noun_ratio"] = sum(1 for t in doc_nlp if t.pos_ == "NOUN") / total if total else 0
            line["verb_ratio"] = sum(1 for t in doc_nlp if t.pos_ == "VERB") / total if total else 0

        return merged_lines

    def _extract_initial_features(self, line, text, page_num, page_dims):
        span = line["spans"][0]
        height = page_dims["height"]
        return {
            "text": text,
            "page_num": page_num,
            "bbox": line["bbox"],
            "font_size": round(span["size"], 2),
            "font_name": span["font"],
            "script": self._get_script(text),
            "role": "content",
            "is_bold": "bold" in span["font"].lower() or (span["flags"] & 1 << 4),
            "is_all_caps": text.isupper() and len(text) > 2 and self._get_script(text) == "Latin",
            "word_count": len(text.split()),
            "y_percent": line["bbox"][1] / height if height else 0
        }

    def _merge_fragmented_lines(self, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not lines:
            return []

        merged = []
        buffer = lines[0]

        for curr in lines[1:]:
            vertical_gap = abs(curr["bbox"][1] - buffer["bbox"][3])
            if (
                curr["page_num"] == buffer["page_num"]
                and curr["font_size"] == buffer["font_size"]
                and vertical_gap < buffer["font_size"] * 0.4
            ):
                buffer["text"] += " " + curr["text"]
                buffer["bbox"] = (
                    min(buffer["bbox"][0], curr["bbox"][0]),
                    min(buffer["bbox"][1], curr["bbox"][1]),
                    max(buffer["bbox"][2], curr["bbox"][2]),
                    max(buffer["bbox"][3], curr["bbox"][3])
                )
            else:
                merged.append(buffer)
                buffer = curr

        merged.append(buffer)
        return merged

    # === Pass 2: Statistical & Contextual Analysis === #

    def _calculate_document_statistics(self) -> Dict[str, float]:
        content = [l for l in self.lines if 7 < l["font_size"] < 30]
        if not content:
            return {"mean_size": 10, "std_dev_size": 1, "body_size": 10, "mean_space": 3}

        font_sizes = [l["font_size"] for l in content]
        spaces = [l["space_before"] for l in content if 0 < l["space_before"] < 20]
        mean = sum(font_sizes) / len(font_sizes)
        std_dev = math.sqrt(sum((s - mean) ** 2 for s in font_sizes) / len(font_sizes)) if len(font_sizes) > 1 else 1.0

        return {
            "mean_size": mean,
            "std_dev_size": max(std_dev, 1.0),
            "body_size": Counter(font_sizes).most_common(1)[0][0],
            "mean_space": sum(spaces) / len(spaces) if spaces else 3.0
        }

    def _tag_contextual_roles(self):
        noise = defaultdict(list)
        for line in self.lines:
            if line["y_percent"] < 0.10:
                line["role"] = "potential_header"
            elif line["y_percent"] > 0.90:
                line["role"] = "potential_footer"

            if line["role"] in {"potential_header", "potential_footer"}:
                noise[line["text"]].append(line)

        for text, lines in noise.items():
            if len(set(l["page_num"] for l in lines)) > 1:
                for l in lines:
                    l["role"] = "noise"

        keywords = {'en': ['chapter', 'introduction', 'conclusion', 'references', 'appendix']}
        for line in self.lines:
            if line["word_count"] < 5 and any(line["text"].lower().startswith(k) for k in keywords['en']):
                line["role"] = "h1_keyword"


    ### Pass 3: The Hybrid Scoring & Classification Engine

    def _get_heading_score(self, line: Dict[str, Any]) -> float:
        """Calculates a heading score using the hybrid engine."""
        if line['role'] in ('noise', 'potential_footer') or not (0 < line['word_count'] < 35) or line['text'].endswith((':', '：')):
            return 0
        
        z_size = (line['font_size'] - self.stats['mean_size']) / self.stats['std_dev_size']
        space_ratio = line['space_before'] / self.stats['mean_space'] if self.stats['mean_space'] > 0 else 1
        stat_score = max(0, z_size) * 3.0 + max(0, space_ratio - 1) * 1.5

        boost = 0
        if line['is_bold']: boost += 2.0
        if line['is_all_caps']: boost += 1.5
        if line['noun_ratio'] > 0.4 and line['verb_ratio'] < 0.1: boost += 2.0
        if line['script'] == 'CJK' and '【' in line['text']: boost += 5.0
        if re.match(r'^\s*(\d{1,2}(\.\d{1,2})*|[A-Z]\.|[IVXLCDM]+\.)', line['text']): boost += 4.5
        return stat_score + boost

    def classify(self) -> Dict[str, Any]:
        """This method executes the entire classification pipeline using the dynamic scoring engine"""
        
        scored_lines = []
        for line in self.lines:
            if line['role'] == 'h1_keyword':
                line['level'] = 'H1'; self.classified_headings.append(line)
            elif line['role'] == 'content':
                score = self._get_heading_score(line)
                if score > 0: line['score'] = score; scored_lines.append(line)
        
        if scored_lines:
            scores = [line['score'] for line in scored_lines]
            mean_score = sum(scores) / len(scores)
            std_dev_score = math.sqrt(sum([(s - mean_score) ** 2 for s in scores]) / len(scores)) if len(scores) > 1 else 0
            dynamic_threshold = mean_score + (std_dev_score * 1.75)
            candidates = [line for line in scored_lines if line['score'] > dynamic_threshold]
            self._refine_and_finalize(candidates)
        
        title_text = ""
        if self.classified_headings:
            title_candidates = [h for h in self.classified_headings if h['page_num'] == 1 and h['y_percent'] < 0.4]
            if title_candidates:
                title_obj = max(title_candidates, key=lambda x: x.get('score', 0))
                title_text = title_obj['text']
                self.classified_headings.remove(title_obj)

        outline = [{"text": h["text"], "page": h["page_num"], "level": h.get("level", "H3")} for h in self.classified_headings]
        outline.sort(key=lambda x: (x["page"], self._get_line_y_pos(x["text"], x["page"])))
        
        return {
            "title": title_text, 
            "outline": outline
        }


    def _refine_and_finalize(self, candidates: List[Dict[str, Any]]):
        """Performs logical hierarchy validation on the final candidates."""
        if not candidates: return
        style_key = lambda line: (line['font_size'], line['is_bold'])
        level_map = {key: f"H{i+1}" for i, key in enumerate(sorted(list(set(style_key(c) for c in candidates)), key=lambda x: -x[0]))}
        for line in candidates:
            level = level_map.get(style_key(line), "H3")
            match = re.match(r"^\s*(\d+(\.\d+)*)", line['text'])
            if match:
                depth = match.group(1).count('.')
                if depth < 3: level = f"H{depth + 1}"
            line['level'] = level
            self.classified_headings.append(line)
            
    def _get_line_y_pos(self, text: str, page_num: int) -> float:
        for line in self.lines:
            if line["text"] == text and line["page_num"] == page_num:
                return line["bbox"][1]
        return float('inf')