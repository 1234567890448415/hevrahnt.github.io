# Nokia 235 4G Movie Converter (EXE-ready)

אפליקציית שולחן עבודה בפייתון להמרת סרטים (עד 5GB בקובץ קלט) לקובץ MP4 מותאם ל־**Nokia 235 4G**.

## מה זה עושה
- ממיר קבצי וידאו נפוצים (`mp4`, `mkv`, `avi`, `mov`, `webm`) ל־MP4.
- שומר פרופיל תאימות למכשירי פיצ'ר-פון:
  - וידאו: H.264 Baseline, רזולוציה 320x240, 25fps.
  - אודיו: AAC mono 64kbps.
- מאפשר בחירת איכות (`High`, `Balanced`, `Data Saver`).
- מגביל קלט עד 5GB.

## דרישות
1. Windows 10/11
2. Python 3.10+
3. ffmpeg מותקן וזמין ב־PATH

בדיקת ffmpeg:
```bat
ffmpeg -version
```

## הרצה מקומית
```bat
python movie_converter_nokia235.py
```

## בניית EXE
1. התקן PyInstaller:
```bat
pip install pyinstaller
```

2. בנה EXE:
```bat
pyinstaller --noconfirm --onefile --windowed --name Nokia235Converter movie_converter_nokia235.py
```

3. קובץ ההפעלה יופיע בנתיב:
`dist\Nokia235Converter.exe`

## הערות איכות
- `High` = איכות טובה יותר וקובץ גדול יותר.
- `Balanced` = איזון טוב לרוב הסרטים.
- `Data Saver` = קובץ קטן יותר, איכות נמוכה יותר.
