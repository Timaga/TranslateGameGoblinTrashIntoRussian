import re
from deep_translator import GoogleTranslator

def translate_text(text, src='en', dest='ru'):
    try:
        return GoogleTranslator(source=src, target=dest).translate(text)
    except Exception as e:
        print(f"Ошибка при переводе текста '{text}': {e}")
        return text

input_file = 'input.txt'
output_file = 'output_translated_1.txt'


with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()


translated_lines = list(lines)


field_data_start_re = re.compile(r'^\s*0\s+Field\s+data')
value_re = re.compile(r'^(\s+1\s+string\s+value\s*=\s*")(.*?)(")')
type_string_re = re.compile(r'^\s+1\s+string\s+typeString\s*=\s*"CustomFieldType_Text"')
title_re = re.compile(r'^\s+1\s+string\s+title\s*=\s*"(.*)"$')

i = 0
while i < len(lines):
    line = lines[i]

    if field_data_start_re.match(line):
        print(f"Найден блок 'Field data' на строке {i + 1}")

        if i + 4 >= len(lines):
            print(f"Недостаточно строк для обработки блока, начинающегося на строке {i + 1}")
            break

        try:
            title_line = lines[i + 1]
            value_line = lines[i + 2]
            type_line = lines[i + 3]
            type_string_line = lines[i + 4]
        except IndexError:
            print(f"Блок на строках {i + 1}-{i + 5} имеет неожиданную длину. Пропускаем.")
            i += 5
            continue

        title_match = title_re.match(title_line)
        value_match = value_re.match(value_line)
        type_match = re.match(r'^\s+0\s+int\s+type\s*=\s*\d+$', type_line)
        type_string_match = type_string_re.match(type_string_line)

        if not (title_match and type_match and type_string_match):
            print(f"Блок на строках {i + 1}-{i + 5} имеет неожиданную структуру. Пропускаем.")
            i += 5
            continue

        if not value_match:
            print(f"Строка 'value' на строке {i + 3} не соответствует ожидаемому формату. Пропускаем блок.")
            i += 5
            continue

        title_text = title_match.group(1)
        if "Dialogue Text" not in title_text:
            print(f"Строка 'title' на строке {i + 2} не содержит 'Dialogue Text'. Пропускаем блок.")
            i += 5
            continue
        try:
            indent, original_value, closing_quote = value_match.groups()
            print(f"Перевод строки {i + 3}: {original_value}")
            original_value = original_value.strip()

            translated_text = translate_text(original_value, src='en', dest='ru')
            print(f"Переведённый текст: {translated_text}")

            translated_text_escaped = translated_text.replace('"', '\\"')

            translated_value_line = f'{indent}{translated_text_escaped}{closing_quote}\n'

            translated_lines[i + 2] = translated_value_line
            print(f"Строка {i + 3} обновлена.")

        except Exception as e:
            print(f"Ошибка при переводе строки {i + 3}: {e}")

        i += 5
    else:
        i += 1

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(translated_lines)

print(f"Перевод завершён. Изменённый файл сохранён как '{output_file}'.")
