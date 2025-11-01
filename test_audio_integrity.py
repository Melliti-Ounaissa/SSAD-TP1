#!/usr/bin/env python
"""
Audio File Integrity Tester
Tests WAV files before and after steganography to diagnose audio cutting issues
"""

import wave
import os
import sys

def test_wav_file(filepath):
    """Test a WAV file and print detailed information"""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath}")
    print(f"{'='*60}")
    
    if not os.path.exists(filepath):
        print(f"❌ File does not exist!")
        return False
    
    file_size = os.path.getsize(filepath)
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    
    try:
        with wave.open(filepath, 'rb') as wav:
            # Get audio parameters
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()
            
            # Calculate duration
            duration = n_frames / float(framerate)
            
            # Print details
            print(f"✓ Valid WAV file")
            print(f"\n📊 Audio Properties:")
            print(f"  Channels: {n_channels} ({'Mono' if n_channels == 1 else 'Stereo' if n_channels == 2 else f'{n_channels} channels'})")
            print(f"  Sample Width: {sample_width} bytes ({sample_width * 8} bits)")
            print(f"  Sample Rate: {framerate:,} Hz")
            print(f"  Total Frames: {n_frames:,}")
            print(f"  Duration: {duration:.2f} seconds")
            
            # Calculate theoretical file size
            data_size = n_frames * n_channels * sample_width
            header_size = 44  # Standard WAV header
            expected_size = data_size + header_size
            
            print(f"\n📏 Size Analysis:")
            print(f"  Expected data: {data_size:,} bytes")
            print(f"  Expected total: {expected_size:,} bytes")
            print(f"  Actual size: {file_size:,} bytes")
            
            if abs(file_size - expected_size) > 100:
                print(f"  ⚠️  Size mismatch! Difference: {abs(file_size - expected_size)} bytes")
            else:
                print(f"  ✓ Size matches expected")
            
            # Read actual audio data
            frames_data = wav.readframes(n_frames)
            actual_data_size = len(frames_data)
            
            print(f"\n🔍 Data Integrity:")
            print(f"  Expected frames data: {data_size:,} bytes")
            print(f"  Actual frames data: {actual_data_size:,} bytes")
            
            if actual_data_size != data_size:
                print(f"  ❌ DATA CORRUPTION! Missing {data_size - actual_data_size} bytes")
                return False
            else:
                print(f"  ✓ All audio data present")
            
            # Calculate message capacity
            capacity = n_frames
            capacity_chars = capacity // 8
            
            print(f"\n💬 Steganography Capacity:")
            print(f"  Can hide: {capacity:,} bits")
            print(f"  Can hide: {capacity_chars:,} characters")
            print(f"  Can hide: ~{capacity_chars//1024:.1f} KB of text")
            
            return True
            
    except wave.Error as e:
        print(f"❌ WAV Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def compare_audio_files(original, stego):
    """Compare original and steganography files"""
    print(f"\n{'='*60}")
    print("COMPARISON: Original vs Steganography")
    print(f"{'='*60}")
    
    # Test both files
    print("\n🔵 ORIGINAL FILE:")
    orig_ok = test_wav_file(original)
    
    print("\n🟢 STEGANOGRAPHY FILE:")
    stego_ok = test_wav_file(stego)
    
    # Compare
    if orig_ok and stego_ok:
        try:
            with wave.open(original, 'rb') as orig_wav, wave.open(stego, 'rb') as stego_wav:
                orig_frames = orig_wav.getnframes()
                stego_frames = stego_wav.getnframes()
                orig_rate = orig_wav.getframerate()
                stego_rate = stego_wav.getframerate()
                
                print(f"\n⚖️  COMPARISON RESULTS:")
                print(f"  Frames: {orig_frames:,} → {stego_frames:,}")
                if orig_frames == stego_frames:
                    print(f"  ✓ Frame count preserved")
                else:
                    print(f"  ❌ Frame count changed! Lost {orig_frames - stego_frames} frames")
                    print(f"     This will cause audio to cut off early!")
                
                print(f"  Duration: {orig_frames/orig_rate:.2f}s → {stego_frames/stego_rate:.2f}s")
                
                if orig_frames != stego_frames:
                    print(f"\n⚠️  AUDIO WILL BE CUT SHORT BY {(orig_frames - stego_frames)/orig_rate:.2f} SECONDS!")
        except Exception as e:
            print(f"❌ Comparison failed: {e}")


def test_uploads_directory():
    """Test all files in uploads directory"""
    upload_dir = 'uploads'
    
    if not os.path.exists(upload_dir):
        print(f"❌ Uploads directory not found: {upload_dir}")
        return
    
    wav_files = [f for f in os.listdir(upload_dir) if f.endswith('.wav')]
    
    if not wav_files:
        print(f"No WAV files found in {upload_dir}")
        return
    
    print(f"\nFound {len(wav_files)} WAV files in {upload_dir}:\n")
    
    for filename in sorted(wav_files):
        filepath = os.path.join(upload_dir, filename)
        test_wav_file(filepath)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        # Compare two files
        compare_audio_files(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        # Test single file
        test_wav_file(sys.argv[1])
    else:
        # Test all files in uploads
        test_uploads_directory()