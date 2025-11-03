import wave
import numpy as np

# fct pour convertir du texte en binaire (l msg secret)

def text_to_binary(text):
    result=''
    for char in text:
        ascii=ord(char)
        result+=format(ascii,'08b')
    return result

# fct pour convertir l binaire en texte (l msg secret)
def binary_to_text(binary):
    message=''
    for i in range(0,len(binary),8):
        byte=binary[i:i+8]
        nbr=int(byte,2)
        message+=chr(nbr)
    return message
     
# fct pour cacher le msg dans l'audio    
def hide_in_audio(input_path, secret_message, output_path):
    audio = wave.open(input_path,'rb')
    n_channels=audio.getnchannels()  #mono wla stereo
    sample_width = audio.getsampwidth() #shhel toul tae l frame
    framerate = audio.getframerate()  #shhel men frame per second
    n_frames=audio.getnframes()   #nbr de frames

    frames=audio.readframes(n_frames)
    audio.close()

    audio_data = np.frombuffer(frames, dtype=np.int16).copy()  #nconvertih from brute data to usable bytes array
    #audio entiers 16 bits, format standard des audios cd
    message_with_end = secret_message + "###END###"
    binary_message = text_to_binary(message_with_end)
    print(f"Longueur du message en bits : {len(binary_message)}")
    print(f"Capacité de l'audio en bits : {len(audio_data)}")
    if len(binary_message)>len(audio_data):
        raise ValueError("ce message est trop long pour l'audio")
        
    for i in range (len (binary_message)):
        audio_data[i] = (audio_data[i] & ~1) | int(binary_message[i])  #modification du lsb de chaque échantillon audio avec le bit du message
            
    stego_audio=wave.open(output_path, 'wb')
    stego_audio.setnchannels(n_channels)
    stego_audio.setsampwidth(sample_width)
    stego_audio.setframerate(framerate)
    stego_audio.writeframes(audio_data.tobytes())
    stego_audio.close()

    return True
    

# fct pour extraire le msg de l'audio   
def extract_from_audio(audio_path):
    audio = wave.open(audio_path, 'rb')
    n_frames = audio.getnframes()
    frames = audio.readframes(n_frames)
    audio.close()
    
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    # extraire les lsb
    binary_message = ""
    for sample in audio_data:
        binary_message += str(sample & 1)  # i take le dernier bit
    
    message = binary_to_text(binary_message)
    
    # find le delimiteur end
    if "###END###" in message:
        return message.split("###END###")[0]
    else:
        return message 
        

# visualisation
def visualize_lsb_changes(original_path, stego_path, secret_message, num_samples=None):
  
    audio_orig = wave.open(original_path, 'rb')
    frames_orig = audio_orig.readframes(audio_orig.getnframes())
    audio_orig.close()
    audio_data_original = np.frombuffer(frames_orig, dtype=np.int16)
    

    audio_stego = wave.open(stego_path, 'rb')
    frames_stego = audio_stego.readframes(audio_stego.getnframes())
    audio_stego.close()
    audio_data_modified = np.frombuffer(frames_stego, dtype=np.int16)
    

    message_with_end = secret_message + "###END###"
    binary_message = text_to_binary(message_with_end)
    

    if num_samples is None:
        num_samples = len(binary_message)
    

    print("\n" + "="*100)
    print("VISUALISATION DES MODIFICATIONS LSB")
    print("="*100)
    print(f"Message caché : '{secret_message}'")
    print(f"Message en binaire : {binary_message} : ({len(binary_message)} bits)")
    print(f"Affichage de {min(num_samples, len(binary_message))} échantillons")
    print("="*100)
    

    print(f"\n{'Index':<8} {'Original':<10} {'Modifié':<10} {'LSB Avant':<12} {'LSB Après':<12} {'Bit Message':<12} {'Changé?'}")
    print("-"*100)
    

    for i in range(min(num_samples, len(binary_message))):
        original = audio_data_original[i]
        modified = audio_data_modified[i]
        lsb_before = original & 1
        lsb_after = modified & 1
        message_bit = binary_message[i]
        changed = "✓ OUI" if original != modified else "✗ NON"
        
        print(f"{i:<8} {original:<10} {modified:<10} {lsb_before:<12} {lsb_after:<12} {message_bit:<12} {changed}")
    
    print("-"*100)
    

    changes = sum(1 for i in range(len(binary_message)) if audio_data_original[i] != audio_data_modified[i])
    print(f"\nStatistiques :")
    print(f"  - Échantillons modifiés : {changes}/{len(binary_message)}")
    print(f"  - Pourcentage de modifications : {(changes/len(binary_message))*100:.2f}%")
    print(f"  - Différence maximale : ±1 (imperceptible à l'oreille)")



# tester mes fcts
def test_steganography():
    print("="*60)
    print("Tests de la stéganographie")
    print("="*60)

    # Test text_to_binary
    result = text_to_binary("Hi")
    expected = "0100100001101001"
    
    if result == expected:
        print("Text to binary works!")
    else:
        print("Text to binary failed")

    # Test binary_to_text
    binary_input = "0100100001101001"
    result = binary_to_text(binary_input)
    expected = "Hi"
    if result == expected:
        print("Binary to text works!")
    else:
        print("Binary to text failed")


    # Test stégano complète
    input_file = "storm-tone.wav"
    output_file = "test_stego.wav"
    secret_message = "Masa2 el khayr 12!"
    
    print(f"\n[Test 3] Stéganographie avec le message : '{secret_message}'")
    
    # Cacher le message
    print("\nCamouflage du message dans l'audio...")
    try:
        hide_in_audio(input_file, secret_message, output_file)
        print("Message caché avec succès!\n")
    except Exception as e:
        print(f"Erreur : {e}")
        return
    
    # VISUALISER (après avoir créé le fichier)
    visualize_lsb_changes(input_file, output_file, secret_message)
    
    #Extraire le message
    print("\nExtraction du message...")
    try:
        extracted_message = extract_from_audio(output_file)
        print(f"Message extrait : '{extracted_message}'")
        print(f"Message original : '{secret_message}'")
        
        if extracted_message == secret_message:
            print("Succès ! Messages identiques!")
        else:
            print("Échec, messages différents")
    except Exception as e:
        print(f"Erreur : {e}")

"""
    # Test hide_in_audio
    input_file="storm-tone.wav"
    output_file = "test_stego.wav"
    secret_message = "Hello World!"
    try:
        hide_in_audio(input_file, secret_message, output_file)
        print("Succeded, msg caché avec succès")
    except Exception as e:
        print(f"Failed, erreur : {e}")
        return  
    
    # Test extract_from_audio
    try:
        extracted_message = extract_from_audio(output_file)
        print(f"Message extrait : '{extracted_message}'")
        print(f"Message original : '{secret_message}'")
        
        if extracted_message == secret_message:
            print("Succeded, msgs identiques !")
        else:
            print("Failed, msgs différents")
            print(f"  Différence : '{secret_message}' ≠ '{extracted_message}'")
    except Exception as e:
        print(f"Failed, erreur : {e}")
"""

if __name__ == "__main__":
    test_steganography()
