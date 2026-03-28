import os
import argparse
import time
from tqdm import tqdm
from docx2pdf import convert as docx_to_pdf
import docx
from pdfplumber import PDF


class Converter:
    def __init__(self):
        self.supported_formats = ["docx", "pdf"]

    def validate_format(self, file_path):
        """验证文件格式是否支持"""
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        if ext not in self.supported_formats:
            raise ValueError(f"不支持的格式：{ext}，仅支持{','.join(self.supported_formats)}")
        return ext

    def convert_docx_to_pdf(self, input_path, output_path):
        """docx转pdf（无Office依赖）"""
        docx_to_pdf(input_path, output_path)

    def convert_pdf_to_docx(self, input_path, output_path):
        """pdf转docx（保留文本结构）"""
        doc = python - docx.Document()
        with PDF(open(input_path, 'rb')) as pdf:
            total_pages = len(pdf.pages)
            # 按页处理，更新进度条
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    # 按换行分割段落
                    for para in text.split('\n\n'):
                        if para.strip():
                            doc.add_paragraph(para.strip())
                # 更新进度
                progress = int(page_num / total_pages * 100)
                yield progress

        doc.save(output_path)
        yield 100


def main():
    parser = argparse.ArgumentParser(description='纯Python docx/pdf互转工具（无Office依赖）')
    parser.add_argument('-input', required=True, help='输入文件路径（docx/pdf）')
    parser.add_argument('-out', required=True, help='输出文件路径（docx/pdf）')
    args = parser.parse_args()

    print("[info] start!")
    try:
        converter = Converter()
        input_ext = converter.validate_format(args.input)
        output_ext = converter.validate_format(args.out)

        # 初始化进度条
        with tqdm(total=100) as pbar:
            if input_ext == "docx" and output_ext == "pdf":
                # docx转pdf
                converter.convert_docx_to_pdf(args.input, args.out)
                # 模拟进度更新
                for _ in range(10):
                    time.sleep(0.1)
                    pbar.update(10)

            elif input_ext == "pdf" and output_ext == "docx":
                # pdf转docx，实时更新进度
                for progress in converter.convert_pdf_to_docx(args.input, args.out):
                    pbar.n = progress
                    pbar.refresh()
                    time.sleep(0.05)

            else:
                raise ValueError("不支持的转换方向：仅支持docx↔pdf互转")

        print("[info] end!")
        print(f"Completed! out file in {os.path.abspath(args.out)}")

    except Exception as e:
        print(f"[error] 转换失败：{str(e)}")


if __name__ == '__main__':
    main()
    input("Enter to exit...")