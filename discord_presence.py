from pypresence import Presence
import time
import sys
import threading
import pickle
import os

client_id = '818186391568646164'  # Fake ID, put your real one here
RPC = Presence(client_id)  # Initialize the client class
RPC.connect()  # Start the handshake loop


while True:
    with open('shutdown.pickle', 'rb') as file:
        if pickle.load(file) == True:
            print('exiy')
            # os._exit(0)
    try:
        with open('discord.pickle', 'rb') as f:
            SONG_INFO = pickle.load(f)
    except:
        time.sleep(1)
    print(SONG_INFO)
    # if not SONG_INFO:
    #     time.sleep(1)
    #     continue
    try:
        name = SONG_INFO['name']
        artist = SONG_INFO['artist']
        album = SONG_INFO['album']
    except:
        print('rp')
        RPC.update(
            state=f"Listening to AudioPlayer",
            large_image='icon',
            details=f'Idle',
            large_text='Audioplayer',
        )

        time.sleep(15)
        continue
    RPC.update(
        state=f"Listening to AudioPlayer",
        large_image='icon',
        details=f'Listining to {name} by {artist} from {album}',
        party_size=[SONG_INFO['id'], SONG_INFO['last']],
        large_text='Audioplayer',
    )

    time.sleep(15)