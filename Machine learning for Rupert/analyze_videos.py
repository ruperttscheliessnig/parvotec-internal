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
    print(f"Error: Missing package: {e}")
    sys.exit(1)

# Configure pytesseract path
pytesseract.pytesseract.pytesseract_cmd = '/opt/homebrew/bin/tesseract'

PROJECT_BASE = Path.cwd()
ASGCT_FOLDER = PROJECT_BASE / "ASGCT2026"
OUTPUT_FOLDER = PROJECT_BASE / "transcripts"
FRAMES_FOLDER = OUTPUT_FOLDER / "key_frames"

OUTPUT_FOLDER.mkdir(exist_ok=True)
FRAMES_FOLDER.mkdir(exist_ok=True)

VIDEOS = [
    "Lir_AAV_LLM.mp4",
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
        size_mb = os.path.getsize(audio_path) / (1024**2)
        print(f"  ✓ Audio extracted: {audio_path.name} ({size_mb:.1f} MB)")
        return audio_path
    except Exception as e:
        print(f"  ✗ Audio extraction failed: {e}")
        return None

def transcribe_audio(audio_path, video_name):
    """Transcribe audio with Whisper."""
    transcript_path = OUTPUT_FOLDER / f"{video_name.replace('.mp4', '')}_transcript.json"
    
    if transcript_path.exists():
        print(f"  ✓ Transcript exists: {transcript_path.name}")
        with open(transcript_path) as f:
            return json.load(f)
    
    try:
        print(f"  🎙️  Transcribing (Whisper medium)...")
        model = whisper.load_model("medium")
        result = model.transcribe(str(audio_path), language="en", verbose=False)
        
        with open(transcript_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        text_len = len(result['text'])
        print(f"  ✓ Transcript done: {text_len} chars")
        return result
    except Exception as e:
        print(f"  ✗ Transcription failed: {e}")
        return None

def extract_key_frames(video_path, video_name, max_frames=12):
    """Extract key frames from video."""
    output_dir = FRAMES_FOLDER / video_name.replace('.mp4', '')
    output_dir.mkdir(exist_ok=True)
    
    try:
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        sample_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
        
        frames_extracted = []
        
        for idx, frame_num in enumerate(sample_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            frame_path = output_dir / f"frame_{idx:02d}_{int(frame_num / fps):.0f}s.png"
            cv2.imwrite(str(frame_path), frame)
            
            frames_extracted.append({
                'frame_num': int(frame_num),
                'timestamp_seconds': frame_num / fps,
                'path': str(frame_path.relative_to(PROJECT_BASE))
            })
        
        cap.release()
        print(f"  ✓ Extracted {len(frames_extracted)} key frames")
        return frames_extracted
    except Exception as e:
        print(f"  ✗ Frame extraction failed: {e}")
        return []

def ocr_frame(frame_path):
    """Run OCR on frame."""
    try:
        img = Image.open(frame_path)
        if img.width < 800 or img.height < 800:
            scale = max(800 / img.width, 800 / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else None
    except Exception:
        return None

def analyze_video(video_path, video_name):
    """Analyze a single video."""
    print(f"\n{'='*70}")
    print(f"📹 {video_name}")
    print(f"{'='*70}")
    
    analysis = {
        'filename': video_name,
        'path': str(video_path),
        'metadata': None,
        'transcript': None,
        'key_frames': [],
    }
    
    print(f"[1/3] Metadata...")
    metadata = get_video_metadata(video_path)
    if metadata:
        analysis['metadata'] = metadata
        print(f"  Duration: {metadata['duration_formatted']}, {metadata['width']}x{metadata['height']}")
    
    print(f"[2/3] Audio + Transcription...")
    audio_path = extract_audio(video_path)
    if audio_path:
        transcript = transcribe_audio(audio_path, video_name)
        if transcript:
            analysis['transcript'] = {
                'text': transcript['text'],
                'segments': len(transcript.get('segments', [])),
            }
    
    print(f"[3/3] Key frames + OCR...")
    key_frames = extract_key_frames(video_path, video_name, max_frames=12)
    analysis['key_frames'] = key_frames
    
    return analysis

def generate_report(all_analyses):
    """Generate markdown report."""
    report_path = OUTPUT_FOLDER / "ASGCT2026_comprehensive_analysis.md"
    
    with open(report_path, 'w') as f:
        f.write("# ASGCT 2026 - Comprehensive Video Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Videos Analyzed:** {len(all_analyses)}\n\n")
        
        for analysis in all_analyses:
            name = analysis['filename'].replace('.mp4', '')
            f.write(f"\n## {name}\n\n")
            
            if analysis['metadata']:
                meta = analysis['metadata']
                f.write(f"**Duration:** {meta['duration_formatted']} | ")
                f.write(f"**Size:** {meta['size_mb']} MB | ")
                f.write(f"**Resolution:** {meta['width']}x{meta['height']}\n\n")
            
            if analysis['transcript']:
                f.write("### Transcript\n\n")
                f.write(f"```\n{analysis['transcript']['text']}\n```\n\n")
            
            f.write("---\n\n")
    
    print(f"\n✅ Report: {report_path}")
    return report_path

def main():
    print("\n🎬 ASGCT 2026 COMPREHENSIVE VIDEO ANALYSIS\n")
    
    all_analyses = []
    
    for video_name in VIDEOS:
        video_path = ASGCT_FOLDER / video_name
        if not video_path.exists():
            print(f"⚠️  Not found: {video_name}")
            continue
        
        try:
            analysis = analyze_video(video_path, video_name)
            all_analyses.append(analysis)
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    if all_analyses:
        generate_report(all_analyses)
        print(f"\n✅ Analyzed {len(all_analyses)} videos")

if __name__ == '__main__':
    main()
