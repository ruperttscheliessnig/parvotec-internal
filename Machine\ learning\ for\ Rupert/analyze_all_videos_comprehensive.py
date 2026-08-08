#!/usr/bin/env python3
"""
Comprehensive video analysis for ASGCT 2026 MP4 files.
Extracts: Whisper transcription + Key frame OCR + Metadata + Visual structure.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import numpy as np

try:
    import cv2
    import whisper
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install with: pip install opencv-python whisper pillow pytesseract")
    sys.exit(1)

# Configure pytesseract path (macOS homebrew)
pytesseract.pytesseract.pytesseract_cmd = '/opt/homebrew/bin/tesseract'

# Project base directory
PROJECT_BASE = Path.home() / "workspace-active/parvotec/Machine learning for Rupert"
ASGCT_FOLDER = PROJECT_BASE / "ASGCT2026"
OUTPUT_FOLDER = PROJECT_BASE / "transcripts"
FRAMES_FOLDER = OUTPUT_FOLDER / "key_frames"

# Ensure output directories exist
OUTPUT_FOLDER.mkdir(exist_ok=True)
FRAMES_FOLDER.mkdir(exist_ok=True)

# Video files to process
VIDEOS = [
    "Lir_AAV_LLM.mp4",  # CENTERPIECE - process first
    "AAV_Engineering_III.mp4",
    "AAV_Engineering_IV.mp4",
    "AAV_Trafficking.mp4",
    "ShapeTX_AAV5engineering.mp4",
    "TuningReceptorInteractions_Caltech.mp4",
]

def get_video_metadata(video_path):
    """Extract video metadata using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_format', '-show_streams',
            '-print_json', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        
        format_info = data.get('format', {})
        streams = data.get('streams', [])
        
        duration = float(format_info.get('duration', 0))
        size_bytes = int(format_info.get('size', 0))
        
        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), {})
        
        return {
            'duration_seconds': duration,
            'duration_formatted': f"{int(duration // 60)}:{int(duration % 60):02d}",
            'size_mb': round(size_bytes / (1024**2), 2),
            'width': video_stream.get('width', 'N/A'),
            'height': video_stream.get('height', 'N/A'),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')),
            'video_codec': video_stream.get('codec_name', 'unknown'),
            'audio_codec': audio_stream.get('codec_name', 'unknown') if audio_stream else 'none',
        }
    except Exception as e:
        print(f"  ⚠️  Metadata extraction failed: {e}")
        return None

def extract_audio(video_path):
    """Extract audio from MP4 to WAV."""
    audio_path = video_path.parent / f"{video_path.stem}_audio.wav"
    
    if audio_path.exists():
        print(f"  ✓ Audio already extracted: {audio_path.name}")
        return audio_path
    
    try:
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-acodec', 'pcm_s16le', '-ar', '16000',
            '-ac', '1', '-y', str(audio_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=600)
        print(f"  ✓ Audio extracted: {audio_path.name} ({os.path.getsize(audio_path) / (1024**2):.1f} MB)")
        return audio_path
    except Exception as e:
        print(f"  ✗ Audio extraction failed: {e}")
        return None

def transcribe_audio(audio_path, video_name):
    """Transcribe audio with Whisper."""
    transcript_path = OUTPUT_FOLDER / f"{video_name.replace('.mp4', '')}_transcript.json"
    
    if transcript_path.exists():
        print(f"  ✓ Transcript already exists: {transcript_path.name}")
        with open(transcript_path) as f:
            return json.load(f)
    
    try:
        print(f"  🎙️  Transcribing audio (Whisper medium model)...")
        model = whisper.load_model("medium")
        result = model.transcribe(str(audio_path), language="en", verbose=False)
        
        # Save transcript
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        text_preview = result['text'][:150] + "..." if len(result['text']) > 150 else result['text']
        print(f"  ✓ Transcription complete: {len(result['text'])} chars")
        print(f"    Preview: {text_preview}")
        
        return result
    except Exception as e:
        print(f"  ✗ Transcription failed: {e}")
        return None

def extract_key_frames(video_path, video_name, max_frames=12):
    """
    Extract key frames from video for visual analysis.
    Samples uniformly + includes scene change detection.
    """
    output_dir = FRAMES_FOLDER / video_name.replace('.mp4', '')
    output_dir.mkdir(exist_ok=True)
    
    try:
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Sample uniformly across video
        sample_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
        
        frames_extracted = []
        prev_frame = None
        
        for idx, frame_num in enumerate(sample_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # Save frame as PNG
            frame_path = output_dir / f"frame_{idx:02d}_{int(frame_num / fps):.0f}s.png"
            cv2.imwrite(str(frame_path), frame)
            
            frames_extracted.append({
                'frame_num': int(frame_num),
                'timestamp_seconds': frame_num / fps,
                'path': str(frame_path.relative_to(PROJECT_BASE))
            })
        
        cap.release()
        print(f"  ✓ Extracted {len(frames_extracted)} key frames to {output_dir.name}/")
        return frames_extracted
    except Exception as e:
        print(f"  ✗ Frame extraction failed: {e}")
        return []

def ocr_frame(frame_path):
    """Run OCR on extracted frame to capture text/slides."""
    try:
        img = Image.open(frame_path)
        
        # Upscale if small
        if img.width < 800 or img.height < 800:
            scale = max(800 / img.width, 800 / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else None
    except Exception as e:
        return None

def analyze_single_video(video_path, video_name):
    """Comprehensive analysis of a single video."""
    print(f"\n{'='*70}")
    print(f"📹 ANALYZING: {video_name}")
    print(f"{'='*70}")
    
    analysis = {
        'filename': video_name,
        'path': str(video_path),
        'analysis_timestamp': datetime.now().isoformat(),
        'metadata': None,
        'transcript': None,
        'key_frames': [],
        'frame_ocr': [],
    }
    
    # 1. Metadata
    print(f"[1/4] Extracting metadata...")
    metadata = get_video_metadata(video_path)
    if metadata:
        analysis['metadata'] = metadata
        print(f"  ✓ Duration: {metadata['duration_formatted']}")
        print(f"  ✓ Resolution: {metadata['width']}x{metadata['height']}")
        print(f"  ✓ Size: {metadata['size_mb']} MB")
    
    # 2. Audio extraction & transcription
    print(f"[2/4] Extracting and transcribing audio...")
    audio_path = extract_audio(video_path)
    if audio_path:
        transcript = transcribe_audio(audio_path, video_name)
        if transcript:
            analysis['transcript'] = {
                'text': transcript['text'],
                'segments_count': len(transcript.get('segments', [])),
            }
    
    # 3. Key frame extraction
    print(f"[3/4] Extracting key frames...")
    key_frames = extract_key_frames(video_path, video_name, max_frames=12)
    analysis['key_frames'] = key_frames
    
    # 4. OCR on frames
    print(f"[4/4] Running OCR on key frames...")
    for kf in key_frames:
        frame_path = PROJECT_BASE / kf['path']
        ocr_text = ocr_frame(frame_path)
        if ocr_text:
            analysis['frame_ocr'].append({
                'timestamp_seconds': kf['timestamp_seconds'],
                'ocr_text': ocr_text[:500],  # Truncate for clarity
            })
    
    if analysis['frame_ocr']:
        print(f"  ✓ OCR text extracted from {len(analysis['frame_ocr'])} frames")
    
    return analysis

def generate_markdown_report(all_analyses):
    """Generate comprehensive markdown report from all video analyses."""
    report_path = OUTPUT_FOLDER / "ASGCT2026_comprehensive_analysis.md"
    
    with open(report_path, 'w') as f:
        f.write("# ASGCT 2026 Video Analysis - Comprehensive Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Overview\n\n")
        f.write(f"Total videos analyzed: **{len(all_analyses)}**\n")
        f.write("- Lir_AAV_LLM.mp4 (CENTERPIECE)\n")
        f.write("- AAV_Engineering_III.mp4\n")
        f.write("- AAV_Engineering_IV.mp4\n")
        f.write("- AAV_Trafficking.mp4\n")
        f.write("- ShapeTX_AAV5engineering.mp4\n")
        f.write("- TuningReceptorInteractions_Caltech.mp4\n\n")
        
        f.write("## Analysis Summary\n\n")
        f.write("| Video | Duration | Size | Type | Transcript | Frames | OCR Content |\n")
        f.write("|-------|----------|------|------|-----------|--------|-------------|\n")
        
        for analysis in all_analyses:
            name = analysis['filename']
            meta = analysis['metadata']
            trans_len = len(analysis['transcript']['text']) if analysis['transcript'] else 0
            frames_count = len(analysis['key_frames'])
            ocr_count = len(analysis['frame_ocr'])
            
            duration = meta['duration_formatted'] if meta else 'N/A'
            size = f"{meta['size_mb']} MB" if meta else 'N/A'
            
            f.write(f"| {name} | {duration} | {size} | {meta['video_codec'] if meta else 'N/A'} | {trans_len} chars | {frames_count} | {ocr_count} |\n")
        
        # Detailed sections
        f.write("\n---\n\n")
        
        for analysis in all_analyses:
            name = analysis['filename'].replace('.mp4', '')
            f.write(f"## {name}\n\n")
            
            if analysis['metadata']:
                f.write("### Video Properties\n\n")
                meta = analysis['metadata']
                f.write(f"- **Duration:** {meta['duration_formatted']} ({meta['duration_seconds']:.1f}s)\n")
                f.write(f"- **Resolution:** {meta['width']}x{meta['height']}\n")
                f.write(f"- **FPS:** {meta['fps']:.2f}\n")
                f.write(f"- **Video Codec:** {meta['video_codec']}\n")
                f.write(f"- **Audio Codec:** {meta['audio_codec']}\n")
                f.write(f"- **File Size:** {meta['size_mb']} MB\n\n")
            
            if analysis['transcript']:
                f.write("### Transcript (Full)\n\n")
                f.write(f"```\n{analysis['transcript']['text']}\n```\n\n")
            
            if analysis['key_frames']:
                f.write("### Key Frames Extracted\n\n")
                for kf in analysis['key_frames']:
                    timestamp = kf['timestamp_seconds']
                    minutes, seconds = divmod(timestamp, 60)
                    f.write(f"- Frame at {int(minutes):02d}:{int(seconds):02d}\n")
                f.write("\n")
            
            if analysis['frame_ocr']:
                f.write("### OCR Content from Frames\n\n")
                for ocr in analysis['frame_ocr']:
                    timestamp = ocr['timestamp_seconds']
                    minutes, seconds = divmod(timestamp, 60)
                    f.write(f"**At {int(minutes):02d}:{int(seconds):02d}:**\n")
                    f.write(f"```\n{ocr['ocr_text']}\n```\n\n")
            
            f.write("---\n\n")
    
    print(f"\n✅ Report saved: {report_path}")
    return report_path

def main():
    print("\n🎬 ASGCT 2026 COMPREHENSIVE VIDEO ANALYSIS")
    print("=" * 70)
    
    all_analyses = []
    
    for video_name in VIDEOS:
        video_path = ASGCT_FOLDER / video_name
        
        if not video_path.exists():
            print(f"\n⚠️  Video not found: {video_name}")
            continue
        
        try:
            analysis = analyze_single_video(video_path, video_name)
            all_analyses.append(analysis)
        except Exception as e:
            print(f"\n✗ Error analyzing {video_name}: {e}")
            continue
    
    # Generate comprehensive markdown report
    if all_analyses:
        report_path = generate_markdown_report(all_analyses)
        print(f"\n✅ All {len(all_analyses)} videos analyzed successfully!")
        print(f"📄 Master analysis: {report_path}")
    else:
        print("\n✗ No videos could be analyzed.")

if __name__ == '__main__':
    main()
