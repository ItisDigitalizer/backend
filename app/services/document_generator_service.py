from docx import Document
import pandas as pd
import zipfile
import io
from pathlib import Path
from typing import List, Dict
from loguru import logger


class DocumentGeneratorService:
    OUTPUT_DIR = Path.cwd() / "templates/output"
    OUTPUT_DIR.mkdir(exist_ok=True)

    def excel_to_dicts(self, excel_content: bytes) -> List[Dict]:
        """Excel bytes → list[dict]"""
        df = pd.read_excel(io.BytesIO(excel_content))
        return df.to_dict("records")

    def fill_docx_template(self, template_path: str, data: Dict, output_path: str):
        """Заполняет один DOCX"""
        doc = Document(template_path)

        # Параграфы
        for paragraph in doc.paragraphs:
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                if placeholder in paragraph.text:
                    paragraph.text = paragraph.text.replace(placeholder, str(value))

        # Таблицы
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for key, value in data.items():
                        placeholder = f"{{{key}}}"
                        if placeholder in cell.text:
                            cell.text = cell.text.replace(placeholder, str(value))

        doc.save(output_path)

    async def generate_documents(
        self,
        template_path: str,
        data_list: List[Dict],
        process_id: str,  # для GenerationProcess.id
    ) -> str:
        """Генерирует документы/ZIP → возвращает путь для скачивания"""
        output_dir = self.OUTPUT_DIR / process_id
        output_dir.mkdir(exist_ok=True)

        if len(data_list) == 1:
            output_path = output_dir / "document.docx"
            self.fill_docx_template(template_path, data_list[0], str(output_path))
            logger.info(f"Создан 1 документ: {output_path}")
            return str(output_path)
        else:
            zip_path = output_dir / "documents.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for i, data in enumerate(data_list):
                    temp_path = output_dir / f"temp_{i + 1}.docx"
                    self.fill_docx_template(template_path, data, str(temp_path))
                    zipf.write(temp_path, f"document_{i + 1}.docx")
                    temp_path.unlink()
            logger.info(f"Создан ZIP: {zip_path} ({len(data_list)} файлов)")
            return str(zip_path)
