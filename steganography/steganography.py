import wave
import numpy as np

# fct pour convertir du texte en binaire (l msg secret)
def text_to_binary(text):
    result = ''
    for char in text:
        ascii = ord(char)
        result += format(ascii, '08b')
    return result

# fct pour convertir l binaire en texte (l msg secret)
def binary_to_text(binary):
    message = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:  # Ensure we have a complete byte
            nbr = int(byte, 2)
            message += chr(nbr)
    return message
     
# fct pour cacher le msg dans l'audio    
def hide_in_audio(input_path, secret_message, output_path):
    # Open and read the input audio file
    audio = wave.open(input_path, 'rb')
    n_channels = audio.getnchannels()  # mono wla stereo
    sample_width = audio.getsampwidth()  # shhel toul tae l frame
    framerate = audio.getframerate()  # shhel men frame per second
    n_frames = audio.getnframes()  # nbr de frames

    frames = audio.readframes(n_frames)
    audio.close()

    # Convert to numpy array for easier manipulation
    audio_data = np.frombuffer(frames, dtype=np.int16).copy()
    
    # Prepare the message with end delimiter
    message_with_end = secret_message + "###END###"
    binary_message = text_to_binary(message_with_end)
    
    # Check if message fits in audio
    if len(binary_message) > len(audio_data):
        raise ValueError(f"Message too long! Message needs {len(binary_message)} samples but audio only has {len(audio_data)} samples.")
    
    print(f"Audio samples: {len(audio_data)}")
    print(f"Message bits: {len(binary_message)}")
    print(f"Message will use {(len(binary_message)/len(audio_data))*100:.2f}% of audio")
    
    # Hide message in LSB of audio samples
    for i in range(len(binary_message)):
        # Clear the LSB and set it to the message bit
        audio_data[i] = (audio_data[i] & ~1) | int(binary_message[i])
    
    # Write the modified audio to output file
    stego_audio = wave.open(output_path, 'wb')
    stego_audio.setnchannels(n_channels)
    stego_audio.setsampwidth(sample_width)
    stego_audio.setframerate(framerate)
    stego_audio.writeframes(audio_data.tobytes())
    stego_audio.close()

    print(f"Message hidden successfully in {output_path}")
    return True
    

# fct pour extraire le msg de l'audio   
def extract_from_audio(audio_path):
    # Open and read the audio file
    audio = wave.open(audio_path, 'rb')
    n_frames = audio.getnframes()
    frames = audio.readframes(n_frames)
    audio.close()
    
    # Convert to numpy array
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    # Extract LSB from each sample
    binary_message = ""
    for sample in audio_data:
        binary_message += str(sample & 1)  # Get the last bit
    
    # Convert binary to text
    message = binary_to_text(binary_message)
    
    # Find and return message before delimiter
    if "###END###" in message:
        return message.split("###END###")[0]
    else:
        # Try to find readable text even without delimiter
        # Stop at first non-printable character sequence
        result = ""
        for char in message:
            if 32 <= ord(char) <= 126 or char in '\n\r\t':
                result += char
            elif len(result) > 10:  # If we have some text, stop at garbage
                break
        return result if result else "No readable message found"
        
# tester mes fcts
def test_steganography():
    print("=" * 60)
    print("Tests de la stéganographie")
    print("=" * 60)

    # Test text_to_binary
    result = text_to_binary("Hi")
    expected = "0100100001101001"
    
    if result == expected:
        print("✓ text_to_binary: Successful")
    else:
        print("✗ text_to_binary: Failed")

    # Test binary_to_text
    binary_input = "0100100001101001"
    result = binary_to_text(binary_input)
    expected = "Hi"
    if result == expected:
        print("✓ binary_to_text: It works!")
    else:
        print("✗ binary_to_text: Failed")

    # Test hide_in_audio
    input_file = "storm-tone.wav"
    output_file = "test_stego.wav"
    secret_message = "Hello World!"
    
    try:
        hide_in_audio(input_file, secret_message, output_file)
        print("✓ hide_in_audio: Succeeded, msg caché avec succès")
    except Exception as e:
        print(f"✗ hide_in_audio: Failed, erreur : {e}")
        return  
    
    # Test extract_from_audio
    try:
        extracted_message = extract_from_audio(output_file)
        print(f"Message extrait : '{extracted_message}'")
        print(f"Message original : '{secret_message}'")
        
        if extracted_message == secret_message:
            print("✓ extract_from_audio: Succeeded, msgs identiques !")
        else:
            print(f"✗ extract_from_audio: Failed, msgs différents")
            print(f"  Différence : '{secret_message}' ≠ '{extracted_message}'")
    except Exception as e:
        print(f"✗ extract_from_audio: Failed, erreur : {e}")


if __name__ == "__main__":
    test_steganography()