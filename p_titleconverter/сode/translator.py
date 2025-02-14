#!/usr/bin/env python
import argparse
from deep_translator import GoogleTranslator

def is_timecode_line(line: str) -> bool:
    return '-->' in line

def is_numeric_line(line: str) -> bool:
    return line.strip().isdigit()

def translate_srt(input_path: str, output_path: str):
    translator = GoogleTranslator(source='en', target='ru')
    print(f"Начало перевода файла: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    output_lines = []
    for idx, line in enumerate(lines):
        if is_numeric_line(line) or is_timecode_line(line) or line.strip() == "":
            output_lines.append(line)
        else:
            try:
                translated_text = translator.translate(line)
                print(f"Строка {idx+1} переведена: {translated_text}")
                output_lines.append(translated_text + "\n")
            except Exception as e:
                print(f"Ошибка при переводе строки {idx+1}: {e}")
                output_lines.append(line)
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(output_lines)
    print(f"Перевод завершён. Результат записан в: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Translate SRT subtitles from English to Russian using deep-translator'
    )
    parser.add_argument('input_file', help='Path to input SRT file')
    parser.add_argument('output_file', help='Path to output translated SRT file')
    args = parser.parse_args()
    
    print(f"Translating file: {args.input_file}")
    try:
        translate_srt(args.input_file, args.output_file)
        print(f"Translation complete: {args.output_file}")
    except Exception as e:
        print(f"Error during translation: {e}")
        exit(1)

if __name__ == '__main__':
    main()
