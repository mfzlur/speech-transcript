import requests

def transcripted_file(filename):

    # Define the URL for the Deepgram API endpoint
    url = "https://api.deepgram.com/v1/listen"

    # Define the headers for the HTTP request
    headers = {
        "Authorization": "Token 267e1b74c95b68233013bc4f0259eb5cb3aec673",
        "Content-Type": "audio/*"
       
    }

    params = {
        "detect_language": "true",
        "paragraphs": "true"
    }

    # Get the audio file
    with open("./uploaded-files/" + filename, "rb") as audio_file:
        # Make the HTTP request
        response = requests.post(url,  params=params, headers=headers,data=audio_file,  verify=False)

    return response.json()

if __name__ == "__main__":
    # print(transcripted_file("harvard.wav")['metadata']['duration'])
    # print(transcripted_file("harvard.wav")['results']['channels'][0]['alternatives'][0]['transcript'])
    # print(transcripted_file("harvard.wav")['results']['channels'][0]['alternatives'][0]['words'])

    print(transcripted_file("My_unnamed_clip_2.wav")['results']['channels'][0]['alternatives'][0]['transcript'])
