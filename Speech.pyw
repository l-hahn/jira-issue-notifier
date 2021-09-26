from gtts import gTTS
import os
import playsound
import pathlib
from pprint import pprint

class speaker():
    def __init__(self,TextPref="",Lang='en',PathPref="sounddb/CRT/"):
        self._TextPref = TextPref
        self._Lang = Lang
        self._PathPref = PathPref
        self._CrtSoundDict = self.default_map()
        self._make_path()

    def create_sound_db(self, Texts = 'NoneNull', Keys = 'NoneNull'):
        del self._CrtSoundDict
        self._CrtSoundDict = {}
        if Texts == 'NoneNull':
            Texts = speaker._Text
        if Keys == 'NoneNull':
            Keys = speaker._CRT
        if len(Texts) != len(Keys):
            raise KeyError("Text data and Key data differ in length!")
        for idx,Text in enumerate(Texts):
            File = self.speak(idx,Text,self._TextPref,self._Lang)
            self._CrtSoundDict[Keys[idx]] = File
            self.play_sound(self.get_db_text2sound_file(Keys[idx]))

    def speak(self,Idx,Text,Pref="",Lang='en'):
        Text2Speech = gTTS(text=f'{Pref}{Text}', lang=Lang)
        File = f'{self._PathPref}{Idx}-voice.mp3'
        Text2Speech.save(File)
        return File

    def play_sound(self,File):
        playsound.playsound(File)

    def get_db_text2sound_file(self,Text):
        if Text in self._CrtSoundDict.keys():
            return self._CrtSoundDict[Text]
        else:
            raise KeyError("Text is not known to sound database!")

    def db(self):
        return self._CrtSoundDict

    def language(self):
        return self._Lang
    def path(self):
        return self._PathPref
    def text_prefix(self):
        return self._Pref
    def set_language(self, Lang):
        self._Lang = Lang
    def set_path(self, Path):
        self._PathPref = Path

    def default_keys(self):
        return speaker._CRT

    def default_text(self):
        return speaker._Text

    def default_map(self):
        return speaker._FileMap

    def _make_path(self):
        pathlib.Path('sounddb/CRT/').mkdir(parents=True, exist_ok=True)

    def has_default_db(self):
        HasDB = True
        for Key in speaker._FileMap:
            if not pathlib.Path(speaker._FileMap[Key]).is_file():
                HasDB = False
        return HasDB


    _CRT = [
        "Request_Type_1",
        "Request_Type_1"
    ]
    _Text = [
        "Incidient RT 1",
        "Important RT 2"
    ]
    _FileMap = {
        'Incidient RT 1': 'sounddb/CRT/1-voice.mp3',
        'Important RT 2': 'sounddb/CRT/2-voice.mp3',
    }


Speaker = speaker("New ticket in")
if not Speaker.has_default_db():
    print("Create DB")
    Speaker.create_sound_db()
