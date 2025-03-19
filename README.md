# Анализатор текстовых файлов

## Обзор
Этот скрипт на Python (`analyze_all.py`) представляет собой комплексный инструмент для анализа различных типов текстовых файлов, таких как PDF, DOCX, HTML и DJVU. Он позволяет проводить ряд операций с текстом, включая распознавание именованных сущностей (NER), извлечение ключевых слов, синтаксический анализ, лемматизацию и стемминг.

## Функциональные возможности
1. **Парсинг файлов**: Поддерживает чтение и извлечение текста из файлов в форматах PDF, DOCX, DOC, HTML и DJVU.
2. **Поддержка нескольких языков**: Может обрабатывать текст на китайском, английском и русском языках, автоматически определяя язык и используя соответствующие языковые модели.
3. **Распознавание именованных сущностей (NER)**: Определяет названия брендов и популярные ключевые слова в тексте.
4. **Извлечение ключевых слов**: Использует алгоритм TextRank для выделения важных ключевых слов.
5. **Синтаксический анализ**: Анализирует часть речи, зависимость и главное слово для каждого токена в тексте.
6. **Лемматизация и стемминг**: Преобразует слова в их нормальную форму (лемму) и стем (основу).

## Установка зависимостей
Перед запуском скрипта необходимо установить следующие библиотеки Python:
```bash
pip install spacy python-docx PyPDF2 beautifulsoup4 sumy langdetect jieba nltk
```
Также требуется скачать языковые модели для Spacy:
```bash
python -m spacy download zh_core_web_sm
python -m spacy download en_core_web_sm
python -m spacy download ru_core_news_sm
```
И загрузить корпус WordNet для NLTK:
```python
import nltk
nltk.download('wordnet')
```
Если вы хотите анализировать файлы в формате DJVU, необходимо установить библиотеку `pydjvu`:
```bash
pip install pydjvu
```

## Использование
1. **Подготовка файла стоп - слов**: Убедитесь, что в директории проекта есть файл `stopwords_zh.txt`, содержащий китайские стоп - слова, по одному на каждой строке.
2. **Запуск скрипта**: В терминале выполните следующую команду:
```bash
python analyze_all.py
```
3. **Ввод пути к файлу**: Введите полный путь к файлу, который вы хотите проанализировать.
4. **Просмотр результатов анализа**: Скрипт выведет распознанные названия брендов, ключевые слова и результаты синтаксического анализа.

## Структура кода
### Основные функции

#### 1. Функции парсинга файлов
- `parse_pdf(file_path)`: Парсит PDF - файл и возвращает извлеченный текст.
```python
def parse_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Ошибка анализа файла .pdf: {e}")
        return ""
```
- `parse_docx(file_path)`: Парсит DOCX и некоторые DOC - файлы и возвращает текст.
```python
def parse_docx(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        logging.error(f"Ошибка анализа файла .docx: {e}")
        return ""
```
- `parse_html(file_path)`: Парсит HTML - файл и возвращает текст.
```python
def parse_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            return text_content
    except FileNotFoundError:
        logging.error(f"файл не найден: {file_path}")
        return ""
    except Exception as e:
        logging.error(f"Ошибка анализа HTML - файла: {e}")
        return ""
```
- `parse_djvu(file_path)`: Пытается распарсить DJVU - файл (требует установки `pydjvu`).
```python
def parse_djvu(file_path):
    try:
        from pydjvu.lib import DjVuDocument
        doc = DjVuDocument(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except ImportError:
        logging.error("Библиотека pydjvu не установлена, и файлы .djvu не могут быть проанализированы.")
        return ""
    except Exception as e:
        logging.error(f"Ошибка анализа файла .djvu: {e}")
        return ""
```

#### 2. Функции анализа текста
- `ner_analysis(text)`: Выполняет NER - анализ, определяя названия брендов и ключевые слова.
```python
def ner_analysis(text):
    try:
        lang = detect(text)
        if lang == 'zh':
            nlp = spacy.load("zh_core_web_sm")
        elif lang == 'ru':
            nlp = spacy.load("ru_core_news_sm")
        else:
            nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        brand_names = []
        keywords = []
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                brand_names.append(ent.text)
        keywords = extract_keywords(text)
        return brand_names, keywords
    except Exception as e:
        logging.error(f"Ошибка при анализе NER: {e}")
        return [], []
```
- `extract_keywords(text)`: Извлекает ключевые слова с использованием алгоритма TextRank.
```python
def extract_keywords(text):
    try:
        lang = detect(text)
        if lang == 'zh' or lang == 'zh-cn':
            words = jieba.lcut(text)
            new_text = " ".join(words)
        else:
            new_text = text
        class SimpleTokenizer:
            def to_sentences(self, text):
                return text.split('.')
            def to_words(self, text):
                return text.split()
        tokenizer = SimpleTokenizer()
        parser = PlaintextParser.from_string(new_text, tokenizer)
        summarizer = TextRankSummarizer()
        sentences = summarizer(parser.document, 10)
        keywords = []
        for sentence in sentences:
            for word in sentence.words:
                if word not in STOPWORDS.get(lang, set()) and word not in keywords:
                    keywords.append(word)
        return keywords
    except Exception as e:
        logging.error(f"Ошибка при извлечении ключевых слов: {e}")
        return []
```
- `syntax_analysis(text)`: Выполняет синтаксический анализ текста.
```python
def syntax_analysis(text):
    try:
        lang = detect(text)
        if lang == 'zh':
            nlp = spacy.load("zh_core_web_sm")
        elif lang == 'ru':
            nlp = spacy.load("ru_core_news_sm")
        else:
            nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for token in doc:
            print(f"слово: {token.text}, Часть речи: {token.pos_}, Зависимости: {token.dep_}, Заглавное слово: {token.head.text}")
    except Exception as e:
        logging.error(f"Ошибка в синтаксическом анализе: {e}")
```
- `lemmatize_text(text)`: Лемматизирует текст.
```python
def lemmatize_text(text):
    lemmatizer = WordNetLemmatizer()
    words = text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(lemmatized_words)
```
- `stem_text(text)`: Стемминг текста.
```python
def stem_text(text):
    stemmer = PorterStemmer()
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words]
    return " ".join(stemmed_words)
```

#### 3. Главная функция
- `main()`: Точка входа в программу.
```python
def main():
    file_path = input("Введите путь к файлу: ")
    if not file_path or not os.path.exists(file_path):
        logging.error("Введенный путь к файлу недействителен.")
        return
    file_extension = file_path.split('.')[-1].lower()
    if file_extension == "pdf":
        text = parse_pdf(file_path)
    elif file_extension == "docx" or file_extension == "doc":
        text = parse_docx(file_path)
    elif file_extension == "html":
        text = parse_html(file_path)
    elif file_extension == "djvu":
        text = parse_djvu(file_path)
    else:
        logging.error("Неподдерживаемый тип файла.")
        return
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    if text:
        lemmatized_text = lemmatize_text(text)
        stemmed_text = stem_text(text)
        brand_names, keywords = ner_analysis(text)
        print("Признанные торговые марки:", brand_names)
        print("Определены популярные ключевые слова:", keywords)
        syntax_analysis(text)
```

## Примечания
- Убедитесь, что введенный путь к файлу корректен, в противном случае скрипт выведет ошибку.
- Если библиотека `pydjvu` не установлена, скрипт не сможет проанализировать файлы в формате DJVU.
- Во время выполнения скрипта записываются логи с уровнем INFO, которые включают время, уровень логирования и сообщение.

## Обработка ошибок
Скрипт отслеживает различные исключения и записывает ошибки в логи. В случае возникновения исключения, в терминале будет выведено сообщение об ошибке и трассировка стека.
