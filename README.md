# opencv-ocr-mandarin-translator
A Python utility for extracting hardcoded Mandarin subtitles from video files using OpenCV and EasyOCR, and translating them in rate-limited batches via `deep-translator`.

## Features

- **Region of Interest (ROI) Isolation:** Crops the lower region of video frames to isolate Chinese text and ignore secondary subtitle lines.
- **Unicode Character Filtering:** Employs regex matching (`\u4e00`–`\u9fff`) to ensure only frames containing actual Chinese characters are processed.
- **Frame Deduplication:** Tracks and ignores identical consecutive subtitle frames to prevent redundant processing.
- **Raw Text Preservation:** Exports extracted Mandarin lines to a text file before invoking the translation API.
- **Rate-Limited Batch Translation:** Translates text in small chunks with time delays to prevent API rate-limiting errors (`429 Too Many Requests`).
- **Progress Tracking:** Displays current frame processing progress and percentage completion in the terminal.
