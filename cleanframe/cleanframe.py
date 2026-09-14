"""
Image metadata remover
by Daniel Luis
github.com/danieldluis
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

# ─── Configuração ───────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {
    '.jpg': 'Imagem', '.jpeg': 'Imagem', '.png': 'Imagem',
    '.webp': 'Imagem', '.bmp': 'Imagem', '.tiff': 'Imagem',
    '.svg': 'SVG',
}


# ─── Remoção de metadata ────────────────────────────────────────

def remove_image_metadata(input_path, output_path):
    """Remove EXIF/metadata de imagens usando Pillow."""
    img = Image.open(input_path)
    data = list(img.get_flattened_data())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    if img.mode in ('RGBA', 'LA', 'PA'):
        clean.putalpha(img.getchannel('A'))
    elif img.mode == 'P' and 'transparency' in img.info:
        img = img.convert('RGBA')
        clean = Image.new('RGBA', img.size)
        clean.putdata(list(img.getdata()))
    clean.save(output_path)
    img.close()
    clean.close()
    return output_path


def remove_svg_metadata(input_path, output_path):
    """Remove metadata de SVG (XML): comments, <metadata>, <desc>, etc."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<metadata[^>]*>.*?</metadata>', '', content, flags=re.DOTALL)
    content = re.sub(r'\s+(?:dc|dcterms|xmp|xmpmm|pdf|photoshop|crs):[\w:]+="[^"]*"', '', content)
    content = re.sub(r'\s+(?:creator|author|title|description|keywords)="[^"]*"', '', content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path


def process_file(input_path, output_dir):
    ext = os.path.splitext(input_path)[1].lower()
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base}_clean{ext}")

    if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'):
        return remove_image_metadata(input_path, output_path)
    elif ext == '.svg':
        return remove_svg_metadata(input_path, output_path)
    else:
        raise ValueError(f"Formato não suportado: {ext}")


# ─── Interface Tkinter ──────────────────────────────────────────

class MetadataRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CleanFrame")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        self.files = []
        self.output_dir = None
        self._build_ui()

    def _build_ui(self):
        frame_select = ttk.LabelFrame(self.root, text="Seleção de Arquivos", padding=10)
        frame_select.pack(fill='x', padx=10, pady=5)

        btn_frame = ttk.Frame(frame_select)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="📁 Selecionar Arquivos", command=self.select_files).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📂 Selecionar Pasta", command=self.select_folder).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Limpar Lista", command=self.clear_files).pack(side='left', padx=5)

        frame_list = ttk.LabelFrame(self.root, text="Arquivos", padding=5)
        frame_list.pack(fill='both', expand=True, padx=10, pady=5)

        self.listbox = tk.Listbox(frame_list, selectmode='extended')
        scrollbar = ttk.Scrollbar(frame_list, orient='vertical', command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        frame_output = ttk.LabelFrame(self.root, text="Saída", padding=10)
        frame_output.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_output, text="Pasta de destino:").pack(side='left')
        self.output_var = tk.StringVar()
        ttk.Entry(frame_output, textvariable=self.output_var, width=40).pack(side='left', padx=5)
        ttk.Button(frame_output, text="...", command=self.select_output_dir).pack(side='left', padx=5)

        frame_btn = ttk.Frame(self.root)
        frame_btn.pack(fill='x', padx=10, pady=10)
        self.btn_process = ttk.Button(frame_btn, text="⚡ Processar", command=self.process)
        self.btn_process.pack(side='left', padx=5)

        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=5)

        frame_log = ttk.LabelFrame(self.root, text="Log", padding=5)
        frame_log.pack(fill='both', expand=True, padx=10, pady=5)
        self.log_text = tk.Text(frame_log, height=6, state='disabled')
        log_scroll = ttk.Scrollbar(frame_log, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scroll.pack(side='right', fill='y')

    def log(self, msg):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Selecionar imagens",
            filetypes=[
                ("Imagens", " ".join(f"*{e}" for e in SUPPORTED_EXTENSIONS)),
                ("Todos", "*.*")
            ]
        )
        for f in files:
            if f not in self.files:
                self.files.append(f)
        self._update_list()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta")
        if not folder:
            return
        for f in os.listdir(folder):
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                full = os.path.join(folder, f)
                if full not in self.files:
                    self.files.append(full)
        self._update_list()

    def clear_files(self):
        self.files.clear()
        self._update_list()

    def select_output_dir(self):
        d = filedialog.askdirectory(title="Pasta de destino")
        if d:
            self.output_dir = d
            self.output_var.set(d)

    def _update_list(self):
        self.listbox.delete(0, 'end')
        for f in self.files:
            ext = os.path.splitext(f)[1].lower()
            tipo = SUPPORTED_EXTENSIONS.get(ext, '?')
            self.listbox.insert('end', f"[{tipo}] {os.path.basename(f)}")

    def process(self):
        if not self.files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return
        if not self.output_dir:
            self.output_dir = filedialog.askdirectory(title="Pasta de destino")
            if not self.output_dir:
                return
            self.output_var.set(self.output_dir)

        self.btn_process.configure(state='disabled')
        total = len(self.files)
        success = 0
        errors = []

        for i, f in enumerate(self.files):
            self.progress.configure(value=(i / total) * 100)
            self.log(f"→ Processando: {os.path.basename(f)}")
            try:
                out = process_file(f, self.output_dir)
                self.log(f"  ✓ OK → {os.path.basename(out)}")
                success += 1
            except Exception as e:
                self.log(f"  ✗ ERRO: {e}")
                errors.append((f, str(e)))

        self.progress.configure(value=100)
        self.btn_process.configure(state='normal')
        self.log(f"\n{'='*40}")
        self.log(f"Concluído: {success}/{total} imagens processadas.")
        if errors:
            self.log(f"Erros: {len(errors)}")
            for f, e in errors:
                self.log(f"  - {os.path.basename(f)}: {e}")
        messagebox.showinfo("Concluído", f"{success}/{total} imagens limpas!\n\nSaída: {self.output_dir}")


# ─── Main ───────────────────────────────────────────────────────

if __name__ == '__main__':
    root = tk.Tk()
    app = MetadataRemoverApp(root)
    root.mainloop()   