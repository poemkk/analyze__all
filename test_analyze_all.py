import unittest
import os
from unittest.mock import patch, MagicMock
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
from analyze_all import (
    parse_pdf,
    parse_docx,
    parse_html,
    ner_analysis,
    extract_keywords,
    main,
    syntax_analysis
)
# ----------------------------------------------
# 测试分析功能模块 Модуль функции анализа теста
# 验证命名实体识别（NER）、关键词提取、语法分析等核心功能
# Проверка основных функций, таких как NER, извлечение ключевых слов и грамматический анализ.
# ----------------------------------------------

class TestFileParsers(unittest.TestCase):
    """测试文件解析功能
    Тестовая функция анализа файла"""

    def setUp(self):
        # 创建测试用临时文件
        # Создайте временный файл для тестирования
        self.valid_pdf = "test.pdf"
        with open(self.valid_pdf, 'wb') as f:
            writer = PyPDF2.PdfWriter()
            page = writer.add_blank_page(width=200, height=200)
            page.add_text("Sample PDF content")  # 添加实际内容
            writer.write(f)
        self.valid_docx = "test.docx"
        doc = Document()
        doc.add_paragraph("Sample DOCX content")  # 添加段落内容
        doc.save(self.valid_docx)
        self.valid_html = "test.html"
        self.invalid_path = "non_existent.pdf"


        # 生成测试HTML内容
        with open(self.valid_html, 'w', encoding='utf-8') as f:
            f.write("<html><body>Test Content</body></html>")

    def tearDown(self):
        # 清理临时文件
        # Очистка временных файлов
        for f in [self.valid_pdf, self.valid_docx, self.valid_html]:
            if os.path.exists(f):
                os.remove(f)

    """测试有效PDF文件的解析，验证返回结果为字符串类型
    Протестируйте синтаксический анализ допустимых PDF-файлов и убедитесь,
     что возвращаемый результат имеет строковый тип.
    """
    def test_parse_pdf_valid(self):
        text = parse_pdf(self.valid_pdf)
        self.assertIsInstance(text, str)

    """测试有效DOCX文件的解析，验证返回结果为字符串类型
    Проверьте синтаксический анализ допустимого файла DOCX и убедитесь,
     что возвращаемый результат имеет строковый тип."""
    def test_parse_docx_valid(self):
        text = parse_docx(self.valid_docx)
        self.assertIsInstance(text, str)

    """测试有效HTML文件的解析，验证内容是否被正确提取
    Проверьте синтаксический анализ допустимых HTML-файлов, 
    чтобы убедиться, что содержимое извлекается правильно."""
    def test_parse_html_valid(self):
        text = parse_html(self.valid_html)
        self.assertIn("Test Content", text)

    """测试解析不存在的文件路径，验证错误日志和返回空字符串
    Тестовый анализ несуществующих путей к файлам,
     проверка регистрации ошибок и возврата пустых строк"""
    def test_parse_invalid_path(self):
        with self.assertLogs(level='ERROR') as log:
            result = parse_pdf(self.invalid_path)
        self.assertIn("file not found", log.output[0])
        self.assertEqual(result, "")

# ----------------------------------------------
# 测试分析功能模块 Модуль функции анализа теста
# 验证命名实体识别（NER）、关键词提取、语法分析等核心功能
# ----------------------------------------------
class TestAnalysisFunctions(unittest.TestCase):
    """测试分析功能"""
    """测试英文NER分析，验证品牌和关键词的识别
    Тестовый анализ NER на английском языке для проверки узнаваемости бренда и ключевых слов"""
    def test_ner_analysis_en(self):
        text = "Apple launched iPhone 15 in California."
        brands, keywords = ner_analysis(text)
        self.assertIn("Apple", brands)
        self.assertIn("iPhone", keywords)

    """测试俄语NER分析，验证品牌和关键词的识别
    Протестируйте анализ NER на русском языке для проверки узнаваемости бренда и ключевых слов"""
    def test_ner_analysis_ru(self):
        text = "Tencent выпустила новую версию WeChat."
        brands, keywords = ner_analysis(text)
        self.assertIn("Tencent", brands)
        self.assertIn("WeChat", keywords)

    """测试英文关键词提取，验证返回结果包含预期关键词
    Проверьте извлечение ключевых слов на английском языке и убедитесь, 
    что возвращенные результаты содержат ожидаемые ключевые слова."""
    def test_keyword_extraction_en(self):
        text = "Artificial intelligence is transforming healthcare."
        keywords = extract_keywords(text)
        expected = {"artificial", "intelligence", "healthcare"}
        self.assertTrue(expected.issubset(set(k.lower() for k in keywords)))

    """测试语法分析功能，验证无错误日志输出
    Протестируйте функцию синтаксического анализа и убедитесь, 
    что журнал ошибок не выводится."""
    def test_syntax_analysis(self):
        text = "The quick brown fox jumps."
        with patch('analyze_all.logging') as mock_logging:
            syntax_analysis(text)
            mock_logging.error.assert_not_called()

    def test_ner_analysis_ru2(self):
        text = "Tencent объявила об инвестициях в сферу искусственного интеллекта."
        brands, keywords = ner_analysis(text)
        self.assertIn("Tencent", brands)
        self.assertIn("интеллекта", keywords)
    def test_ner_analysis_ru3(self):
        text = "Apple выпустила новый iPhone."
        brands, keywords = ner_analysis(text)
        self.assertIn("Apple", brands)
        self.assertIn("iPhone", keywords)


if __name__ == '__main__':
    unittest.main()