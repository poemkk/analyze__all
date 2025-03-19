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


class TestFileParsers(unittest.TestCase):
    """测试文件解析功能"""

    def setUp(self):
        # 创建测试用临时文件
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
        for f in [self.valid_pdf, self.valid_docx, self.valid_html]:
            if os.path.exists(f):
                os.remove(f)

    def test_parse_pdf_valid(self):
        text = parse_pdf(self.valid_pdf)
        self.assertIsInstance(text, str)

    def test_parse_docx_valid(self):
        text = parse_docx(self.valid_docx)
        self.assertIsInstance(text, str)

    def test_parse_html_valid(self):
        text = parse_html(self.valid_html)
        self.assertIn("Test Content", text)

    def test_parse_invalid_path(self):
        with self.assertLogs(level='ERROR') as log:
            result = parse_pdf(self.invalid_path)
        self.assertIn("file not found", log.output[0])
        self.assertEqual(result, "")


class TestAnalysisFunctions(unittest.TestCase):
    """测试分析功能"""

    def test_ner_analysis_en(self):
        text = "Apple Inc. launched iPhone 15 in California."
        brands, keywords = ner_analysis(text)
        self.assertIn("Apple Inc.", brands)
        self.assertIn("iPhone", keywords)

    def test_ner_analysis_zh(self):
        text = "Tencent has released a new version of WeChat."
        brands, keywords = ner_analysis(text)
        self.assertIn("Tencent", brands)
        self.assertIn("WeChat", keywords)

    def test_keyword_extraction_en(self):
        text = "Artificial intelligence is transforming healthcare."
        keywords = extract_keywords(text)
        expected = {"artificial", "intelligence", "healthcare"}
        self.assertTrue(expected.issubset(set(k.lower() for k in keywords)))

    def test_syntax_analysis(self):
        text = "The quick brown fox jumps."
        with patch('analyze_all.logging') as mock_logging:
            syntax_analysis(text)
            mock_logging.error.assert_not_called()


class TestMainFlow(unittest.TestCase):
    """测试主流程"""

    @patch('builtins.input', return_value='test.pdf')
    @patch('analyze_all.parse_pdf')
    def test_main_valid_flow(self, mock_parse, mock_input):
        mock_parse.return_value = "Sample text"
        with patch('analyze_all.ner_analysis') as mock_ner:
            mock_ner.return_value = (["Brand"], ["Keyword"])
            main()
            mock_parse.assert_called_once_with('test.pdf')

    @patch('builtins.input', return_value='invalid.txt')
    def test_main_invalid_type(self, mock_input):
        with self.assertLogs(level='ERROR') as log:
            main()
        self.assertIn("Unsupported file type", log.output[0])

    @patch('builtins.input', return_value='non_existent.pdf')
    def test_main_invalid_path(self, mock_input):
        with self.assertLogs(level='ERROR') as log:
            main()
        self.assertIn("The file path entered is invalid", log.output[0])


if __name__ == '__main__':
    unittest.main()