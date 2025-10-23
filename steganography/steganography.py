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
        
# tester mes fcts
def test_steganography():
    print("="*60)
    print("Tests de la stéganographie")
    print("="*60)

    # Test text_to_binary
    result = text_to_binary("Hi")
    expected = "0100100001101001"
    
    if result == expected:
        print("Successful")
    else:
        print("Failed")

    # Test binary_to_text
    binary_input = "0100100001101001"
    result = binary_to_text(binary_input)
    expected = "Hi"
    if result == expected:
        print("It works!")
    else:
        print("Failed")

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


if __name__ == "__main__":
    test_steganography()



        






