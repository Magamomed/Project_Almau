import re
from datetime import datetime

MONTHS_RU = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}

def parse_russian_date(text):
    match = re.search(r'(\d{1,2}) (\w+) (\d{4})', text)
    if match:
        day, month_text, year = match.groups()
        month = MONTHS_RU.get(month_text.lower())
        if month:
            return f"{year}-{month}-{int(day):02}"
    return None

def extract_general_info(text):
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    result = {
        'full_name': '',
        'birth_date': '',
        'birth_place': '',
        'citizenship': '',
        'iin': ''
    }

    # Извлечение ФИО
    for line in lines:
        words = line.split()
        if len(words) == 3 and all(w[0].isupper() for w in words):
            print(f"[DEBUG] Найдено ФИО: {line}")
            result['full_name'] = line.strip()
            break

    # Извлечение ИИН
    for line in lines:
        match = re.search(r'\b\d{12}\b', line)
        if match:
            print(f"[DEBUG] Найден ИИН: {match.group()}")
            result['iin'] = match.group()
            break

    # Извлечение даты рождения
    for line in lines:
        date = parse_russian_date(line)
        if date:
            print(f"[DEBUG] Найдена дата рождения: {date}")
            result['birth_date'] = date
            break

    # Извлечение места рождения (после даты рождения)
    for idx, line in enumerate(lines):
        if result['birth_date'] and line.strip().startswith(result['birth_date'].split('-')[0]):
            if idx + 1 < len(lines):
                print(f"[DEBUG] Найдено место рождения: {lines[idx + 1]}")
                result['birth_place'] = lines[idx + 1]
            break

    # Извлечение гражданства (улучшенный алгоритм)
    for idx, line in enumerate(lines):
        # Проверяем наличие ключевого слова с учетом возможных OCR-ошибок
        if "гражд" in line.lower():
            # Если в строке есть разделитель, используем часть после него
            if '|' in line:
                parts = line.split('|')
                if len(parts) > 1:
                    potential = parts[1].strip()
                    if potential:
                        print(f"[DEBUG] Найдено гражданство по разделителю: {potential}")
                        result['citizenship'] = potential
                        break
            # Иначе ищем ближайшую непустую строку после метки
            for j in range(idx + 1, len(lines)):
                if lines[j].strip():
                    print(f"[DEBUG] Найдено гражданство во второй строке: {lines[j].strip()}")
                    result['citizenship'] = lines[j].strip()
                    break
            break

    return result

def extract_passport_info(text):
    result = {
        'number': '',
        'issue_date': '',
        'issued_by': ''
    }

    match = re.search(r'удостоверение личности\s*(N|№)?\s*(\w+)', text.lower())
    if match:
        result['number'] = match.group(2)

    date_match = re.search(r'выдано.*?(\d{1,2} [а-я]+ \d{4})', text.lower())
    if date_match:
        result['issue_date'] = parse_russian_date(date_match.group(1))

    issue_by_match = re.search(r'выдано (мвд рк|.+?),', text.lower())
    if issue_by_match:
        result['issued_by'] = issue_by_match.group(1).strip()

    return result

def extract_education(text):
    lines = text.splitlines()
    education = []
    start = False

    for idx, line in enumerate(lines):
        if 'образование' in line.lower():
            print(f"[DEBUG] Найден блок образования: {line}")
            start = True
            continue
        if start:
            # Завершаем, если дошли до следующего логического блока
            if any(end in line.lower() for end in ['сведения о юридических лицах', 'трудовой деятельности']):
                print(f"[DEBUG] Конец блока образования на строке: {line}")
                break
            if line.strip():
                print(f"[DEBUG] Строка образования: {line}")
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    education.append({
                        'institution': parts[0],
                        'period': parts[1] if len(parts) > 1 else '',
                        'specialization': parts[2] if len(parts) > 2 else '',
                        'diploma': parts[3] if len(parts) > 3 else ''
                    })

    return education


def extract_relatives(text):
    lines = text.splitlines()
    relatives = []
    keywords = ['родственник', 'сведения о супруге', 'близких родственниках']

    for idx, line in enumerate(lines):
        if any(k in line.lower() for k in keywords):
            print(f"[DEBUG] Найден блок родственников: {line}")
            for rel_line in lines[idx + 1:]:
                if not rel_line.strip() or rel_line.lower().startswith('сведения о'):
                    break
                if len(rel_line.split()) >= 2:
                    print(f"[DEBUG] Родственник: {rel_line}")
                    relatives.append({
                        'full_name': rel_line.strip(),
                        'birth_year': '',
                        'relation': '',
                        'job': '',
                        'position': ''
                    })
            break

    return relatives

def extract_companies(text):
    companies = []
    pattern = re.compile(r'наименование.*?юридического лица.*?:?\s*(.+)', re.IGNORECASE)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if pattern.search(line):
            name = pattern.search(line).group(1).strip()
            bin_ = ''
            address = ''
            activity = ''
            share = ''
            for j in range(i + 1, min(i + 6, len(lines))):
                if 'бин' in lines[j].lower():
                    bin_ = lines[j].split()[-1]
                if 'адрес' in lines[j].lower():
                    address = lines[j]
                if 'вид' in lines[j].lower() and 'деятельности' in lines[j].lower():
                    activity = lines[j]
                if 'доля' in lines[j].lower():
                    share = re.findall(r'\d+%', lines[j])
                    share = share[0] if share else ''
            companies.append({
                'name': name,
                'bin': bin_,
                'address': address,
                'activity': activity,
                'share_percent': share
            })
    return companies

def extract_work_experience(text):
    lines = text.splitlines()
    work = []
    start = False

    for idx, line in enumerate(lines):
        if 'трудовой деятельности' in line.lower():
            print(f"[DEBUG] Найден блок трудовой деятельности: {line}")
            start = True
            continue
        if start:
            if any(end in line.lower() for end in ['сведения об участии', 'аудит', 'инвестиционных комитетах']):
                print(f"[DEBUG] Конец блока трудовой деятельности: {line}")
                break
            if line.strip():
                print(f"[DEBUG] Строка трудовой деятельности: {line}")
                work.append({
                    'organization': line.strip(),
                    'start_date': None,
                    'end_date': None,
                    'position': '',
                    'disciplinary': '',
                    'reason': '',
                    'notes': ''
                })
    return work

def extract_investment_membership(text):
    memberships = []
    pattern = r'сведения о членстве.*?инвестиционн.*?комитетах.*?:?\s*(.*)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        block = match.group(1)
        lines = block.splitlines()
        for line in lines:
            if line.strip() and not line.strip().lower().startswith('привлекался'):
                memberships.append({
                    'start_date': '',
                    'end_date': '',
                    'organization': line.strip()
                })
    return memberships

def extract_all(text):
    return {
        'general': extract_general_info(text),
        'passport': extract_passport_info(text),
        'education': extract_education(text),
        'relatives': extract_relatives(text),
        'companies': extract_companies(text),
        'work': extract_work_experience(text),
        'investment_membership': extract_investment_membership(text),
        'court_cases': [],
        'economic_crimes': [],
        'activity_bans': []
    }
