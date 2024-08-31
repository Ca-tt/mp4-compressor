.PHONY: clean

exe:
    pyinstaller --noconsole --onefile --name "MP4 compressor" --icon=img/mp4.ico src/main.py

clean:
    rm -rf build dist src/__pycache__ src/*.spec *.spec
